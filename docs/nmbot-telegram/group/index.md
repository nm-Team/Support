---
title: 使用群组功能
description: 添加和配置 nmBot，管理群组消息与成员，并设置自动回复和配置迁移。
---

# 使用群组功能 {#使用群组功能}

<span id="_1"></span>

你可以用 nmBot [管理群组消息和成员](moderation/index.md)，也可以设置[自动回复与消息](automation/index.md)，让它回答常见问题、发送群组通知。第一次使用时，请先[启用“群组管理功能”](setup.md)，再按群组需要开启各项功能。

## 管理消息和成员 {#管理消息和成员}

你可以为新成员设置[“入群验证”](moderation/join-verification.md)，让他们验证身份后再发言；用[“骚扰消息拦截”](moderation/anti-spam.md)识别广告和诈骗内容，或[按类型自动删除消息](moderation/auto-delete-messages.md)，限制群组中可以发送的内容。

成员违反群规时，你可以[增加警告](moderation/warnings.md)，在警告次数达到阈值后自动封禁，也可以直接[禁言、封禁或移出成员](moderation/member-actions.md)。对于短时间内频繁发言的情况，可以设置[“发言频率限制”](moderation/speaking-frequency.md)，按消息类型调整计数权重。

<span id="_2"></span>

## 自动回复和发送消息 {#自动回复和发送消息}

你可以创建[“关键词回复”](automation/keyword-replies.md)，按消息内容、发送者等条件自动回复群规或帮助说明。[“消息模板”](automation/message-templates.md)可以在关键词回复、入群欢迎等功能中复用，方便统一维护常用内容。

你还可以设置[“入群欢迎”“退群消息”和“入群请求通知消息”](automation/member-messages.md)，在成员加入、退出或申请加入时发送内容。需要按时间发送通知或调整群组设置时，可以创建[“定时任务”](automation/scheduled-tasks.md)。

<span id="_3"></span>

## 备份与迁移配置 {#备份与迁移配置}

管理多个群组时，你可以[备份与迁移配置](configuration/index.md)，复用已有的群组设置、关键词回复和消息模板。[导入配置](configuration/import-export.md)前，nmBot 面板会列出将要修改的设置和新增内容，你可以忽略不需要修改的群组设置。
