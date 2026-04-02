# VaultX Android APP 构建指南

## 概述

VaultX Android 版本使用 **Kivy** 框架开发，可以打包为 Android APK 安装到手机上。

## 环境要求

### Windows 系统（需要 WSL）
```bash
# 1. 安装 WSL2 (Windows Subsystem for Linux)
# 在 PowerShell 中以管理员运行:
wsl --install -d ubuntu-22.04

# 2. 进入 WSL，安装构建依赖
sudo apt update
sudo apt install -y python3-pip python3-dev git zip unzip

# 3. 安装 Android SDK
mkdir -p ~/android-sdk/cmdline-tools
cd ~/android-sdk/cmdline-tools
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-11076708_latest.zip
mv cmdline-tools latest
export ANDROID_HOME=~/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# 4. 接受协议
yes | sdkmanager --licenses 2>/dev/null
sdkmanager "platforms;android-34" "build-tools;34.0.0" "ndk;26b" 2>/dev/null
```

### macOS / Linux 系统
```bash
# 安装 Homebrew (macOS)
brew install python3 pip git

# 安装 Android SDK
brew install --cask android-sdk
```

## 安装 Buildozer

```bash
# 在 Linux/macOS/WSL 中运行:
pip3 install buildozer

# 安装编译依赖
pip3 install numpy cython
```

## 构建步骤

### 方法一：自动构建（推荐）

```bash
cd E:\CODE\VaultX\android

# 如果在 Windows，使用 WSL
wsl

# 进入目录
cd /mnt/e/CODE/VaultX/android

# 首次构建
buildozer android debug

# 等待下载依赖和编译...
# 完成后 APK 在 bin/ 目录下
```

### 方法二：使用 Docker（无需配置环境）

```bash
# 下载 Docker 镜像
docker pull kivy/buildozer

# 挂载目录并构建
docker run -v $(pwd):/home/user/code kivy/buildozer android debug
```

### 方法三：分步构建

```bash
# 1. 初始化 buildozer
buildozer init

# 2. 安装依赖到 spec 配置的虚拟环境
buildozer android p4a

# 3. 构建
buildozer android debug
```

## 构建输出

构建成功后，APK 文件在：
```
bin/vaultx-1.0.0-arm64-v8a_armeabi-v7a-debug.apk
```

## 安装到手机

### 方法一：ADB 安装
```bash
# 连接手机（开启 USB 调试）
adb install bin/vaultx-1.0.0-*-debug.apk
```

### 方法二：直接传输
- 将 APK 文件传输到手机
- 在手机上打开 APK 文件
- 允许安装来自未知来源的应用

## 签名 APK（发布版本）

```bash
# 1. 生成签名密钥
keytool -genkey -v -keystore my-release-key.keystore -alias vaultx -keyalg RSA -keysize 2048 -validity 10000

# 2. 打包签名
jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore my-release-key.keystore bin/vaultx-*-release-unsigned.apk vaultx

# 3. 对齐优化
zipalign -v 4 bin/vaultx-*-release-unsigned.apk bin/vaultx-*-release.apk
```

## 常见问题

### Q: 编译失败，提示缺少 NDK
```bash
# 安装 NDK
sdkmanager "ndk;26b"
```

### Q: 编译失败，提示权限错误
```bash
# 添加执行权限
chmod +x ~/.buildozer/android/platform/python-for-android/*.sh
```

### Q: 在 Windows 上构建太慢
- 强烈建议使用 WSL2 或 Docker
- Windows 原生构建非常慢且容易出错

### Q: 找不到 APK 文件
```bash
# 查看构建日志
buildozer android debug 2>&1 | tee build.log

# 手动查找
find . -name "*.apk" -type f
```

## 数据同步

Android 版本的 VaultX 数据文件位置：
```
/data/data/org.vaultx/files/.vaultx/vault.enc
```

### 与桌面版共享数据
1. 在桌面版中 **📤 导出** 备份
2. 将备份文件传输到手机
3. 在 Android 版中 **📥 导入** 备份

## 技术栈

- **框架**: Kivy 2.x
- **语言**: Python 3
- **加密**: cryptography (Fernet/AES-256)
- **打包**: Buildozer + PyInstaller (Android) / PyInstaller (Windows)
- **目标平台**: Android 7.0+

## 项目结构

```
android/
├── main.py           # 主程序
├── buildozer.spec    # 构建配置
├── README.md         # 本文档
└── bin/              # 编译输出目录
    └── vaultx-*.apk  # APK 文件
```

## 下一步

1. 复制 `E:\CODE\VaultX\android` 目录到 Linux/WSL 环境
2. 按照上述步骤构建 APK
3. 将 APK 传输到手机安装

## 支持

- 如果构建遇到问题，请提供完整的错误日志
- 可以尝试搜索 Kivy/Buildozer 相关问题

---

**版本**: 1.0.0  
**更新**: 2026-04-01
