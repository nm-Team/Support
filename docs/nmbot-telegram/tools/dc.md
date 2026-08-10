# Telegram 数据中心查询

nmBot 的 Telegram 数据中心查询功能可以帮助您快速查找账号所在的 Telegram 数据中心。

## 查询数据中心

您可以在与 nmBot 的私信或 nmBot 所在群组中使用 `/dc` 指令查询您账号所在的数据中心。

!!! note
    若群组管理员启用了“限制群成员使用指令”功能，您可能无法在群组中使用 `/dc` 指令。
    同时，我们建议您尽可能在私信中使用 `/dc` 指令，以免影响群组中的其他用户。

在群组中查询数据中心时，除了您的数据中心，nmBot 还会显示根据群组头像所推测的群组数据中心。
同时，您可以使用 `/dc` 指令回复一条消息，以查询该消息发送者的数据中心。
您还可以在 `/dc` 指令后添加一个 Telegram 用户 ID 或群组/频道用户名，以查询该用户的数据中心。

!!! note
    所有对话必须设置头像才能查询数据中心。

## 关于 Telegram 数据中心

Telegram 有 5 个数据中心 (Data Center, DC)，其中 DC1 与 DC3 位于美国迈阿密 (Miami, USA)，DC2 与 DC4 位于荷兰阿姆斯特丹 (Amsterdam, NL)，DC5 位于新加坡 (Singapore)。

一般来说，您的账号处于哪个数据中心并不影响您正常使用 Telegram。
但如果你想进一步了解自己账号位于的数据中心，或是在查看某些文件甚至访问 Telegram 时遇到了问题，你可以使用 nmBot 内置的 Telegram 数据中心查询功能来查询某个账号或文件归属的数据中心。

这一操作通过检查文件标识符来完成。
对于个人用户、群组和频道，nmBot 通过获取并解码头像的文件标识符，来判断该文件所在的数据中心，进而得出该对话的数据中心。
这一判断并不一定总是准确的，例如，对群组和频道而言，其头像的数据中心可能会随设置头像的对话管理员变化而变化。

若要了解关于 Telegram 数据中心的详情，您可以参考这篇第三方文章：  
[Telegram DC 之都市传说 - Coxxs](https://dev.moe/2564)[（在互联网档案馆查看）](http://web.archive.org/web/20230211164632/https://dev.moe/2564)

若要了解关于查询的细节，您可以参考这篇第三方文章：  
[通过 Telegram file_id 判断文件存储的数据中心 - WooMai](https://woomai.me/talk/telegram-determine-dc-by-file-id/#%E6%9F%A5%E8%AF%A2%E6%95%B0%E6%8D%AE%E4%B8%AD%E5%BF%83)[（在互联网档案馆查看）](http://web.archive.org/web/20221206175516/https://woomai.me/talk/telegram-determine-dc-by-file-id/#%E6%9F%A5%E8%AF%A2%E6%95%B0%E6%8D%AE%E4%B8%AD%E5%BF%83)
