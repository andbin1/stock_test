@echo off
chcp 65001 > nul
title 量化回测系统 - 依赖安装

echo ╔═══════════════════════════════════════════════════════╗
echo ║         量化回测系统 - 依赖包安装工具               ║
echo ╚═══════════════════════════════════════════════════════╝
echo.

:: 检查 Python
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

echo ✓ 检测到 Python 环境：
python --version
echo.

:: 升级 pip
echo 📦 升级 pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
echo.

:: 安装依赖
echo 📥 开始安装依赖包...
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

pip install -r requirements_release.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo ❌ 安装失败！
    echo.
    echo 可能的原因：
    echo   1. 网络连接问题
    echo   2. Python 版本过低（需要 3.8+）
    echo   3. 权限不足
    echo.
    echo 解决方案：
    echo   - 检查网络连接
    echo   - 尝试使用管理员权限运行
    echo   - 更换镜像源
    echo.
    pause
    exit /b 1
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo ✅ 依赖安装完成！
echo.
echo 下一步：运行 "启动应用.bat" 启动系统
echo.
pause
