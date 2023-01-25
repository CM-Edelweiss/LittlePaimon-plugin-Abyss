<p align="center" >
  <a href="https://github.com/CMHopeSunshine/LittlePaimon/tree/nonebot2"><img src="http://static.cherishmoon.fun/LittlePaimon/readme/logo.png" width="256" height="256" alt="LittlePaimon"></a>
</p>
<h1 align="center">小派蒙|LittlePaimon-plugin-Abyss</h1>
<h4 align="center">✨为LittlePaimon插件提供实时便签和签到接入接码平台✨</h4>

<p align="center">
    <a href="https://cdn.jsdelivr.net/gh/CMHopeSunshine/LittlePaimon@master/LICENSE"><img src="https://img.shields.io/github/license/CMHopeSunshine/LittlePaimon" alt="license"></a>
    <img src="https://img.shields.io/badge/Python-3.9+-yellow" alt="python">
    <img src="https://img.shields.io/badge/Version-3.0.0rc3-green" alt="version">
    <a href="https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&inviteCode=MmWrI&from=246610&biz=ka"><img src="https://img.shields.io/badge/QQ频道交流-尘世闲游-blue?style=flat-square" alt="QQ guild"></a>
</p>

## 丨❗注意

代码没有经过充分测试，可能有亿点问题，有问题请提issues

vaapi应该是http://...?..=..&或者http://...?

## 丨📖 使用
把`LittlePaimon-plugin-Abyss`文件夹放在`LittlePaimon\LittlePaimon\plugins\`里

指令看小派蒙帮助图

## 丨⚙️ 配置
在 nonebot2 项目的`.env.*`文件中添加下表中的必填配置
| 配置项 | 必填 | 默认值 |  说明 |
|:-----:|:----:|:----:|:----:|
| enable | 否 | True | 米游社签到开关 |
| enable_hour | 否 | 7 | 时 |
| enable_minute | 否 | 5 | 分 |
| myb | 否 | True | 米游币获取开关 |
| myb_hour | 否 | 8 | 时 |
| myb_minute | 否 | 5 | 分 |
| appkey | 是 | ? | 人人图像打码的key |
| whitelist | 是 | [] | 可使用的群 |
| vaapi | 否 | 空 | 使用别的接码 |

## 丨💸鸣谢
- [LittlePaimon](https://github.com/CMHopeSunshine/LittlePaimon)实时便签和米游币获取代码（~~直接开抄~~）
- [GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID/tree/nonebot2-beta1)签到代码（~~直接开抄~~）