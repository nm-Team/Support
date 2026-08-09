# Repository Guidelines

## Project Overview

nmTeam Support 官方支持文档站（https://support.nmteam.xyz）的构建工具链。纯文档 + Python 工具链仓库：内容为简体中文，覆盖 nmBot（Telegram 机器人）及其 Plus / Intelligence 产品线；工具链负责扫描 `docs/` 与 `assets/`，自动生成 mkdocs 目录结构（nav）、各目录 `index.md`、图片 WebP 优化与重定向脚本，再用 `mkdocs-material` 构建静态站。

本项目是 main 分支旧版（单文件 `generate.py`/`manage.py`/`redirects_manager.py` + `runtime.txt` 3.7 + pip）的现代化重构：**uv 管理、Python 3.14+、`src/` 包结构、Typer CLI、pytest 测试、ruff/mdformat 检查、三平台 CI**。

## Architecture & Data Flow

数据流（四输入 → 生成 → 构建）：

```
docs/ (markdown 源) ─┐
assets/ (images/icons/styles 母版) ─┤
mkdocs-template.yml ─┤ generate() → cache/ ─copytree→ generated/ (mkdocs docs_dir) → mkdocs build --strict → site/
redirects.json ──────┘        (含生成的 assets/js/redirects.js)
```

构建后还有一步：`stage_markdown_copies()` 把 `cache/` 下每个 `.md` 复制到 `site/`
同路径（如 `site/nmbot-telegram/mcp.md`），作为每页的 Markdown 版本，供
`/llms.txt` 链接、View-as-Markdown 按钮与 ChatGPT/Claude 打开。

`generate()`（`src/nmteam_support/generator.py`）编排的完整链路：

1. 清空重建 `cache/`
1. `scanner.scan_docs()` 递归扫描 `docs/` 得到文档树（`SKIP_DIRS`/`INTERNAL_DIRS` 过滤）
1. 写入处理后的页面（非 index.md 注入贡献提示，`contributing.py`）
1. `index.py` 为每目录生成 `index.md`（自动 generated 标记 + docsList 卡片，`docslist.py` 渲染 HTML）
1. `image_pipeline.py` 用 PIL 为 assets 中每张 PNG/JPEG 生成 `.webp` 兄弟文件（质量 80；PNG 另出 256 色有损 fallback）
1. `nav.py` 生成 nav YAML，`template.py` 替换 `mkdocs-template.yml` 的 `# NAV_ARIA_START`/`# NAV_ARIA_END` 标记块写入 `mkdocs.yml`
1. `redirects.py` 读 `redirects.json` 生成 `cache/assets/js/redirects.js`
1. `llms.py` 用扫描树 + 模板 `site_url` 生成 `cache/llms.txt`（llmstxt.org 规范：H1 + blockquote + H2 分节链接，链接指向 `.md` 版本；非 md 文件会被 mkdocs 原样拷到 `site/llms.txt`）
1. copytree 到 `generated/`，交给 `mkdocs build --strict`

**图片双层管线**（关键机制）：生成期 `image_pipeline.py` 产出同名 `.webp` 兄弟文件；渲染期 `markdown_images.py`（mkdocs 扩展，注册在 mkdocs-template.yml 的 markdown_extensions 中）把本地栅格图 `<img>` 改写为 WebP-first `<picture>`，靠同名 `.webp` 约定对接。外部 URL 不下载不镜像。Markdown 中仍写普通图片语法。

`mkdocs.yml`、`cache/`、`generated/`、`site/` 均为生成产物（gitignore），**永远不要手改**；配置改 `mkdocs-template.yml`，nav 由脚本生成。

## Key Directories

| 路径                                          | 用途                                                                                                                                                                                                                                                  |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/nmteam_support/`                         | 工具链包（16 个模块，见 Important Files）                                                                                                                                                                                                             |
| `docs/`                                       | **真实文档源**（唯一需要手工编辑的内容位置）                                                                                                                                                                                                          |
| `docs/nmbot-telegram/`                        | 产品中枢：`panel/`、`plus/`、`legal/`、`group/`、`faq/`、`business/`、`tools/`、`nmbot-intelligence/`、`credit/`、`update-log/`（`YYYY-MM.md` 月度日志）、`mcp/`                                                                                      |
| `docs/contact-us/`、`docs/nmteam-account/`    | 其他产品线                                                                                                                                                                                                                                            |
| `docs/superpowers/`                           | 本地设计与实现工件（plans/specs），**已 gitignore，勿提交**                                                                                                                                                                                           |
| `assets/images/`                              | 图片母版：`shared/`（站级共享）、`nmbot/`（含 `mcp/`、`update-pictures/` 子目录）；`assets/icons/`（SVG）、`assets/styles/`（CSS）、`assets/js/`（AI 工具脚本 `ai-tools.js`，随构建 stage 到生成站）                                                  |
| `overrides/`                                  | mkdocs `custom_dir`：`main.html` 覆写 site_meta 移除主题版本号；`partials/actions.html` 追加 Fumadocs 风格 Open 菜单（GitHub / Markdown / Scira AI / ChatGPT / Claude / Cursor，样式在 `assets/styles/ai-tools.css`，交互在 `assets/js/ai-tools.js`） |
| `scripts/`                                    | 三平台薄启动器（`nmteam.sh` / `nmteam.ps1` / `nmteam.bat`）                                                                                                                                                                                           |
| `tests/`                                      | pytest 测试（17 个文件 + conftest.py）                                                                                                                                                                                                                |
| `cache/`、`generated/`、`site/`、`mkdocs.yml` | 生成产物，勿手改勿提交                                                                                                                                                                                                                                |

## Development Commands

```bash
uv sync                            # 安装依赖（按 .python-version 3.14 自动管理 Python）
uv run nmteam install              # 同上，CLI 封装
uv run nmteam dev                  # 生成文档结构 + mkdocs serve http://127.0.0.1:8000，
                                   # 监听 docs/、assets/、mkdocs-template.yml 变化自动重生成 + 热更新
uv run nmteam build                # generate() + mkdocs build --strict → site/，
                                   # 再 stage 每页 .md 副本到 site/
uv run nmteam generate             # 仅重新生成文档结构
uv run nmteam clean                # 清理 cache/ generated/ site/
uv run nmteam check                # 全部质量检查（见下）
uv run nmteam redirects list|add "/old/" "/new/"|remove "/old/"
uv run nmteam --help
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
- 核心模型用 `frozen dataclass`（`models.py`：`PageMetadata`/`DocEntry`）；类型标注齐全（`typing`）。
- ruff 约束：`line-length = 100`（`E501` ignore）、`target py314`、`select = E,F,I,UP,B,SIM,W,C4,RUF`、`isort known-first-party = nmteam_support`、双引号、空格缩进。
- 错误处理显式：如 `redirects.py` 对损坏的 `redirects.json` 抛 `RedirectConfigError`（绝不静默清空覆盖，管理命令不写坏文件）。
- 依赖注入轻量：`GeneratorOptions`/`default_options` 传参，函数式模块（scanner/frontmatter/nav/docslist 等），无重 OOP。

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
| `src/nmteam_support/cli.py`                                   | Typer 入口 `main`；install/dev/generate/build/clean/check + redirects 子命令                                                                           |
| `src/nmteam_support/generator.py`                             | `generate()` 端到端编排 + `GeneratorOptions`/`default_options`                                                                                         |
| `src/nmteam_support/scanner.py`                               | 递归扫描 docs/ 树，SKIP_DIRS/INTERNAL_DIRS 过滤                                                                                                        |
| `src/nmteam_support/frontmatter.py`                           | frontmatter 解析（title/description/index/flag）                                                                                                       |
| `src/nmteam_support/index.py` + `docslist.py`                 | 每目录 index.md 生成 + docsList 卡片 HTML                                                                                                              |
| `src/nmteam_support/nav.py` + `template.py`                   | nav YAML 生成；NAV_ARIA 标记块替换写 mkdocs.yml                                                                                                        |
| `src/nmteam_support/contributing.py`                          | 非 index.md 注入贡献提示 admonition                                                                                                                    |
| `src/nmteam_support/redirects.py`                             | redirects.json 管理（损坏保护）+ redirects.js 生成                                                                                                     |
| `src/nmteam_support/image_pipeline.py` + `markdown_images.py` | PIL 生成 .webp 兄弟文件；mkdocs 扩展包 WebP-first `<picture>`                                                                                          |
| `src/nmteam_support/llms.py`                                  | `render_llms_txt()` 从扫描树生成 `/llms.txt`（llmstxt.org 规范；链接指向各页 `.md` 版本）                                                              |
| `src/nmteam_support/models.py`                                | `PageMetadata`/`DocEntry` frozen dataclass                                                                                                             |
| `pyproject.toml`                                              | 包元数据、依赖、入口、pytest/ruff/hatchling 配置                                                                                                       |
| `uv.lock`                                                     | 锁定依赖（mkdocs 1.6.1、mkdocs-material 9.7.7、mkdocs-minify-plugin 0.8.0、pillow 12.3.0、typer 0.27.1、pytest 9.1.1、ruff 0.16.2、mdformat 1.0.0 等） |
| `mkdocs-template.yml`                                         | mkdocs 配置模板（material zh 黄色双 palette、minify 插件、custom_dir overrides、`nmteam_support.markdown_images` 扩展、NAV_ARIA 标记）                 |
| `redirects.json`                                              | 顶层 `redirects` 对象：`{旧路径带斜杠: 新路径}`                                                                                                        |
| `.github/workflows/ci.yml`                                    | 三 OS 矩阵 CI（push main/dev + PR）：uv sync --frozen → nmteam check → 验证三个启动器                                                                  |
| `.mdformat.toml`                                              | mdformat 配置（wrap=keep、LF）                                                                                                                         |
| `overrides/main.html`                                         | 移除 meta 中 mkdocs-material 版本号                                                                                                                    |
| `overrides/partials/actions.html`                             | 覆盖 material actions partial：保留编辑/查看按钮，追加六项 Open 操作菜单                                                                               |
| `assets/js/ai-tools.js`                                       | 菜单交互：开关状态、外部点击/Escape 关闭、View-as-Markdown 开发模式提示，以及 Scira AI / ChatGPT / Claude / Cursor 页面 URL 深链                       |
| `assets/styles/ai-tools.css`                                  | Open 触发器与半透明弹层样式，适配明暗主题和窄屏                                                                                                        |

## Runtime/Tooling Preferences

- **uv** 为唯一包管理器（`uv sync`，lockfile `uv.lock`）；Python 由 uv 按 `.python-version`（3.14）自动管理，不手动装。
- 构建后端 **hatchling**；无 Node/npm 组件。
- 强制检查：**ruff**（lint + format）+ **mdformat** + **pytest** + **mkdocs strict build**，全部由 `uv run nmteam check` 一键执行，CI 三平台门禁。
- gitattributes：`*.md` 强制 LF。
- 许可证 MIT（Copyright 2022 nmTeam）。

## Testing & QA

- **pytest**（dev 组 `pytest>=9.0`），配置在 pyproject.toml：`testpaths = ["tests"]`、`pythonpath = ["src"]`、`addopts = "-ra"`。
- 测试约定：`tests/` 单层目录，每个模块一个 `test_<module>.py`（test_cli、test_generator、test_scanner、test_frontmatter、test_nav、test_index、test_docslist、test_contributing、test_redirects、test_image_pipeline、test_markdown_images、test_models、test_scripts、test_build_config 等）。
- `test_llms.py` 覆盖 llms.txt 生成（标题/摘要/分节/.md 链接/base_url/空树）；`test_generator.py` 覆盖 llms.txt 落盘与 `stage_markdown_copies` 镜像 cache。
- 输入构造分级：conftest 的 `docs_dir` fixture（tmp_path 构造最小 docs 树，含 index/hide_docs_list/hide frontmatter）→ `tmp_path` 手写单文件 → 全流程 generate 集成。**不依赖真实 docs/ 内容**。
- CLI 测试用 `typer.testing.CliRunner` + monkeypatch；启动器测试用 subprocess + 假 uv 脚本。
- **无覆盖率门槛**（无 pytest-cov、CI 无 coverage 步骤）——新增功能时给模块补 `test_<module>.py` 行为测试即可。
- CI 在 ubuntu/macos/windows 三平台跑全量 check；提交前本地至少跑 `uv run nmteam check`。
