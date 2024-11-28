#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
from command_handler.command_handler import CommandHandler
from modles.mock_ssh_models import DeviceBaseInfo, DeviceInfo


class CiscoCommandHandler(CommandHandler):
    def __init__(self, device_mock_config: DeviceInfo):
        super().__init__(device_mock_config)
        self.info = DeviceBaseInfo(
            vendor="cisco",
            model="ASA",
            version="9.6.0",
            description="Cisco ASA Plugin"
        )

    @property
    def is_as_device(self) -> bool:
        if self.info.vendor + self.info.model + self.info.version == \
                self.device_mock_config.vendorName + self.device_mock_config.typeName + self.device_mock_config.versionName:
            return True

    async def switch_mode(self, prompt, command) -> str:
        mode_map_data = await self.convert_to_dict(self.cmd_config.switch_mode_map)
        if command in mode_map_data:
            prompt = mode_map_data[command]
        else:
            raise ValueError(f"{command} Not Find")
        return prompt

    async def exit_mode(self, prompt, command, process) -> str:
        if command in self.exit_list:
            mode_map = self.mode_map
            if prompt.endswith(mode_map.login):
                process.exit(0)
            elif prompt.endswith(mode_map.enable):
                prompt = self.mode_map.login
            elif prompt.endswith(mode_map.config):
                prompt = self.mode_map.enable
            else:
                raise ValueError(f"{prompt} Mode Not Find")
            return prompt
        else:
            return prompt

    async def enable_password(self, prompt, command) -> str:
        if not command and prompt == "Password:":
            prompt = self.mode_map.enable
        return prompt

    @staticmethod
    async def cmd_ignore() -> list:
        return ["exit", "end"]
