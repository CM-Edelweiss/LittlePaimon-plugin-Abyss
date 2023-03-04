import asyncio
import datetime

from LittlePaimon.database import Player, LastQuery
from LittlePaimon.utils import logger
from LittlePaimon.plugins.Paimon_DailyNote.draw import draw_daily_note_card
from LittlePaimon.utils.api import get_mihoyo_private_data, get_ds, get_cookie
from LittlePaimon.utils.requests import aiorequests

from .api import get_pass_challenge


def mihoyo_headers(cookie, challenge, q='', b=None) -> dict:
    return {
        'DS':                get_ds(q, b),
        'Origin':            'https://webstatic.mihoyo.com',
        'Cookie':            cookie,
        'x-rpc-app_version': "2.11.1",
        'User-Agent':        'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                             'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer':           'https://webstatic.mihoyo.com/',
        "x-rpc-challenge":  challenge
    }


DAILY_NOTE_API = 'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote'


async def handle_ssbq(player: Player):
    data = await get_mihoyo_private_data(player.uid, player.user_id, 'daily_note')
    await LastQuery.update_or_create(user_id=player.user_id,
                                     defaults={'uid': player.uid, 'last_time': datetime.datetime.now()})
    if isinstance(data, str):
        logger.info('原神体力', '➤', {'用户': player.user_id,
                    'UID': player.uid}, f'获取数据失败, {data}', False)
        return f'{player.uid}{data}\n'
    elif data['retcode'] == 1034:
        logger.info('原神体力', '➤', {
                    '用户': player.user_id, 'UID': player.uid}, '获取数据失败，状态码为1034，疑似验证码', False)
        await asyncio.sleep(1)
        challenge = await get_pass_challenge(player.uid, player.user_id)
        logger.info('原神体力', '➤', {'用户': player.user_id,
                    'UID': player.uid}, '成功获取challenge', True)
        if challenge is not None:
            server_id = 'cn_qd01' if player.uid[0] == '5' else 'cn_gf01'
            # cookie_info = await PrivateCookie.get_or_none(user_id=player.user_id, uid=player.uid)
            cookie_info = await get_cookie(player.user_id, player.uid, True, True)
            await asyncio.sleep(1)
            res = await aiorequests.get(url=DAILY_NOTE_API,
                                        headers=mihoyo_headers(q=f'role_id={player.uid}&server={server_id}',
                                                               cookie=cookie_info.cookie, challenge=challenge),
                                        params={
                                            "server":  server_id,
                                            "role_id": player.uid
                                        })
            data = res.json()
            try:
                img = await draw_daily_note_card(data['data'], player.uid)
                logger.info('原神体力', '➤➤', {
                            '用户': player.user_id, 'UID': player.uid}, '绘制图片成功', True)
                return img
            except Exception as e:
                logger.info('原神体力', '➤➤', {
                            '用户': player.user_id, 'UID': player.uid}, f'绘制图片失败，{e}', False)
                return f'{player.uid}绘制图片失败，{e}'
        else:
            return f'{player.uid}无法越过验证码'
    elif data['retcode'] != 0:
        logger.info('原神体力', '➤', {'用户': player.user_id, 'UID': player.uid},
                    f'获取数据失败，code为{data["retcode"]}， msg为{data["message"]}', False)
        return f'{player.uid}获取数据失败，msg为{data["message"]}\n'
    else:
        logger.info('原神体力', '➤', {'用户': player.user_id,
                    'UID': player.uid}, '获取数据成功', True)
        try:
            img = await draw_daily_note_card(data['data'], player.uid)
            logger.info('原神体力', '➤➤', {
                        '用户': player.user_id, 'UID': player.uid}, '绘制图片成功', True)
            return img
        except Exception as e:
            logger.info('原神体力', '➤➤', {
                        '用户': player.user_id, 'UID': player.uid}, f'绘制图片失败，{e}', False)
            return f'{player.uid}绘制图片失败，{e}'
