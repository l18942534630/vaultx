@echo off
chcp 65001 > nul
title VaultX - 修复 WSL 并本地构建

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║     VaultX - 修复 WSL 并本地构建 APK                     ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

echo [!] 这将重置 WSL Ubuntu 并重新安装所有依赖
echo [!] 整个过程需要 30-60 分钟
echo.
pause

echo.
echo [1/4] 重置 WSL Ubuntu...
wsl --unregister Ubuntu 2>nul
wsl --install -d ubuntu-22.04 --no-launch

echo.
echo [2/4] 初始化 WSL（等待 30 秒）...
timeout /t 30 /nobreak >nul

echo.
echo [3/4] 安装构建依赖...
wsl -d ubuntu-22.04 -- bash -c "sudo apt-get update && sudo apt-get install -y git openjdk-17-jdk-headless zlib1g-dev python3 python3-pip && pip3 install --user buildozer kivy cryptography cython"

echo.
echo [4/4] 复制项目并构建...
wsl -d ubuntu-22.04 -- bash -c "cp -r /mnt/e/CODE/VaultX/android ~/vaultx-android && cd ~/vaultx-android && ~/.local/bin/buildozer android debug"

echo.
echo ═══════════════════════════════════════════════════════════
if %errorlevel% == 0 (
    echo [√] 构建成功！
) else (
    echo [!] 构建过程出现问题，请查看上方日志
)
echo ═══════════════════════════════════════════════════════════
echo.
echo APK 文件位于：
echo   \\wsl$\Ubuntu-22.04\home\%USERNAME%\vaultx-android\bin\
echo.
pause
