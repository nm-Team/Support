# Support
[**nmTeam 支持**](https://support.nmteam.xyz)官方网站。使用 `mkdocs-material` 进行构建。

# 快速开始

## 安装依赖
```bash
# 方式1: 使用管理脚本自动安装
python manage.py install

# 方式2: 手动安装
pip install -r requirements.txt
```

## 开发模式 (推荐)
```bash
# 启动开发服务器 (支持热更新)
python manage.py dev

# 或使用便捷脚本 (Windows)
.\dev.ps1 dev
dev.bat dev

# 或使用便捷脚本 (Linux/macOS)
./dev.sh dev
```

开发模式会：
- 自动生成文档结构
- 启动 MkDocs 开发服务器 (http://127.0.0.1:8000)
- 监听 `docs/` 目录文件变化并自动重新生成
- 支持热更新，修改后自动刷新页面

## 构建生产版本
```bash
# 构建静态站点
python manage.py build

# 或使用便捷脚本
.\dev.ps1 build
```

构建过程会：
1. 运行 `generate.py` 生成文档结构
2. 执行 `mkdocs build` 生成静态站点到 `site/` 目录

## 其他命令
```bash
# 清理生成的文件
python manage.py clean

# 查看帮助
python manage.py help
```

# 传统部署方式

如果你更喜欢传统的分步操作：

- 安装依赖 `pip install -r requirements.txt`
- 启动本地服务器 `python -m mkdocs serve`
- 构建生成目录 `python generate.py`
- 构建静态界面 `python -m mkdocs build`

# 贡献

欢迎您在 GitHub 上提出问题并贡献文档。
