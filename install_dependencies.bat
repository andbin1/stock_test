@echo off
setlocal enabledelayedexpansion

title Stock Backtest System - Installing Dependencies

echo ========================================================
echo    Stock Backtest System - Dependency Installer
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

echo [OK] Python detected:
python --version
echo.

REM Upgrade pip
echo [STEP 1] Upgrading pip...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)
echo.

REM Install dependencies
echo [STEP 2] Installing dependencies...
echo --------------------------------------------------------
echo.

pip install -r requirements_release.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed!
    echo.
    echo Possible reasons:
    echo   1. Network connection issues
    echo   2. Python version too old (requires 3.8+)
    echo   3. Insufficient permissions
    echo.
    echo Solutions:
    echo   - Check network connection
    echo   - Run as Administrator
    echo   - Try different pip mirror
    echo.
    pause
    exit /b 1
)

echo.
echo --------------------------------------------------------
echo.
echo [SUCCESS] Dependencies installed successfully!
echo.
echo Next step: Run "start_app.bat" to start the system
echo.
pause
