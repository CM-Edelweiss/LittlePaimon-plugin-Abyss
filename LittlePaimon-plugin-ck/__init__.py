'''
未经过重复测试,我测试试能用（，建议帮助里和ysb合拼
https://github.com/CM-Edelweiss/LittlePaimon-plugin-Abyss
'''

import re
import json
import httpx
from asyncio import sleep
from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from LittlePaimon.utils.message import CommandUID
from LittlePaimon.database import PrivateCookie
from LittlePaimon.utils import logger
from LittlePaimon.utils.api import get_cookie,COOKIE_TOKEN_API
from nonebot.permission import SUPERUSER

http = httpx.Client(timeout=20, transport=httpx.HTTPTransport(retries=10))

shua = on_command('刷新ck', priority=5, block=True, state={
    'pm_name':        '刷新ck',
    'pm_description': '通过stoken刷新ck',
    'pm_usage':       '刷新ck[uid]',
    'pm_priority':    1
})


shuaxa = on_command('刷新全部ck', priority=5,permission=SUPERUSER, block=True, state={
    'pm_name':        '刷新全部ck',
    'pm_description': '刷新全部ck,仅超级管理员可用',
    'pm_usage':       '刷新全部ck',
    'pm_priority':    2
})

@shua.handle()
async def _(event: MessageEvent,uid=CommandUID()):
    data = await shuaxin(event.user_id,uid)
    await shua.finish(data)

async def shuaxin(user_id:str,uid:str):
    cookie = await get_cookie(user_id, uid, True, True)
    if not cookie:
        return '未绑定私人cookie，绑定方法二选一：\n1.通过米游社扫码绑定：\n请发送指令[原神扫码绑定]\n2.获取cookie的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取后，使用[ysb cookie]指令绑定'
    if not cookie.stoken:
        return "未绑定stoken，无法刷新"
    if 'mid' in cookie.stoken:
        stoken = re.findall(r'stoken=(.*);mid',cookie.stoken)
    else:
        stoken = re.findall(r'stoken=(.*);',cookie.stoken)
    headers = {
    'x-rpc-app_version': '2.11.1',
    'User-Agent': (
        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) '
        'AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1'
    ),
    'x-rpc-client_type': '5',
    'Referer': 'https://webstatic.mihoyo.com/',
    'Origin': 'https://webstatic.mihoyo.com',
    'Cookie': cookie.stoken,
    }
    req = http.get(url=COOKIE_TOKEN_API, headers=headers,
                    params={'stoken': stoken,'uid': cookie.mys_id})
    data = req.json()
    if data['retcode'] == 0:
        cookie_token = data['data']['cookie_token']
        await PrivateCookie.update_or_create(user_id=user_id, uid=uid, mys_id=cookie.mys_id,
                                                defaults={
                                                    'cookie': f'account_id={cookie.mys_id};cookie_token={cookie_token}',
                                                    'stoken': cookie.stoken,
                                                    'status': '1'})
        logger.info('原神Cookie', '➤', {'用户': user_id, 'uid': uid}, '通过stoken刷新成功', True)
        return f'UID{uid}通过stoken刷新成功'
    else:
        logger.info('原神Cookie', '➤', {'用户': user_id, 'uid': uid}, '通过stoken刷新失败', False)
        return 'stoken已失效，请重新绑定'

@shuaxa.handle()
async def _(event: MessageEvent):
    logger.info('原神Cookie', '开始刷新所有cookie')
    await shuaxa.send('开始刷新所有cookie，请稍等...', at_sender=True)
    private_cookies = await PrivateCookie.all()
    useless_private = []
    wust_private = []
    for cookie in private_cookies:
        data = await shuaxin(str(cookie.user_id),str(cookie.uid))
        if 'stoken已失效，请重新绑定' in data:
            useless_private.append(cookie.uid)
        if '未绑定stoken，无法刷新' in data:
            wust_private.append(cookie.uid)
        await sleep(1)
    msg = f'当前共{len(private_cookies)}个私人ck。\n'
    if useless_private or wust_private:
        if useless_private:
            msg += '其中失效stoken有:' + ' '.join(useless_private) + '\n'
        if wust_private:
            msg += '其中未绑定stoken有:' + ' '.join(wust_private) + '\n'
    else:
        msg += '私人ck全部刷新成功\n'
    await shuaxa.finish(msg, at_sender=True)