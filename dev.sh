#!/bin/bash
# nmTeam Documentation Development Script
# Unix/Linux shell script

echo "nmTeam Documentation Manager"
echo

if [ $# -eq 0 ]; then
    echo "用法: ./dev.sh [command]"
    echo
    echo "可用命令:"
    echo "  dev      启动开发模式"
    echo "  build    构建静态站点"
    echo "  clean    清理生成文件"
    echo "  install  安装依赖"
    echo
    exit 0
fi

python manage.py "$@"
