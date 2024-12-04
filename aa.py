#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
import requests

headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
}
# command = ["aa", "aa20", "aa2", "aa3", "aa4", "aa5", "aa6", "aa7", "aa8", "aa9", "aa10", "aa11", "aa12", "aa13", "aa14", "aa15", "aa16", "aa17"]
# for i in command:
json_data = {
    'protocol': 'ssh',
    'ip': '192.168.10.160',
    'port': 8020,
    'username': 'admin',
    'password': 'r00tme',
    'enable_password': '',
    'vendor': 'array',
    'model': 'ag',
    'version': '9.4.0',
    'encode': 'utf-8',
    'vsys': 'default',
    'commands': [
        {
            'type': 'raw',
            'mode': 'enable',
            'command': "aa18",
            'template': 'Value UPTIME ((\\d+\\s\\w+.s.,?\\s?){4})\nValue LAST_REBOOT_REASON (.+)\nValue BIOS (\\d+.\\d+(.+)?)\nValue OS (\\d+.\\d+(.+)?)\nValue BOOT_IMAGE (.*)\nValue PLATFORM (\\w+)\nValue HOSTNAME (.*)\nValue SERIAL (\\w+)\n\nStart\n  ^\\s+(BIOS:\\s+version)\\s+${BIOS}\\s*$$\n  ^\\s+(NXOS: version|system:\\s+version)\\s+${OS}\\s*$$\n  ^\\s+(NXOS|kickstart)\\s+image\\s+file\\s+is:\\s+${BOOT_IMAGE}\\s*$$\n  ^\\s+cisco\\s+${PLATFORM}\\s+[cC]hassis\n  ^\\s+cisco\\s+Nexus\\d+\\s+${PLATFORM}\n  # Cisco N5K platform\n  ^\\s+cisco\\s+Nexus\\s+${PLATFORM}\\s+[cC]hassis\n  ^\\s+Device\\s+name:\\s+${HOSTNAME}$$\n  ^\\s+cisco\\s+.+-${PLATFORM}\\s*\n  # Nexus intel platform uses Board ID as serial/license\n  ^\\s*Processor\\s[Bb]oard\\sID\\s+${SERIAL}$$\n  ^Kernel\\s+uptime\\s+is\\s+${UPTIME}\n  ^\\s+Reason:\\s${LAST_REBOOT_REASON} -> Record\n',
        },
    ],
    'timeout': 10,
}

response = requests.post('http://192.168.30.98:8000/api/v1/cmd', headers=headers, json=json_data).json()
print(response)
assert response['code'] == 'R0010'
print(f"command: a18 code: {response['code']}|   msg: {response['msg']}")
