#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VaultX Android APK 构建脚本 (Python 版本)
不依赖 apt，直接使用 Python 工具链
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run(cmd, desc=""):
    """执行命令"""
    if desc:
        print(f"\n[*] {desc}")
    print(f"    $ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=os.path.expanduser("~/vaultx-android"))
    if result.returncode != 0:
        print(f"[!] 命令失败: {cmd}")
        return False
    return True

def main():
    print("=" * 60)
    print("VaultX Android APK 构建脚本 (Python)")
    print("=" * 60)
    
    # 1. 复制项目
    print("\n[1/4] 准备项目...")
    project_dir = Path.home() / "vaultx-android"
    if not project_dir.exists():
        print(f"    复制项目到 {project_dir}")
        shutil.copytree("/mnt/e/CODE/VaultX/android", project_dir)
    else:
        print(f"    项目已存在: {project_dir}")
    
    # 2. 安装 Python 包
    print("\n[2/4] 安装 Python 包...")
    packages = [
        "buildozer",
        "kivy",
        "cryptography",
        "cython",
    ]
    for pkg in packages:
        print(f"    安装 {pkg}...")
        run(f"python3 -m pip install --user --break-system-packages {pkg} 2>/dev/null || python3 -m pip install --user {pkg}", f"安装 {pkg}")
    
    # 3. 初始化 buildozer
    print("\n[3/4] 初始化 buildozer...")
    os.chdir(project_dir)
    if not Path(".buildozer").exists():
        run("~/.local/bin/buildozer init || buildozer init", "初始化 buildozer")
    
    # 4. 构建 APK
    print("\n[4/4] 构建 APK...")
    print("    这可能需要 30-60 分钟（首次）...")
    run("~/.local/bin/buildozer android debug || buildozer android debug", "构建 APK")
    
    # 完成
    print("\n" + "=" * 60)
    print("✅ 构建完成！")
    print("=" * 60)
    print(f"\nAPK 文件位置:")
    print(f"  {project_dir}/bin/")
    
    # 列出 APK
    bin_dir = project_dir / "bin"
    if bin_dir.exists():
        apks = list(bin_dir.glob("*.apk"))
        for apk in apks:
            size_mb = apk.stat().st_size / (1024*1024)
            print(f"  ✓ {apk.name} ({size_mb:.1f} MB)")
    
    print("\n在 Windows 中打开:")
    print(f"  \\\\wsl$\\Ubuntu\\home\\{os.getenv('USER')}\\vaultx-android\\bin\\")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[!] 错误: {e}")
        sys.exit(1)
