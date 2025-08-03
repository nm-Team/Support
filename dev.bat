@echo off
REM nmTeam Documentation Development Script
REM Windows 批处理脚本

echo nmTeam Documentation Manager
echo.

if "%1"=="" (
    echo 用法: dev.bat [command]
    echo.
    echo 可用命令:
    echo   dev      启动开发模式
    echo   build    构建静态站点
    echo   clean    清理生成文件
    echo   install  安装依赖
    echo.
    goto :eof
)

python manage.py %*
