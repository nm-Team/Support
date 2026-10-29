---
title: 打开并登录“nmBot 面板”
description: 从 Telegram 或浏览器打开面板，登录后选择要管理的群组。
index: 1
---

<span id="如何启动-nmbot-面板"></span>
<span id="nmbot"></span>

# 打开并登录“nmBot 面板” { #启动-nmbot-面板 }

你可以在 nmBot 面板中管理群组、频道和个人设置。在 Telegram 中打开迷你 App，或在浏览器中登录后，都可以进入同一个面板。

<span id="在-telegram-中启动-nmbot-面板"></span>
<span id="telegram-nmbot"></span>

## 在 Telegram 中打开 { #mini-app }

1. 打开你与 nmBot 的私信，发送 `/panel`。nmBot 会回复面板入口。
1. 点按回复中的 Telegram 面板链接，打开迷你 App。

你也可以直接点按 nmBot 私信中的菜单按钮打开面板。如果 Telegram 请求授权，请确认使用的是你要管理群组的账号。

<span id="在-web-浏览器中启动-nmbot-面板"></span>
<span id="web-nmbot"></span>

## 在浏览器中登录 { #browser }

1. 打开 [nmBot 面板](https://nmbot.nmnm.fun)。页面会显示可用的登录方式。
1. 选择“通过 Telegram 登录”，按照 Telegram 授权窗口中的提示完成登录。

如果你已经[绑定 nmTeam 账号](authorization.md#%E7%BB%91%E5%AE%9A-nmteam-%E8%B4%A6%E5%8F%B7)，也可以选择“通过 nmTeam 账号登录”。尚未绑定的 nmTeam 账号不能用来登录面板。

<span id="panel"></span>

### 通过 `/panel` 指令打开 { #通过-panel-指令打开 }

你也可以在 Telegram 中发送 `/panel`，再点按“在浏览器中打开并登录”。这会打开浏览器中的面板登录入口。

## 选择要管理的群组 {#选择要管理的群组}

登录后，打开“对话”，选择目标群组。如果列表中没有该群组，先[将群组添加到面板](../group/reg-panel.md)。要让 nmBot 开始处理群组中的违规消息，还需要[授予管理员权限并启用“群组管理功能”](../group/setup.md)。

## 常见问题 {#常见问题}

如果页面无法打开，按[无法访问 nmBot 面板](../faq/cannot-access-panel.md)中的步骤检查。如果能打开页面却无法登录，查看[无法登录 nmBot 面板](../faq/cannot-log-in-to-panel.md)。

你可以在[管理面板登录和账号绑定](authorization.md)中了解登录授权、退出账号和取消绑定的方法。
