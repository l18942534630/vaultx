# -*- coding: utf-8 -*-
"""测试 Android 版本代码"""
import sys
sys.path.insert(0, '.')

# 检查语法
try:
    import ast
    with open('main.py', 'r', encoding='utf-8') as f:
        source = f.read()
    ast.parse(source)
    print("✅ 语法检查通过")
except SyntaxError as e:
    print(f"❌ 语法错误: {e}")
    sys.exit(1)

# 检查依赖
print("\n检查依赖...")
missing = []
for mod in ['kivy', 'cryptography', 'jnius']:
    try:
        __import__(mod)
        print(f"  ✅ {mod}")
    except ImportError:
        print(f"  ⚠️ {mod} (未安装，跳过运行时测试)")
        missing.append(mod)

print("\n" + "="*50)
print("Android 版本代码检查完成")
print("="*50)
print("\n下一步:")
print("1. 将 E:\\CODE\\VaultX\\android 目录复制到 Linux/WSL 环境")
print("2. 按照 android/README.md 构建 APK")
print("3. 将 APK 安装到手机")
