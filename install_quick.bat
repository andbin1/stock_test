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

REM Detect Python version and select requirements file
python -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>&1
if errorlevel 1 (
    set REQ_FILE=requirements_release.txt
    echo [INFO] Using requirements_release.txt
) else (
    set REQ_FILE=requirements_py312.txt
    echo [INFO] Python 3.12+ detected, using requirements_py312.txt
)
echo.

echo [INFO] Installing dependencies using Tsinghua mirror...
echo.

REM Try Tsinghua mirror
pip install -r %REQ_FILE% -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo [RETRY] Trying Aliyun mirror...
    pip install -r %REQ_FILE% -i https://mirrors.aliyun.com/pypi/simple

    if errorlevel 1 (
        echo.
        echo [RETRY] Trying Tencent mirror...
        pip install -r %REQ_FILE% -i https://mirrors.cloud.tencent.com/pypi/simple
        
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
