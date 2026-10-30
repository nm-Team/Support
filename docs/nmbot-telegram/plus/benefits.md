---
title: 查看 nmBot+ 权益
description: 分清个人和群组的订阅范围，查看各项高级功能的设置方法。
index: 1
---

<span id="nmbot"></span>

# 查看 nmBot+ 权益 {#nmbot-权益}

您可以在 nmBot 面板的“nmBot+”中查看所选账号、群组或频道适用的权益。个人和对话的订阅分别生效。只有在功能明确支持时，个人订阅才能用于您管理的群组，例如处理成员时删除最近消息。

<span id="_1"></span>

## 查看群组的 nmBot+ 权益 {#群组}

在 nmBot 面板的“对话”中选择目标群组，再打开“nmBot+”。这里会列出该群组可用的高级功能；购买入口还会显示适用于该群组类型和成员人数的计划。

您可以从对应功能页面了解订阅后开放的设置：

- [群组功能管理权限](../group/admin-rights-and-features.md)允许群主调整不同功能的管理权限。
- [“骚扰消息拦截”](../group/moderation/anti-spam.md)提供自定义骚扰规则。
- [“自定义指令列表”](../group/configuration/commands.md)允许调整群组输入框的指令菜单。
- [“呼叫群组管理员”](../group/moderation/call-administrators.md)提供自定义关键词和私信通知等选项。
- [删除成员最近消息](../group/moderation/member-actions.md#%E6%B8%85%E7%90%86%E6%9C%80%E8%BF%91%E6%B6%88%E6%81%AF)可配合封禁、禁言、移出或警告使用。
- [“入群验证”](../group/moderation/join-verification.md)提供更多验证和封禁设置。
- [“退群消息”和“入群请求通知消息”](../group/automation/member-messages.md)可以在成员退出或申请加入时发送模板，入群欢迎还可选择更多自动删除时长。
- [“新成员权限限制”](../group/moderation/new-member-permissions.md)允许为新成员设置临时发言限制。
- [“定时任务”](../group/automation/scheduled-tasks.md)可以选择“不更改权限限制”来仅发送消息，并使用置顶和清理上次任务消息等高级设置。未订阅群组也能创建调整权限或自动删除设置的任务，并随任务发送消息。
- [“关键词回复”](../group/automation/keyword-replies.md)提供更多回复和动作选项。
- [“联防联控机制”](../group/moderation/joint-prevention.md)支持加入更多共享方案，以及自动添加或同步新封禁的用户。
- [“按消息类型删除消息”](../group/moderation/auto-delete-messages.md)可在删除违规内容后警告发送者。
- [退群成员的“自动封禁”](../group/moderation/departing-members.md)可以设置封禁时长。
- [“nmartChat+”](../nmbot-intelligence/nmartchat.md)支持继续对话，[“同频气氛组”](../group/automation/channel-commentary.md)提供更多语气和人设选择。

<span id="_2"></span><span id="_3"></span><span id="_4"></span><span id="_5"></span><span id="_6"></span><span id="_7"></span><span id="_8"></span><span id="_9"></span><span id="_10"></span><span id="_11"></span><span id="_12"></span><span id="_13"></span><span id="_14"></span><span id="_15"></span><span id="_16"></span><span id="_17"></span>
<span id="nmbot-配置权限管理"></span><span id="自定义骚扰规则"></span><span id="群组指令列表设置"></span><span id="呼叫群组管理员"></span><span id="封禁并删除最近消息"></span><span id="入群验证"></span><span id="入群请求通知消息"></span><span id="封禁退出群组的用户时长"></span><span id="新成员权限限制"></span><span id="定时任务"></span><span id="关键词回复"></span><span id="入群欢迎"></span><span id="按消息类型警告用户"></span><span id="解锁限制"></span>

订阅不会替代 Telegram 管理员权限。执行删除、禁言或封禁时，nmBot 和操作人仍然需要相应权限。

<span id="nmbot_1"></span><span id="解锁限制_1"></span><span id="封禁并删除最近消息_1"></span>

## 查看个人的 nmBot+ 权益 {#用户}

从 nmBot 面板的“设置”打开“nmBot+”，您会看到个人账号适用的权益。这里购买的计划作用于您的个人账号，具体可用功能会列在页面中。

个人订阅支持以下功能：

- [nmBot MCP](../mcp.md)可保留更多访问令牌，并获得更高的请求额度。
- [“nmBot Copilot”](../nmbot-intelligence/copilot.md#%E9%80%89%E6%8B%A9%E6%99%BA%E8%83%BD%E8%81%8A%E5%A4%A9%E7%AD%89%E7%BA%A7)可以选择“高级”智能聊天等级。
- 在您有管理权限的群组中，可以使用[清理最近消息的成员操作](../group/moderation/member-actions.md#%E6%B8%85%E7%90%86%E6%9C%80%E8%BF%91%E6%B6%88%E6%81%AF)和 `/dwarn`，即使该群组没有订阅。
- [“接收群组呼叫管理员通知”](../panel/settings/notifications.md)可以关闭，让 nmBot 跳过向您发送这类通知。
- [“商业关键词回复”](../business/keyword-replies.md)可使用自动删除和标记已读，并可创建更多[“商业定时任务”](../business/scheduled-task.md)。

## 处理 nmBot+ 权益没有生效 {#处理权益没有生效}

您可以在购买对象的“nmBot+”中查看“当前状态”和“过期日”。如果个人状态显示激活而群组仍显示未激活，需要查看目标群组自己的订阅状态。

付款后，页面可能先提示正在处理订单。状态长时间没有更新时，可以[联系 nmTeam 支持](../support.md)。
