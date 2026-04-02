#!/bin/bash
# VaultX Android APK 构建脚本 (WSL/Linux)

set -e

echo "============================================================"
echo "VaultX Android APK 构建脚本"
echo "============================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在 WSL 中
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo -e "${GREEN}[检测] 运行在 WSL 环境${NC}"
    IN_WSL=1
else
    echo -e "${GREEN}[检测] 运行在 Linux 环境${NC}"
    IN_WSL=0
fi

# 1. 检查并安装系统依赖
echo ""
echo -e "${YELLOW}[1/6] 检查系统依赖...${NC}"

if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3 python3-pip python3-dev git zip unzip openjdk-17-jdk autoconf libtool pkg-config libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev automake wget lzip help2man
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3 python3-pip python3-devel git zip unzip java-17-openjdk-devel autoconf libtool pkgconfig ncurses-devel cmake libffi-devel openssl-devel automake wget lzip help2man
elif command -v brew &> /dev/null; then
    brew install python3 git autoconf automake libtool
fi

# 2. 安装 Python 包
echo ""
echo -e "${YELLOW}[2/6] 安装 Python 包...${NC}"
pip3 install --user --upgrade pip
pip3 install --user cython
pip3 install --user buildozer
pip3 install --user kivy

# 确保 buildozer 在 PATH 中
export PATH="$HOME/.local/bin:$PATH"

# 3. 设置 Android SDK (buildozer 会自动下载)
echo ""
echo -e "${YELLOW}[3/6] 配置 Android SDK...${NC}"
export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
export ANDROID_NDK_HOME="$HOME/.buildozer/android/platform/android-ndk"

# 4. 准备项目目录
echo ""
echo -e "${YELLOW}[4/6] 准备项目目录...${NC}"

if [ "$IN_WSL" -eq 1 ]; then
    # WSL 环境，从 Windows 复制
    PROJECT_DIR="$HOME/vaultx-android"
    if [ ! -d "$PROJECT_DIR" ]; then
        cp -r "/mnt/e/CODE/VaultX/android" "$PROJECT_DIR"
        echo "已从 Windows 复制项目"
    fi
else
    # 纯 Linux 环境
    PROJECT_DIR="$HOME/vaultx-android"
    if [ ! -d "$PROJECT_DIR" ]; then
        # 检查是否存在 Windows 挂载点
        if [ -d "/mnt/e/CODE/VaultX/android" ]; then
            cp -r "/mnt/e/CODE/VaultX/android" "$PROJECT_DIR"
        else
            echo "请手动将 VaultX/android 目录复制到: $PROJECT_DIR"
            read -p "按回车继续..."
        fi
    fi
fi

cd "$PROJECT_DIR"
echo "项目目录: $(pwd)"

# 5. 初始化 buildozer (首次)
echo ""
echo -e "${YELLOW}[5/6] 初始化 buildozer...${NC}"
if [ ! -d ".buildozer" ]; then
    buildozer init || true
fi

# 6. 构建 APK
echo ""
echo -e "${YELLOW}[6/6] 构建 APK...${NC}"
echo -e "${RED}注意: 首次构建需要下载 Android SDK/NDK，可能需要 30-60 分钟${NC}"
echo ""

# 构建调试版 APK
buildozer android debug || {
    echo ""
    echo -e "${RED}构建失败！${NC}"
    echo "常见问题解决方案:"
    echo "1. 如果提示 'SDK location not found'，运行:"
    echo "   buildozer android p4a"
    echo "2. 如果提示 NDK 错误，运行:"
    echo "   buildozer android p4a --ndk-api=21"
    echo "3. 如果网络问题，设置代理:"
    echo "   export HTTP_PROXY=http://your-proxy:port"
    echo "   export HTTPS_PROXY=http://your-proxy:port"
    exit 1
}

# 完成
echo ""
echo "============================================================"
echo -e "${GREEN}构建成功！${NC}"
echo "============================================================"
echo ""
echo "APK 文件位置:"
echo "  $(pwd)/bin/"
ls -lh bin/*.apk 2>/dev/null || echo "  (APK 文件将在构建完成后显示)"
echo ""
if [ "$IN_WSL" -eq 1 ]; then
    echo "在 Windows 资源管理器中打开:"
    echo "  \\\\wsl\$\\Ubuntu\\home\\$USER\\vaultx-android\\bin\\"
fi
echo ""
echo "将 APK 传输到手机并安装即可使用。"
