---
title: 使用“nmartChat”对话
description: 在私信或群组中与 nmBot 对话，或为群组启用 nmartChat+。
index: 2
---

# 使用“nmartChat”对话 {#nmartchat-智能聊天}

你可以在私信或群组中用“nmartChat”与 nmBot 对话。在群组中发送以 `nm` 开头的文字，或回复 nmBot 的消息，就可以发起对话。

<span id="nmartchat"></span>
<span id="nmartchat_1"></span>
<span id="nmartchat_2"></span>

## 开始对话 {#开始聊天}

1. 打开与 nmBot 的私信，或进入允许“nmartChat”的群组。
1. 发送 `nm 今天过得怎么样`，或回复 nmBot 的消息输入你想说的话。
1. nmBot 会在原消息下回复。你可以继续回复它的消息来延续对话。

在私信中，你也可以直接发送普通文字。转发的消息不会触发这类对话回复。如果不希望某条文字触发回复，可以在文字中加入 `-n`。

## 开启或关闭群组“nmartChat” {#群聊中如何开启-nmartchat}

你需要[启用“群组管理功能”](../group/setup.md)，并拥有“智能聊天”的[群组功能管理权限](../group/admin-rights-and-features.md)。

1. 在 nmBot 面板的“对话”中选择目标群组，打开“智能聊天”。
1. 打开或关闭“nmartChat”。更改会直接保存，后续群组消息按新的设置处理。

“群组管理功能”关闭时，“nmartChat”默认开启，nmBot 面板中的“智能聊天”设置只读。要关闭群组中的“nmartChat”，需要先启用“群组管理功能”。

## <nmbot-plus-icon></nmbot-plus-icon> 启用“nmartChat+” {#启用-nmartchat-plus}

订阅 nmBot+ 的群组可以在“智能聊天”中打开“nmartChat+”。你回复“nmartChat+”的消息继续对话时，它可以利用 nmBot 智能，结合这段对话之前的内容作答。

“nmartChat+”使用生成式人工智能，回复可能出现错误或不合适的内容。关闭这项选项后，群组会恢复普通“nmartChat”的回复方式。

## 用贴纸和“nmartChat”互动 {#nmartchat-贴纸回复逻辑}

你可以在私信中发送贴纸，或在群组中用贴纸回复 nmBot。它可能回复同一张贴纸，也可能从原贴纸包或群组贴纸包中选择其他贴纸。没有贴纸包的贴纸可能无法触发回复。

## 如果没有收到对话回复 {#没有收到聊天回复}

你可以检查群组中的“nmartChat”开关，以及消息是否为转发、包含 `-n`，或是普通机器人指令。短时间内连续请求时，部分消息可能没有回复，可以稍后重试。

如果你希望 nmBot 评论频道自动转发到讨论群的帖子，可以配置[“同频气氛组”](../group/automation/channel-commentary.md)。
