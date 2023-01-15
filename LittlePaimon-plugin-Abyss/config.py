from tortoise import fields
from tortoise.models import Model
from nonebot import get_driver
from pydantic import BaseModel, Extra

class Config(BaseModel, extra=Extra.ignore):
    enable: bool = True
    enable_hour: int = 7#时
    enable_minute: int = 5#分
    myb: bool = True
    myb_hour: int = 8#时
    myb_minute: int = 5#分
    appkey: str = '?'
    whitelist:list = []

plugin_config = Config.parse_obj(get_driver().config)

auto_sign_enable = plugin_config.enable
auto_sign_hour = plugin_config.enable_hour
auto_sign_minute = plugin_config.enable_minute
myb_enable =plugin_config.myb
myb_hour = plugin_config.myb_hour
myb_minute = plugin_config.myb_minute
key = plugin_config.appkey
bai = plugin_config.whitelist