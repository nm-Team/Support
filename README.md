# Support

[**nmTeam 支持**](https://support.nmteam.xyz)官方网站。使用 `mkdocs-material` 构建；项目由 `uv` 初始化并管理依赖，通过 Typer 提供统一的跨平台命令行入口。

## 环境要求

- Python 3.14+（由 `uv` 按 `.python-version` 自动管理）
- [uv](https://docs.astral.sh/uv/)（`curl -LsSf https://astral.sh/uv/install.sh | sh`）

## 快速开始

### 安装依赖

```bash
uv sync
```

也可以使用统一 CLI：

```bash
uv run nmteam install
```

### 开发模式

```bash
uv run nmteam dev
```

开发模式会：

- 自动生成文档结构（`cache/`、`generated/`、`mkdocs.yml`）
- 启动 MkDocs 开发服务器（<http://127.0.0.1:8000>）
- 监听 `docs/`、`assets/` 和 MkDocs 模板变化并自动重新生成，浏览器热更新

### 构建生产版本

```bash
uv run nmteam build
```

构建结果输出到 `site/` 目录。

最终 HTML 会由 `mkdocs-minify-plugin` 压缩；生成器元标签仅保留 MkDocs
版本，不暴露主题及其版本。

## 静态资源

仓库内资源统一存放在：

- `assets/images/`：PNG、JPEG 图片母版
- `assets/icons/`：SVG 图标
- `assets/styles/`：站点样式

文档使用 `/assets/...` 引用这些资源。生成文档时，每张 PNG 或 JPEG
图片会同时产生：

- WebP 优先版本：质量 80
- 原格式 fallback：JPEG 使用质量 80；PNG 使用 256 色有损量化

Markdown 中仍使用普通图片语法，构建工具会自动输出 WebP
优先的 `<picture>` 元素。外部 URL 不会被下载或镜像。

## AI 支持

站点面向语言模型提供以下能力：

- `/llms.txt`：按 [llmstxt.org](https://llmstxt.org/) 规范生成的站点索引，
    每个链接指向页面的 Markdown 版本。
- 每页 Markdown 版本：`nmteam build` 时在每个页面旁生成同路径的 `.md` 文件
    （如 `/nmbot-telegram/mcp.md`）。
- 页面顶部的文章操作区（首页不显示）：**复制 Markdown** 直接复制当前页面
    原文；**使用［品牌图标］打开** 菜单提供 GitHub 源文件、Markdown 版本，
    以及 Perplexity、Grok、ChatGPT、Claude Web、Claude Desktop、
    Claude Code、OpenAI Codex、Cursor 八种 AI 打开方式。

注意：`llms.txt` 与 `.md` 版本由 `nmteam build` 输出到 `site/`；开发模式
（`nmteam dev`）下复制和 View as Markdown 会提示先构建，AI 操作仍可通过
当前页面 URL 打开。

### 其他命令

```bash
uv run nmteam generate # 仅重新生成文档结构
uv run nmteam clean    # 清理 cache/、generated/ 和 site/
uv run nmteam serve    # 预览 site/（.md 以 text/plain; charset=utf-8 提供）
uv run nmteam --help   # 显示完整命令帮助
```

`nmteam serve` 默认监听 `127.0.0.1:8124`，可用 `--port` / `--bind`
调整。与裸 `python -m http.server` 不同，它把 `.md` 文件的
`Content-Type` 显式设为 `text/plain; charset=utf-8`（Python 3.13+ 的
`mimetypes` 会把 `.md` 判为 `text/markdown`，部分客户端会下载而非内联
显示），保证每页 Markdown 版本在任何浏览器中都能直接阅读。

## 平台启动器

直接运行 `uv run nmteam` 是推荐方式。`scripts/` 也提供不包含业务逻辑的薄启动器；它们会自动定位仓库根目录并原样传递参数。

=== "Linux / macOS"

    ```bash
    scripts/nmteam.sh dev
    ```

=== "PowerShell"

    ```powershell
    .\scripts\nmteam.ps1 dev
    ```

=== "Windows Batch"

    ```batch
    scripts\nmteam.bat dev
    ```

## 质量检查

一条命令运行 Ruff lint、Ruff format check、pytest、mdformat 和 MkDocs strict build：

```bash
uv run nmteam check
```

也可以单独运行：

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run mdformat --check README.md docs/
uv run nmteam build
```

以上检查由 CI（`.github/workflows/ci.yml`）自动执行。

## 重定向管理

```bash
uv run nmteam redirects list
uv run nmteam redirects add "/old-path/" "/new-path/"
uv run nmteam redirects remove "/old-path/"
```

管理命令不会用空配置覆盖损坏的 `redirects.json`；修复配置后再重试即可。

## 贡献

欢迎您在 GitHub 上提出问题并贡献文档。
