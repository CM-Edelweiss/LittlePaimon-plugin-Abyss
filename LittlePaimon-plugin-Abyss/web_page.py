from amis import (
    Form,
    LevelEnum,
    InputTime,
    Divider,
    InputText,
    Alert,
    Html,
    PageSchema,
    Page,
    Switch,
    Remark,
    InputTag,
    Action,
    Select,
)

from LittlePaimon.web.pages import admin_app

global_config_form = Form(
    title="全局配置",
    name="abyss_config",
    api="post:/LittlePaimon/api/abyss_config",
    body=[
        InputText(
            label="appkey密钥",
            name="appkey密钥",
            value="${appkey密钥}",
            labelRemark=Remark(shape="circle", content="人人网key密钥"),
        ),
        InputText(
            label="非白名单回复",
            name="非白名单回复",
            value="${非白名单回复}",
            labelRemark=Remark(shape="circle", content="非白名用户使用失败的回复"),
        ),
        Select(
            label="打码模式",
            name="打码模式",
            value="${打码模式}",
            labelRemark=Remark(shape="circle", content="选择打码模式"),
            options=[
                {"label": "人人", "value": "rr"},
                {"label": "第三方", "value": "dsf"},
                {"label": "人工(未完工)", "value": "rg"},
            ],
        ),
        InputText(
            label="人工验证网站",
            name="人工验证网站",
            value="${人工验证网站}",
            labelRemark=Remark(
                shape="circle",
                content="自定义人工验证网站(后面不要加/)",
            ),
        ),
        Select(
            label="自动签到打码模式",
            name="自动签到打码模式",
            value="${自动签到打码模式}",
            labelRemark=Remark(shape="circle", content="自动签到下打码模式(打码模式选择人工时生效)"),
            options=[
                {"label": "人人", "value": "rr"},
                {"label": "第三方", "value": "dsf"},
            ],
        ),
        InputText(
            label="第三方过码",
            name="第三方过码",
            value="${第三方过码}",
            labelRemark=Remark(
                shape="circle",
                content="使用第三方平台,例子(baidu.com?或者baidu.com?shen=114514&)开启后将放弃人人,人人key不填也没事",
            ),
        ),
        Divider(),
        InputTag(
            label="群聊白名单",
            name="群聊白名单",
            value="${群聊白名单}",
            enableBatchAdd=True,
            placeholder="添加白名单群号,回车添加",
            joinValues=False,
            extractValue=True,
            labelRemark=Remark(shape="circle", content="那些群可以用"),
        ),
        InputTag(
            label="用户白名单",
            name="用户白名单",
            value="${用户白名单}",
            enableBatchAdd=True,
            placeholder="添加启用白名单QQ号,回车添加",
            joinValues=False,
            extractValue=True,
            labelRemark=Remark(shape="circle", content="那些人可以用"),
        ),
        Divider(),
        Switch(
            label="验证米游社签到开关",
            name="验证米游社签到开关",
            value="${验证米游社签到开关}",
            onText="开启",
            offText="关闭",
        ),
        InputTime(
            label="验证米游社自动签到开始时间",
            name="验证米游社签到开始时间",
            value="${验证米游社签到开始时间}",
            labelRemark=Remark(shape="circle", content="会在每天这个时间点进行米游社自动签到任务，修改后重启生效"),
            inputFormat="HH时mm分",
            format="HH:mm",
        ),
        Divider(),
        Switch(
            label="验证星铁签到开关",
            name="验证星铁签到开关",
            value="${验证星铁签到开关}",
            onText="开启",
            offText="关闭",
        ),
        InputTime(
            label="验证星铁自动签到开始时间",
            name="验证星铁签到开始时间",
            value="${验证星铁签到开始时间}",
            labelRemark=Remark(shape="circle", content="会在每天这个时间点进行星铁自动签到任务，修改后重启生效"),
            inputFormat="HH时mm分",
            format="HH:mm",
        ),
        Divider(),
        Switch(
            label="验证米游币自动获取开关",
            name="验证米游币获取开关",
            value="${验证米游币获取开关}",
            onText="开启",
            offText="关闭",
        ),
        InputTime(
            label="验证米游币自动获取开始时间",
            name="验证米游币开始执行时间",
            value="${验证米游币开始执行时间}",
            labelRemark=Remark(shape="circle", content="会在每天这个时间点进行米游币自动获取任务，修改后重启生效"),
            inputFormat="HH时mm分",
            format="HH:mm",
        ),
    ],
    actions=[
        Action(label="保存", level=LevelEnum.success, type="submit"),
        Action(label="重置", level=LevelEnum.warning, type="reset"),
    ],
)
tips = Alert(
    level="info",
    body=Html(
        html='显示不全请刷新网页,本插件<a href="https://github.com/CM-Edelweiss/LittlePaimon-plugin-Abyss" target="_blank">仓库地址</a>有问题请提issues或者<a href="https://qm.qq.com/cgi-bin/qm/qr?k=YlwBl3cCmMm0kBWakulAIG5Y1fhu5ja8&noverify=0&personal_qrcode_source=3" target="_blank">加我QQ</a>'
    ),
)
page = PageSchema(
    url="/abyss/configs",
    icon="fa fa-cube",
    label="加强签到",
    schema=Page(
        title="加强签到",
        initApi="/LittlePaimon/api/abyss_config_g",
        body=[tips, global_config_form],
    ),
)
admin_app.pages[0].children.append(page)
