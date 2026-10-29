---
title: 获取“自定义表情”信息
description: 在私聊中获取已有自定义表情的 ID、HTML 和 MarkdownV2 写法。
index: 5
---

# 获取“自定义表情”信息

你可以把已有的 Telegram 自定义表情发给 nmBot，获取它的 ID 和格式代码。这项工具用于查看已有表情的信息，不会新建自定义表情。

## 查询“自定义表情”

1. 打开与 nmBot 的私聊。
1. 发送一条只包含自定义表情的消息。nmBot 会回复每个表情的 ID、HTML 和 MarkdownV2 写法。
1. 复制需要的格式代码，填入支持相应格式的[“消息模板”](../group/automation/message-templates.md)。

消息中不能混入普通文字、空格或普通表情，也不能附带其他类型的文字格式。群组中的消息不会触发这项查询。

如果你需要把图片调整为表情尺寸，可以使用[“转为表情”](stickers-and-emoji.md)。
