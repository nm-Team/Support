#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
nmTeam Documentation Management Tool
管理脚本，提供开发和构建指令
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from generate import generate


class DocumentationHandler(FileSystemEventHandler):
    """文档变更监听器"""
    
    def __init__(self):
        self.last_modified = {}
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # 只监听 .md 文件和配置文件
        if not (event.src_path.endswith('.md') or 
                event.src_path.endswith('.yml') or
                event.src_path.endswith('.yaml')):
            return
            
        # 防止频繁触发
        now = time.time()
        if event.src_path in self.last_modified:
            if now - self.last_modified[event.src_path] < 1:
                return
        self.last_modified[event.src_path] = now
        
        print(f"检测到文件变更: {event.src_path}")
        self.rebuild_docs()
    
    def rebuild_docs(self):
        """重新构建文档"""
        try:
            print("🔄 重新生成文档...")
            generate()
            print("✅ 文档重新生成完成")
        except Exception as e:
            print(f"❌ 文档生成失败: {e}")


def run_mkdocs_serve():
    """运行 MkDocs 开发服务器"""
    try:
        # 首先生成文档
        print("🚀 启动开发服务器...")
        generate()
        
        # 启动 MkDocs 服务器
        process = subprocess.Popen(
            [sys.executable, "-m", "mkdocs", "serve", "--dev-addr", "127.0.0.1:8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 实时输出日志
        for line in iter(process.stdout.readline, ''):
            print(line.rstrip())
            
    except KeyboardInterrupt:
        print("\n🛑 开发服务器已停止")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"❌ 启动开发服务器失败: {e}")


def dev_command():
    """开发模式：启动文件监听和开发服务器"""
    print("🔥 启动开发模式...")
    print("📁 监听 docs/ 目录变化...")
    
    # 设置文件监听
    event_handler = DocumentationHandler()
    observer = Observer()
    observer.schedule(event_handler, "docs", recursive=True)
    observer.schedule(event_handler, "mkdocs-template.yml", recursive=False)
    
    # 启动监听
    observer.start()
    
    try:
        # 在单独线程中运行 MkDocs 服务器
        server_thread = threading.Thread(target=run_mkdocs_serve)
        server_thread.daemon = True
        server_thread.start()
        
        print("✅ 开发环境已启动")
        print("🌐 访问 http://127.0.0.1:8000 查看文档")
        print("📝 修改 docs/ 目录下的文件将自动重新生成")
        print("💡 按 Ctrl+C 停止服务")
        
        # 保持主线程运行
        server_thread.join()
        
    except KeyboardInterrupt:
        print("\n🛑 停止开发模式...")
    finally:
        observer.stop()
        observer.join()


def build_command():
    """构建模式：生成文档并构建静态站点"""
    print("🏗️  开始构建...")
    
    try:
        # 步骤1: 生成文档
        print("📝 第1步: 生成文档结构...")
        generate()
        print("✅ 文档生成完成")
        
        # 步骤2: 构建静态站点
        print("🔨 第2步: 构建静态站点...")
        result = subprocess.run(
            [sys.executable, "-m", "mkdocs", "build", "--clean"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 静态站点构建完成")
            print("📁 输出目录: site/")
        else:
            print(f"❌ 构建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False
    
    return True


def clean_command():
    """清理生成的文件"""
    print("🧹 清理中...")
    
    dirs_to_clean = ['cache', 'generated', 'site']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            import shutil
            shutil.rmtree(dir_name)
            print(f"🗑️  已删除: {dir_name}/")
    
    print("✅ 清理完成")


def install_command():
    """安装依赖"""
    print("📦 安装依赖...")
    
    try:
        # 更新 requirements.txt 以包含 watchdog
        requirements_path = "requirements.txt"
        with open(requirements_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'watchdog' not in content:
            with open(requirements_path, 'a', encoding='utf-8') as f:
                f.write('watchdog\n')
            print("📝 已更新 requirements.txt")
        
        # 安装依赖
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ 依赖安装完成")
        else:
            print(f"❌ 依赖安装失败: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")


def show_help():
    """显示帮助信息"""
    help_text = """
nmTeam Documentation Management Tool

用法:
    python manage.py <command>

可用命令:
    dev       启动开发模式 (文件监听 + 热更新服务器)
    build     构建静态站点 (生成文档 + 构建)
    clean     清理生成的文件
    install   安装依赖包
    help      显示此帮助信息

示例:
    python manage.py dev      # 启动开发服务器
    python manage.py build    # 构建生产版本
    python manage.py clean    # 清理临时文件
"""
    print(help_text)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        'dev': dev_command,
        'build': build_command,
        'clean': clean_command,
        'install': install_command,
        'help': show_help,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ 未知命令: {command}")
        show_help()


if __name__ == "__main__":
    main()
