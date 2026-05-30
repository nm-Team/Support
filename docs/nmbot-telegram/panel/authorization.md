---
title: 管理对 nmBot 的授权
description: 了解在使用 nmBot 面板时的 Telegram 授权与 nmTeam 账号绑定。
index: 2
---

# 管理对 nmBot 的授权

在使用 nmBot 和 nmBot 面板时，您或许会授权 nmBot 访问您的 Telegram 账号。

## 在通过 Telegram 迷你 App 使用或通过网页登录 nmBot 面板时授权

在通过 Telegram 迷你 App 使用或通过网页登录 nmBot 面板时，您需要授权 nmBot 获取您的 Telegram 账号信息，以便 nmBot 确认确实是您在登录。
根据登录方式的不同，nmBot 获取的信息可能包括您的账号名称、用户名、用户 ID、头像等，同时还可能获得向您发送私信的权限。技术细节可在 [Telegram 迷你 App](https://core.telegram.org/bots/webapps#webappinitdata) 和 [Telegram Login Widget](https://core.telegram.org/widgets/login-legacy#receiving-authorization-data) 网站查看。
此授权仅用于身份验证，并将不会允许 nmBot 访问您的个人账号或收取、修改或发送您的消息。
Telegram 会在首次请求时向您显示弹窗来要求您确认授权。只有您在 Telegram 应用中点击确认或 Telegram 网站上授权并在 Telegram 应用中验证，这些信息才会发送给 nmBot。

![Telegram 登录授权弹窗](https://github.com/user-attachments/assets/487aff88-1ef4-4806-9b67-cb1e90b8c8c1)

当通过网页上的 Telegram Login Widget 登录 nmBot 面板时，请求权限的机器人可能来自 @nmpanelbot 而不是 @nmnmfunbot。这是我们向新版 nmBot 面板过渡时的备用机器人。

### 管理您的 Telegram 授权

您可以在设置 (Settings) - 隐私和安全 (Privacy and Security) - 活跃网站 (Active Websites) 查看现有授权。

![Telegram 活跃网站授权列表](https://github.com/user-attachments/assets/3e684ede-e7e0-45d1-862b-13c8ef633001)

若不再需要授权，可以向右滑动并选择“注销 (Log out)”来取消授权。

## 绑定 nmTeam 账号

您可以将 nmTeam 账号绑定到您 Telegram 账号的 nmBot 中，方法是登录 nmBot 面板，转到设置并点选 nmTeam 账号设置项。
nmBot 将获取您的 nmTeam 账号 ID、头像、昵称、邮箱等基本信息，这些信息可在授权页面查看。
