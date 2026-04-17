#!/usr/bin/env python
"""
超市管理系统后端启动脚本
使用方法: python run_backend.py
"""

import subprocess
import sys
import os

def install_dependencies():
    """安装项目依赖"""
    print("正在安装项目依赖...")
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    if result.returncode != 0:
        print("依赖安装失败，请检查requirements.txt文件")
        sys.exit(1)
    print("依赖安装完成")

def run_server():
    """运行Flask服务器"""
    print("正在启动Flask服务器...")
    print("服务器将在 http://localhost:5000 上运行")
    
    # 设置环境变量
    os.environ['FLASK_APP'] = 'APP.py'
    
    # 运行Flask应用
    subprocess.run([sys.executable, "APP.py"])

if __name__ == "__main__":
    print("超市管理系统后端启动程序")
    
    # 检查是否已安装依赖
    if not os.path.exists("venv"):
        print("提示: 建议在虚拟环境中运行此项目")
        print("可执行以下命令创建虚拟环境:")
        print(f"  python -m venv venv")
        print(f"  venv\\Scripts\\activate")
        print(f"  pip install -r requirements.txt")
        print()
        
    install_dependencies()
    run_server()