# Repository Guidelines

## Project Overview

nmTeam Support 官方支持文档站（https://support.nmteam.xyz）的构建工具链。纯文档 + Python 工具链仓库：内容为简体中文，覆盖 nmBot（Telegram 机器人）及其 Plus / Intelligence 产品线；自研 MkDocs 插件负责扫描 `docs/` 与 `assets/`，在构建期提供 nav、目录页、贡献提示、图片 WebP 优化与重定向脚本，再用 `mkdocs-material` 构建静态站。

本项目是 main 分支旧版（单文件 `generate.py`/`manage.py`/`redirects_manager.py` + `runtime.txt` 3.7 + pip）的现代化重构：**uv 管理、Python 3.14+、`src/` 包结构、Typer CLI、pytest 测试、ruff/mdformat 检查、三平台 CI**。

## Architecture & Data Flow

数据流（输入 → 单次构建）：

```
docs/ (Markdown 源) ───────────────┐
assets/ (images/icons/styles 母版) ├→ nmteam-support MkDocs 插件 → site/
redirects.json ────────────────────┘
```

`src/nmteam_support/plugin.py` 编排完整链路：

1. `scanner.refresh_catalog()` 递归扫描 `docs/`，按 mtime + size 复用未变页面，只重新读取变更 Markdown。
1. `nav.py` 直接提供 MkDocs 原生 nav 数据结构，不再生成或解析 YAML。
1. `index.py` 与 `contributing.py` 在 `on_page_markdown` 阶段转换页面，不写源目录副本。
1. `redirects.py` 与 `llms.py` 通过 MkDocs 1.6 虚拟文件 API 提供 `redirects.js` 和 `llms.txt`。
1. 非栅格资源由 MkDocs 直接从 `assets/` 复制；`image_pipeline.py` 并行优化 PNG/JPEG 并直接写入最终 `site/assets/`。dirty build 会跳过目标较新的图片。
1. 生产 build 的 `on_post_build` 直接把处理后的 Markdown 版本写到 `site/` 同路径，供 `/llms.txt`、“复制 Markdown”和 AI 菜单使用。

开发模式只使用 MkDocs 原生 `--dirtyreload` 与插件生命周期，没有第二套 watcher。`docs_dir` 固定为 `docs`，不允许重新引入 `cache/`、`generated/` 或生成式 `mkdocs.yml`。

**图片管线**：`image_pipeline.py` 直接在最终输出中产出同名 `.webp` 兄弟文件；`markdown_images.py`（注册在 `mkdocs.yml`）把本地栅格图 `<img>` 改写为 WebP-first `<picture>`。外部 URL 不下载不镜像。Markdown 中仍写普通图片语法。

## Key Directories

| 路径                                          | 用途                                                                                                                                                                                                                                                                       |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/nmteam_support/`                         | 工具链包（见 Important Files）                                                                                                                                                                                                                                             |
| `docs/`                                       | **真实文档源**（唯一需要手工编辑的内容位置）                                                                                                                                                                                                                               |
| `docs/nmbot-telegram/`                        | 产品中枢：`panel/`、`plus/`、`legal/`、`group/`、`faq/`、`business/`、`tools/`、`nmbot-intelligence/`、`credit/`、`update-log/`（`YYYY-MM.md` 月度日志）、`mcp/`                                                                                                           |
| `docs/contact-us/`、`docs/nmteam-account/`    | 其他产品线                                                                                                                                                                                                                                                                 |
| `docs/superpowers/`                           | 本地设计与实现工件（plans/specs），**已 gitignore，勿提交**                                                                                                                                                                                                                |
| `assets/images/`                              | 图片母版：`shared/`（站级共享）、`nmbot/`（含 `mcp/`、`update-pictures/` 子目录）；`assets/icons/`（SVG）、`assets/styles/`（CSS）、`assets/js/`（AI 工具脚本 `ai-tools.js`）                                                                                           |
| `overrides/`                                  | mkdocs `custom_dir`：`main.html` 覆写 site_meta 移除主题版本号；`partials/actions.html` 追加 Fumadocs 风格文章操作区（复制 Markdown + GitHub / Markdown / Perplexity / Grok / ChatGPT / Claude Web / Claude Desktop / Claude Code / OpenAI Codex / Cursor 打开菜单）；`.icons/ai/` 存放菜单品牌图标 |
| `scripts/`                                    | 三平台薄启动器（`nmteam.sh` / `nmteam.ps1` / `nmteam.bat`）                                                                                                                                                                                                                |
| `tests/`                                      | pytest 行为与生命周期测试                                                                                                                                                                                                                                                  |
| `mkdocs.yml`                                  | 受版本控制的 MkDocs 单一配置源；nav 由插件在内存中设置                                                                                                                                                                                                                     |
| `site/`                                       | 唯一生成目录，勿手改勿提交                                                                                                                                                                                                                                                 |

## Development Commands

```bash
uv sync                            # 安装依赖（按 .python-version 3.14 自动管理 Python）
uv run nmteam dev                  # MkDocs dirty reload，默认 http://127.0.0.1:8000
uv run nmteam build                # 单次严格构建 → site/
uv run nmteam preview              # 预览 site/，Markdown 以 text/plain 提供
uv run nmteam check                # 全部质量检查（见下）
uv run nmteam redirects list|add "/old/" "/new/"|remove "/old/"
uv run nmteam --help
uv run nmteam --verbose build      # 显示详细 MkDocs 日志
```

平台启动器（定位仓库根后原样透传参数，无业务逻辑）：`scripts/nmteam.sh dev`、`.\scripts\nmteam.ps1 dev`、`scripts\nmteam.bat dev`。

**质量检查**（`nmteam check`，CI 同样执行）：

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run mdformat --check README.md docs/
uv run nmteam build   # 内部为 mkdocs build --strict，严格模式会因警告失败
```

## Code Conventions & Common Patterns

Python（`src/nmteam_support/`）：

- Python 3.14+（`pyproject.toml` `requires-python = ">=3.14"`，`.python-version` = 3.14）。
- CLI 用 **Typer**（`cli.py`，命令树 + `QUALITY_COMMANDS` 编排），不用 argparse。
- 核心模型用 dataclass（`models.py`：`PageMetadata`/`DocEntry`；`scanner.py`：`DocumentCatalog`/`SourcePage`）；类型标注齐全。
- ruff 约束：`line-length = 100`（`E501` ignore）、`target py314`、`select = E,F,I,UP,B,SIM,W,C4,RUF`、`isort known-first-party = nmteam_support`、双引号、空格缩进。
- 错误处理显式：如 `redirects.py` 对损坏的 `redirects.json` 抛 `RedirectConfigError`（绝不静默清空覆盖，管理命令不写坏文件）。
- 插件类只承载 MkDocs 生命周期状态；scanner/frontmatter/nav/docslist 等领域逻辑保持函数式，不新增 staging 兼容层。

Markdown 文档（`docs/`）：

- front matter 用 YAML：`title` + `description`（description 供列表卡片）；可选 `index: <int>` 排序；`index.md` 可用 `hide_docs_list: true` 与 `hide: [navigation]`。
- 常用 `!!! note` / `!!! warning` / `!!! success` / `!!! faq` admonition 与 `??? question` 折叠块；表格（对齐列 `:---`）；步骤用有序列表。
- 付费功能用 `<nmbot-plus-icon></nmbot-plus-icon>` 行内徽标（样式 `assets/styles/plus.css`，远程 svg）；智能功能可用 `nmbot-intelligence-icon`。
- **图片一律绝对路径引用 `/assets/images/...`**（不要用相对 `./img/`），构建时自动产出 WebP 优先 `<picture>`；logo 等品牌资源用外部 URL（websiteres.nmteam.xyz）。
- 更新日志：`docs/nmbot-telegram/update-log/YYYY-MM.md`，标题 `# nmBot YYYY 年 M 月更新`，`## 日期 时间` + `### 问题修复` / `### 新功能` 列表；配图放 `assets/images/nmbot/update-pictures/nmbot-YYMM.png`。
- Markdown 由 **mdformat** 统一格式（`.mdformat.toml`：wrap=keep、LF 行尾；插件 mdformat-mkdocs + mdformat-front-matters 保护 admonition 与 front matter，不需要手写 extensions 列表）。

## Important Files

| 文件                                                          | 职责                                                                                                                                                   |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/nmteam_support/cli.py`                                   | Typer 入口；dev/build/preview/check + redirects 子命令，直接调用 MkDocs Python API                                                                     |
| `src/nmteam_support/plugin.py`                                | MkDocs 生命周期编排：虚拟文件、页面转换、资源输出和生产 Markdown 副本                                                                                  |
| `src/nmteam_support/scanner.py`                               | 增量扫描 docs/ 树，按文件戳复用未变页面，过滤内部目录                                                                                                  |
| `src/nmteam_support/frontmatter.py`                           | frontmatter 解析（title/description/index/flag）                                                                                                       |
| `src/nmteam_support/index.py` + `docslist.py`                 | 构建期目录页 Markdown + docsList 卡片 HTML                                                                                                             |
| `src/nmteam_support/nav.py`                                  | 生成 MkDocs 原生 nav 数据结构                                                                                                                          |
| `src/nmteam_support/contributing.py`                          | 非 index.md 注入贡献提示 admonition                                                                                                                    |
| `src/nmteam_support/redirects.py`                             | redirects.json 管理（损坏保护）+ redirects.js 生成                                                                                                     |
| `src/nmteam_support/image_pipeline.py` + `markdown_images.py` | 并行、增量地直写图片变体；MkDocs 扩展输出 WebP-first `<picture>`                                                                                       |
| `src/nmteam_support/llms.py`                                  | `render_llms_txt()` 从扫描树生成 `/llms.txt`（llmstxt.org 规范；链接指向各页 `.md` 版本）                                                              |
| `src/nmteam_support/models.py`                                | `PageMetadata`/`DocEntry` frozen dataclass                                                                                                             |
| `pyproject.toml`                                              | 包元数据、依赖、入口、pytest/ruff/hatchling 配置                                                                                                       |
| `uv.lock`                                                     | 锁定依赖（mkdocs 1.6.1、mkdocs-material 9.7.7、mkdocs-minify-plugin 0.8.0、pillow 12.3.0、typer 0.27.1、pytest 9.1.1、ruff 0.16.2、mdformat 1.0.0 等） |
| `mkdocs.yml`                                                  | MkDocs 单一配置源（direct docs_dir、nmteam-support、Material、minify、Markdown 扩展）                                                                  |
| `redirects.json`                                              | 顶层 `redirects` 对象：`{旧路径带斜杠: 新路径}`                                                                                                        |
| `.github/workflows/ci.yml`                                    | 三 OS 矩阵 CI（push main/dev + PR）：uv sync --frozen → nmteam check → 验证三个启动器                                                                  |
| `.mdformat.toml`                                              | mdformat 配置（wrap=keep、LF）                                                                                                                         |
| `overrides/main.html`                                         | 移除 meta 中 mkdocs-material 版本号                                                                                                                    |
| `overrides/partials/actions.html`                             | 覆盖 material actions partial：保留编辑/查看按钮，追加复制 Markdown 按钮与十项文章打开菜单                                                             |
| `assets/js/ai-tools.js`                                       | 文章操作交互：复制当前页 Markdown、菜单开关、外部点击/Escape 关闭、开发模式提示，以及八种 AI 服务的页面 URL 深链                                        |
| `assets/styles/ai-tools.css`                                  | 文章操作按钮组与半透明弹层样式，适配明暗主题和窄屏                                                                                                      |

## Runtime/Tooling Preferences

- **uv** 为唯一包管理器（`uv sync`，lockfile `uv.lock`）；Python 由 uv 按 `.python-version`（3.14）自动管理，不手动装。
- 构建后端 **hatchling**；无 Node/npm 组件。
- 强制检查：**ruff**（lint + format）+ **mdformat** + **pytest** + **mkdocs strict build**，全部由 `uv run nmteam check` 一键执行，CI 三平台门禁。
- gitattributes：`*.md` 强制 LF。
- 许可证 MIT（Copyright 2022 nmTeam）。

## Testing & QA

- **pytest**（dev 组 `pytest>=9.0`），配置在 pyproject.toml：`testpaths = ["tests"]`、`pythonpath = ["src"]`、`addopts = "-ra"`。
- 测试约定：`tests/` 单层目录，每个模块一个 `test_<module>.py`；`test_plugin.py` 覆盖插件事件，`test_lifecycle.py` 使用真实 MkDocs 完成端到端构建。
- `test_llms.py` 覆盖 llms.txt 生成；`test_scanner.py` 验证未变 Markdown 对象被复用且 changed_paths 精确。
- 输入构造分级：conftest 的 `docs_dir` fixture（tmp_path 构造最小 docs 树）→ 插件事件测试 → 真实 MkDocs 生命周期集成。**不依赖真实 docs/ 内容**。
- CLI 测试用 `typer.testing.CliRunner` + monkeypatch；启动器测试用 subprocess + 假 uv 脚本。
- **无覆盖率门槛**（无 pytest-cov、CI 无 coverage 步骤）——新增功能时给模块补 `test_<module>.py` 行为测试即可。
- CI 在 ubuntu/macos/windows 三平台跑全量 check；提交前本地至少跑 `uv run nmteam check`。
