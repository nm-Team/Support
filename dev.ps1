# nmTeam Documentation Management PowerShell Script
# Enable UTF-8 encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

param(
    [Parameter(Position=0)]
    [string]$Command = "",
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$RemainingArgs
)

Write-Host "nmTeam Documentation Manager" -ForegroundColor Cyan
Write-Host ""

if ($Command -eq "" -or $Command -eq "help") {
    Write-Host "用法: .\dev.ps1 <command>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "可用命令:" -ForegroundColor Green
    Write-Host "  dev      启动开发模式 (文件监听 + 热更新)" -ForegroundColor White
    Write-Host "  build    构建静态站点 (生成文档 + 构建)" -ForegroundColor White
    Write-Host "  clean    清理生成的文件" -ForegroundColor White
    Write-Host "  install  安装依赖包" -ForegroundColor White
    Write-Host "  help     显示帮助信息" -ForegroundColor White
    Write-Host ""
    Write-Host "示例:" -ForegroundColor Yellow
    Write-Host "  .\dev.ps1 dev      # 启动开发服务器" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 build    # 构建生产版本" -ForegroundColor Gray
    Write-Host "  .\dev.ps1 clean    # 清理临时文件" -ForegroundColor Gray
    exit 0
}

# 执行 Python 脚本
$arguments = @($Command) + $RemainingArgs
& python manage.py $arguments
