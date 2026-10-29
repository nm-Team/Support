# Support

[**nmTeam 支持**](https://support.nmteam.xyz)官方网站。使用 `mkdocs-material` 构建；项目由 `uv` 管理依赖，通过 Typer 提供统一的跨平台命令行入口。

## 环境要求

- Python 3.14+（由 `uv` 按 `.python-version` 自动管理）
- [uv](https://docs.astral.sh/uv/)（`curl -LsSf https://astral.sh/uv/install.sh | sh`）

## 快速开始

### 安装依赖

```bash
uv sync
```

### 开发模式

```bash
uv run nmteam dev
```

开发模式会：

- 让 MkDocs 直接读取 `docs/`，不创建中间目录
- 启动 MkDocs 开发服务器（<http://127.0.0.1:8000>）
- 使用 MkDocs 原生 dirty reload 监听 `docs/`、`assets/` 和重定向配置
- 仅重新读取变更的 Markdown，并仅处理变更的图片资源

### 构建生产版本

```bash
uv run nmteam build
```

构建结果输出到 `site/` 目录。

MkDocs 插件会在一次构建中完成动态导航、目录页、贡献提示、`llms.txt`、
重定向脚本、HTML 压缩和图片优化。图片与压缩后的 HTML 存放在 `.cache/`
（可随时删除，仅会多付一次冷构建），不会创建 `cache/` 或 `generated/`
副本。

最终 HTML 由插件自行压缩并缓存；生成器元标签仅保留 MkDocs
版本，不暴露主题及其版本。

### 文章更新时间

文章底部显示该 Markdown 源文件最近一次 Git 提交的日期和时间，统一为
北京时间（UTC+8）。修改其他文章或重新构建不会改变这篇文章的时间。
格式调整和文件重命名也属于 Git 修改记录。

构建环境需要安装 Git。检测到浅克隆时，构建工具会自动从 `origin`（或唯一的
远程仓库）补齐当前提交的历史，再读取文章时间。补齐只获取 Git 历史，不切换
提交，也不修改文档内容，因此支持按提交 SHA 检出的预览部署和旧版本部署。
已有完整历史时不会发起网络请求。GitHub Actions 保持 `fetch-depth: 0`。

浅克隆环境需要能访问原来的 Git 远程仓库。自动获取历史最多等待 120 秒，失败会
输出 Git 错误原因并终止构建；也可以预先运行 `git fetch --unshallow <remote>`。

没有 Git 历史的源码副本、尚未提交的新文章，以及没有 Markdown 源文件的自动
目录页不会显示更新时间。已有文章的本地未提交修改仍显示上次提交的时间。
文件修改时间和编译时间都不会用作替代值。

## 静态资源

仓库内资源统一存放在：

- `assets/images/`：PNG、JPEG 图片母版
- `assets/icons/`：SVG 图标
- `assets/styles/`：站点样式

文档使用 `/assets/...` 引用这些资源。生成文档时，每张 PNG 或 JPEG
图片会同时产生：

- WebP 优先版本：质量 80，编码 effort 5
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

### 预览生产构建

```bash
uv run nmteam preview
```

`nmteam preview` 默认监听 `127.0.0.1:8124`，可用 `--port` / `--host`
调整。与裸 `python -m http.server` 不同，它把 `.md` 文件的
`Content-Type` 显式设为 `text/plain; charset=utf-8`（Python 3.13+ 的
`mimetypes` 会把 `.md` 判为 `text/markdown`，部分客户端会下载而非内联
显示），保证每页 Markdown 版本在任何浏览器中都能直接阅读。

默认仅输出生命周期摘要和错误。需要 MkDocs 详细日志时，在子命令前添加
全局选项 `--verbose`，例如 `uv run nmteam --verbose build`。

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

### 内部链接检查

内部链接检查作为独立步骤在 GitHub Actions 的三平台 CI 中执行，也可以在
Actions 页面手动运行 CI 并选择分支。它不计入 `nmteam check`，不作为提交前的
强制要求。需要手动检查时运行：

```bash
uv run nmteam check-links
```

命令先严格构建，再离线检查 `site/` 中 HTML 的 `href`、`src` 等引用，覆盖
相对路径、根路径、与 `site_url` 同域名的完整 URL、静态资源及 HTML 章节锚点。
中文和百分号编码的路径、中文章节锚点及旧锚点别名都按实际构建结果检查。
目录链接必须有 `index.html`，路径大小写在所有平台上严格匹配。
外部网站和 `mailto:`、`tg:` 等协议不发起网络请求。

发现失效链接时，命令输出生成页面路径、行号、原始 URL 和失败原因，并返回非零
退出码。已有 `404.html` 或客户端重定向规则不会让缺失页面通过检查。
检查针对本次构建，不验证生产服务器的部署、网络或重定向配置。

CI 会复用 `nmteam check` 刚生成的产物，避免重复构建：

```bash
uv run nmteam check-links --no-build
```

本地使用 `--no-build` 前，需要确保 `site/` 已经按最新内容构建。

## 性能基准

构建性能的测量在 `benchmarks/`，使用 `pytest-benchmark`。它们不计入
`pytest` 与 `nmteam check`（后者只看 `tests/`），需要显式运行：

```bash
uv run pytest benchmarks/
uv run pytest benchmarks/ --benchmark-sort=name
uv run pytest benchmarks/test_bench_image_pipeline.py -k method
```

与保存的基线对比，用于判断一次改动是否真的更快：

```bash
uv run pytest benchmarks/ --benchmark-json=/tmp/base.json
# 改动之后
uv run pytest benchmarks/ --benchmark-compare=/tmp/base.json --benchmark-compare-fail=min:5%
```

`test_bench_build.py` 在独立进程中运行真实的 `nmteam build`，因此也把
解释器启动计入结果；其余文件在进程内测量编码参数、缓存命中路径与
压缩开销。所有基准都针对仓库自身的真实资源，而不是合成输入。

## 重定向管理

```bash
uv run nmteam redirects list
uv run nmteam redirects add "/old-path/" "/new-path/"
uv run nmteam redirects remove "/old-path/"
```

管理命令不会用空配置覆盖损坏的 `redirects.json`；修复配置后再重试即可。

## 贡献

欢迎您在 GitHub 上提出问题并贡献文档。
