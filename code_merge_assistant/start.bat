@echo off
REM Windows 快速启动脚本

echo 🔀 代码合并辅助工具 - 启动中...
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python，请先安装 Python
    pause
    exit /b 1
)

REM 检查依赖是否安装
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo 📦 正在安装依赖...
    pip install -r requirements.txt
)

echo ✅ 依赖检查完成
echo.
echo 🚀 启动 Web 界面...
echo 📍 访问地址: http://localhost:5678
echo 💡 按 Ctrl+C 停止服务
echo.

python web_ui.py
