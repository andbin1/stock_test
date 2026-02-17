@echo off
setlocal enabledelayedexpansion

title Starting Application...

echo ========================================================
echo    Stock Trading Backtest System V2.1
echo ========================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python 3.8+
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected:
python --version
echo.

REM Check Python version
python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 and sys.version_info[1] >= 8 else 1)" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python version too old. Need 3.8+
    echo.
    set /p continue="Continue anyway? (Y/N): "
    if /i "!continue!" == "Y" (
        echo Continuing...
    ) else (
        echo Cancelled.
        pause
        exit /b 1
    )
) else (
    echo [OK] Python version OK
)
echo.

REM Check dependencies
echo [INFO] Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] Dependencies not found!
    echo.
    set /p install="Install now? (Y/N): "
    if /i "!install!" == "Y" (
        echo.
        echo [INFO] Detecting Python version...
        python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 and sys.version_info[1] >= 12 else 1)" >nul 2>&1
        if errorlevel 1 (
            set REQ_FILE=requirements_release.txt
        ) else (
            set REQ_FILE=requirements_py312.txt
        )
        echo [INFO] Using: !REQ_FILE!
        echo [INFO] Installing...
        pip install -r !REQ_FILE! -i https://pypi.tuna.tsinghua.edu.cn/simple
        if errorlevel 1 (
            echo [RETRY] Trying another mirror...
            pip install -r !REQ_FILE! -i https://mirrors.aliyun.com/pypi/simple
            if errorlevel 1 (
                echo.
                echo [ERROR] Installation failed
                pause
                exit /b 1
            )
        )
        echo [OK] Dependencies installed
    ) else (
        echo.
        echo [ERROR] Cannot start without dependencies
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies OK
)
echo.

REM Create directories
if not exist "data_cache" mkdir data_cache
if not exist "data_cache\cache" mkdir "data_cache\cache"
if not exist "backtest_results" mkdir backtest_results
if not exist "logs" mkdir logs

echo [INFO] Starting application...
echo.
echo --------------------------------------------------------
echo.
echo   URL: http://localhost:5000
echo.
echo   Press Ctrl+C to stop
echo.
echo --------------------------------------------------------
echo.

REM Start application
python app_with_cache.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application failed to start
    echo.
    echo Common issues:
    echo   - Port 5000 already in use
    echo   - Missing dependencies
    echo.
    pause
)
