"""
LittlePaimon-plugin-Abyss的人工验证后端
"""

from gevent import monkey

monkey.patch_all()

import threading
import time
from flask import Flask, abort, jsonify, request, send_from_directory, render_template
from gevent.pywsgi import WSGIServer
from uuid import uuid4

app = Flask(__name__)

cv_put = threading.Condition()
cv_get = threading.Condition()


tasks = {}
pending = []
doing = []
done = []
ddd = []


def main(address="0.0.0.0", port=5000):
    http_server = WSGIServer((address, port), app)
    http_server.serve_forever()


@app.route("/")
def root():
    return f"<html><head><title>Edelweiss的验证</title>后端./geetest?gt=XXX&challenge=XXX&uid=XXX<br />人工./validate?uid=XXX<br />默认超时为30s</html>"


@app.route("/geetest")
def crack():
    print(request.args)
    if all([key in request.args for key in ["gt", "challenge", "uid"]]):
        session = str(uuid4())
        uid = request.args.get("uid")
        tasks[session] = {
            "code": -1,
            "gt": request.args.get("gt"),
            "challenge": request.args.get("challenge"),
            "success": request.args.get("success", 1),
            "validate": "",
            "seccode": "",
            "uid": uid,
        }
        print(f"UID{uid}:加入列表")
        pending.append(session)
        ddd.append(session)
        with cv_put:
            cv_put.notify_all()
        with cv_get:
            if cv_get.wait_for(lambda: session in done, timeout=30):
                if tasks[session]["code"] == 0:
                    challenge = tasks[session]["challenge"]
                    validate = tasks[session]["validate"]
                    seccode = tasks[session]["seccode"]
                    del tasks[session]
                    ddd.remove(session)
                    return jsonify(
                        {
                            "code": 0,
                            "message": "success",
                            "data": {
                                "challenge": challenge,
                                "validate": validate,
                                "seccode": seccode,
                            },
                        }
                    )
                else:
                    del tasks[session]
                    ddd.remove(session)
                    return jsonify(
                        {
                            "code": -2,
                            "message": "error",
                        }
                    )
            else:
                if session in pending:
                    pending.remove(session)
                if session in doing:
                    doing.remove(session)
                done.append(session)
                del tasks[session]
                ddd.remove(session)
                return jsonify(
                    {
                        "code": -3,
                        "message": "timeout",
                    }
                )
    else:
        return jsonify(
            {
                "code": -1,
                "message": "gt challenge and uid error",
            }
        )


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        "static", "favicon.ico", mimetype="image/vnd.microsoft.icon"
    )


@app.route("/feedback", methods=["POST"])
def feedback():
    if all([key in request.form for key in ["session", "code"]]):
        session = request.form.get("session")
        if session in doing:
            if request.form.get("code") == "0" and all(
                [key in request.form for key in ["challenge", "validate", "seccode"]]
            ):
                tasks[session]["code"] = 0
                tasks[session]["challenge"] = request.form.get("challenge")
                tasks[session]["validate"] = request.form.get("validate")
                tasks[session]["seccode"] = request.form.get("seccode")
            doing.remove(session)
            done.append(session)
            with cv_get:
                cv_get.notify_all()
            return jsonify(
                {
                    "code": 0,
                    "message": "success",
                }
            )
        else:
            return jsonify(
                {
                    "code": -2,
                    "message": "invalid session",
                }
            )
    else:
        return jsonify(
            {
                "code": -1,
                "message": "invalid parameter",
            }
        )


@app.route("/fetch")
def fetch():
    with cv_put:
        if cv_put.wait_for(lambda: pending, timeout=15):
            session = pending.pop(0)
            doing.append(session)
            uid = tasks[session]
            if uid["uid"] == request.args.get("uid"):
                return jsonify(
                    {
                        "session": session,
                        "gt": uid["gt"],
                        "challenge": uid["challenge"],
                        "success": uid["success"],
                    }
                )
            else:
                abort(503)
        else:
            abort(503)


@app.route("/validate")
def task2():
    if all([key in request.args for key in ["uid"]]):
        uid = request.args.get("uid")
        print(f"UID{uid}:访问网页")
        for uid2 in ddd:
            if uid2 in tasks:
                if ck := tasks[uid2]["uid"]:
                    if uid in ck:
                        print(uid2)
                        return render_template("geetest.html", uid=uid)
        return f"<html><head><title>Edelweiss的验证</title><h1>UID{uid} 当前无剩余验证</h1></head></html>"
    else:
        return f"<html><head><title>Edelweiss的验证</title><h1>你的访问UID呢</h1></head></html>"


if __name__ == "__main__":
    main()
