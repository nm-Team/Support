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
- 监听 `docs/` 目录变化并自动重新生成，浏览器热更新

### 构建生产版本

```bash
uv run nmteam build
```

构建结果输出到 `site/` 目录。

### 其他命令

```bash
uv run nmteam generate # 仅重新生成文档结构
uv run nmteam clean    # 清理 cache/、generated/ 和 site/
uv run nmteam --help   # 显示完整命令帮助
```

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
