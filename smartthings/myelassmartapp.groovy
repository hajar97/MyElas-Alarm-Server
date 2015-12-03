/*
 *  MyElas Alarm Panel integration via REST API callbacks
 *
 *  Author: Elnar Hajiyev <ehajiyev@gmail.com>
 */

definition(
    name: "MyElas Integration",
    namespace: "",
    author: "Elnar Hajiyev <ehajiyev@gmail.com>",
    description: "MyElas Integration App",
    category: "My Apps",
    iconUrl: "https://s3.amazonaws.com/smartapp-icons/SafetyAndSecurity/App-MindYourHome.png",
    iconX2Url: "https://s3.amazonaws.com/smartapp-icons/SafetyAndSecurity/App-MindYourHome@2x.png",
    oauth: true
)

import groovy.json.JsonBuilder

preferences {

  section("Alarm Panel:") {
    input "paneldevices", "capability.polling", title: "MyElas Alarm Panel (required)", multiple: false, required: false
  }
  section("Zone Devices:") {
    input "zonedevices", "capability.polling", title: "MyElas Zone Devices (required)", multiple: true, required: false
  }
  section("Notifications (optional) - NOT WORKING:") {
    input "sendPush", "enum", title: "Push Notifiation", required: false,
      metadata: [
       values: ["Yes","No"]
      ]
    input "phone1", "phone", title: "Phone Number", required: false
  }
  section("Notification events (optional):") {
    input "notifyEvents", "enum", title: "Which Events?", description: "default (none)", required: false, multiple: false,
     options:
      ['all','panelready','panelnotready','panelarmed','panelpartarmed','panelalarm'
      ]
  }

  section("Modes") {
    input "awayModes", "mode",
        title:      "Arm 'Away' in these Modes",
        multiple:   true,
        required:   false

    input "stayModes", "mode",
        title:      "Partarm in these Modes",
        multiple:   true,
        required:   false

    input "disarmModes", "mode",
        title:      "Disarm in these Modes",
        multiple:   true,
        required:   false
  }
}

mappings {
  path("/panel/:eventcode/:zoneorpart") {
    action: [
      GET: "updateZoneOrPanel"
    ]
  }
  path("/panel/:eventcode/:zoneorpart/:message") {
    action: [
      GET: "updateZoneOrPanel"
    ]
  }
}

def installed() {
  log.debug "Installed!"
  atomicState.lastMode = location.mode;
  subscribe(location, "mode", modeChangeHandler)
  subscribe(location, "alarmSystemStatus", alarmHandler)
}

def updated() {
  log.debug "Updated!"
  atomicState.lastMode = location.mode;
  subscribe(location, "mode", modeChangeHandler)
  subscribe(location, "alarmSystemStatus", alarmHandler)
}

void updateZoneOrPanel() {
  update()
}

private update() {
    def zoneorpanel = params.zoneorpart
    def message = params.message

    // Add more events here as needed
    // Each event maps to a command in your "MyElas Panel" device type
    def eventMap = [
      '100':"panel ready",
      '110':"panel notready",
      '120':"panel armed",
      '130':"panel partarmed",
      '140':"panel alarm",
      '200':"zone inactive",
      '210':"zone inactive",
      '220':"zone bypassed",
      '230':"zone alarm",
      '300':"zone closed",
      '310':"zone open",
      '320':"zone bypassed",
      '330':"zone alarm",
      '400':"zone clear",
      '410':"zone smoke",
      '420':"zone bypassed",
      '500':"zone clear",
      '510':"zone water",
      '520':"zone bypassed",
      '600':"zone clear",
      '610':"zone carbonMonoxide",
      '620':"zone bypassed"
    ]

    // get our passed in eventcode
    def eventCode = params.eventcode
    if (eventCode)
    {
      // Lookup our eventCode in our eventMap
      def opts = eventMap."${eventCode}"?.tokenize()
      // log.debug "Options after lookup: ${opts}"
      // log.debug "Zone or panel: $zoneorpanel"
      if (opts[0])
      {
        // We have some stuff to send to the device now
        // this looks something like panel.zone("open", "1")
        // log.debug "Test: ${opts[0]} and: ${opts[1]} for $zoneorpanel"
        if ("${opts[0]}" == 'zone') {
           //log.debug "It was a zone...  ${opts[1]}"
           updateZoneDevices(zonedevices,"$zoneorpanel","${opts[1]}", message)
        }
        if ("${opts[0]}" == 'panel') {
           //log.debug "It was a zone...  ${opts[1]}"
           updatePanelDevices(paneldevices, "$zoneorpanel","${opts[1]}", message)
        }
      }
    }
}

private updateZoneDevices(zonedevices,zonenum,zonestatus,zonemessage) {
  log.debug "zonedevices: $zonedevices - ${zonenum} is ${zonestatus}"
  // log.debug "zonedevices.id are $zonedevices.id"
  // log.debug "zonedevices.displayName are $zonedevices.displayName"
  // log.debug "zonedevices.deviceNetworkId are $zonedevices.deviceNetworkId"
  def zonedevice = zonedevices.find { it.deviceNetworkId == "zone${zonenum}" }
  if (zonedevice) {
      log.debug "Was True... Zone Device: $zonedevice.displayName at $zonedevice.deviceNetworkId is ${zonestatus}"
      //Was True... Zone Device: Front Door Sensor at zone1 is closed
      zonedevice.zone("${zonestatus}")
      if (zonemessage != null) {
        log.debug "Sending push notification: ${zonemessage}"
        sendMessage(zonemessage)
      }
    }
}

private updatePanelDevices(paneldevices, panelnum, panelstatus, panelmessage) {
  log.debug "paneldevices: $paneldevices - ${panelnum} is ${panelstatus}"
  def paneldevice = paneldevices.find { it.deviceNetworkId == "panel${panelnum}" }
  if (paneldevice) {
    log.debug "Was True... Panel device: $paneldevice.displayName at $paneldevice.deviceNetworkId is ${panelstatus}"
    //Was True... Zone Device: Front Door Sensor at zone1 is closed
   	paneldevice.panel("${panelstatus}", "${panelnum}")
    if(panelstatus == "armed" && location.currentState("alarmSystemStatus")?.value != "away") {
    	log.debug "Changing mode to Away"
        atomicState.lastMode = "Away"
        sendLocationEvent(name: "alarmSystemStatus", value: "away")
    }
    else if(panelstatus == "partarmed" && location.currentState("alarmSystemStatus")?.value != "stay") {
    	log.debug "Changing mode to Night"
        atomicState.lastMode = "Night"
        sendLocationEvent(name: "alarmSystemStatus", value: "stay")
    }
    else if(panelstatus == "ready" && location.currentState("alarmSystemStatus")?.value != "off") {
    	log.debug "Changing mode to Home"
        atomicState.lastMode = "Home"
        sendLocationEvent(name: "alarmSystemStatus", value: "off")
    }
    if (panelmessage != null) {
        log.debug "Sending push notification: ${panelmessage}"
        sendMessage(panelmessage)
    }
  }
}

def modeChangeHandler(evt) {
    log.debug "MyElas mode changed from ${atomicState.lastMode} to ${evt.value}"

    String mode = evt.value
    //Only take action if lastMode is not the same as new mode
    if(atomicState.lastMode != mode) {
    	if (settings.awayModes?.contains(mode)) {
    	   paneldevices.each {
              log.debug("Arming... ${it.deviceNetworkId}"-"panel")
              it.arm()
           }
    	} else if (settings.stayModes?.contains(mode)) {
           paneldevices.each {
              log.debug("Partarming... ${it.deviceNetworkId}"-"panel")
              it.partarm()
           }
    	} else if (settings.disarmModes?.contains(mode)) {
           paneldevices.each {
              log.debug("Disarming... ${it.deviceNetworkId}"-"panel")
              it.disarm()
           }
    	}

    atomicState.lastMode = mode
    }
}

def alarmHandler(evt) {
  log.debug "MyElas home monitor mode changed to : ${evt.value}"

  if(evt.value == "away" && location.mode != "Away")
  	location.setMode("Away")
  if(evt.value == "stay" && location.mode != "Night")
  	location.setMode("Night")
  if(evt.value == "off" && location.mode != "Home")
  	location.setMode("Home")
}

private sendMessage(msg) {
    def newMsg = "Alarm Notification: $msg"
    if (phone1) {
        sendSms(phone1, newMsg)
    }
    if (sendPush == "Yes") {
        sendPush(newMsg)
    }
}