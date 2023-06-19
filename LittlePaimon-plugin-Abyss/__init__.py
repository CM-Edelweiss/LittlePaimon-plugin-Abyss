from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    PrivateMessageEvent,
    GroupMessageEvent,
    Bot,
    Message,
)
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata

from LittlePaimon.database import PrivateCookie, MihoyoBBSSub
from LittlePaimon.utils import logger, NICKNAME, DRIVER
from LittlePaimon.utils.message import CommandUID, CommandSwitch, CommandPlayer

from .static import get_pass_challenge
from .sr_api import sr_sign_in, sr_bbs_auto_sign
from .ssbq import handle_ssbq, handle_ssbq2
from .coin_handle import mhy_bbs_coin, bbs_auto_coin
from .config import config
from .sign_handle import sign_in, bbs_auto_sign
from . import web_page, web_api


@DRIVER.on_startup
async def start():
    logger.info("人工验证", "➤", "", "请使用pip install flask gevent安装依赖，安装过请忽略", True)
    logger.info(
        "人工验证",
        "➤",
        "",
        "在根目录请使用python LittlePaimon\plugins\LittlePaimon-plugin-Abyss\geetest\run.py打开人工验证后端",
        True,
    )
    logger.info("人工验证", "➤", "", f"ip:{config.ip}端口:5000", True)


__plugin_meta__ = PluginMetadata(
    name="加强签到",
    description="加强签到",
    usage="加强签到",
    extra={
        "author": "Edelweiss",
        "version": "2.0",
        "priority": 7,
    },
)


sign = on_command(
    "验证签到",
    priority=7,
    block=True,
    state={
        "pm_name": "验证签到",
        "pm_description": "*执行米游社签到操作，并对验证码进行验证",
        "pm_usage": "验证签到(uid)[on|off]",
        "pm_priority": 1,
    },
)


all_sign = on_command(
    "全部验证重签",
    priority=7,
    block=True,
    permission=SUPERUSER,
    rule=to_me(),
    state={
        "pm_name": "米游社验证重签",
        "pm_description": "重签全部米游社签到任务，需超级用户权限",
        "pm_usage": "@Bot 全部验证重签",
        "pm_priority": 2,
    },
)

ti = on_command(
    "验证体力",
    priority=7,
    block=True,
    state={
        "pm_name": "体力",
        "pm_description": "*验证体力(uid)",
        "pm_usage": "查看原神体力，并对验证码进行验证",
        "pm_priority": 3,
    },
)

get_coin = on_command(
    "验证米游币获取",
    priority=7,
    block=True,
    state={
        "pm_name": "验证米游币获取",
        "pm_description": "*执行米游币任务操作，并对验证码进行验证",
        "pm_usage": "验证米游币获取(uid)[on|off]",
        "pm_priority": 4,
    },
)

all_coin = on_command(
    "全部验证重做",
    priority=7,
    block=True,
    permission=SUPERUSER,
    rule=to_me(),
    state={
        "pm_name": "全部验证重做",
        "pm_description": "重做全部米游币获取任务，需超级用户权限",
        "pm_usage": "@Bot 全部验证重做",
        "pm_priority": 5,
    },
)


sr_sign = on_command(
    "sr验证签到",
    priority=7,
    block=True,
    state={
        "pm_name": "sr验证签到",
        "pm_description": "*执行星铁签到操作，并对验证码进行验证",
        "pm_usage": "sr验证签到[on|off]",
        "pm_priority": 6,
    },
)

sr_all_sign = on_command(
    "sr全部验证重签",
    priority=7,
    block=True,
    permission=SUPERUSER,
    rule=to_me(),
    state={
        "pm_name": "sr米游社验证重签",
        "pm_description": "重签全部星铁签到任务，需超级用户权限",
        "pm_usage": "@Bot sr全部验证重签",
        "pm_priority": 7,
    },
)
get_pass = on_command(
    "米游社过码",
    priority=8,
    rule=to_me(),
    state={
        "pm_name": "米游社过码",
        "pm_description": "进行一次米游社社区验证码验证,可能解开一些过不去的地方",
        "pm_usage": "米游社过码",
        "pm_priority": 8,
    },
)


list = []
sr_list = []


@get_pass.handle()
async def _(
    bot: Bot,
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    uid=CommandUID(),
):
    if isinstance(event, GroupMessageEvent):
        groupid = event.group_id
    else:
        groupid = ""
    if (
        (groupid in config.whitelist)
        or (event.user_id in config.whlist)
        or (str(event.user_id) in bot.config.superusers)
        or (config.vaapikai == "rg")
    ):
        if config.vaapikai == "rg":
            await get_pass.send(
                f"请前往{config.ip}/validate?uid={uid}进行手动验证,如果无法访问请刷新,直到出结果",
                at_sender=True,
            )
        data = await get_pass_challenge(str(event.user_id), uid)
        await get_pass.finish(data, at_sender=True)


@sr_sign.handle()
async def _(
    bot: Bot,
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    switch=CommandSwitch(),
):
    if isinstance(event, GroupMessageEvent):
        groupid = event.group_id
    else:
        groupid = ""
    if (
        (groupid in config.whitelist)
        or (event.user_id in config.whlist)
        or (str(event.user_id) in bot.config.superusers)
        or (config.vaapikai == "rg")
    ):
        from LittlePaimon.plugins.star_rail_info.data_handle import get_uid

        # 一样的函数名真是太屮了
        uid2 = get_uid(str(event.user_id))  # 星铁uid
        from LittlePaimon.utils.message import get_uid  # 原神uid 用于获取ck

        uid = await get_uid(event=event)
        if not uid2:
            await sr_sign.finish("请先使用命令[星铁绑定uid]来绑定星穹铁道UID")
        if not uid:
            await sr_sign.finish("请先使用命令[ysb uid]来绑定原神UID")
        if switch is None:
            if f"{event.user_id}-{uid2}" in sr_list:
                await sr_sign.finish(f"你已经有验证任务了，{NICKNAME}会忙不过来的", at_sender=True)
            else:
                GF = f"{NICKNAME}开始为UID{uid2}执行加强星铁签到"
                if config.vaapikai == "rg":
                    GF += f",\n请前往{config.ip}/validate?uid={uid2}进行手动验证,如果无法访问请刷新,直到出结果"
                await sr_sign.send(GF, at_sender=True)
                logger.info(
                    "加强星铁签到", "➤", {"用户": str(event.user_id), "uid": uid2}, "执行签到", True
                )
                sr_list.append(f"{event.user_id}-{uid2}")
                _, result = await sr_sign_in(str(event.user_id), uid2, uid, False)
                sr_list.remove(f"{event.user_id}-{uid2}")
                await sr_sign.finish(result, at_sender=True)
        elif isinstance(event, GroupMessageEvent) and (
            (groupid in config.whitelist)
            or (event.user_id in config.whlist)
            or (str(event.user_id) in bot.config.superusers)
        ):
            sub_data = {
                "user_id": event.user_id,
                "uid": uid,
                "sub_event": "星铁签到",
            }
            if switch:
                # switch为开启，则添加订阅
                if await PrivateCookie.get_or_none(user_id=str(event.user_id), uid=uid):
                    await MihoyoBBSSub.update_or_create(
                        **sub_data,
                        defaults={
                            "group_id": event.group_id
                            if isinstance(event, GroupMessageEvent)
                            else event.user_id
                        },
                    )
                    logger.info(
                        "加强星铁自动签到",
                        "➤",
                        {"用户": str(event.user_id), "uid": uid2},
                        "开启成功",
                        True,
                    )
                    await sr_sign.finish(f"UID{uid2}开启加强星铁签到", at_sender=True)
                else:
                    await sr_sign.finish(
                        f"UID{uid2}尚未绑定Cookie！请先使用ysb指令绑定吧！", at_sender=True
                    )
            else:
                # switch为关闭，则取消订阅
                if sub := await MihoyoBBSSub.get_or_none(**sub_data):
                    await sub.delete()
                    logger.info(
                        "加强星铁自动签到",
                        "➤",
                        {"用户": str(event.user_id), "uid": uid2},
                        "关闭成功",
                        True,
                    )
                    await sr_sign.finish(f"UID{uid2}关闭加强星铁自动签到成功", at_sender=True)
                else:
                    await sr_sign.finish(f"UID{uid2}尚未开启加强星铁自动签到，无需关闭！", at_sender=True)
        else:
            await sr_sign.finish("不支持订阅", at_sender=True)
    else:
        await sr_sign.finish(config.hfu, at_sender=True)


@sr_all_sign.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await sr_all_sign.send(f"{NICKNAME}开始执行全部加强星铁重签，需要一定时间...")
    await sr_bbs_auto_sign()


@sign.handle()
async def _(
    bot: Bot,
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    uid=CommandUID(),
    switch=CommandSwitch(),
):
    if isinstance(event, GroupMessageEvent):
        groupid = event.group_id
    else:
        groupid = ""
    if (
        (groupid in config.whitelist)
        or (event.user_id in config.whlist)
        or (str(event.user_id) in bot.config.superusers)
        or (config.vaapikai == "rg")
    ):
        if switch is None:
            if f"{event.user_id}-{uid}" in list:
                await sign.finish(f"你已经有验证任务了，{NICKNAME}会忙不过来的", at_sender=True)
            else:
                GF = f"{NICKNAME}开始为UID{uid}执行加强米游社签到"
                if config.vaapikai == "rg":
                    GF += f",\n请前往{config.ip}/validate?uid={uid}进行手动验证,如果无法访问请刷新,直到出结果"
                await sign.send(GF, at_sender=True)
                logger.info(
                    "加强米游社签到", "➤", {"用户": str(event.user_id), "uid": uid}, "执行签到", True
                )
                list.append(f"{event.user_id}-{uid}")
                _, result = await sign_in(str(event.user_id), uid, False)
                list.remove(f"{event.user_id}-{uid}")
                await sign.finish(result, at_sender=True)
        elif isinstance(event, GroupMessageEvent) and (
            (groupid in config.whitelist)
            or (event.user_id in config.whlist)
            or (str(event.user_id) in bot.config.superusers)
        ):
            sub_data = {"user_id": event.user_id, "uid": uid, "sub_event": "米游社验证签到"}
            if switch:
                # switch为开启，则添加订阅
                if await PrivateCookie.get_or_none(user_id=str(event.user_id), uid=uid):
                    await MihoyoBBSSub.update_or_create(
                        **sub_data,
                        defaults={
                            "group_id": event.group_id
                            if isinstance(event, GroupMessageEvent)
                            else event.user_id
                        },
                    )
                    logger.info(
                        "加强米游社自动签到",
                        "➤",
                        {"用户": str(event.user_id), "uid": uid},
                        "开启成功",
                        True,
                    )
                    await sign.finish(f"UID{uid}开启加强米游社签到", at_sender=True)
                else:
                    await sign.finish(
                        f"UID{uid}尚未绑定Cookie！请先使用ysb指令绑定吧！", at_sender=True
                    )
            else:
                # switch为关闭，则取消订阅
                if sub := await MihoyoBBSSub.get_or_none(**sub_data):
                    await sub.delete()
                    logger.info(
                        "加强米游社自动签到",
                        "➤",
                        {"用户": str(event.user_id), "uid": uid},
                        "关闭成功",
                        True,
                    )
                    await sign.finish(f"UID{uid}关闭加强米游社自动签到成功", at_sender=True)
                else:
                    await sign.finish(f"UID{uid}尚未开启加强米游社自动签到，无需关闭！", at_sender=True)
        else:
            await sign.finish("不支持订阅", at_sender=True)
    else:
        await sign.finish(config.hfu, at_sender=True)


@all_sign.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await all_sign.send(f"{NICKNAME}开始执行全部加强重签，需要一定时间...")
    await bbs_auto_sign()


@ti.handle()
async def _(
    bot: Bot,
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    players=CommandPlayer(),
):
    if isinstance(event, GroupMessageEvent):
        groupid = event.group_id
    else:
        groupid = ""
    if (
        (groupid in config.whitelist)
        or (event.user_id in config.whlist)
        or (str(event.user_id) in bot.config.superusers)
        or (config.vaapikai == "rg")
    ):
        for player in players:
            if f"{event.user_id}-{player.uid}" in list:
                await ti.finish(f"你已经有验证任务了，{NICKNAME}会忙不过来的", at_sender=True)
            else:
                logger.info(
                    "原神体力",
                    "➤",
                    {"用户": str(event.user_id), "uid": player.uid},
                    "开始执行查询",
                    True,
                )
                result = Message()
                list.append(f"{event.user_id}-{player.uid}")
                msg = await handle_ssbq(player)
                if msg == "疑似验证码":
                    if config.vaapikai == "rg":
                        await ti.send(
                            f"请前往{config.ip}/validate?uid={player.uid}进行手动验证,如果无法访问请刷新,直到出结果",
                            at_sender=True,
                        )
                    else:
                        await ti.send(f"UID{player.uid}遇验证码阻拦,开始尝试过码", at_sender=True)
                    msg = await handle_ssbq2(player)
                result += msg
                list.remove(f"{event.user_id}-{player.uid}")
        await ti.finish(result, at_sender=True)
    else:
        await ti.finish(config.hfu, at_sender=True)


@get_coin.handle()
async def _(
    bot: Bot,
    event: Union[GroupMessageEvent, PrivateMessageEvent],
    uid=CommandUID(),
    switch=CommandSwitch(),
):
    if isinstance(event, GroupMessageEvent):
        groupid = event.group_id
    else:
        groupid = ""
    if (
        (groupid in config.whitelist)
        or (event.user_id in config.whlist)
        or (str(event.user_id) in bot.config.superusers)
        or (config.vaapikai == "rg")
    ):
        if switch is None:
            # 没有开关参数，手动执行米游币获取
            if f"{event.user_id}-{uid}" in list:
                await get_coin.finish(f"你已经有验证任务了，{NICKNAME}会忙不过来的", at_sender=True)
            else:
                GF = f"{NICKNAME}开始为UID{uid}执行加强米游币获取"
                if config.vaapikai == "rg":
                    GF += f",\n请前往{config.ip}/validate?uid={uid}进行手动验证,如果无法访问请等待,直到出结果"
                await get_coin.send(GF, at_sender=True)
                logger.info(
                    "加强米游币获取", "➤", {"用户": str(event.user_id), "uid": uid}, "执行获取", True
                )
                list.append(f"{event.user_id}-{uid}")
                result = await mhy_bbs_coin(str(event.user_id), uid, False)
                list.remove(f"{event.user_id}-{uid}")
                await get_coin.finish(result, at_sender=True)
        elif isinstance(event, GroupMessageEvent) and (
            (groupid in config.whitelist)
            or (event.user_id in config.whlist)
            or (str(event.user_id) in bot.config.superusers)
        ):
            sub_data = {"user_id": event.user_id, "uid": uid, "sub_event": "米游币验证获取"}
            if switch:
                # switch为开启，则添加订阅
                if (
                    ck := await PrivateCookie.get_or_none(
                        user_id=str(event.user_id), uid=uid
                    )
                ) and ck.stoken is not None:
                    await MihoyoBBSSub.update_or_create(
                        **sub_data,
                        defaults={
                            "group_id": event.group_id
                            if isinstance(event, GroupMessageEvent)
                            else event.user_id
                        },
                    )
                    logger.info(
                        "加强米游币自动获取",
                        "➤",
                        {"用户": str(event.user_id), "uid": uid},
                        "开启成功",
                        True,
                    )
                    await get_coin.finish(f"UID{uid}开启加强米游币自动获取成功", at_sender=True)
                else:
                    await get_coin.finish(
                        f"UID{uid}尚未绑定Cookie或Cookie中没有login_ticket！请先使用ysb指令绑定吧！",
                        at_sender=True,
                    )
            else:
                # switch为关闭，则取消订阅
                if sub := await MihoyoBBSSub.get_or_none(**sub_data):
                    await sub.delete()
                    logger.info(
                        "加强米游币自动获取",
                        "➤",
                        {"用户": str(event.user_id), "uid": uid},
                        "关闭成功",
                        True,
                    )
                    await get_coin.finish(f"UID{uid}关闭加强米游币自动获取成功", at_sender=True)
                else:
                    await get_coin.finish(
                        f"UID{uid}尚未开启加强米游币自动获取，无需关闭！", at_sender=True
                    )
        else:
            await get_coin.finish("不支持订阅", at_sender=True)
    else:
        await get_coin.finish(config.hfu, at_sender=True)


@all_coin.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await all_coin.send(f"{NICKNAME}开始执行加强myb全部重做，需要一定时间...")
    await bbs_auto_coin()
