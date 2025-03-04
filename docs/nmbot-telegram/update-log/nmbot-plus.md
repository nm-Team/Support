---
index: -2411
---

# nmBot+ (2024 年 11 月)

![nmBot+](../img/update-pictures/nmBot%20plus.png)

nmTeam 今日推出 nmBot+，一项为需要更多高级功能的 nmBot 用户和群组量身打造的专属付费方案。

nmBot+ 首发搭载 20 多项新功能，覆盖入群验证、群组管理、关键词回复等多个高级场景。

在群组中，nmBot+ 主要包括如下新功能：

- 管理员权限控制：作为群组的所有者，控制其他管理员对各项 nmBot 配置的修改权限。
- 更低限制：关键词回复、定时任务设置数量提高，同频气氛组每日回复条数提高、部分功能可设置消息模板数量提升。
- 自定义骚扰规则：自定义要判断为骚扰消息和骚扰用户的规则。
- 入群验证：添加自定义文本，自定义验证消息删除时间并享受超时时间和封禁时长的更多自定义选项。
- 新成员权限限制：限制新入群的成员在群组中可发送消息的类别。
- 关键词回复：警告发送指定关键词的用户。
- 定时任务：在群组中发送定时消息。
- 限制群成员发送指令：自定义在群组中要启用的指令。
- 自定义指令列表：自由选择群组输入框中显示的机器人指令。
- 呼叫群组管理员：自定义呼叫群组管理员的关键词，并在私信中接收通知。

为了使更多群组承担得起高级功能，nmBot+ 为群组提供更低的订阅价格：83% 的活跃群组每月只需 0.4 美元即可订阅 nmBot+。

nmBot+ 在 nmBot 面板开放购买，您需要在 Telegram 迷你 App 中打开 nmBot 面板并使用 Telegram 星币支付。成员数量超 1000 人的群组可在面板中领取 15 天免费试用。

\* 所有功能以实际使用为准，功能可能会根据实际情况调改。

## 2024 年 11 月 21 日 11:15
nmBot 版本号：24.11.5-wine+5911

- 修复了特定情况下“同频气氛组”和“自动回复频道帖子”功能对媒体组消息重复回复多次的问题。

## 2024 年 11 月 20 日 22:36
nmBot 版本号：24.11.4-wine+5910

- 修复了入群验证骚扰用户封禁时长设为“使用默认时长”时，设置无法正常生效的问题。
- 修复了选择消息模板时，“其他模板”部分的隐藏其他模板按钮图标未正常显示的问题。

## 2024 年 11 月 19 日 17:00
nmBot 版本号：24.11.3-wine+5908

- 为适用于个人账号的 nmBot+ 计划添加了额外说明，以免要为群组购买 nmBot+ 的用户误为个人账号购买 nmBot+。
- 修复了试用 nmBot+ 订阅会出现在可购买列表中的问题。

## 2024 年 11 月 19 日 14:01
nmBot 版本号：24.11.2-wine+5906

- 修复了保存商业关键词回复的问题。

## 2024 年 11 月 17 日 21:32
nmBot 版本号：24.11.1-wine+5903

- 增加了 /paysupport 指令，以便用户了解如何就支付问题获得支持。
- 添加了频道帖子调试信息的输出，并尝试暂时解决部分频道功能特定情况下不起作用的问题。
- 修复了支付处理出现未知错误时提示文本的问题。

## 2024 年 11 月 17 日 12:00
### <nmbot-plus-icon></nmbot-plus-icon> nmBot+
- 推出 nmBot+，这款付费计划允许您解锁更多高级 nmBot 功能。

### <nmbot-plus-icon></nmbot-plus-icon> nmBot 配置权限管理 
- 群组的所有者可以为不同用户设定对 nmBot 设置的管理权限。
    - 对于各项功能，权限可设为“默认”“可更改群组信息的管理员”“可添加管理员的管理员”或“仅群主”。
    - 群主还可为特定群组管理员针对某项功能添加例外。

### <nmbot-plus-icon></nmbot-plus-icon> 自定义骚扰规则
- 群组管理员可在 nmBot 骚扰消息拦截和入群验证自动拒绝骚扰用户入群功能中补充自己的匹配规则。

### <nmbot-plus-icon></nmbot-plus-icon> 群组指令列表设置 
- 群组管理员现在可以自定义在 Telegram App 中聊天时，消息输入框中出现的指令列表。

### <nmbot-plus-icon></nmbot-plus-icon> 呼叫群组管理员
- 支持自定义呼叫关键词：群组管理员可通过正则表达式自定义触发“呼叫群组管理员”功能的消息内容。
- 支持在私信中接收通知：群组成员呼叫 nmBot 时，在私信中向所有群组管理员（适用时包括匿名管理员）发送提示消息。
- 启用在私信中接收通知时，可关闭群组中呼叫消息中对群组管理员的提及。

### 入群验证
- <nmbot-plus-icon></nmbot-plus-icon> 支持自定义入群验证消息：群组管理员可在入群验证消息中添加自定义文本。
- nmBot 面板中支持查看入群验证历史记录。
    - <nmbot-plus-icon></nmbot-plus-icon> 订阅了 nmBot+ 的群组可查看 15 天内的历史记录，其他群组可查看 15 分钟内的历史记录。 
- <nmbot-plus-icon></nmbot-plus-icon> 入群验证可自定义更多验证超时时间和封禁用户时间。
- <nmbot-plus-icon></nmbot-plus-icon> 入群验证可为被 nmBot 识别或举报为骚扰的用户和被管理员拒绝的用户设置与默认不同的封禁用户时间。
- <nmbot-plus-icon></nmbot-plus-icon> 入群验证支持永久封禁多次加入群组失败的用户。
- 优化了 nmBot 面板“入群验证”页面设置项的排列。

### <nmbot-plus-icon></nmbot-plus-icon> 新成员权限限制
- 支持限制新加入群组的成员在一段时间内可发送消息的类型。

### 定时任务
- “锁定模式”现已更名为“定时任务”。
- <nmbot-plus-icon></nmbot-plus-icon> 支持在群组中发送定时消息。

### <nmbot-plus-icon></nmbot-plus-icon> 关键词回复
- 支持使用 nmBot AI 自动生成关键词回复。
- 支持通过关键词回复警告用户。
- 支持设置关键词回复随机发送消息的数量。

### <nmbot-plus-icon></nmbot-plus-icon> 入群欢迎
- 支持自定义入群欢迎消息的自动删除时间。

### <nmbot-plus-icon></nmbot-plus-icon> 解锁限制
- nmBot+ 为群组解锁一系列设置权限：
    - 同频气氛组功能的每日最大可回复消息数增加。
    - 关键词回复、定时任务的最大可设置数量增加。
    - 解锁“限制群成员发送指令”功能。
    - 关键词回复、锁定模式、自动回复频道消息功能的最大可选择消息模板数量增加。

### 其他改进
- 调整了“限制群成员使用指令”功能的开放逻辑：本次功能更新后使用 nmBot 的群组将无法免费使用“限制群成员使用指令”功能，订阅 nmBot+ 即可使用；本次功能更新前已经使用过 nmBot 的群组，群组成员数量达到 2000 人时即可使用该功能。
- 群组管理员修改部分无权限修改的设置时，新增了用户无权限修改的提示。
- 调整了 nmBot 面板设置项“新功能”标志的样式。

### 问题修复
- 修复了“已启用指令限制”提示无法正常显示的问题。
- 修复了 nmBot 面板部分对话框中输入框的边框颜色不正确的问题。
- 修复了在页面上的特定位置打开上下文菜单时位置计算异常的问题。
- 修复了 nmBot 面板无法正确显示话题群组的问题。
