@echo off
chcp 65001 > nul
title VaultX Android APK 构建

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║          VaultX Android APK 一键构建                      ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

REM 检查 WSL
wsl --list --verbose > nul 2>&1
if errorlevel 1 (
    echo [!] WSL 未安装，正在安装 Ubuntu-22.04...
    echo     这可能需要几分钟，请耐心等待...
    wsl --install -d ubuntu-22.04
    if errorlevel 1 (
        echo [X] 安装失败。请手动运行: wsl --install -d ubuntu-22.04
        pause
        exit /b 1
    )
    echo [√] WSL 安装成功，请重启电脑后重新运行此脚本
    pause
    exit /b 0
)

echo [√] WSL 已安装
echo.

REM 检查项目目录
if not exist "E:\CODE\VaultX\android\main.py" (
    echo [X] 找不到项目文件: E:\CODE\VaultX\android\main.py
    pause
    exit /b 1
)

echo [*] 正在准备 WSL 构建环境...
echo     (首次运行需要下载 Android SDK/NDK，约需 30-60 分钟)
echo.

REM 创建构建命令
set BUILD_CMD=bash -c "cd /mnt/e/CODE/VaultX/android && bash build.sh 2>&1"

REM 运行构建
wsl %BUILD_CMD%

if errorlevel 1 (
    echo.
    echo [X] 构建过程中出现错误
    echo     请检查上方的错误信息
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo [√] 构建完成！
echo ═══════════════════════════════════════════════════════════
echo.
echo APK 文件位于 WSL 内:
echo   \\wsl$\Ubuntu\home\%USERNAME%\vaultx-android\bin\
echo.
echo 正在打开 APK 所在目录...
explorer "\\wsl$\Ubuntu\home\%USERNAME%\vaultx-android\bin"

pause
