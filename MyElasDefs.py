## Alarm Server
## Supporting MyElas
## Written by ehajiyev@gmail.com
##
## This code is under the terms of the GPL v3 license.

elas_ResponseTypes = {
    100 : {'name' : "partition ready", 'description' : 'MyElas Panel Ready'},
    110 : {'name' : "partition notready", 'description' : 'MyElas Panel Not Ready'},
    120 : {'name' : "partition armed", 'description' : 'MyElas Panel Armed'},
    130 : {'name' : "partition partarmed", 'description' : 'MyElas Panel Partarmed'},
    140 : {'name' : "partition alarm", 'description' : 'MyElas Panel Alarm'},
    200 : {'name' : "zone inactive", 'description' : 'Motion Zone Ready'},
    210 : {'name' : "zone active", 'description' : 'Motion Zone Active'},
    220 : {'name' : "zone bypassed", 'description' : 'Motion Zone Bypassed'},
    230 : {'name' : "zone alarm", 'description' : 'Motion Zone Alarm'},
    300 : {'name' : "zone closed", 'description' : 'Entry Zone Closed'},
    310 : {'name' : "zone open", 'description' : 'Entry Zone Open'},
    320 : {'name' : "zone bypassed", 'description' : 'Entry Zone Bypassed'},
    330 : {'name' : "zone alarm", 'description' : 'Entry Zone Alarm'},
    400 : {'name' : "zone clear", 'description' : 'Smoke Clear'},
    410 : {'name' : "zone smoke", 'description' : 'Smoke Alarm'},
    420 : {'name' : "zone bypassed", 'description' : 'Smoke Bypassed'},
    500 : {'name' : "zone clear", 'description' : 'Water Clear'},
    510 : {'name' : "zone water", 'description' : 'Water Alarm'},
    520 : {'name' : "zone bypassed", 'description' : 'Water Bypassed'},
    600 : {'name' : "zone clear", 'description' : 'Gas Clear'},
    610 : {'name' : "zone carbonMonoxide", 'description' : 'Gas Alarm'},
    620 : {'name' : "zone bypassed", 'description' : 'Gas Bypassed'},
  }
