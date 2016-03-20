#!/usr/bin/python
## Alarm Server
## Supporting MyElas
## Written by donnyk+envisalink@gmail.com
## Rewritten by ehajiyev@gmail.com
##
## This code is under the terms of the GPL v3 license.


import asyncore, asynchat
import ConfigParser
import datetime
import os, socket, string, urlparse, ssl
import StringIO, mimetools
import json
import time
import getopt
import requests
import threading
import logging
import logging.handlers
import argparse
import sys

from MyElasDefs import elas_ResponseTypes

class CodeError(Exception): pass

ALARMSTATE={'version' : 0.1, 'devices' : {}}
MAXZONES=64

def getMessageType(code):
    return elas_ResponseTypes[code]

# Make a class we can use to capture stdout and sterr in the log
class MyLogger(object):
        def __init__(self, logger, level):
                """Needs a logger and a logger level."""
                self.logger = logger
                self.level = level

        def write(self, message):
                # Only log if there is a message (not just a new line)
                if message.rstrip() != "":
                        self.logger.log(self.level, message.rstrip())

class AlarmServerConfig():
    def __init__(self, configfile):

        self._config = ConfigParser.ConfigParser()
        self._config.read(configfile)

        self.LOGURLREQUESTS = self.read_config_var('alarmserver', 'logurlrequests', True, 'bool')
        self.ALARMSERVERPORT = self.read_config_var('alarmserver', 'port', 8111, 'int')
        self.ALARMSERVERSSL = self.read_config_var('alarmserver', 'ssl', False, 'bool')
        self.POLLRATE = self.read_config_var('alarmserver', 'pollrate', 60, 'int')
        self.PANELNUMBER = self.read_config_var('alarmserver', 'panelnumber', 1, 'int')
        self.CERTFILE = self.read_config_var('alarmserver', 'certfile', 'server.crt', 'str')
        self.KEYFILE = self.read_config_var('alarmserver', 'keyfile', 'server.key', 'str')
        self.MAXNUMRETRIES = self.read_config_var('alarmserver', 'MAXNUMRETRIES', 3, 'int')
        self.MYELASHOST = self.read_config_var('myelas', 'host', 'myelas', 'str')
        self.MYELASUSER = self.read_config_var('myelas', 'user', 'user', 'str')
        self.MYELASPASS = self.read_config_var('myelas', 'pass', 'pass', 'str')
        self.ALARMCODE = self.read_config_var('myelas', 'alarmcode', 1111, 'int')
        self.CALLBACKURL_BASE = self.read_config_var('alarmserver', 'callbackurl_base', '', 'str')
        self.CALLBACKURL_APP_ID = self.read_config_var('alarmserver', 'callbackurl_app_id', '', 'str')
        self.CALLBACKURL_ACCESS_TOKEN = self.read_config_var('alarmserver', 'callbackurl_access_token', '', 'str')
        self.CALLBACKURL_EVENT_CODES = self.read_config_var('alarmserver', 'callbackurl_event_codes', '', 'str')

        self.ZONENAMES={}
        for i in range(1, MAXZONES+1):
            self.ZONENAMES[i]=self.read_config_var('alarmserver', 'zone'+str(i), False, 'str', True)

    def defaulting(self, section, variable, default, quiet = False):
        if quiet == False:
            print('Config option '+ str(variable) + ' not set in ['+str(section)+'] defaulting to: \''+str(default)+'\'')

    def read_config_var(self, section, variable, default, type = 'str', quiet = False):
        try:
            if type == 'str':
                return self._config.get(section,variable)
            elif type == 'bool':
                return self._config.getboolean(section,variable)
            elif type == 'int':
                return int(self._config.get(section,variable))
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            self.defaulting(section, variable, default, quiet)
            return default

class HTTPChannel(asynchat.async_chat):
    def __init__(self, server, sock, addr):
        asynchat.async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator("\r\n\r\n")
        self.header = None
        self.data = ""
        self.shutdown = 0

    def collect_incoming_data(self, data):
        self.data = self.data + data
        if len(self.data) > 16384:
        # limit the header size to prevent attacks
            self.shutdown = 1

    def found_terminator(self):
        if not self.header:
            # parse http header
            fp = StringIO.StringIO(self.data)
            request = string.split(fp.readline(), None, 2)
            if len(request) != 3:
                # badly formed request; just shut down
                self.shutdown = 1
            else:
                # parse message header
                self.header = mimetools.Message(fp)
                self.set_terminator("\r\n")
                self.server.handle_request(
                    self, request[0], request[1], self.header
                    )
                self.close_when_done()
            self.data = ""
        else:
            pass # ignore body data, for now

    def pushstatus(self, status, explanation="OK"):
        self.push("HTTP/1.0 %d %s\r\n" % (status, explanation))

    def pushok(self, content):
        self.pushstatus(200, "OK")
        self.push('Content-type: application/json\r\n')
        self.push('Expires: Sat, 26 Jul 1997 05:00:00 GMT\r\n')
        self.push('Last-Modified: '+ datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' GMT\r\n')
        self.push('Cache-Control: no-store, no-cache, must-revalidate\r\n' ) 
        self.push('Cache-Control: post-check=0, pre-check=0\r\n') 
        self.push('Pragma: no-cache\r\n' )
        self.push('\r\n')
        self.push(content)

    def pushfile(self, file):
        self.pushstatus(200, "OK")
        extension = os.path.splitext(file)[1]
        if extension == ".html":
            self.push("Content-type: text/html\r\n")
        elif extension == ".js":
            self.push("Content-type: text/javascript\r\n")
        elif extension == ".png":
            self.push("Content-type: image/png\r\n")
        elif extension == ".css":
            self.push("Content-type: text/css\r\n")
        self.push("\r\n")
        self.push_with_producer(push_FileProducer(sys.path[0] + os.sep + 'html' + os.sep + file))

class MyElasClient(requests.Session):
    def __init__(self, config):
        # Call parent class's __init__ method
        requests.Session.__init__(self)

        # Set config
        self._config = config

        # Set running
        self._running = True

        self.do_connect()
        self.panelStatusUpdate()

    def do_connect(self):
        logger.info("Connecting to %s" % (self._config.MYELASHOST))
        
        self.post(self._config.MYELASHOST, data = {'username':self._config.MYELASUSER, 'password':self._config.MYELASPASS, 'code':str(self._config.ALARMCODE)})
        response = self.post('https://www.myelas.com/ELAS/WebUI/Security/GetCPState')
        
        json_object = response.json()
        error = json_object['error']
        
        # Everything went well
        if error == 0:
            logger.info("Connected to %s" % (self._config.MYELASHOST))
        else:
            logger.error("Failed to connect to %s" % (self._config.MYELASHOST))

        return error

    def handle_close(self):
        self._running = False
        self.close()
        logger.info("Disconnected from %s" % (self._config.MYELASHOST))

    def send_command(self, url, commandtype, passcode, bypassZoneId, retry = 0):
        if(retry > self._config.MAXNUMRETRIES):
            return

        if url == 'https://www.myelas.com/ELAS/WebUI/Security/GetCPState': # Its a poll command
            to_send = {'IsAlive':'true'}
            logger.info('TX > ' + url + ' -> ' + str(to_send))
            response = self.post(url, to_send)
        else:
            to_send = {'type':commandtype, 'passcode':passcode, 'bypassZoneId':bypassZoneId}
            logger.info('TX > ' + url + ' -> ' + str(to_send))
            response = self.post(url, to_send)
        
        LATESTALARMSTATE = response.json()
        logger.info(str(LATESTALARMSTATE))
        error = LATESTALARMSTATE.get('error', 0)
        error_message = ''
        isOffline = LATESTALARMSTATE.get('IsOffline', False)
        failedToUpdate = LATESTALARMSTATE.get('overview') is None

        if isOffline is True or error == 3:
            error_message = 'System went offline'
        if isOffline is True or error != 0:
            logger.error("Error: %s" % (error_message))
            error = self.do_connect()
            if(error == 0): self.send_command(url, commandtype, passcode, bypassZoneId, retry + 1)
            return

        if failedToUpdate is True:
            logger.error('Failed to get panel update.')
        else:
            logger.info("Command executed successfully.")
            # if command is to refresh/poll panel state then handle update
            self.handle_update(LATESTALARMSTATE)
            logger.info("Command handled successfully.")


    def handle_update(self, LATESTALARMSTATE):
        partInfo = LATESTALARMSTATE['overview']['partInfo']
        panel_not_ready = False
        lastAlarms = LATESTALARMSTATE['overview']['lastAlarms']
        bypassed = LATESTALARMSTATE['overview']['bypassed']
        detectors = LATESTALARMSTATE['detectors']['parts'][0]['detectors']
        
        # from received information first handle each zone update
        for detector in detectors:
            id = detector['id'] + 1
            name = detector['name']
            bypassed = detector['bypassed']
            filter = detector['filter']

            if 'DOOR' in name: # This is an entry detector
                code = 300 # door is closed
                if filter == 'triggered' : code = 310 # door is open
                if bypassed is True : code = 320 # door is bypassed
                if code == 310 : panel_not_ready = True
            elif 'FIRE' in name: # This is a smoke detector
                code = 400
                if filter == 'triggered' : code = 410 # smoke is detected/tested
                if bypassed is True : code = 420
            elif 'FLOOD' in name: # This is a water leak detector
                code = 500
                if filter == 'triggered' : code = 510 # flood is detected/tested
                if bypassed is True : code = 520
            elif 'GAS' in name: # This is a carbon monoxide gas detector
                code = 600
                if filter == 'triggered' : code = 610 # gas is detected/tested
                if bypassed is True : code = 620
            else: # This is a motion or generic detector
                code = 200
                if filter == 'triggered' : code = 210 # motion is detected/tested
                if bypassed is True : code = 220
            zone_number = id
            event = getMessageType(code)

            # Handle zone event
            logger.info("Handle zone event: " + str(code) + ", from zone: " + name)
            self.handle_event(code, zone_number, event)

        # next from received information handle panel update
        # compare previous state with the new state to avoid unnecessary updates to SmartThings
        # to know the state of the panel full processing of all zones is needed
        # for example, to know if code is notready if zone is open, or code is alarm if one of the
        # zones is alarmed

        if(panel_not_ready):
            code = 110
        elif('Yes' in partInfo['armedStr']):
            code = 120
        elif('Yes' in partInfo['disarmedStr']):
            code = 100
        elif('Yes' in partInfo['partarmedStr']):
            code = 130
        else:
            return

        event = getMessageType(code)
        message = ''
        # If there were any errors arming, send them as push notification
        if LATESTALARMSTATE.get('armFailures') is not None:
            message = LATESTALARMSTATE['armFailures']['text']
            logger.info("Arm failure message recorded: " + message)

        # Handle panel event
        logger.info("Handle panel event: " + str(code))
        self.handle_event(code, self._config.PANELNUMBER, event, message)

        # TODO: Test other states of zones apart from the two implemented
        # TODO: Find a way of arming panel from iOS app
        # TODO: Find a way of warning user after 10 mins of house switching to Away and panel is not armed
        # TODO: Make passwords to be not stored in plain text
        # TODO: Make disarming require an ALARMCODE that is provided through SmartThings


    def panelStatusUpdate(self):
        # Only run as long as we are running
        if(self._running is True):
            threading.Timer(self._config.POLLRATE, self.panelStatusUpdate).start()
            self.send_command('https://www.myelas.com/ELAS/WebUI/Security/GetCPState', None, None, None)

    def handle_event(self, code, zone_or_panel_number, event, message = ''):
        panel_state_changed = False
        network_id = event['type'] + str(zone_or_panel_number)
        if network_id not in ALARMSTATE['devices']:
            ALARMSTATE['devices'][network_id] = code
            panel_state_changed = True
        elif ALARMSTATE['devices'][network_id] != code:
            ALARMSTATE['devices'][network_id] = code
            panel_state_changed = True

        if panel_state_changed is True:
            self.callbackurl_event(code, zone_or_panel_number, event, message)

    def callbackurl_event(self, code, zone_or_panel_number, event, message):
        myEvents = self._config.CALLBACKURL_EVENT_CODES.split(',')
        # Determin what events we are sending to smartthings then send if we match
        if str(code) in myEvents:
           # Now check if Zone has a custom name, if it does then send notice to Smartthings
           # Check for event type
           if event['type'] == 'panel':
               logger.info("Callback message: " + message);
               myURL = self._config.CALLBACKURL_BASE + "/" + self._config.CALLBACKURL_APP_ID + "/panel/" + str(code) + "/" + str(zone_or_panel_number) + \
                       "/" + message + "?access_token=" + self._config.CALLBACKURL_ACCESS_TOKEN
               logger.info("Executing callback: " + myURL)
           elif event['type'] == 'zone':
             # Is our zone setup with a custom name, if so we care about it
             if self._config.ZONENAMES[zone_or_panel_number]:
               myURL = self._config.CALLBACKURL_BASE + "/" + self._config.CALLBACKURL_APP_ID + "/panel/" + str(code) + "/" + str(zone_or_panel_number) + "?access_token=" + self._config.CALLBACKURL_ACCESS_TOKEN
             else:
               # We don't care about this zone
               return
           else:
             # Unhandled event type..
             return

           # If we made it here we should send to Smartthings
           try:
             # Note: I don't currently care about the return value, fire and forget right now
             requests.get(myURL)
             #print "myURL: ", myURL
             #print "Exit code: ", r.status_code
             #print "Response data: ", r.text
             time.sleep(0.5)
           except:
             print sys.exc_info()[0]

class push_FileProducer:
    # a producer which reads data from a file object

    def __init__(self, file):
        self.file = open(file, "rb")

    def more(self):
        if self.file:
            data = self.file.read(2048)
            if data:
                return data
            self.file = None
        return ""

class AlarmServer(asyncore.dispatcher):
    def __init__(self, config):
        # Call parent class's __init__ method
        asyncore.dispatcher.__init__(self)

        # Create MyElas client object
        self._myelasclient = MyElasClient(config)

        #Store config
        self._config = config

        # Create socket and listen on it
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(("0.0.0.0", config.ALARMSERVERPORT))
        self.listen(5)

    def handle_accept(self):
        # Accept the connection
        conn, addr = self.accept()
        if (config.LOGURLREQUESTS):
            logger.info('Incoming web connection from %s' % repr(addr))

        try:
            if(config.ALARMSERVERSSL is False):
                # HTTP Connection
                HTTPChannel(self, conn, addr)
            else:
                # HTTPS Connection
                HTTPChannel(self, ssl.wrap_socket(conn, server_side=True, certfile=config.CERTFILE, keyfile=config.KEYFILE, ssl_version=ssl.PROTOCOL_TLSv1), addr)
        except ssl.SSLError:
            return

    def handle_request(self, channel, method, request, header):
        if (config.LOGURLREQUESTS):
            logger.info('Web request: '+str(method)+' '+str(request))

        query = urlparse.urlparse(request)
        query_array = urlparse.parse_qs(query.query, True)

        if query.path == '/':
            channel.pushfile('index.html')
        elif query.path == '/api/alarm/status':
            channel.pushok(json.dumps(ALARMSTATE))
        elif query.path == '/api/alarm/arm':
            channel.pushok(json.dumps({'response' : 'Request to arm received'}))
            self._myelasclient.send_command('https://www.myelas.com/ELAS/WebUI/Security/ArmDisarm', '-1:armed', '------', '-1')
        elif query.path == '/api/alarm/partarm':
            channel.pushok(json.dumps({'response' : 'Request to part arm received'}))
            self._myelasclient.send_command('https://www.myelas.com/ELAS/WebUI/Security/ArmDisarm', '-1:partially', '------', '-1')
        elif query.path == '/api/alarm/disarm':
            channel.pushok(json.dumps({'response' : 'Request to disarm received'}))
            self._myelasclient.send_command('https://www.myelas.com/ELAS/WebUI/Security/ArmDisarm', '-1:disarmed', str(self._config.ALARMCODE), '-1')
        elif query.path == '/api/refresh':
            channel.pushok(json.dumps({'response' : 'Request to refresh data received'}))
            self._myelasclient.send_command('https://www.myelas.com/ELAS/WebUI/Security/GetCPState', None, None, None)
        elif query.path == '/favicon.ico':
            channel.pushfile('favicon.ico')
        else:
            if len(query.path.split('/')) == 2:
                try:
                    with open(sys.path[0] + os.sep + 'html' + os.sep + query.path.split('/')[1]) as f:
                        f.close()
                        channel.pushfile(query.path.split('/')[1])
                except IOError as e:
                    print "I/O error({0}): {1}".format(e.errno, e.strerror)
                    channel.pushstatus(404, "Not found")
                    channel.push("Content-type: text/html\r\n")
                    channel.push("File not found")
                    channel.push("\r\n")
            else:
                if (config.LOGURLREQUESTS):
                    logger.error("Invalid file requested")

                channel.pushstatus(404, "Not found")
                channel.push("Content-type: text/html\r\n")
                channel.push("\r\n")

    def handle_close(self):
        self._myelasclient.handle_close()
        self.close()

def usage():
    print 'Usage: '+sys.argv[0]+' -c <configfile>'

def main(argv):
    try:
      opts, args = getopt.getopt(argv, "hc:", ["help", "config="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--config"):
            global conffile
            conffile = arg

if __name__=="__main__":
    # Deafults
    CONFIG_FILENAME = "AlarmServer.cfg"
    LOG_FILENAME = "/tmp/AlarmServer.log"
    LOG_LEVEL = logging.INFO

    # Define and parse command line arguments
    parser = argparse.ArgumentParser(description="MyElas Alarm Server")
    parser.add_argument("-c", "--config", help="file to read configuration from (default '" + CONFIG_FILENAME + "')")
    parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

    # If the config or log file is specified on the command line then override the default
    args = parser.parse_args()
    if args.log:
        LOG_FILENAME = args.log
    if args.config:
        CONFIG_FILENAME = args.config

    # Configure logging to log to a file, making a new file at midnight and keeping the last 3 day's data
    # Give the logger a unique name (good practice)
    logger = logging.getLogger(__name__)
    # Set the log level to LOG_LEVEL
    logger.setLevel(LOG_LEVEL)
    # Make a handler that writes to a file, making a new file at midnight and keeping 3 backups
    handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
    # Format each log message like this
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    # Attach the formatter to the handler
    handler.setFormatter(formatter)
    # Attach the handler to the logger
    logger.addHandler(handler)
    # Read configuration
    config = AlarmServerConfig(CONFIG_FILENAME)

    # Replace stdout with logging to file at INFO level
    sys.stdout = MyLogger(logger, logging.INFO)
    # Replace stderr with logging to file at ERROR level
    sys.stderr = MyLogger(logger, logging.ERROR)

    logger.info('Alarm Server Starting')
    logger.info('Currently Supporting MyElas only')
    logger.info('Tested on a COMMPACT')

    server = AlarmServer(config)

    try:
        while True:
            asyncore.loop(timeout=2, count=1)
            # insert scheduling code here.
    except KeyboardInterrupt:
        logger.info("Crtl+C pressed. Shutting down.")

        # server.shutdown(socket.SHUT_RDWR)
        server.handle_close()
        sys.exit()
