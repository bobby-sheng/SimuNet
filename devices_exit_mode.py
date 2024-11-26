#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>

import asyncssh

EXIT_MAPPING_TABLE = {"CiscoASA>": "cisco_asa_960",
                      "hostname>": "cisco_asa_960",

                      }


class ExitMode:
    def __init__(self, process: asyncssh.SSHServerProcess,
                 command,
                 login_prompt,
                 prompt,
                 exit_map,
                 CommandType,
                 mode_level):

        self.process = process
        self.command = command
        self.prompt = prompt
        self.login_prompt = login_prompt
        self.exit_map = exit_map
        self.CommandType = CommandType
        self.mode_level = mode_level

    async def cisco_asa_960(self):
        if self.prompt != self.login_prompt and self.command in self.exit_map:
            self.prompt = self.mode_level[self.mode_level.index(self.prompt) - 1]
            self.process.stdout.write(self.prompt)
        elif self.prompt == self.login_prompt and self.command == self.CommandType.EXIT.value:
            self.process.exit(0)
        else:
            self.process.stdout.write("Mode Unsupported Exit\n")
            self.process.stdout.write(self.prompt)
        return self.prompt

    async def handle_exit(self):
        # 根据当前提示符查找相应的处理函数
        exit_function_name = EXIT_MAPPING_TABLE.get(self.login_prompt)
        if exit_function_name and hasattr(self, exit_function_name):
            exit_function = getattr(self, exit_function_name)
            return await exit_function()
        else:
            self.process.stdout.write("No exit function found for the current prompt.\n")
            self.process.stdout.write(self.prompt)
            return self.prompt
