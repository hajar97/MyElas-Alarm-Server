/*
 *  MyElas Zone Water
 *
 *  Author: Elnar Hajiyev <ehajiyev@gmail.com>
 *  Date: 2015-11-17
 */

// for the UI
metadata {
  definition (name: "MyElas Zone Water", author: "ehajiyev@gmail.com") {
    // Change or define capabilities here as needed
    capability "Refresh"
    capability "Water Sensor"
    capability "Sensor"
    capability "Polling"

    attribute "alarmState", "string"
    // Add commands as needed
    command "zone"
  }

  simulator {
    // Nothing here, you could put some testing stuff here if you like
  }

  tiles {
    // Main Row
    standardTile("zone", "device.alarmState", width: 2, height: 2, canChangeBackground: true, canChangeIcon: true) {
      state "dry",  label: 'dry',  icon: "st.alarm.water.dry", backgroundColor: "#ffffff"
      state "wet",  label: 'WET',  icon: "st.alarm.water.wet", backgroundColor: "#e86d13"
      state "bypassed",  label: 'bypassed',  icon: "st.alarm.water.wet", backgroundColor: "#ffffff"
    }

    // This tile will be the tile that is displayed on the Hub page.
    main "zone"

    // These tiles will be displayed when clicked on the device, in the order listed here.
    details(["zone"])
  }
}

// handle commands
def zone(String state) {
  def text = null
  def results = []
  // state will be a valid state for a zone (open, closed)
  // zone will be a number for the zone
  log.debug "Zone: ${state}"

  if (state == "wet") {
        text = "$device.displayName water leak was detected!"
        log.debug "$text"
        // these are displayed:false because the composite event is the one we want to see in the app
        sendEvent(name: "water", value: "wet", descriptionText: text, displayed: false)

  } else if (state == "dry") {
        text = "$device.displayName water leak is clear"
        log.debug "$text"
        sendEvent(name: "water", value: "dry", descriptionText: text, displayed: false)
  }

  // Send final event?
  sendEvent (name: "alarmState", value: "${newState}")
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