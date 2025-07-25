# Telegram <ruby>数据中心<rt>DataCenter</rt></ruby>查询

可以帮助您快速查询账号所在的 Telegram 数据中心。

## 操作＞查询<ruby>数据中心<rt>DataCenter</rt></ruby>

　　方法1. <b>私信 nmBot 之后发送`/dc`指令。</b><br/>
　　方法2. <b>在 nobot 所在的群组中使用 `/dc` 指令。</b>

⚠️ 需要设置头像才能查询。<br/>
　　群组管理员可以限制用户使用 `/dc` 指令。详情请转到nobot后台中`限制群成员使用指令`功能<br>
　　为避免泄露隐私以及影响其他用户，请尽可能在私信中使用。

⚠️ 在群组中查询数据中心时，除了您的数据中心，nmBot 还会依据群组头像推测群组所在的数据中心。<br>
　　可以使用 `/dc` 指令回复一条消息，以查询该消息发送者的数据中心。<br>
　　您还可以在 `/dc` 指令后添加一个 Telegram 用户 ID 或群组/频道用户名，以查询该用户的数据中心。


## 关于＞Telegram <ruby>数据中心<rt>DataCenter</rt></ruby>

　　Telegram 有 5 个<ruby>数据中心<rt>DataCenter</rt></ruby>，其中 DC1 与 DC3 位于<ruby>美国迈阿密<rt>USA Miami</rt></ruby>，DC2 与 DC4 位于<ruby>荷兰阿姆斯特丹<rt>NL Amsterdam</rt></ruby>，DC5 位于<ruby>新加坡<rt>Singapore</rt></ruby>。

　　账号所在的数据中心，在正常情况下并不会影响您正常使用 Telegram。

　　对于个人用户、群组和频道，nmBot 通过获取并解码头像的文件标识符，来判断该文件所在的数据中心，进而得出该对话的数据中心。
　　这一判断并不总是准确的，例如，对群组和频道而言，其头像的数据中心可能会随设置头像的对话管理员的变化而变化。

　　若要了解关于 Telegram 数据中心的详情，您可以参考第三方文章：  
[Telegram DC 之都市传说 - Coxxs](https://dev.moe/2564)[（在互联网档案馆查看）](http://web.archive.org/web/20230211164632/https://dev.moe/2564)

　　若要了解关于查询的细节，您可以参考第三方文章：  
[通过 Telegram file_id 判断文件存储的数据中心 - WooMai](https://woomai.me/talk/telegram-determine-dc-by-file-id/#%E6%9F%A5%E8%AF%A2%E6%95%B0%E6%8D%AE%E4%B8%AD%E5%BF%83)[（在互联网档案馆查看）](http://web.archive.org/web/20221206175516/https://woomai.me/talk/telegram-determine-dc-by-file-id/#%E6%9F%A5%E8%AF%A2%E6%95%B0%E6%8D%AE%E4%B8%AD%E5%BF%83)
