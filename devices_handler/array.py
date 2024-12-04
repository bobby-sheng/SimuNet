#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
from command_handler.command_handler import CommandHandler
from modles.mock_ssh_models import DeviceBaseInfo, DeviceInfo


class ArrayCommandHandler(CommandHandler):
    def __init__(self, device_mock_config: DeviceInfo):
        super().__init__(device_mock_config)
        self.info = DeviceBaseInfo(
            vendor="array",
            model="ag",
            version="9.6.0",
            description="Cisco Base Plugin"
        )
        self.switch_vsys_prompt = None

    @property
    def is_selective(self):
        if self.info.vendor + self.info.model + self.info.version == \
                self.device_mock_config.vendorName + self.device_mock_config.typeName + self.device_mock_config.versionName:
            return True

    async def switch_mode(self, prompt, command):
        mode_map = self.mode_map
        if command == "switch vpndg":
            if prompt.endswith(mode_map.enable):
                self.switch_vsys_prompt = mode_map.enable
                return mode_map.vsys_enable
            elif prompt.endswith(mode_map.config):
                self.switch_vsys_prompt = mode_map.config
                return mode_map.vsys_config
            else:
                raise ValueError(f"{prompt} Mode Not Find")

        if command == "configure terminal":
            if prompt.endswith(mode_map.vsys_enable):
                return mode_map.vsys_config

        for mode_cmd in self.switch_mode_map:
            if mode_cmd.cmd == command:
                return mode_cmd.response
        return prompt

    async def exit_mode(self, prompt, command, process):
        if command in self.exit_list:
            mode_map = self.mode_map
            if prompt.endswith(mode_map.login):
                process.exit(0)
            elif prompt.endswith(mode_map.enable):
                prompt = self.mode_map.login
            elif prompt.endswith(mode_map.config):
                prompt = self.mode_map.enable
            elif prompt.endswith(mode_map.vsys_config):
                prompt = self.mode_map.vsys_enable
            elif prompt.endswith(mode_map.vsys_enable):
                prompt = self.switch_vsys_prompt
            else:
                raise ValueError(f"{prompt} Mode Not Find")
            return prompt
        else:
            return prompt

    async def enable_password(self, prompt, command):
        if not command and prompt == "Enable password:":
            prompt = self.mode_map.enable
        return prompt

    @staticmethod
    async def cmd_ignore():
        return ["exit"]
