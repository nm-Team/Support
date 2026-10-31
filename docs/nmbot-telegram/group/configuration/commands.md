---
title: 设置“自定义指令列表”
description: 选择群组输入框中显示的指令，或恢复默认菜单。
index: 2
---

<span id="_1"></span>

# 设置“自定义指令列表” {#设置自定义指令列表和指令映射}

你可以为群组调整 Telegram 输入框中的指令菜单，让成员更容易找到常用指令。“自定义指令列表”只改变菜单中显示的项目，指令本身的功能和权限要求不会改变。

![Telegram 群组输入框上方显示的机器人指令菜单](/assets/images/nmbot/guides/group-commands-menu.png)

<span id="_2"></span>

## <nmbot-plus-icon></nmbot-plus-icon> 设置“自定义指令列表” {#设置自定义指令列表}

目标群组需要订阅 nmBot+，你需要拥有修改其他管理功能的[群组功能管理权限](../admin-rights-and-features.md)。

1. 在 nmBot 面板的“对话”中选择目标群组，打开“自定义指令列表”。
1. 勾选需要在 Telegram 输入框菜单中显示的指令。至少保留一项。
1. 点按“保存”。如果保存成功，你会看到“保存成功”，群组的指令菜单会使用这次选择。

管理员和普通成员可能看到不同的菜单。若要禁止成员使用指令，请设置[“限制群成员使用指令”](../moderation/command-restrictions.md#%E5%85%81%E8%AE%B8%E4%BD%BF%E7%94%A8%E7%9A%84%E6%8C%87%E4%BB%A4)。

你可以重新打开页面，点按“取消自定义设置”恢复默认菜单。

<span id="创建指令映射"></span>
<span id="_3"></span>
<span id="移除指令映射"></span>
<span id="_4"></span>

如果你想为自己的常用指令设置别名，可以[创建和管理“指令映射”](../../tools/command-mapping.md)。
