/*
 *  MyElas Zone Device
 *
 *  Author: Elnar Hajiyev <ehajiyev@gmail.com>
 *  Date: 2015-11-17
 */

// for the UI
metadata {
  definition (name: "MyElas Zone Entry", author: "ehajiyev@gmail.com") {
    // Change or define capabilities here as needed
    capability "Refresh"
    capability "Contact Sensor"
    capability "Polling"

    // Add commands as needed
    command "zone"
  }

  simulator {
    // Nothing here, you could put some testing stuff here if you like
  }

  tiles {
    // Main Row
    standardTile("zone", "device.contact", width: 2, height: 2, canChangeBackground: true, canChangeIcon: true) {
      state "closed", label: '${name}', icon: "st.contact.contact.closed", backgroundColor: "#79b821"
      state "open",   label: '${name}', icon: "st.contact.contact.open",   backgroundColor: "#ffa81e"
      state "bypassed", label: '${name}', icon: "st.contact.contact.open", backgroundColor: "#ffffff"
      state "alarm",  label: '${name}', icon: "st.contact.contact.open",   backgroundColor: "#ff0000"
    }

    // This tile will be the tile that is displayed on the Hub page.
    main "zone"

    // These tiles will be displayed when clicked on the device, in the order listed here.
    details(["zone"])
  }
}

// handle commands
def zone(String state) {
  // state will be a valid state for a zone (open, closed)
  // zone will be a number for the zone
  log.debug "Zone: ${state}"
  sendEvent (name: "contact", value: "${state}")
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