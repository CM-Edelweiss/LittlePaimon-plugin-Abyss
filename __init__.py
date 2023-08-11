from .LittlePaimon_plugin_Abyss.main import *
from LittlePaimon.utils import logger

logger.info("人工验证", "➤", "", "请使用pip install flask gevent安装依赖，安装过请忽略", True)
logger.info(
    "人工验证",
    "➤",
    "",
    "在根目录请使用python LittlePaimon\plugins\LittlePaimon-plugin-Abyss\geetest\run.py打开人工验证后端",
    True,
)
logger.info("人工验证", "➤", "", f"ip:{config.ip}端口:5000", True)
