---
title: 关于 nmTeam 帮助文档
description: 了解关于此帮助文档的信息。
index: 200
---

## nmTeam 帮助文档
nmTeam 帮助文档由 nmTeam 成员和社区志愿者共同编辑。

您可以在 [GitHub](https://github.com/nm-Team/nmBot-Telegram-doc) 上参与贡献此文档。

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