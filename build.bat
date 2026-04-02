@echo off
chcp 65001 > nul
echo ========================================
echo VaultX 打包脚本
echo ========================================
echo.

echo [1/3] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo.
echo [2/3] 安装依赖...
pip install -r requirements.txt -q

echo.
echo [3/3] 打包 EXE...
pyinstaller --onefile --windowed --name "VaultX" --clean main.py

echo.
echo ========================================
echo 打包完成！
echo 输出目录: dist\VaultX.exe
echo ========================================
pause
