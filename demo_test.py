#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
from enum import Enum
a= ["CiscoASA>", "CiscoASA#", "CiscoASA(config)#"]

class CommandType(Enum):
    EXIT = 'exit'
    HISTORY = 'history'
    UNSUPPORTED = 'unsupported'
    CISCO_ENABLE_PASSWORD = 'Password:'
    ARRAY_ENABLE_PASSWORD = 'Enable password:'




if "Enable password:" in CommandType.name:
    print("unsupported")