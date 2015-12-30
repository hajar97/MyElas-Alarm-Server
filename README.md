# MyElas-Alarm-Server
----

Author: Elnar Hajiyev \<ehajiyev at gmail dot com\>
Based on the original code of the [AlarmServer](https://github.com/juggie/AlarmServer) by the community of creative networkers. 

Smartthings code for [MyElas](https://www.myelas.com) (or [Electronics Line](http://www.electronics-line.com)) alarm panels via REST API

Smartthings support is beta, so install at your own risk. Follow the rough steps below to get it setup. 

### Configure Smartthings to support MyElas integration

#### Setup a Smartthings developer account at:

* EU: [https://graph-eu01-euwest1.api.smartthings.com](https://graph-eu01-euwest1.api.smartthings.com)
* USA: [https://graph.api.smartthings.com](https://graph.api.smartthings.com)

#### Setup Smartthings device types

Using the Smartthings IDE create 6 new device types using the code from the smartthings directory.

There are 6 types of devices you can create:

* MyElas Panel                 - (Shows panel status info)
* MyElas Zone Carbone Monoxide - (Carbon monoxide detector: clear/GAS/bypassed)
* MyElas Zone Entry            - (Contact sensor: closed/open/ALARM/bypassed)
* MyElas Zone Motion           - (Motion sensor: ready/motion/ALARM/bypassed)
* MyElas Zone Smoke            - (Smoke detector: clear/SMOKE/bypassed)
* MyElas Zone Water            - (Water sensor: dry/WET/bypassed)

In the Web IDE for Smartthings create a new device type for each of the above devices and paste in the code for each device from the corresponding groovy files in the 
[repo](https://github.com/hajar97/MyElas-Alarm-Server/tree/master/smartthings).
You can name them whatever you like, but it is recommended to use the names above since those names directly identify what they do.
For all the device types make sure you save them and then publish them for yourself.

#### Create panel device

Create a new device and choose the type of "MyElas Panel" that you published earlier. The network id needs to be **partition1**.

#### Create individual zones
Create a new "Zone Device" for each Zone you want Smartthings to show you status for. 

The network id needs to be the word 'zone' followed by the matching zone number that your panel system sees it as.

For example: **zone1** or **zone5**

#### Create smart app
Create a new Smartthings App in the IDE, call it 'MyElas Integration' or whatever you like. 
Use the code from 'myelassmartapp.groovy' file for the new smartapp.
Click "Enable OAuth in Smart App" and copy down the generated "OAuth Client ID" and the "OAuth Client Secret", you will need them later to generate an access code.
Click "Create" and when the code section comes up select all the text and replace it with the code from the file 'myelassmartapp.groovy'.
Click "Save" then "Publish" -> "For Me".

#### Create Smartthings callback URL for smart app:
For details on how to do that follow these instructions:

* [http://docs.smartthings.com/en/latest/smartapp-web-services-developers-guide/authorization.html](http://docs.smartthings.com/en/latest/smartapp-web-services-developers-guide/authorization.html)
* [https://github.com/kholloway/smartthings-dsc-alarm/blob/master/RESTAPISetup.md](https://github.com/kholloway/smartthings-dsc-alarm/blob/master/RESTAPISetup.md)

Note that to configure callback URL in EU you will need to replace all references to graph.api.smartthings.com with graph-eu01-euwest1.api.smartthings.com. 

### Install AlarmServer on your server/computer/Raspberry Pi

This code was tested on Electronics Line [CommPact](http://www.electronics-line.com/products/product/1392) panels via [MyElas REST API](https://www.myelas.com) (Last tested on 30/12/2015).

    git clone https://github.com/hajar97/MyElas-Alarm-Server.git
    cd MyElas-Alarm-Server

Python 2.X is required. Project requires at least one additional Python module as shown below.
Install the required requests python module:

    pip install requests

#### Configure AlarmServer

Copy AlarmServerExample.cfg to AlarmServer.cfg and configure key configuration parameters.

OpenSSL certificate files server.crt and server.key are not provided. To generate a self signed cert issue the following in a command prompt:
`openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout server.key -out server.crt`

Openssl will ask you some questions. The only semi-important one is the 'common name' field. 
You want this set to your servers fqdn, e.g. alarmserver.example.com. 
If you have a real ssl cert from a certificate authority and it has intermediate certs then you'll 
need to bundle them all up or the webbrowser will complain about it not being a valid cert. 
To bundle the certs use cat to include your cert, then the intermediates (ie cat mycert.crt > combined.crt; cat intermediates.crt >> combined.crt) 

List all zones available in your panel. 

Update Smartthings app ID and access token in callback URL section.
 
Finally provide MyElas account details and alarm code

#### Run AlarmServer

Test run AlarmServer.py and make sure you don't get any errors:

    ./AlarmServer.py

AlarmServer should work at this point and not complain about anything and you should be able to open a web browser up to your computer/server on HTTP port 8111 and see the AlarmServer web page.

#### AlarmServer REST API Info

*/api/alarm/status*

* Returns a JSON dump of all zones and their statuses
 
*/api/alarm/arm*

* Full arm panel

*/api/alarm/partarm*

* Part arm panel

*/api/alarm/disarm*

* Disarm panel

*/api/refresh*

* Refresh data from alarm panel

#### AlarmServer Launcher
File 'alarmserver.sh' contains a script that allows running AlarmServer as a linux service. Feel free to use it if and as necessary.
