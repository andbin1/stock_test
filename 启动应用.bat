@echo off
setlocal enabledelayedexpansion

title Stock Backtest System - Starting...

echo ========================================================
echo    Stock Backtest System V2.1 - Quantitative Trading
echo ========================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.8 or higher first.
    echo Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python environment detected:
python --version
echo.

REM Check Python version (lenient check for beta/dev versions)
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python version might be too old
    echo This system requires Python 3.8 or higher
    echo.
    set /p continue="Continue anyway? (Y/N): "
    if /i not "!continue!"=="Y" (
        echo Startup cancelled.
        pause
        exit /b 1
    )
) else (
    echo [OK] Python version check passed
)
echo.

REM Check dependencies
echo [INFO] Checking dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [WARNING] Required dependencies not found!
    echo.
    set /p install="Install dependencies now? (Y/N): "
    if /i "!install!"=="Y" (
        echo.
        echo [INFO] Installing dependencies (using Tsinghua mirror)...
        pip install -r requirements_release.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        if errorlevel 1 (
            echo [RETRY] Trying Aliyun mirror...
            pip install -r requirements_release.txt -i https://mirrors.aliyun.com/pypi/simple
            if errorlevel 1 (
                echo.
                echo [ERROR] Failed to install dependencies
                echo Please run install_dependencies.bat manually
                pause
                exit /b 1
            )
        )
        echo [OK] Dependencies installed
    ) else (
        echo.
        echo [ERROR] Cannot start without dependencies
        echo Please run: install_dependencies.bat
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies check passed
)
echo.

REM Create necessary directories
if not exist "data_cache" mkdir data_cache
if not exist "data_cache\cache" mkdir data_cache\cache
if not exist "backtest_results" mkdir backtest_results
if not exist "logs" mkdir logs

echo [INFO] Starting Flask application...
echo.
echo --------------------------------------------------------
echo.
echo   Access URL: http://localhost:5000
echo   
echo   Press Ctrl+C to stop the server
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
    echo   - Python version incompatible
    echo.
    pause
)
