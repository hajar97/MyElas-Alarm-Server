## Alarm Server
## Supporting MyElas
## Written by ehajiyev@gmail.com
##
## This code is under the terms of the GPL v3 license.

elas_ResponseTypes = {
    100 : {'name' : "partition ready", 'description' : 'MyElas Panel Ready', 'type' : 'panel'},
    110 : {'name' : "partition notready", 'description' : 'MyElas Panel Not Ready', 'type' : 'panel'},
    120 : {'name' : "partition armed", 'description' : 'MyElas Panel Armed', 'type' : 'panel'},
    130 : {'name' : "partition partarmed", 'description' : 'MyElas Panel Partarmed', 'type' : 'panel'},
    140 : {'name' : "partition alarm", 'description' : 'MyElas Panel Alarm', 'type' : 'panel'},
    200 : {'name' : "zone inactive", 'description' : 'Motion Zone Ready', 'type' : 'zone'},
    210 : {'name' : "zone active", 'description' : 'Motion Zone Active', 'type' : 'zone'},
    220 : {'name' : "zone bypassed", 'description' : 'Motion Zone Bypassed', 'type' : 'zone'},
    230 : {'name' : "zone alarm", 'description' : 'Motion Zone Alarm', 'type' : 'zone'},
    300 : {'name' : "zone closed", 'description' : 'Entry Zone Closed', 'type' : 'zone'},
    310 : {'name' : "zone open", 'description' : 'Entry Zone Open', 'type' : 'zone'},
    320 : {'name' : "zone bypassed", 'description' : 'Entry Zone Bypassed', 'type' : 'zone'},
    330 : {'name' : "zone alarm", 'description' : 'Entry Zone Alarm', 'type' : 'zone'},
    400 : {'name' : "zone clear", 'description' : 'Smoke Clear', 'type' : 'zone'},
    410 : {'name' : "zone smoke", 'description' : 'Smoke Alarm', 'type' : 'zone'},
    420 : {'name' : "zone bypassed", 'description' : 'Smoke Bypassed', 'type' : 'zone'},
    500 : {'name' : "zone clear", 'description' : 'Water Clear', 'type' : 'zone'},
    510 : {'name' : "zone water", 'description' : 'Water Alarm', 'type' : 'zone'},
    520 : {'name' : "zone bypassed", 'description' : 'Water Bypassed', 'type' : 'zone'},
    600 : {'name' : "zone clear", 'description' : 'Gas Clear', 'type' : 'zone'},
    610 : {'name' : "zone carbonMonoxide", 'description' : 'Gas Alarm', 'type' : 'zone'},
    620 : {'name' : "zone bypassed", 'description' : 'Gas Bypassed', 'type' : 'zone'},
  }
