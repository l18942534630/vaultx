#!/bin/bash
# VaultX Android APK 构建 - 完整依赖安装

set -e

echo "=========================================="
echo "VaultX Android APK 构建"
echo "=========================================="
echo ""

# 设置 PATH
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:~/.local/bin

# 1. 更新包管理器
echo "[1/3] 更新包管理器..."
sudo apt-get update -qq 2>/dev/null || true

# 2. 安装所有必需的依赖（非交互模式）
echo "[2/3] 安装构建依赖..."
DEBIAN_FRONTEND=noninteractive sudo apt-get install -y \
    git \
    openjdk-17-jdk-headless \
    zlib1g-dev \
    libssl-dev \
    libffi-dev \
    python3-dev \
    autoconf \
    libtool \
    pkg-config \
    libncurses5-dev \
    libncursesw5-dev \
    cmake \
    automake \
    wget \
    2>/dev/null || echo "部分依赖安装可能失败，继续..."

# 3. 构建 APK
echo "[3/3] 构建 APK..."
cd ~/vaultx-android
buildozer android debug

echo ""
echo "=========================================="
echo "✅ 构建完成！"
echo "=========================================="
echo ""
echo "APK 文件位于:"
echo "  ~/vaultx-android/bin/"
ls -lh ~/vaultx-android/bin/*.apk 2>/dev/null || echo "  (APK 文件生成中...)"
