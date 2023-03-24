from LittlePaimon.database import Player, LastQuery
from LittlePaimon.utils import logger
from LittlePaimon.plugins.Paimon_DailyNote.draw import draw_daily_note_card
from LittlePaimon.utils.api import get_mihoyo_private_data, get_ds, get_cookie, mihoyo_headers
from .api import tilioc


async def handle_ssbq(player: Player):
    await LastQuery.update_last_query(player.user_id, player.uid)
    data = await get_mihoyo_private_data(player.uid, player.user_id, 'daily_note')
    if isinstance(data, str):
        logger.info('原神体力', '➤', {'用户': player.user_id,
                    'UID': player.uid}, f'获取数据失败, {data}', False)
        return f'{player.uid}{data}\n'
    elif data['retcode'] == 1034:
        logger.info('原神体力', '➤', {'用户': player.user_id, 'UID': player.uid},
                    '获取数据失败，状态码为1034，疑似验证码', False)
        return '疑似验证码'
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

            return f'{player.uid}绘制图片失败，{e}\n'


async def handle_ssbq2(player: Player):
    cookie_info = await get_cookie(player.user_id, player.uid, True, True)
    server_id = 'cn_qd01' if player.uid[0] == '5' else 'cn_gf01'
    if not await tilioc(mihoyo_headers(q=f'role_id={player.uid}&server={server_id}', cookie=cookie_info.cookie)):
        return f'{player.uid}尝试越过验证码失败，请重试'
    data = await get_mihoyo_private_data(player.uid, player.user_id, 'daily_note')
    if isinstance(data, str):
        logger.info('原神体力', '➤', {'用户': player.user_id,
                    'UID': player.uid}, f'获取数据失败, {data}', False)
        return f'{player.uid}{data}\n'
    elif data['retcode'] == 1034:
        logger.info('原神体力', '➤', {'用户': player.user_id, 'UID': player.uid},
                    '发生错误，请联系作者', False)
        return '发生错误'
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

            return f'{player.uid}绘制图片失败，{e}\n'
