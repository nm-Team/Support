---
title: 获取自定义表情信息
description: 在私信中获取已有自定义表情的 ID、HTML 和 MarkdownV2 写法。
index: 5
---

# 获取自定义表情信息

你可以把已有的 Telegram 自定义表情发给 nmBot，获取它的 ID 和格式代码。这项工具用于查看已有表情的信息，不会新建自定义表情。

## 查询自定义表情

1. 打开与 nmBot 的私信。
1. 发送一条只包含自定义表情的消息。nmBot 会回复每个表情的 ID、HTML 和 MarkdownV2 写法。
1. 复制需要的格式代码，填入支持相应格式的[“消息模板”](../group/automation/message-templates.md)。

消息中不能混入普通文字、空格或普通表情，也不能附带其他类型的文字格式。群组中的消息不会触发这项查询。

如果你需要把图片[转为表情尺寸](stickers-and-emoji.md)，可以回复图片发送 `/toemoji`。
