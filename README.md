# Support
[**nmTeam 支持**](https://support.nmteam.xyz)官方网站。使用 `mkdocs-material` 构建，工具链由 `uv` 管理。

## 环境要求
- Python 3.14+（由 `uv` 按 `.python-version` 自动管理）
- [uv](https://docs.astral.sh/uv/)（`curl -LsSf https://astral.sh/uv/install.sh | sh`）

## 快速开始

### 安装依赖
```bash
uv sync
```

### 开发模式（推荐）
```bash
uv run python manage.py dev
```
开发模式会：
- 自动生成文档结构（`cache/`、`generated/`、`mkdocs.yml`）
- 启动 MkDocs 开发服务器（http://127.0.0.1:8000）
- 监听 `docs/` 目录变化并自动重新生成，浏览器热更新

### 构建生产版本
```bash
uv run python manage.py build
```
构建结果输出到 `site/` 目录。

### 其他命令
```bash
uv run python manage.py clean     # 清理 cache/ generated/ site/
uv run python manage.py install   # 等价于 uv sync
uv run python -m nmteam_support   # 仅重新生成文档结构
```

## 质量检查
```bash
uv run ruff check .              # lint
uv run ruff format --check .     # Python 格式检查
uv run pytest                    # 单元测试
uv run mdformat --check docs/    # Markdown 格式检查
uv run mkdocs build --strict     # 严格模式构建
```
以上步骤由 CI（`.github/workflows/ci.yml`）自动执行。

## 重定向管理
```bash
uv run python redirects_manager.py list
uv run python redirects_manager.py add "/old-path/" "/new-path/"
uv run python redirects_manager.py remove "/old-path/"
```

## 贡献
欢迎您在 GitHub 上提出问题并贡献文档。
