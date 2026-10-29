---
title: 接入“nmBot MCP”并管理访问令牌
description: 创建 MCP Access Token，让外部工具在您的权限内读取和修改 nmBot 配置。
---

<span id="mcp-beta"></span><span id="mcp-配置-beta-版"></span><span id="mcp-配置可以做什么"></span><span id="mcp"></span>

# 接入“nmBot MCP”并管理访问令牌 {#接入-nmbot-mcp}

您可以在“MCP 配置”中创建访问令牌，让支持 MCP 的外部工具管理您的 nmBot 设置。工具能够读取和修改您的数据，所能执行的操作仍受您自己的账号和对话管理权限限制。

<span id="_1"></span><span id="使用前须知"></span><span id="在哪里打开-mcp-配置"></span>

## 创建“MCP Access Token” {#创建-mcp-access-token}

您需要先[登录面板](panel/launch.md)。普通账号最多保留 1 个有效令牌；个人账号订阅[“nmBot+”](plus/index.md)后，最多保留 5 个。

1. 在面板的“设置”中打开“MCP 配置”。
1. 点按“创建 Token”。页面会说明令牌允许外部工具读取和修改数据。
1. 点按“继续创建”。
1. 输入“Token 名称”，例如 `My VS Code`。
1. 确认创建。看到“Token 已创建”后，完整令牌会显示在弹窗中。
1. 点按“拷贝并关闭”，保存令牌。

<span id="_2"></span><span id="创建后会看到什么"></span><span id="为什么我之后看不到完整-token"></span><span id="token_2"></span>

完整令牌只显示一次，返回列表后只能看到掩码。持有令牌的人或工具可以访问您的 nmBot 数据；令牌泄露后，可以在列表中删除它，原令牌便无法继续连接。

## 配置“nmBot MCP”的连接 {#在其他-mcp-客户端中使用}

在支持 HTTP MCP 的客户端中，您需要填写以下连接信息：

- 服务地址：`https://nmbot-api.nmnm.fun/mcp`。
- 连接方式：HTTP，使用客户端的 Streamable HTTP 选项。
- HTTP 请求头：`Authorization: Bearer <您的 MCP Access Token>`。

您需要把占位文字替换为刚才创建的令牌，并保留 `Bearer ` 前缀。工具会列出账号可用的操作，其中可能包含发送消息、修改设置或删除数据的操作。外部客户端如何要求操作确认，取决于客户端自身的设置。

<span id="vs-code-nmbot"></span><span id="1-mcp"></span><span id="1-打开-mcp-用户配置"></span><span id="2-nmbot-mcp"></span><span id="2-添加-nmbot-mcp-服务器配置"></span><span id="3"></span><span id="3-保存并检查是否已加载"></span>

## 在“VS Code”中接入“nmBot MCP” {#在-vs-code-中使用-nmbot-mcp}

以下示例采用 [VS Code 格式的 MCP 配置](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)，适用于支持此格式和交互式输入变量的 Local 会话。Copilot 会话使用的配置格式和凭据传入方式可能不同，您可以按 [VS Code 的连接说明](https://code.visualstudio.com/docs/agent-customization/mcp-servers)选择对应配置位置。

1. 打开命令面板，运行 `MCP: Open User Configuration`。
1. 在打开的配置中加入下面的服务器和输入项。如果已有其他配置，把对应条目加入现有的 `servers` 和 `inputs`。

```json
{
  "inputs": [
    {
      "type": "promptString",
      "id": "nmbot-token",
      "description": "nmBot MCP Access Token",
      "password": true
    }
  ],
  "servers": {
    "nmbot": {
      "type": "http",
      "url": "https://nmbot-api.nmnm.fun/mcp",
      "headers": {
        "Authorization": "Bearer ${input:nmbot-token}"
      }
    }
  }
}
```

1. 保存配置，运行 `MCP: List Servers`，选择 `nmbot` 并启动。
1. 在凭据输入框中输入令牌。
1. 让工具读取您自己的 nmBot 设置，检查实际调用的服务器和返回结果。

客户端能列出工具并成功返回请求结果，才表示连接可用。仅保存配置或看到服务器名称，还不能确认令牌有效。

<span id="openclaw-nmbot-mcp"></span><span id="openclaw"></span><span id="openclaw-配置位置"></span><span id="openclaw_1"></span><span id="openclaw-排错建议"></span>

## 在“OpenClaw”中接入“nmBot MCP” {#在-openclaw-中使用-nmbot-mcp}

[OpenClaw 的 MCP 设置](https://docs.openclaw.ai/tools/mcp)支持直接添加远程服务器。您可以在控制界面的“Settings”→“MCP”中点按“Add server”，选择“Streamable HTTP”，填入 nmBot 服务地址。

您还需要在该服务器的配置中设置 `Authorization` 请求头，值为 `Bearer <您的 MCP Access Token>`。凭据的保存方式取决于 OpenClaw 的配置环境，可以按其官方说明设置。保存后，运行 `openclaw mcp doctor nmbot --probe` 检查名为 `nmbot` 的服务器是否可连接。

<span id="nmbot-preview-mcp"></span>

## 接入“nmBot Preview MCP” {#使用-nmbot-preview-mcp}

如果您使用[“nmBot Preview”](beta.md)，服务地址为 `https://nmbot-preview-api.nmnm.fun/mcp`。您需要在对应版本的面板中创建令牌，并在客户端中使用不同的服务器名称，方便区分两个服务。

<span id="_3"></span>

## 了解“nmBot MCP”的请求限制 {#速率限制}

您需要控制客户端的请求频率，以下是已经公布的限制：

- 普通账号：每分钟 5 次，每小时 50 次。
- 个人账号订阅“nmBot+”后：每分钟 20 次，每小时 500 次。

请求过于频繁时，客户端会暂时无法继续请求，您可以稍后重试。

<span id="token"></span><span id="_4"></span>

## 删除“MCP Access Token” {#token-管理建议}

在“MCP 配置”的“已创建 Token”中，找到对应名称，点按“删除 Token”并确认。看到“Token 已删除”后，使用这个令牌的客户端将无法继续连接。删除不可撤销。

<span id="_5"></span><span id="常见问题"></span><span id="token_1"></span><span id="为什么我不能创建多个-token"></span>

达到令牌数量上限时，“创建 Token”会显示“已达上限”。您可以删除不再需要的令牌，或查看个人订阅的可用数量。

<span id="vs-code-nmbot-mcp"></span><span id="为什么我在-vs-code-中看不到-nmbot-服务器"></span>

如果客户端连接失败，您可以检查服务地址、`Bearer ` 前缀和令牌是否完整。已经删除的令牌需要换成新令牌。如果客户端没有使用配置中的服务器，可以查看它实际读取的配置位置和工具启用状态。

<span id="_6"></span><span id="mcp-access-token"></span><span id="mcp_1"></span><span id="mcp_2"></span><span id="更多资源"></span><span id="相关说明"></span>

您也可以从面板的“更多 Agents 资源”打开“nmBot Agent Skills”，获取配套的官方技能包。
