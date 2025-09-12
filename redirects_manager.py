#!/usr/bin/env python3
"""
简单的重定向管理工具
用法:
  python redirects_manager.py add "/old-path/" "/new-path/"
  python redirects_manager.py remove "/old-path/"
  python redirects_manager.py list
"""

import json
import sys
import os

REDIRECTS_FILE = 'redirects.json'

def load_redirects():
    """加载重定向配置"""
    if not os.path.exists(REDIRECTS_FILE):
        return {"redirects": {}}
    
    try:
        with open(REDIRECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"redirects": {}}

def save_redirects(config):
    """保存重定向配置"""
    with open(REDIRECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def add_redirect(old_path, new_path):
    """添加重定向"""
    config = load_redirects()
    config['redirects'][old_path] = new_path
    save_redirects(config)
    print(f"已添加重定向: {old_path} -> {new_path}")

def remove_redirect(old_path):
    """删除重定向"""
    config = load_redirects()
    if old_path in config['redirects']:
        del config['redirects'][old_path]
        save_redirects(config)
        print(f"已删除重定向: {old_path}")
    else:
        print(f"未找到重定向: {old_path}")

def list_redirects():
    """列出所有重定向"""
    config = load_redirects()
    if not config['redirects']:
        print("当前没有配置任何重定向")
        return
    
    print("当前重定向规则:")
    for old_path, new_path in config['redirects'].items():
        print(f"  {old_path} -> {new_path}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1]
    
    if command == 'add':
        if len(sys.argv) != 4:
            print("用法: python redirects_manager.py add \"/old-path/\" \"/new-path/\"")
            return
        add_redirect(sys.argv[2], sys.argv[3])
    
    elif command == 'remove':
        if len(sys.argv) != 3:
            print("用法: python redirects_manager.py remove \"/old-path/\"")
            return
        remove_redirect(sys.argv[2])
    
    elif command == 'list':
        list_redirects()
    
    else:
        print(f"未知命令: {command}")
        print(__doc__)

if __name__ == '__main__':
    main()
