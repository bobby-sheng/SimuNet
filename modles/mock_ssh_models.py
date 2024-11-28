#!/usr/bin/env python3.10.6
# -*- coding: utf-8 -*-
# Author: Bobby Sheng <Bobby@sky-cloud.net>
from typing import List
from pydantic import BaseModel, Field
from dataclasses import dataclass


@dataclass
class DeviceBaseInfo:
    """
    Device base Info
    """
    vendor: str
    model: str
    version: str
    description: str


class CommandResponse(BaseModel):
    cmd: str = Field(description="命令")
    response: str = Field(description="命令响应")


class ModeMap(BaseModel):
    login: str = Field(description="登录模式提示符")
    enable: str = Field(description="启用模式提示符")
    config: str = Field(description="配置模式提示符")

    class Config:
        extra = 'allow'


class DeviceInfo(BaseModel):
    vendorName: str = Field(description="设备厂商名称")
    typeName: str = Field(description="设备类型名称")
    versionName: str = Field(description="设备版本名称")
    port: int = Field(description="设备端口")
    config_file_name: str = Field(description="配置文件名称")


class CmdResList(BaseModel):
    mode_map: ModeMap
    exit_list: List[str]
    login: List[CommandResponse]
    enable: List[CommandResponse]
    config: List[CommandResponse]
    switch_mode_map: List[CommandResponse]

    class Config:
        extra = 'allow'
