#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
import abc
import yaml
import aiofiles
from pydantic import parse_obj_as
from typing import List, Dict

from modles.mock_ssh_models import CmdResList, DeviceInfo, DeviceBaseInfo, ModeMap, CommandResponse


class CommandHandler(abc.ABC):
    def __init__(self, device_mock_config: DeviceInfo):
        self.device_mock_config = device_mock_config
        self.info = DeviceBaseInfo(
            vendor="base",
            model="base",
            version="base",
            description="Base Plugin"
        )
        self.cmd_config = CmdResList
        self.mode_map = ModeMap
        self.exit_list = []
        self.login = CommandResponse
        self.enable = CommandResponse
        self.config = CommandResponse
        self.switch_mode_map = CommandResponse
        self.vsys_enable = CommandResponse
        self.vsys_config = CommandResponse
        self.prompt = None

    @abc.abstractmethod
    def is_as_device(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def switch_mode(self, prompt, command):
        raise NotImplementedError

    @abc.abstractmethod
    async def exit_mode(self, prompt, command, process):
        raise NotImplementedError

    @abc.abstractmethod
    async def enable_password(self, prompt, command):
        raise NotImplementedError

    @abc.abstractmethod
    async def cmd_ignore(self) -> list:
        raise NotImplementedError

    async def get_login_mode(self):
        return self.mode_map.login

    async def initialize(self):
        file_path = self.device_mock_config.config_file_name
        self.cmd_config = await self.read_and_parse_file(file_path)
        self.mode_map = self.cmd_config.mode_map
        self.exit_list = self.cmd_config.exit_list
        self.login = self.cmd_config.login
        self.enable = self.cmd_config.enable
        self.config = self.cmd_config.config
        self.switch_mode_map = self.cmd_config.switch_mode_map
        try:
            self.vsys_enable = self.cmd_config.vsys_enable
            self.vsys_config = self.cmd_config.vsys_config
        except:
            pass
        return self.cmd_config

    @staticmethod
    async def convert_to_dict(command_responses: List[CommandResponse]) -> Dict[str, str]:
        return {cr.cmd: cr.response for cr in command_responses}

    @staticmethod
    async def read_and_parse_file(filename: str):
        async with aiofiles.open(f"mockssh_mode_config/{filename}", 'r', encoding='utf-8') as file:
            content = await file.read()
            data = yaml.safe_load(content)
            return CmdResList(**data)

    async def get_mode_cmd(self, prompt):
        mode_map = self.mode_map.dict()
        for mode, attr_name in mode_map.items():
            if prompt.endswith(attr_name):
                return parse_obj_as(list[CommandResponse], getattr(self, mode))
        raise ValueError(f"{prompt} Mode Not Found")

    async def exec_cmd(self, prompt, command, process):
        self.prompt = prompt
        ignore = await self.cmd_ignore()

        if "password" in self.prompt.lower():
            self.prompt = await self.enable_password(self.prompt, command)
        # 命令为空，直接返回
        if not command:
            return self.prompt

        mode_cmd_data = await self.convert_to_dict(await self.get_mode_cmd(self.prompt))

        # 命令是否存在模型下的命令列表
        if command in mode_cmd_data and command not in ignore:
            response = mode_cmd_data[command]
            if response != "switch_mode":
                process.stdout.write(self.prompt + response + "\n")
            else:
                command = command
        elif command in ignore:
            command = command
        else:
            process.stdout.write("CmdRes Unsupported\n")
            return self.prompt

        mode_map_data = await self.convert_to_dict(self.cmd_config.switch_mode_map)
        # 命令是否为切换命令、退出命令
        if command in mode_map_data:
            self.prompt = await self.switch_mode(self.prompt, command)
        # 命令是否为退出命令
        if command in self.exit_list:
            self.prompt = await self.exit_mode(self.prompt, command, process)

        return self.prompt
