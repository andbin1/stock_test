@echo off
REM Quick installation script without user interaction
REM Uses Tsinghua mirror by default

title Quick Install - Stock Backtest System

echo ========================================================
echo    Quick Installation (No interaction required)
echo ========================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [OK] Python detected
python --version
echo.

echo [INFO] Installing dependencies using Tsinghua mirror...
echo.

REM Try Tsinghua mirror
pip install -r requirements_release.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo [RETRY] Trying Aliyun mirror...
    pip install -r requirements_release.txt -i https://mirrors.aliyun.com/pypi/simple
    
    if errorlevel 1 (
        echo.
        echo [RETRY] Trying Tencent mirror...
        pip install -r requirements_release.txt -i https://mirrors.cloud.tencent.com/pypi/simple
        
        if errorlevel 1 (
            echo.
            echo [ERROR] Installation failed with all mirrors!
            pause
            exit /b 1
        )
    )
)

echo.
echo [SUCCESS] Installation complete!
echo.
echo Run start_app.bat to launch the application
echo.
pause
