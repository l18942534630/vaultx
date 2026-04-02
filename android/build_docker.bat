@echo off
chcp 65001 > nul
title VaultX Android APK 构建 (Docker)

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║     VaultX Android APK 构建 (Docker 方案)                ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

REM 检查 Docker
docker --version > nul 2>&1
if errorlevel 1 (
    echo [!] Docker 未安装
    echo.
    echo 请先安装 Docker Desktop:
    echo   https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo [√] Docker 已安装
echo.

REM 检查项目
if not exist "main.py" (
    echo [!] 找不到 main.py，请确保在 android 目录下运行
    pause
    exit /b 1
)

echo [*] 准备构建...
echo     首次构建需要 30-60 分钟
echo     后续构建需要 5-10 分钟
echo.

REM 拉取镜像
echo [1/3] 拉取 Kivy 构建镜像...
docker pull kivy/buildozer

echo.
echo [2/3] 构建 APK...
docker run -v %cd%:/home/user/code kivy/buildozer android debug

if errorlevel 1 (
    echo.
    echo [!] 构建失败
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════
echo [√] 构建完成！
echo ═══════════════════════════════════════════════════════════
echo.
echo APK 文件位于:
echo   %cd%\bin\
echo.
echo 正在打开 bin 目录...
explorer "%cd%\bin"

pause
