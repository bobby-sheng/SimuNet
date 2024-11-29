#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
import socket
import asyncssh
from typing import Optional
import logging.config
from command_handler.command_handler_factory import CommandHandlerFactory


logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)
USER_DATABASE = {
    'admin': 'r00tme',
    'user': 'r00tme'
}


class MockSshDevice(asyncssh.SSHServer):
    """ Create mock SSH-device """

    def __init__(self, port: int = 8022):
        self._port = port
        self._device_mock_config = {}
        self._ssh_acceptor = None

    def connection_made(self, conn: asyncssh.SSHServerConnection):
        peer_name = conn.get_extra_info('peername')
        client_ip, client_port = peer_name[0], peer_name[1]
        logging.info(f"SSH connection received from {client_ip}:{client_port}")

    def password_auth_supported(self) -> bool:
        return True

    def validate_password(self, username: str, password: str) -> bool:
        return USER_DATABASE.get(username) == password

    def connection_lost(self, exc: Optional[Exception]):
        if exc:
            logging.error('SSH connection error: %s', exc)
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
    def device_mock_config(self) -> dict:
        """ Get device prompt """
        return self._device_mock_config

    @device_mock_config.setter
    def device_mock_config(self, value: dict):
        """ Set device prompt """
        self._device_mock_config = value

    async def handle_request(self, process: asyncssh.SSHServerProcess):
        """ Handle incoming SSH-request """
        _history = []  # 重置命令历史

        # 创建命令处理器
        try:
            command_handler = await CommandHandlerFactory.create_handler(self._device_mock_config)
            # 获取login prompt
            prompt = await command_handler.get_login_mode()
            process.stdout.write(prompt)
        except Exception as e:
            process.stdout.write(f"An unexpected error occurred: {e}")
            raise ValueError(f"An unexpected error occurred: {e}")

        try:
            async for command in process.stdin:
                command = command.rstrip('\n')
                device_info = command_handler.info
                logging.info(f"[{device_info.vendor}:{device_info.model}:{device_info.version}] --> 输入命令：{command}")

                prompt = await command_handler.exec_cmd(prompt, command, process)

                if command == "history":
                    process.stdout.write('\n'.join(_history) + '\n')
                _history.append(command)

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