@echo off
echo ====================================
echo 时间序列预测Web应用 - 快速启动
echo ====================================
echo.

echo [1/3] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.13+
    pause
    exit /b 1
)

echo.
echo [2/3] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [3/3] 启动Flask服务器...
echo.
echo ====================================
echo 应用已启动！
echo 请在浏览器中访问: http://localhost:5000
echo 按 Ctrl+C 停止服务器
echo ====================================
echo.

python app.py

pause