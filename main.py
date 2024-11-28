#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
import yaml
from fastapi import FastAPI
from simunet.mock_ssh_devices import MockSshDevice

MOCKSSHCONFIGPATH = "simunet/mock_ssh_config.yaml"

app = FastAPI()


async def run_ssh_server(port, device_mock_config):
    device = MockSshDevice(port=port)
    device.device_mock_config = device_mock_config
    return device


@app.on_event("startup")
async def startup_event():
    with open(MOCKSSHCONFIGPATH, 'r', encoding='utf-8') as data:
        data_list = yaml.safe_load(data)
        # 确保 data_list 是一个列表
    if not isinstance(data_list, list):
        raise ValueError("YAML data should be a list of devices info")

    # 启动所有 SSH 服务
    servers_list = []
    for server_devices in data_list:
        device = await run_ssh_server(server_devices.get('port'), server_devices)
        servers_list.append(device)
        await device.__aenter__()  # 启动 SSH 服务

    # 保存服务器列表，以便在关闭事件中使用
    app.state.servers_list = servers_list


@app.on_event("shutdown")
async def shutdown_event():
    # 停止所有 SSH 服务
    for server in app.state.servers_list:
        await server.__aexit__(None, None, None)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
