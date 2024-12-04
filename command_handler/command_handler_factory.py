#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
from devices_handler.cisco import CiscoCommandHandler
from devices_handler.array import ArrayCommandHandler
from modles.mock_ssh_models import DeviceInfo


class CommandHandlerFactory:

    @staticmethod
    async def create_handler(device_mock_config):
        mock_config = DeviceInfo(**device_mock_config)
        if (handler := CiscoCommandHandler(mock_config)).is_selective:
            await handler.initialize()
            return handler

        elif (handler := ArrayCommandHandler(mock_config)).is_selective:
            await handler.initialize()
            return handler

        else:
            raise ValueError(f"Unsupported vendor: {device_mock_config}")
