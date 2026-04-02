# -*- coding: utf-8 -*-
"""
VaultX - 本地密码管理器
主程序入口
"""
import sys
from pathlib import Path

# 确保编码
if sys.platform == 'win32':
    import locale
    if sys.stdout:
        sys.stdout.reconfigure(encoding='utf-8')

# 导入GUI模块
from vaultx.gui import VaultXApp

def main():
    """主入口"""
    app = VaultXApp()
    app.run()

if __name__ == "__main__":
    main()
