#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
import yaml
import uvicorn
import asyncio
from fastapi import FastAPI
from simunet.mock_ssh_devices import MockSshDevice

MOCKSSHCONFIGPATH = "simunet/mock_ssh_config.yaml"

app = FastAPI()


def create_ssh_server(port, device_mock_config):
    device = MockSshDevice(port=port)
    device.device_mock_config = device_mock_config
    return device


async def on_startup() -> None:
    """ put all post up logic here """
    try:
        with open(MOCKSSHCONFIGPATH, 'r', encoding='utf-8') as data:
            data_list = yaml.safe_load(data)
            # 确保 data_list 是一个列表
        if not isinstance(data_list, list):
            raise ValueError("YAML data should be a list of devices info")

        # 启动所有 SSH 服务
        devices = []
        for server_devices in data_list:
            device = create_ssh_server(server_devices.get('port'), server_devices)
            devices.append(device)

        startup_tasks = [device.start() for device in devices]
        await asyncio.gather(*startup_tasks)

        # 保存服务器列表，以便在关闭事件中使用
        app.state.servers_list = devices
    except Exception as e:
        raise


async def on_shutdown() -> None:
    """ put all clean logic here """
    try:
        # 停止所有 SSH 服务
        for server in app.state.servers_list:
            await server.stop()
    except Exception as e:
        raise


# 在 app 实例上注册事件处理器
app.add_event_handler("startup", on_startup)
app.add_event_handler("shutdown", on_shutdown)


def start():
    uvicorn.run("main:app", host="0.0.0.0", port=7011, reload=True)

