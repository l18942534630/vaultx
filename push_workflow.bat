@echo off
chcp 65001 > nul
title VaultX - 推送 GitHub Actions 工作流

echo.
echo  ╔═══════════════════════════════════════════════════════════╗
echo  ║     VaultX - 推送 GitHub Actions 工作流                   ║
echo  ╚═══════════════════════════════════════════════════════════╝
echo.

cd /d E:\CODE\VaultX

echo [1/4] 添加工作流文件...
git add .github/workflows/build-apk.yml

echo.
echo [2/4] 提交更改...
git commit -m "Add GitHub Actions workflow for building APK"

echo.
echo [3/4] 推送到 GitHub...
git push origin main

echo.
echo ═══════════════════════════════════════════════════════════
echo [4/4] 完成！
echo ═══════════════════════════════════════════════════════════
echo.
echo 📱 下一步：
echo.
echo 1. 打开浏览器访问你的 GitHub 仓库
echo    https://github.com/YOUR_USERNAME/vaultx
echo.
echo 2. 点击顶部的 "Actions" 标签
echo.
echo 3. 找到正在运行的工作流 "Build Android APK"
echo.
echo 4. 等待构建完成（约 10-20 分钟）
echo.
echo 5. 构建完成后，点击工作流 → 滚动到底部 "Artifacts" → 下载 vaultx-apk.zip
echo.
echo 6. 解压后得到 .apk 文件，传输到手机安装
echo.
pause
