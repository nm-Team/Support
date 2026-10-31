---
title: 将 nmBot 设置为商业机器人
description: 在 Telegram 中连接 nmBot，选择允许处理的私信和账号权限。
index: 1
---

# 将 nmBot 设置为商业机器人 {#将-nmbot-设置为商业机器人}

如果你希望 nmBot 以你的身份回复私信，或定时更改你的个人资料，可以在 Telegram 中将它连接到个人账号。你可以自己选择允许 nmBot 处理的私信，以及它能够执行的操作。

<span id="android-telegram"></span>
<span id="ios-telegram"></span>
<span id="telegram-desktop"></span>
<span id="在-android-版-telegram-中设置"></span>
<span id="在-ios-版-telegram-中设置"></span>
<span id="在-telegram-desktop-中设置"></span>

## 连接 nmBot

你可以在 Telegram 的[“聊天自动化 (Chat Automation)”入口](https://telegram.org/blog/ai-bot-revolution-11-new-features#chat-automation-in-profiles)连接 nmBot。不同客户端的入口名称可能略有不同。

1. 打开 Telegram 的“设置 (Settings)”。
1. 打开“聊天自动化 (Chat Automation)”，选择要连接的机器人。
1. 输入 `nmnmfunbot`，选择 nmBot。
1. 选择允许处理的私信和需要的权限，完成连接。

如果你的客户端仍显示旧入口，可以在“Telegram Business”下打开“聊天机器人 (Chatbot)”设置。

## 在 nmBot 面板查看“商业机器人状态” {#查看商业机器人状态}

1. [打开 nmBot 面板](../panel/launch.md)，选择“商业”。
1. 在“商业机器人状态”下查看“当前状态”。显示“已设置”时，表示账号已经连接。
1. 点按“当前状态”，查看已授权的权限。

如果显示“未设置”，nmBot 无法代你执行商业功能。你可以[检查 Telegram 中的连接](#%E9%9D%A2%E6%9D%BF%E6%98%BE%E7%A4%BA%E6%9C%AA%E8%AE%BE%E7%BD%AE)。

## 选择授权范围

你可以在 Telegram 中决定 nmBot 能够处理哪些私信。被排除的对话不会交给 nmBot 处理。

你需要根据要使用的功能授予权限：

- [“商业关键词回复”](keyword-replies.md)需要回复消息权限。自动删除和标记已读还需要各自对应的权限。
- [“商业定时任务”](scheduled-task.md)需要更改名称、简介或用户名的权限，取决于你在任务中选择更新的资料。

授权后，nmBot 可以在所选对话中以你的身份操作。撤销某项权限后，依赖这项权限的操作会失败。

## 断开连接

你可以在 Telegram 的机器人连接设置中断开 nmBot。nmBot 会向你发送连接停用通知，nmBot 面板中的状态会变为“未设置”。已经发送的消息和已经更改的账号资料不会因为断开连接而恢复。

<span id="_3"></span>

## 如果 nmBot 面板中显示“未设置” {#面板显示未设置}

你可以先在 Telegram 中检查连接是否启用。如果 Telegram 中已经连接，但 nmBot 面板状态没有同步，可以断开后重新连接。重新连接时需要再次确认允许处理的私信和权限。
