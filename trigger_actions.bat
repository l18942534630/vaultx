@echo off
chcp 65001 > nul
title VaultX - 触发 GitHub Actions

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║     VaultX - 触发 GitHub Actions 构建                    ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

cd /d E:\CODE\VaultX

echo [*] 创建一个空提交来触发 GitHub Actions...
git commit --allow-empty -m "Trigger GitHub Actions build"

echo.
echo [*] 推送到 GitHub...
git push origin main

echo.
echo ═══════════════════════════════════════════════════════════
echo [√] 完成！
echo ═══════════════════════════════════════════════════════════
echo.
echo 📱 现在请：
echo.
echo 1. 打开浏览器访问：
echo    https://github.com/l18942534630/vaultx/actions
echo.
echo 2. 你应该能看到 "Build Android APK" 正在运行
echo.
echo 3. 点击它查看构建进度
echo.
pause
