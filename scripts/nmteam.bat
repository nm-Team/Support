@echo off
setlocal
cd /d "%~dp0.."
uv run nmteam %*
exit /b %errorlevel%
