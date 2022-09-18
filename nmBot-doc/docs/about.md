<center>
<!-- 图片 -->
<img src="https://websiteres.nmteam.xyz/producticon/nmBot/logo@128.png" width="128" height="128" alt="nmBot logo" />  
## nmBot  
© 2022 nmTeam. All rights reserved.  
</center>
nmBot 是由 nmTeam 出品的 Telegram 机器人，兼具扎实可靠的群组管理功能和温暖搞笑的互动娱乐功能。  

nmBot 高效安全、保障隐私。欢迎在您的群组免费使用 nmBot。  

## 关于 nmBot 帮助文档

此帮助文档由 nmTeam 成员和社区志愿者共同编辑。

## 贡献者
<style>
    #contributors {
        display: flex;
        flex-wrap: wrap;
    }
    .contributor {
        display: flex;
        flex-direction: row;
        align-items: center;
        margin: 1rem 1rem 1rem 0;
    }
    .contributor img {
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    .contributor span {
        font-size: 1.2em;
        color: #000;
    }
</style>
<div id="contributors"></div>
<script>
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("GET","https://api.github.com/repos/nm-Team/nmBot-Telegram-Doc/contributors",true);
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var contributors = JSON.parse(xmlhttp.responseText);
            var contributorsDiv = document.getElementById("contributors");
            for (var i = 0; i < contributors.length; i++) {
                var contributor = contributors[i];
                var contributorDiv = document.createElement("div");
                contributorDiv.innerHTML = '<a class="contributor" href="' + contributor.html_url + '" target="_blank"><img src="' + contributor.avatar_url + '" alt="' + contributor.login + '" /><span>'+contributor.login+'</span></a>';
                contributorsDiv.appendChild(contributorDiv);
            }
        }
    }
    xmlhttp.send();
</script>