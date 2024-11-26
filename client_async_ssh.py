#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
from main import connect_to_ssh_server_assert, connect_to_ssh_server_write
import asyncio


async def connections():
    tasks = [
        connect_to_ssh_server_assert("localhost", 8022, "CiscoASA>", "show version", "Cisco"),
        connect_to_ssh_server_assert("localhost", 8023, "Huawei>", "show version", "Cisco"),
    ]

    await asyncio.gather(*tasks)  # Concurrently connect to all servers


async def connections_write():
    tasks = [
        connect_to_ssh_server_write("localhost", 8022, "CiscoASA>", "show version"),
    ]

    result = await asyncio.gather(*tasks)  # Concurrently connect to all servers

    return result

if __name__ == '__main__':
    result = asyncio.run(connections_write())
    for i in result:
        print(i)