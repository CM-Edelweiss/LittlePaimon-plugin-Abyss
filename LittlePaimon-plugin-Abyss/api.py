import copy
import json
import time
import random
import string
from typing import Union, Dict

import httpx
from LittlePaimon.utils.api import md5, get_cookie, random_text, random_hex, get_old_version_ds, get_ds
from LittlePaimon.utils.requests import aiorequests
from LittlePaimon.utils import logger
from LittlePaimon.database import PrivateCookie

from .config import config

# 签到列表
SIGN_LIST_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home'
# 签到信息
SIGN_INFO_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info'
# 执行签到
SIGN_URL = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'


# 验证码
bbs_api = "https://bbs-api.mihoyo.com"
bbs_get_captcha = bbs_api + "/misc/api/createVerification?is_high=true"
bbs_captcha_verify = bbs_api + "/misc/api/verifyVerification"

VERIFICATION_URL = 'https://api-takumi-record.mihoyo.com/game_record/app/card/wapi/createVerification?is_high=false'
VERIFY_URL = 'https://api-takumi-record.mihoyo.com/game_record/app/card/wapi/verifyVerification'

_HEADER = {
    'x-rpc-app_version': '2.11.1',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
    'x-rpc-client_type': '5',
    'Referer': 'https://webstatic.mihoyo.com/',
    'Origin': 'https://webstatic.mihoyo.com',
}


async def query_score():
    url = f'http://api.rrocr.com/api/integral.html?appkey={config.appkey}'
    try:
        response = await aiorequests.get(url)
    except httpx.RequestError as exc:
        return False, f'访问失败,{exc}'
    data = response.json()
    if data['status'] == -1:
        logger.info('查询积分', '➤', '', '失败', False)
        return True, '查询积分失败'
    integral = data['integral']
    if int(integral) < 10:
        logger.info('人人积分', '➤', '', '积分不足', False)
        return True, f'积分还剩{integral}'
    logger.info('人人积分', '➤', '', integral, True)
    return False, f'积分还剩{integral}'


async def vaapigt(gt, challenge) -> str:
    """validate,challenge"""
    url = f'{config.vaapi}gt={gt}&challenge={challenge}'
    try:
        response = await aiorequests.get(url,
                                         timeout=60)
    except httpx.RequestError as exc:
        logger.info('第三方验证', '➤', '错误', exc, False)
        return None, None
    data = response.json()
    if 'data' in data and 'validate' in data['data']:
        logger.info('第三方验证', '➤', '', '成功', True)
        validate = data['data']['validate']
        challenge = data['data']['challenge']
        return validate, challenge
    else:
        # 打码失败输出错误信息,返回None
        logger.info('第三方验证', '➤', '', '失败', False)
        validate = None
        challenge = None
        return validate, challenge  # 失败返回None 成功返回validate


async def rrocr(gt, challenge, referer) -> str:
    """validate,challenge"""
    jifen, _ = await query_score()
    if jifen:
        validate = None
        challenge = None
        return validate, challenge
    try:
        response = await aiorequests.post('http://api.rrocr.com/api/recognize.html', params={
            'appkey': config.appkey,
            'gt': gt,
            'challenge': challenge,
            'referer': referer,
            'sharecode': 'a83baa99828342ccac180b19217e2a93'  # ？不明
        }, timeout=60)
    except httpx.RequestError as exc:
        logger.info('第三方验证', '➤', '错误', exc, False)
        return None, None
    data = response.json()
    if 'data' in data and 'validate' in data['data']:
        logger.info('人人验证', '➤', '', data['msg'], True)
        validate = data['data']['validate']
        challenge = data['data']['challenge']
        return validate, challenge
    else:
        # 打码失败输出错误信息,返回None
        logger.info('人人验证', '➤', '', data['msg'], False)
        validate = None
        challenge = None
        return validate, challenge  # 失败返回None 成功返回validate


async def tilioc(header: Dict):
    header['DS'] = get_ds('is_high=false')
    raw_data = await aiorequests.get(
        url=VERIFICATION_URL,
        headers=header,
    )
    raw_data = raw_data.json()
    gt = raw_data['data']['gt']
    ch = raw_data['data']['challenge']

    vl, ch = await get_validate(gt, ch, VERIFICATION_URL)

    if vl:
        header['DS'] = get_ds(
            '',
            {
                'geetest_challenge': ch,
                'geetest_validate': vl,
                'geetest_seccode': f'{vl}|jordan',
            },
        )
        _ = await aiorequests.post(
            url=VERIFY_URL,
            headers=header,
            json={
                'geetest_challenge': ch,
                'geetest_validate': vl,
                'geetest_seccode': f'{vl}|jordan',
            },
        )
        logger.info('统一验证', '➤', '', '成功', True)
        return True
    else:
        logger.info('统一验证', '➤', '', '失败', False)
        return False


async def get_validate(gt, challenge, referer) -> str:
    '''体力和签到验证函数'''
    if config.vaapikai == 'dsf':
        validate, challenge = await vaapigt(gt, challenge)
    elif config.vaapikai == 'rr':
        validate, challenge = await rrocr(gt, challenge, referer)
    elif config.vaapikai == 'and':
        validate, challenge = await vaapigt(gt, challenge)
        if validate is None:
            validate, challenge = await rrocr(gt, challenge, referer)
    else:
        validate = None
        challenge = None
        logger.info('验证', '➤', '', '错误的配置', False)
    return validate, challenge  # 失败返回None 成功返回validate


async def get_pass_challenge(uid, user_id) -> str:
    '''米游币验证函数'''
    cookie_info = await get_cookie(user_id, uid, True, True)
    for w in range(2):
        if validate is not None:
            break
        else:
            logger.info('米游社加强签到', '➤', {
                '用户': user_id, 'UID': uid}, f'该用户出现校验码，开始尝试进行验证...，开始重试第 {w+1} 次！', True)
            headers = {
                "DS": get_old_version_ds(),
                "cookie": cookie_info.stoken,
                "x-rpc-client_type": '2',
                "x-rpc-app_version": "2.38.1",
                "x-rpc-sys_version": "12",
                "x-rpc-channel": "miyousheluodi",
                "x-rpc-device_id": random_hex(32),
                "x-rpc-device_name": random_text(random.randint(1, 10)),
                "x-rpc-device_model": "Mi 10",
                "Referer": "https://app.mihoyo.com",
                "Host": "bbs-api.mihoyo.com",
                "User-Agent": "okhttp/4.8.0"
            }
            req = await aiorequests.get(url=bbs_get_captcha, headers=headers)
            data = req.json()
            if data["retcode"] != 0:
                return None
            if config.vaapikai == 'dsf':
                validate, _ = await vaapigt(data["data"]["gt"], data["data"]["challenge"])
            elif config.vaapikai == 'rr':
                validate, _ = await rrocr(data["data"]["gt"], data["data"]["challenge"],
                                          "https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id"
                                          "=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon")
            elif config.vaapikai == 'and':
                validate, _ = await vaapigt(data["data"]["gt"], data["data"]["challenge"])
                if validate is None and w == 1:
                    validate, _ = await rrocr(data["data"]["gt"], data["data"]["challenge"],
                                              "https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id"
                                              "=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon")
            else:
                logger.info('验证', '➤', '', '错误的配置', False)
                return None
    check_req = await aiorequests.post(url=bbs_captcha_verify, headers=headers,
                                       json={"geetest_challenge": data["data"]["challenge"],
                                             "geetest_seccode": validate+"|jordan",
                                             "geetest_validate": validate})
    check = check_req.json()
    if check["retcode"] == 0:
        logger.info('验证', '➤', {'用户': user_id,
                                'UID': uid}, '成功获取challenge', True)
        return check["data"]["challenge"]
    return None


async def get_sign_info(uid, cookie) -> str:
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    HEADER = copy.deepcopy(_HEADER)
    HEADER['Cookie'] = cookie
    req = await aiorequests.get(url=SIGN_INFO_URL, headers=HEADER,
                                params={"act_id": 'e202009291139501', 'region': server_id, 'uid': uid})
    data = req.json()
    return data


def old_version_get_ds_token(mysbbs=False):
    n = 'N50pqm7FSy2AkFz2B3TqtuZMJ5TOl3Ep'
    i = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5('salt=' + n + '&t=' + i + '&r=' + r)
    return i + ',' + r + ',' + c


async def mihoyo_bbs_sign(user_id: str, uid: str, Header={}) -> Union[dict, str]:
    # cookie_info = await PrivateCookie.get_or_none(user_id=user_id, uid=uid)
    cookie_info = await get_cookie(user_id, uid, True, True)
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    HEADER = copy.deepcopy(_HEADER)
    HEADER['User_Agent'] = (
        'Mozilla/5.0 (Linux; Android 10; MIX 2 Build/QKQ1.190825.002; wv) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
        'Chrome/83.0.4103.101 Mobile Safari/537.36 miHoYoBBS/2.35.2'
    )
    HEADER['Cookie'] = cookie_info.cookie
    HEADER['x-rpc-device_id'] = random_hex(32)
    HEADER['x-rpc-app_version'] = '2.35.2'
    HEADER['x-rpc-client_type'] = '5'
    HEADER['X_Requested_With'] = 'com.mihoyo.hyperion'
    HEADER['DS'] = old_version_get_ds_token(True)
    HEADER['Referer'] = (
        'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html'
        '?bbs_auth_required=true&act_id=e202009291139501&utm_source=bbs'
        '&utm_medium=mys&utm_campaign=icon'
    )
    HEADER.update(Header)
    req = await aiorequests.post(url=SIGN_URL, headers=HEADER,
                                 json={'act_id': 'e202009291139501', 'uid': uid, 'region': server_id})
    data = req.json()
    return data


async def get_sign_list() -> dict:
    req = await aiorequests.get(url=SIGN_LIST_URL, headers=_HEADER,
                                params={'act_id': 'e202009291139501'})
    data = req.json()
    return data
