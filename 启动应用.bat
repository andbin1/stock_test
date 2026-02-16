@echo off
chcp 65001 > nul
title 量化回测系统 - 启动中...

echo ╔═══════════════════════════════════════════════════════╗
echo ║     量化回测系统 V2.1 - 多策略量化交易回测平台      ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

:: 检查 Python 是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未检测到 Python 环境
    echo.
    echo 请先安装 Python 3.8 或更高版本
    echo 下载地址：https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✓ Python 环境检测成功
echo.

:: 检查依赖是否安装
echo 📦 检查依赖包...
python -c "import flask" > nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  检测到缺少必要的依赖包
    echo.
    set /p install="是否现在安装依赖？(Y/N): "
    if /i "%install%"=="Y" (
        echo.
        echo 📥 正在安装依赖包...
        pip install -r requirements_release.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        if errorlevel 1 (
            echo.
            echo ❌ 依赖安装失败，请检查网络连接
            pause
            exit /b 1
        )
        echo ✓ 依赖安装完成
    ) else (
        echo.
        echo ❌ 缺少依赖包，无法启动应用
        echo 请手动运行：pip install -r requirements_release.txt
        pause
        exit /b 1
    )
)

echo ✓ 依赖检查完成
echo.

:: 创建必要的目录
if not exist "data_cache" mkdir data_cache
if not exist "data_cache\cache" mkdir data_cache\cache
if not exist "backtest_results" mkdir backtest_results
if not exist "logs" mkdir logs

echo 🚀 启动 Flask 应用...
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo   访问地址：http://localhost:5000
echo   按 Ctrl+C 停止服务
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

:: 启动应用
python app_with_cache.py

if errorlevel 1 (
    echo.
    echo ❌ 应用启动失败
    pause
)
