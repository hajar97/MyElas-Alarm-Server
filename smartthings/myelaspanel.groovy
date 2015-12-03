/*
 *  MyElas Panel
 *
 *  Author: Elnar Hajiyev <ehajiyev@gmail.com>
 *  Date: 2015-11-17
 */

// for the UI
metadata {
  // Automatically generated. Make future change here.
  definition (name: "MyElas Panel", author: "Elnar Hajiyev <ehajiyev@gmail.com>") {
    // Change or define capabilities here as needed
    capability "Refresh"
    capability "Polling"
    //capability "Switch"

    // Add commands as needed
    command "panel"
    command "arm"
    command "partarm"
    command "disarm"

    preferences {
      input("ip", "string", title:"IP Address", description: "IP Address of MyElas Alarm Server", required: true, displayDuringSetup: true)
      input("port", "string", title:"Port", description: "Port of MyElas Alarm Server", required: true, displayDuringSetup: true)
      input("alarmcode", "string", title:"Alarm Code", description: "Code to arm/disarm MyElas", required: true, displayDuringSetup: true)
    }
  }

  simulator {
    // Nothing here, you could put some testing stuff here if you like
  }

  tiles {
    standardTile("myelaspanel", "device.myelaspanel", width: 2, height: 2, canChangeBackground: true, canChangeIcon: true) {
      state "armed",     label: 'Armed',        backgroundColor: "#79b821", icon:"st.Home.home3"
      state "partarmed", label: 'Part\nArmed',  backgroundColor: "#79b821", icon:"st.Home.home3"
      state "notready",  label: 'Open',         backgroundColor: "#ffcc00", icon:"st.Home.home2"
      state "ready",     label: 'Ready',        backgroundColor: "#79b821", icon:"st.Home.home2"
      state "alarm",     label: 'Alarm',        backgroundColor: "#ff0000", icon:"st.Home.home3"
    }
    //standardTile("arm", "device.switch", decoration: "flat", canChangeIcon: false) {
    //    state "default", label:'Arm', action:"arm", icon:"st.Home.home3", backgroundColor:"#ffffff"
    //}
    //standardTile("partarm", "device.switch", decoration: "flat", canChangeIcon: false) {
    //    state "default", label:'Partarm', action:"partarm", icon:"st.Home.home4", backgroundColor:"#ffffff"
    //}
    //standardTile("disarm", "device.switch", decoration: "flat", canChangeIcon: false) {
    //    state "default", label:'Disarm', action:"disarm", icon:"st.Home.home2", backgroundColor:"#ffffff"
    //}

    main "myelaspanel"
    details(["myelaspanel"])

    // These tiles will be displayed when clicked on the device, in the order listed here.
    // details(["arm", "partarm", "disarm"])
  }
}

// parse events into attributes
def parse(String description) {
  log.debug "Parsing '${description}'"
  def myValues = description.tokenize()

  log.debug "Parsing LAN message"
  def msg = parseLanMessage(description)

  log.debug "Event Parse function: ${description}"
  sendEvent (name: "${myValues[0]}", value: "${myValues[1]}")
}

def panel(String state, String panel) {
    // state will be a valid state for the panel (ready, notready, armed, etc)
    // panel will be a panel number, for most users this will always be 1

    log.debug "State: ${state} for panel: ${panel}"
    sendEvent (name: "myelaspanel", value: "${state}")
}

def arm() {
	log.trace "ARM"
    //sendEvent(name:"myelaspanel", value: "armed", displayed: true)
    sendEvent(name:"Command", value: "Arm", displayed: true)

    def hostAddress = getHostAddress()
    log.trace "Callback address: ${hostAddress}"
    def result = new physicalgraph.device.HubAction(
        method: "PUT",
        path: "/api/alarm/arm",
        headers: [
            HOST: hostAddress
        ]
        )

    log.trace result
    return result
}

def partarm() {
	log.trace "PARTARM"
    //sendEvent(name:"myelaspanel", value: "partarmed", displayed: true)
    sendEvent(name:"Command", value: "Partarm", displayed: true)

    def hostAddress = getHostAddress()
    log.trace "Callback address: ${hostAddress}"
    def result = new physicalgraph.device.HubAction(
        method: "PUT",
        path: "/api/alarm/partarm",
        headers: [
            HOST: hostAddress
        ]
        )

    log.trace result
    return result
}

def disarm() {
	log.trace "DISARM"
    //sendEvent(name:"myelaspanel", value: "ready", displayed: true)
    sendEvent(name:"Command", value: "Disarm", displayed: true)

    def hostAddress = getHostAddress()
    log.trace "Callback address: ${hostAddress}"
    def result = new physicalgraph.device.HubAction(
        method: "PUT",
        path: "/api/alarm/disarm",
        headers: [
            HOST: hostAddress
        ]
        )

    log.trace result
    return result
}

// gets the address of the device
private getHostAddress() {
    //def ip = getDataValue("ip")
    //def port = getDataValue("port")

    if (!ip || !port) {
        def parts = device.deviceNetworkId.split(":")
        if (parts.length == 2) {
            ip = parts[0]
            port = parts[1]
        } else {
            log.warn "Can't figure out ip and port for device: ${device.id}"
        }
    }

    log.debug "Using IP: $ip and port: $port for device: ${device.id}"
    return ip + ":" + port
}

def poll() {
  log.debug "Executing 'poll'"
  // TODO: handle 'poll' command
  // On poll what should we do? nothing for now..
}

def refresh() {
  log.debug "Executing 'refresh' which is actually poll()"
  poll()
  // TODO: handle 'refresh' command
}