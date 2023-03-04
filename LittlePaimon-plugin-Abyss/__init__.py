from typing import Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import PrivateMessageEvent, GroupMessageEvent, Bot, Message
from nonebot.permission import SUPERUSER
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata

from LittlePaimon.database import PrivateCookie, MihoyoBBSSub
from LittlePaimon.utils import logger, NICKNAME
from LittlePaimon.utils.message import CommandUID, CommandSwitch, CommandPlayer

from .ssbq import handle_ssbq
from .coin_handle import mhy_bbs_coin, bbs_auto_coin
from .config import config
from .sign_handle import sign_in, bbs_auto_sign
from . import web_page, web_api

__plugin_meta__ = PluginMetadata(
    name='原神加强签到',
    description='原神加强签到',
    usage='原神加强签到',
    extra={
        'author':   'Edelweiss',
        'version':  '1.0',
        'priority': 7,
    }
)


sign = on_command('验证签到', priority=8, block=True, state={
    'pm_name':        '验证签到',
    'pm_description': '*执行米游社签到操作，并对验证码进行验证',
    'pm_usage':       '验证签到(uid)[on|off]',
    'pm_priority':    1
})


all_sign = on_command('全部验证重签', priority=8, block=True, permission=SUPERUSER, rule=to_me(), state={
    'pm_name':        '米游社验证重签',
    'pm_description': '重签全部米游社签到任务，需超级用户权限',
    'pm_usage':       '@Bot 全部验证重签',
    'pm_priority':    2
})

ti = on_command('验证体力', priority=8, block=True, state={
    'pm_name':        '体力',
    'pm_description': '*验证体力(uid)',
    'pm_usage':       '查看原神体力，并对验证码进行验证',
    'pm_priority':    3
})

get_coin = on_command('验证米游币获取', priority=8, block=True, state={
    'pm_name':        '验证米游币获取',
    'pm_description': '*执行米游币任务操作，并对验证码进行验证',
    'pm_usage':       '验证米游币获取(uid)[on|off]',
    'pm_priority':    4
})

all_coin = on_command('全部验证重做', priority=8, block=True, permission=SUPERUSER, rule=to_me(), state={
    'pm_name':        '全部验证重做',
    'pm_description': '重做全部米游币获取任务，需超级用户权限',
    'pm_usage':       '@Bot 全部验证重做',
    'pm_priority':    5
})


list = []


@sign.handle()
async def _(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], uid=CommandUID(), switch=CommandSwitch()):
    if isinstance(event, GroupMessageEvent):
        groupid = event.group_id
    else:
        groupid = ''
    if (groupid in config.whitelist) or (event.user_id in config.whlist) or (str(event.user_id) in bot.config.superusers):
        if switch is None:
            if f'{event.user_id}-{uid}' in list:
                await sign.finish(f'你已经有验证任务了，{NICKNAME}会忙不过来的', at_sender=True)
            else:
                await sign.send(f'{NICKNAME}开始为UID{uid}执行加强米游社签到，请稍等...', at_sender=True)
                logger.info('加强米游社签到', '➤', {'用户': str(
                    event.user_id), 'uid': uid}, '执行签到', True)
                list.append(f'{event.user_id}-{uid}')
                _, result = await sign_in(str(event.user_id), uid)
                list.remove(f'{event.user_id}-{uid}')
                await sign.finish(result, at_sender=True)
        elif isinstance(event, GroupMessageEvent):
            sub_data = {
                'user_id':    event.user_id,
                'uid':        uid,
                'sub_event': '米游社验证签到'
            }
            if switch:
                # switch为开启，则添加订阅
                if await PrivateCookie.get_or_none(user_id=str(event.user_id), uid=uid):
                    await MihoyoBBSSub.update_or_create(**sub_data, defaults={
                        'group_id': event.group_id if isinstance(event, GroupMessageEvent) else event.user_id})
                    logger.info('加强米游社自动签到', '➤', {'用户': str(
                        event.user_id), 'uid': uid}, '开启成功', True)
                    await sign.finish(f'UID{uid}开启加强米游社签到', at_sender=True)
                else:
                    await sign.finish(f'UID{uid}尚未绑定Cookie！请先使用ysb指令绑定吧！', at_sender=True)
            else:
                # switch为关闭，则取消订阅
                if sub := await MihoyoBBSSub.get_or_none(**sub_data):
                    await sub.delete()
                    logger.info('加强米游社自动签到', '➤', {'用户': str(
                        event.user_id), 'uid': uid}, '关闭成功', True)
                    await sign.finish(f'UID{uid}关闭加强米游社自动签到成功', at_sender=True)
                else:
                    await sign.finish(f'UID{uid}尚未开启加强米游社自动签到，无需关闭！', at_sender=True)
        else:
            await sign.finish('不支持订阅', at_sender=True)
    else:
        await sign.finish(config.hfu, at_sender=True)


@all_sign.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await all_sign.send(f'{NICKNAME}开始执行全部加强重签，需要一定时间...')
    await bbs_auto_sign()


@ti.handle()
async def _(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], players=CommandPlayer()):
    if isinstance(event, GroupMessageEvent):
        groupid = event.group_id
    else:
        groupid = ''
    if (groupid in config.whitelist) or (event.user_id in config.whlist) or (str(event.user_id) in bot.config.superusers):

        for player in players:
            if f'{event.user_id}-{player.uid}' in list:
                await ti.finish(f'你已经有验证任务了，{NICKNAME}会忙不过来的', at_sender=True)
            else:
                logger.info('原神体力', '➤', {'用户': str(
                    event.user_id), 'uid': player.uid}, '开始执行查询', True)
                result = Message()
                list.append(f'{event.user_id}-{player.uid}')
                result += await handle_ssbq(player)
                list.remove(f'{event.user_id}-{player.uid}')
        await ti.finish(result, at_sender=True)
    else:
        await ti.finish(config.hfu, at_sender=True)


@get_coin.handle()
async def _(bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], uid=CommandUID(), switch=CommandSwitch()):
    if isinstance(event, GroupMessageEvent):
        groupid = event.group_id
    else:
        groupid = ''
    if (groupid in config.whitelist) or (event.user_id in config.whlist) or (str(event.user_id) in bot.config.superusers):
        if switch is None:
            # 没有开关参数，手动执行米游币获取
            if f'{event.user_id}-{uid}' in list:
                await get_coin.finish(f'你已经有验证任务了，{NICKNAME}会忙不过来的', at_sender=True)
            else:
                await get_coin.send(f'开始为UID{uid}执行加强米游币获取，请稍等...', at_sender=True)
                logger.info('加强米游币获取', '➤', {'用户': str(
                    event.user_id), 'uid': uid}, '执行获取', True)
                list.append(f'{event.user_id}-{uid}')
                result = await mhy_bbs_coin(str(event.user_id), uid)
                list.remove(f'{event.user_id}-{uid}')
                await get_coin.finish(result, at_sender=True)
        elif isinstance(event, GroupMessageEvent):
            sub_data = {
                'user_id':   event.user_id,
                'uid':       uid,
                'sub_event': '米游币验证获取'
            }
            if switch:
                # switch为开启，则添加订阅
                if (ck := await PrivateCookie.get_or_none(user_id=str(event.user_id), uid=uid)) and ck.stoken is not None:
                    await MihoyoBBSSub.update_or_create(**sub_data, defaults={
                        'group_id': event.group_id if isinstance(event, GroupMessageEvent) else event.user_id})
                    logger.info('加强米游币自动获取', '➤', {'用户': str(
                        event.user_id), 'uid': uid}, '开启成功', True)
                    await get_coin.finish(f'UID{uid}开启加强米游币自动获取成功', at_sender=True)
                else:
                    await get_coin.finish(f'UID{uid}尚未绑定Cookie或Cookie中没有login_ticket！请先使用ysb指令绑定吧！', at_sender=True)
            else:
                # switch为关闭，则取消订阅
                if sub := await MihoyoBBSSub.get_or_none(**sub_data):
                    await sub.delete()
                    logger.info('加强米游币自动获取', '➤', {'用户': str(
                        event.user_id), 'uid': uid}, '关闭成功', True)
                    await get_coin.finish(f'UID{uid}关闭加强米游币自动获取成功', at_sender=True)
                else:
                    await get_coin.finish(f'UID{uid}尚未开启加强米游币自动获取，无需关闭！', at_sender=True)
        else:
            await get_coin.finish('不支持订阅', at_sender=True)
    else:
        await get_coin.finish(config.hfu, at_sender=True)


@all_coin.handle()
async def _(event: Union[GroupMessageEvent, PrivateMessageEvent]):
    await all_coin.send(f'{NICKNAME}开始执行加强myb全部重做，需要一定时间...')
    await bbs_auto_coin()
