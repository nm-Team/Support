---
title: 管理“账号与会话”
description: 了解 Telegram 登录授权、退出 nmBot 面板账号，以及绑定或取消绑定 nmTeam 账号的方法。
index: 2
---

<span id="nmbot"></span>

# 管理“账号与会话” { #管理对-nmbot-面板的授权 }

您可以使用 Telegram 账号登录 nmBot 面板，也可以在绑定 nmTeam 账号后使用它登录。登录 nmBot 面板与授予机器人群组管理员权限是两项独立操作；能登录 nmBot 面板，不代表能修改任意群组的设置。

<span id="telegram-app-nmbot"></span>

## 确认 Telegram 登录授权 { #在通过-telegram-迷你-app-使用或通过网页登录-nmbot-面板时授权 }

在浏览器中选择“通过 Telegram 登录”后，请检查 Telegram 授权窗口显示的账号和服务，再按提示确认。nmBot 面板用 Telegram 提供的身份信息识别您的账号；请求范围可能包括基本个人资料和允许机器人给您发送私信。

这些登录权限不允许机器人代替您的个人账号读取其他聊天或发送消息。您可以按 [Telegram 登录说明](https://core.telegram.org/bots/telegram-login)了解授权范围，并在授权窗口中确认实际请求的信息。

<span id="telegram"></span>

## 退出 nmBot 面板账号 { #管理您的-telegram-授权 }

如果您通过浏览器会话登录，打开“设置”中的“账号与会话”，在“当前会话”中选择“注销”。退出后，您仍可以通过 Telegram 或已绑定的 nmTeam 账号重新登录。

“其他会话”列出此设备上保存的其他登录账号，您可以切换账号、在新页面中登录，或注销相应登录。在 Telegram 迷你 App 中打开 nmBot 面板时，账号来自 Telegram 提供的身份，页面中的会话选项可能与浏览器不同。

退出 nmBot 面板会话不会自动取消 nmTeam 账号绑定。如果您需要撤销 Telegram 对网站的登录授权，还需要在 Telegram 中管理相应的网站授权。

<span id="nmteam"></span>

## 绑定 nmTeam 账号 { #绑定-nmteam-账号 }

绑定后，您可以在 nmBot 面板登录页面选择“通过 nmTeam 账号登录”。首次绑定前，需要先用 Telegram 登录。

1. 打开 nmBot 面板的[“绑定 nmTeam 账号”页面](https://nmbot.nmnm.fun/#/settings/account/bind-nmteam-account)。页面会显示当前绑定状态。
1. 选择“绑定 nmTeam 账号”，在 nmTeam 账号授权页面检查账号和请求的信息后确认。
1. 返回 nmBot 面板，看到“绑定成功！”后检查显示的账号。

每个 nmTeam 账号只能绑定 1 个 Telegram 账号，每个 Telegram 账号也只能绑定 1 个 nmTeam 账号。将已与其他账号绑定的 nmTeam 账号用于新绑定时，原有绑定会解除。

## 取消 nmTeam 账号绑定 {#取消-nmteam-账号绑定}

在“绑定 nmTeam 账号”页面选择“取消绑定”。看到“取消绑定成功！”后，该 nmTeam 账号不再用于这项 nmBot 面板登录绑定。您仍可以使用 Telegram 登录 nmBot 面板。
