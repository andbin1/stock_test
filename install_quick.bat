@echo off
REM Quick installation without user interaction

title Quick Install

echo ========================================================
echo    Quick Installation
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

REM Detect Python version
python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 and sys.version_info[1] >= 12 else 1)" >nul 2>&1
if errorlevel 1 (
    set REQ_FILE=requirements_release.txt
    echo [INFO] Using requirements_release.txt
) else (
    set REQ_FILE=requirements_py312.txt
    echo [INFO] Using requirements_py312.txt
)
echo.

echo [INFO] Installing via Tsinghua mirror...
echo.

REM Try Tsinghua mirror
pip install -r %REQ_FILE% -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo [RETRY] Trying Aliyun...
    pip install -r %REQ_FILE% -i https://mirrors.aliyun.com/pypi/simple

    if errorlevel 1 (
        echo.
        echo [RETRY] Trying Tencent...
        pip install -r %REQ_FILE% -i https://mirrors.cloud.tencent.com/pypi/simple

        if errorlevel 1 (
            echo.
            echo [ERROR] Installation failed!
            pause
            exit /b 1
        )
    )
)

echo.
echo [SUCCESS] Installation complete!
echo.
echo Run: 启动应用.bat
echo.
pause
