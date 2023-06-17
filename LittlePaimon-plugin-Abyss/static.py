""""摆"""
import json
import random
from LittlePaimon.utils.api import (
    random_hex,
    random_text,
    get_old_version_ds,
    get_cookie,
)
from LittlePaimon.utils.requests import aiorequests
from LittlePaimon.utils.logger import logger
from .api import get_validate

# 验证码
bbs_api = "https://bbs-api.mihoyo.com"
bbs_get_captcha = bbs_api + "/misc/api/createVerification?is_high=true"
bbs_captcha_verify = bbs_api + "/misc/api/verifyVerification"


async def get_pass_challenge(user_id, uid) -> str:
    cookie = await get_cookie(user_id, uid, True, True)
    if not cookie:
        return "你尚未绑定Cookie和Stoken，请先用ysb指令绑定！"
    if cookie.stoken is None:
        return "你绑定Cookie中没有login_ticket，请重新用ysb指令绑定！"
    headers = {
        "DS": get_old_version_ds(),
        "cookie": cookie.stoken,
        "x-rpc-client_type": "2",
        "x-rpc-app_version": "2.38.1",
        "x-rpc-sys_version": "12",
        "x-rpc-channel": "miyousheluodi",
        "x-rpc-device_id": random_hex(32),
        "x-rpc-device_name": random_text(random.randint(1, 10)),
        "x-rpc-device_model": "Mi 10",
        "Referer": "https://app.mihoyo.com",
        "Host": "bbs-api.mihoyo.com",
        "User-Agent": "okhttp/4.8.0",
    }
    req = await aiorequests.get(
        url=bbs_get_captcha,
        headers=headers,
        timeout=30,
    )
    data = req.json()
    if data["retcode"] != 0:
        return "过码失败，请检查stoken是否有效"
    gt = data["data"]["gt"]
    ch = data["data"]["challenge"]
    validate, ch = await get_validate(gt, ch, bbs_get_captcha, uid, False)
    if validate:
        req = await aiorequests.post(
            url=bbs_captcha_verify,
            headers=headers,
            json={
                "geetest_challenge": data["data"]["challenge"],
                "geetest_seccode": validate + "|jordan",
                "geetest_validate": validate,
            },
        )
        check = req.json()
        if check["retcode"] == 0:
            logger.info("米游社过码", "➤", "", "成功", True)
            return "过码成功,不一定解除"
    return "过码失败,请稍后再试"
