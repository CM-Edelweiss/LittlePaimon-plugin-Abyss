from pydantic import BaseModel, Field
from LittlePaimon.utils.files import load_yaml, save_yaml
from pathlib import Path
from typing import Literal, List

PAIMON_CONFIG = Path() / "config" / "Abyss_config.yml"


class ConfigModel(BaseModel):
    enable: bool = Field(True, alias="验证米游社签到开关")
    enable_hour: int = Field(7, alias="验证米游社签到开始时间(小时)")
    enable_minute: int = Field(5, alias="验证米游社签到开始时间(分钟)")
    sr_enable: bool = Field(True, alias="验证星铁签到开关")
    sr_enable_hour: int = Field(7, alias="验证星铁签到开始时间(小时)")
    sr_enable_minute: int = Field(5, alias="验证星铁签到开始时间(分钟)")
    myb: bool = Field(True, alias="验证米游币获取开关")
    myb_hour: int = Field(8, alias="验证米游币开始执行时间(小时)")
    myb_minute: int = Field(0, alias="验证米游币开始执行时间(分钟)")
    appkey: str = Field("", alias="appkey密钥")
    ip: str = Field("127.0.0.1:5000", alias="人工验证网站")
    whitelist: List[int] = Field([], alias="群聊白名单")
    whlist: List[int] = Field([], alias="用户白名单")
    vaapikai: Literal["rr", "dsf", "rg"] = Field("rr", alias="打码模式")
    vaapikai2: Literal["rr", "dsf"] = Field("rr", alias="自动签到打码模式")
    vaapi: str = Field("", alias="第三方过码")
    hfu: str = Field("就不给你用~", alias="非白名单回复")

    @property
    def alias_dict(self):
        return {v.alias: k for k, v in self.__fields__.items()}

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.__fields__:
                self.__setattr__(key, value)
            elif key in self.alias_dict:
                self.__setattr__(self.alias_dict[key], value)


class ConfigManager:
    if PAIMON_CONFIG.exists():
        config = ConfigModel.parse_obj(load_yaml(PAIMON_CONFIG))
    else:
        config = ConfigModel()
        save_yaml(config.dict(by_alias=True), PAIMON_CONFIG)

    @classmethod
    def save(cls):
        save_yaml(cls.config.dict(by_alias=True), PAIMON_CONFIG)


config = ConfigManager.config
