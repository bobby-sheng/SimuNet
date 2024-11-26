#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
import sys
import socket
import json
import asyncio
import asyncssh
from typing import Optional
import logging.config
from enum import Enum
from devices_exit_mode import ExitMode

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)
USER_DATABASE = {
    'admin': 'r00tme',
    'user': 'r00tme'
}


class CommandType(Enum):
    EXIT = 'exit'
    HISTORY = 'history'
    UNSUPPORTED = 'unsupported'
    CISCO_ENABLE_PASSWORD = 'Password:'
    ARRAY_ENABLE_PASSWORD = 'Enable password:'


class MockSshDevice(asyncssh.SSHServer):
    """ Create mock SSH-device """

    def __init__(self, port: int = 8022):
        self._port = port
        self._prompt = ""
        self._cmd_resp_map = {}
        self._switch_mode_map = {}
        self._exit_map = []
        self._mode_level = []
        self._ssh_acceptor = None

    def connection_made(self, conn: asyncssh.SSHServerConnection):
        logging.info(f"SSH connection received from {conn.get_extra_info('peername')[0]}")

    def password_auth_supported(self) -> bool:
        return True

    def validate_password(self, username: str, password: str) -> bool:
        return USER_DATABASE.get(username) == password

    def connection_lost(self, exc: Optional[Exception]):
        if exc:
            logging.info('SSH connection error: ' + str(exc), file=sys.stderr)
        else:
            logging.info('SSH connection closed')

    def begin_auth(self, username: str) -> bool:
        # Without authentication
        return True

    @property
    def port(self) -> int:
        """ Get used SSH-port """
        return self._port

    @property
    def prompt(self) -> str:
        """ Get device prompt """
        return self._prompt

    @prompt.setter
    def prompt(self, value: str):
        """ Set device prompt """
        if type(value) is not str:
            raise RuntimeError("MockSshDevice.prompt must be of type string")

        self._prompt = value

    @property
    def cmd_resp_map(self) -> dict:
        """ Get command to response map """
        return self._cmd_resp_map

    @property
    def switch_mode_map(self) -> dict:
        """ Get command to response map """
        return self._switch_mode_map

    @property
    def exit_map(self) -> list:
        """ Get command to response map """
        return self._exit_map

    @property
    def mode_level(self) -> list:
        """ Get command to response map """
        return self._mode_level

    @cmd_resp_map.setter
    def cmd_resp_map(self, value: dict):
        """ Set command to response map """
        if type(value) is not dict:
            raise RuntimeError("MockSshDevice.cmd_resp_map must be of type dict")
        # All keys must be non-empty strings
        if not all(isinstance(key, str) and key for key in value.keys()):
            raise RuntimeError("MockSshDevice.cmd_resp_map must not contain empty commands")

        # Process each command, removing leading and trailing new lines & spaces in commands & their responses
        cleaned_value = {}
        for cmd, cmd_info in value.items():
            cleaned_cmd = cmd.strip()
            cleaned_response = cmd_info['response'].strip()
            cleaned_mode = cmd_info['mode']
            cleaned_value[cleaned_cmd] = {'response': cleaned_response, 'mode': cleaned_mode}

        self._cmd_resp_map = cleaned_value

    @switch_mode_map.setter
    def switch_mode_map(self, value: dict):
        """ Set command to response map """
        if type(value) is not dict:
            raise RuntimeError("MockSshDevice.cmd_resp_map must be of type dict")
        # All keys must be non-empty strings
        if not all(value.keys()):
            raise RuntimeError("MockSshDevice.cmd_resp_map must not contain empty commands")

        # Remove leading and trailing new lines & spaces in commands & their responses
        value = {cmd.strip(): response.strip() for cmd, response in value.items()}

        self._switch_mode_map = value

    @exit_map.setter
    def exit_map(self, value: dict):
        """ Set command to response map """
        self._exit_map = value

    @mode_level.setter
    def mode_level(self, value: dict):
        """ Set command to response map """
        self._mode_level = value

    async def handle_request(self, process: asyncssh.SSHServerProcess):
        """ Handle incoming SSH-request """
        _history = []  # 重置命令历史
        prompt = self.prompt
        if prompt:
            process.stdout.write(prompt)

        try:
            async for command in process.stdin:
                command = command.rstrip('\n')
                logging.info(f"输入命令：{command}")

                # 捕获退出，exit作为login模式close session，其他的命令作为模式切换返回上级
                if command in self._exit_map or command == CommandType.EXIT.value:
                    exit_mode = ExitMode(process=process,
                                         command=command,
                                         login_prompt=self.prompt,
                                         prompt=prompt,
                                         exit_map=self._exit_map,
                                         CommandType=CommandType,
                                         mode_level=self._mode_level
                                         )
                    prompt = await exit_mode.handle_exit()
                    continue
                elif command == CommandType.HISTORY.value:
                    process.stdout.write('\n'.join(_history) + '\n')
                    process.stdout.write(prompt)
                    continue

                # 将命令添加到历史记录
                _history.append(command)

                # enable 密码处理
                if prompt in [CommandType.ARRAY_ENABLE_PASSWORD.value, CommandType.CISCO_ENABLE_PASSWORD.value]:
                    prompt = self.switch_mode_map[prompt]
                    process.stdout.write(prompt)
                    continue

                # 获取切换模式，指定命令捕获完成后将prompt设置为指定的模式字符
                if command in self.switch_mode_map:
                    if self.switch_mode_map[command]:
                        prompt = self.switch_mode_map[command]
                        process.stdout.write(prompt)
                        continue

                # 指定指令处理，返回预先写好的响应，有做可在此模式下执行的判断
                if command in self.cmd_resp_map:
                    if self.cmd_resp_map[command]:
                        if prompt in self.cmd_resp_map[command]["mode"]:
                            process.stdout.write(prompt + self.cmd_resp_map[command]["response"] + '\n')
                        else:
                            process.stdout.write("Mode Unsupported CmdRes\n")
                elif command == '':
                    pass
                else:
                    process.stdout.write("CmdRes Unsupported Command\n")

                process.stdout.write(prompt)

        except asyncssh.BreakReceived:
            process.stdout.write('\n')
            process.exit(0)
        except Exception as e:
            # 其他所有异常的通用处理
            logging.error(f"An unexpected error occurred: {e}")
            # 这里可以进行一些清理工作或者提供一些默认的处理
            process.exit(0)
        finally:
            process.close()

    async def start(self):
        """ Start mock SSH-device """
        self._ssh_acceptor = await asyncssh.create_server(
            MockSshDevice,
            '',
            self.port,
            family=socket.AF_INET,  # IPv4 socket
            server_host_keys=['keys/private_key'],
            trust_client_host=True,
            process_factory=self.handle_request
        )
        logging.info(f"ssh服务启动：{self._ssh_acceptor.get_addresses()}")

    async def stop(self):
        """ Stop mock SSH-device """
        self._ssh_acceptor.close()
        await self._ssh_acceptor.wait_closed()

    async def __aenter__(self):
        await self.start()

    async def __aexit__(self, exc_type, exc, tb):
        await self.stop()


async def run_ssh_server(port, prompt, cmd_resp_map, switch_mode_map, exit_map, mode_level):
    device = MockSshDevice(port=port)
    device.prompt = prompt
    device.cmd_resp_map = cmd_resp_map
    device.switch_mode_map = switch_mode_map
    device.exit_map = exit_map
    device.mode_level = mode_level
    await device.__aenter__()  # Start the SSH server
    return device


async def main():
    with open('asycn_ssh_config.json', 'r', encoding='utf-8') as data:
        data_list = json.load(data)
    servers_list = [run_ssh_server(
        server_devices["port"],
        server_devices["prompt"],
        server_devices["cmd_resp_map"],
        server_devices["switch_mode_map"],
        server_devices["exit_map"],
        server_devices["mode_level"]) for
        server_devices in data_list]

    await asyncio.gather(*servers_list)  # 并发启动所有服务器
    await asyncio.sleep(360000)


if __name__ == '__main__':
    asyncio.run(main())
