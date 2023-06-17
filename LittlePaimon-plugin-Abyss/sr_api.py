from email import header
import random
import asyncio
import time
import copy
from collections import defaultdict
from nonebot import get_bot
from typing import Union, Dict
from LittlePaimon.database import MihoyoBBSSub
from LittlePaimon.utils import logger, scheduler
from LittlePaimon.utils.api import get_cookie
from LittlePaimon.utils.requests import aiorequests
from LittlePaimon.plugins.star_rail_info.data_handle import get_uid
from .api import (
    _HEADER,
    get_validate,
    query_score,
    old_version_get_ds_token,
)
from .config import config

# 列表
OLD_URL = "https://api-takumi.mihoyo.com"
STAR_RAIL_SIGN_LIST_URL = f"{OLD_URL}/event/luna/home"
# 获得签到信息
STAR_RAIL_SIGN_INFO_URL = f"{OLD_URL}/event/luna/info"
# 签到
STAR_RAIL_SIGN_URL = f"{OLD_URL}/event/luna/sign"


async def sr_mihoyo_bbs_sign(uid: str, ck: str, Header={}) -> Union[dict, str]:
    HEADER = copy.deepcopy(_HEADER)
    HEADER["Cookie"] = ck
    HEADER["x-rpc-app_version"] = "2.44.1"
    HEADER["x-rpc-client_type"] = "5"
    HEADER["X_Requested_With"] = "com.mihoyo.hyperion"
    HEADER["DS"] = old_version_get_ds_token(True)
    HEADER["Referer"] = "https://webstatic.mihoyo.com"
    HEADER.update(header)
    data = await aiorequests.post(
        url=STAR_RAIL_SIGN_URL,
        headers=HEADER,
        json={
            "act_id": "e202304121516551",
            "region": "prod_gf_cn",
            "uid": uid,
            "lang": "zh-cn",
        },
    )
    return data.json()


async def sr_get_sign_info(uid, ck):
    HEADER = copy.deepcopy(_HEADER)
    HEADER["Cookie"] = ck
    data = await aiorequests.get(
        url=STAR_RAIL_SIGN_INFO_URL,
        headers=HEADER,
        params={
            "act_id": "e202304121516551",
            "lang": "zh-cn",
            "region": "prod_gf_cn",
            "uid": uid,
        },
    )
    return data.json()


async def sr_get_sign_list() -> dict:
    data = await aiorequests.get(
        url=STAR_RAIL_SIGN_LIST_URL,
        headers=_HEADER,
        params={
            "act_id": "e202304121516551",
            "lang": "zh-cn",
        },
    )
    return data.json()


already = 0

# 签到函数


async def sr_sign_in(user_id, uid, uid2, re: bool) -> str:
    logger.info("星铁加强签到", "➤", {"用户": user_id, "UID": uid}, "开始执行签到！", True)
    cookie = await get_cookie(user_id, uid2, True, True)
    if not cookie:
        return (
            False,
            "未绑定私人cookies，绑定方法二选一：\n1.通过原神扫码绑定：\n请发送指令[原神扫码绑定]\n2.获取cookies的教程：\ndocs.qq.com/doc/DQ3JLWk1vQVllZ2Z1\n获取后，使用[ysb cookie]指令绑定",
        )
    # 获得签到信息
    sign_info = await sr_get_sign_info(uid, cookie.cookie)
    print(sign_info)
    # 获取签到列表
    sign_list = await sr_get_sign_list()
    print(sign_list)
    # 初步校验数据
    if sign_info and "data" in sign_info and sign_info["data"]:
        sign_info = sign_info["data"]
    else:
        logger.info(
            "星铁加强签到", "➤", {"用户": user_id, "UID": uid}, "出错, 请检查Cookies是否过期！", False
        )
        return False, "签到失败...请检查Cookies是否过期！"
    # 检测是否已签到
    if sign_info["is_sign"]:
        logger.info("星铁加强签到", "➤", {"用户": user_id, "UID": uid}, "今天已经签过了", True)
        global already
        already += 1
        getitem = sign_list["data"]["awards"][int(sign_info["total_sign_day"]) - 1][
            "name"
        ]
        getnum = sign_list["data"]["awards"][int(sign_info["total_sign_day"]) - 1][
            "cnt"
        ]
        get_im = f"签到获得{getitem}x{getnum}"
        sign_missed = sign_info["sign_cnt_missed"]
        return True, f"今日已签到!\n{get_im}\n本月漏签次数：{sign_missed}"
    # 实际进行签到
    Header = {}
    for index in range(4):
        # 进行一次签到
        sign_data = await sr_mihoyo_bbs_sign(
            uid=uid,
            ck=cookie.cookie,
            Header=Header,
        )
        # 检测数据
        if (
            sign_data
            and "data" in sign_data
            and sign_data["data"]
            and "risk_code" in sign_data["data"]
        ):
            # 出现校验码
            if sign_data["data"]["risk_code"] == 5001:
                logger.info(
                    "星铁加强签到",
                    "➤",
                    {"用户": user_id, "UID": uid},
                    f"该用户出现校验码，开始尝试进行验证...，开始重试第 {index + 1} 次！",
                    True,
                )
                gt = sign_data["data"]["gt"]
                challenge = sign_data["data"]["challenge"]
                validate, challeng = await get_validate(
                    gt, challenge, STAR_RAIL_SIGN_URL, uid, re
                )
                if (validate is not None) and (challeng is not None):
                    delay = 10 + random.randint(1, 10)
                    Header["x-rpc-challenge"] = challeng
                    Header["x-rpc-validate"] = validate
                    Header["x-rpc-seccode"] = f"{validate}|jordan"
                    logger.info(
                        "星铁加强签到",
                        "➤",
                        {"用户": user_id, "UID": uid},
                        f"已获取验证码, 等待时间{delay}秒",
                        True,
                    )
                    await asyncio.sleep(delay)
                else:
                    delay = 60 + random.randint(1, 60)
                    logger.info(
                        "星铁加强签到",
                        "➤",
                        {"用户": user_id, "UID": uid},
                        f"未获取验证码,等待{delay}秒后重试...",
                        False,
                    )
                    await asyncio.sleep(delay)
                continue
            # 成功签到!
            else:
                if index == 0:
                    logger.info(
                        "星铁加强签到", "➤", {"用户": user_id, "UID": uid}, f"该用户无校验码!", True
                    )
                    result = "[无验证]"
                else:
                    logger.info(
                        "星铁加强签到",
                        "➤",
                        {"用户": user_id, "UID": uid},
                        f"该用户重试 {index} 次验证成功!",
                        True,
                    )
                    result = "[有验证]"
                break
        # 重试超过阈值
        else:
            logger.info("星铁加强签到", "➤", {"用户": user_id, "UID": uid}, f"超过请求阈值...", False)
            return False, "签到失败...请求失败!\n请过段时间使用签到或手动进行签到"
    # 签到失败
    else:
        result = "签到失败!"
        logger.info(
            "星铁加强签到", "➤", {"用户": user_id, "UID": uid}, f"签到失败, 结果: {result}", False
        )
        return False, result
    # 获取签到列表
    status = sign_data["message"]
    getitem = sign_list["data"]["awards"][int(sign_info["total_sign_day"])]["name"]
    getnum = sign_list["data"]["awards"][int(sign_info["total_sign_day"])]["cnt"]
    get_im = f"本次签到获得{getitem}x{getnum}"
    new_sign_info = await sr_get_sign_info(uid, cookie.cookie)
    new_sign_info = new_sign_info["data"]
    if new_sign_info["is_sign"]:
        mes_im = "签到成功"
    else:
        result = f"签到失败, 状态为:{status}"
        return False, result
    sign_missed = sign_info["sign_cnt_missed"]
    result = f"{mes_im}{result}!\n{get_im}\n本月漏签次数：{sign_missed}"
    logger.info(
        "星铁加强签到",
        "➤",
        {"用户": user_id, "UID": uid},
        f"签到完成, 结果: {mes_im}, 漏签次数: {sign_missed}",
        True,
    )
    return True, result


@scheduler.scheduled_job(
    "cron",
    hour=config.sr_enable_hour,
    minute=config.sr_enable_minute,
    misfire_grace_time=10,
)
async def _():
    await sr_bbs_auto_sign()


async def sr_bbs_auto_sign():
    """
    指定时间，执行所有星铁签到任务
    """
    if not config.sr_enable:
        return
    t = time.time()  # 计时用
    subs = await MihoyoBBSSub.filter(sub_event="星铁签到").all()
    if not subs:
        # 如果没有星铁原神签到订阅，则不执行签到任务
        return
    logger.info(
        "星铁加强签到",
        f"开始执行星铁加强签到，共<m>{len(subs)}</m>个任务，预计花费<m>{round(100 * len(subs) / 60, 2)}</m>分钟",
    )
    coin_result_group = defaultdict(list)
    for sub in subs:
        uid2 = get_uid(str(sub.user_id))  # 星铁uid
        im, result = await sr_sign_in(str(sub.user_id), uid2, sub.uid, True)
        if (not im) and ("Cookie" in result):
            sub_data = {
                "user_id": str(sub.user_id),
                "uid": sub.uid,
                "sub_event": "星铁签到",
            }
            if sub := await MihoyoBBSSub.get_or_none(**sub_data):
                logger.info(
                    "星铁加强签到",
                    "➤",
                    {"用户": str(sub.user_id), "UID": uid2},
                    "ck失效已经自动取消签到",
                    False,
                )
                await sub.delete()
        result = result if im else f"UID{uid2}{result}"
        if sub.user_id != sub.group_id:
            coin_result_group[sub.group_id].append(
                {
                    "user_id": sub.user_id,
                    "uid": uid2,
                    "result": "失败" not in result and "Cookies" not in result,
                }
            )
        await asyncio.sleep(random.randint(15, 25))
    if config.vaapikai == "rr":
        _, jifen = await query_score()
    elif config.vaapikai == "dsf":
        jifen = "第三方验证"
    else:
        jifen = "错误的配置"
        logger.info("验证", "➤", "", "错误的配置", False)
    for group_id, result_list in coin_result_group.items():
        result_num = len(result_list)
        if result_fail := len(
            [result for result in result_list if not result["result"]]
        ):
            fails = "\n".join(
                result["uid"] for result in result_list if not result["result"]
            )
            msg = f"本群星铁签到共{result_num}个任务，其中成功{result_num - result_fail}个，失败{result_fail}个，失败的UID列表：\n{fails}\n方式:{jifen}"
        else:
            msg = f"本群星铁签到共{result_num}个任务，已全部完成\n方式:{jifen}"
        try:
            await get_bot().send_group_msg(group_id=int(group_id), message=msg)
        except Exception as e:
            logger.info("星铁加强签到", "➤➤", {"群": group_id}, f"发送结果失败: {e}", False)
        await asyncio.sleep(random.randint(3, 6))

    logger.info("星铁加强签到", f"获取完成，共花费<m>{round((time.time() - t) / 60, 2)}</m>分钟")
