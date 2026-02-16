#!/usr/bin/env python
"""
命令运行工具 - 自动处理 Windows 路径问题
避免 Bash 中的 "cd: too many arguments" 错误
"""

import subprocess
import sys
from pathlib import Path
import os

# 项目根目录（自动识别）
PROJECT_ROOT = Path(__file__).parent

def run_command(cmd, description=""):
    """执行命令并返回结果"""
    print(f"\n{'='*60}")
    if description:
        print(f"🔄 {description}")
    print(f"📝 命令: {cmd}")
    print(f"📂 目录: {PROJECT_ROOT}")
    print('='*60)

    try:
        # 改变工作目录到项目根
        os.chdir(PROJECT_ROOT)

        # 执行命令
        result = subprocess.run(cmd, shell=True, text=True)

        if result.returncode == 0:
            print(f"\n✅ 命令执行成功")
        else:
            print(f"\n❌ 命令执行失败 (退出码: {result.returncode})")

        return result.returncode

    except Exception as e:
        print(f"\n❌ 执行错误: {e}")
        return 1

def main():
    """主程序"""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1].lower()

    commands = {
        'test': ('python test_backtest_selection.py', '运行回测功能测试'),
        'app': ('python app_with_cache.py', '启动 Flask 应用'),
        'check': ('python -m py_compile app_with_cache.py data_manager.py', 'Python 语法检查'),
        'status': ('python data_manager.py status', '查看缓存状态'),
        'help': (None, None),
    }

    if command == 'help':
        print_help()
        return 0

    if command not in commands:
        print(f"❌ 未知命令: {command}")
        print_help()
        return 1

    cmd, desc = commands[command]
    if cmd:
        return run_command(cmd, desc)

    return 0

def print_help():
    """打印帮助信息"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║         回测系统 - 命令运行工具 (自动处理路径)                   ║
╚════════════════════════════════════════════════════════════════╝

🎯 使用方法:
  python run_commands.py <command>

📋 可用命令:

  test      运行回测功能测试套件
            └─ python test_backtest_selection.py

  app       启动 Flask Web 应用
            └─ python app_with_cache.py
            └─ 打开: http://localhost:5000

  check     Python 语法检查
            └─ python -m py_compile app_with_cache.py data_manager.py

  status    查看数据缓存状态
            └─ python data_manager.py status

  help      显示帮助信息

📝 示例:

  # 运行测试
  python run_commands.py test

  # 启动应用
  python run_commands.py app

  # 语法检查
  python run_commands.py check

💡 为什么需要这个工具?

  ✗ 直接用 Bash 可能报错:
    bash: cd: too many arguments

  ✅ 这个工具自动处理 Windows 路径问题

📍 项目目录自动检测: {PROJECT_ROOT}

""".format(PROJECT_ROOT=PROJECT_ROOT))

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
