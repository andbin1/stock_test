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

REM Check Python version (more lenient check)
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Python version might be too old
    echo This system requires Python 3.8 or higher
    echo Your version:
    python --version
    echo.
    set /p continue="Continue anyway? (Y/N): "
    if /i not "!continue!"=="Y" (
        echo Installation cancelled.
        pause
        exit /b 1
    )
)

REM Select pip mirror
echo [STEP 1] Select pip mirror source:
echo.
echo   1. Tsinghua University (recommended)
echo   2. Aliyun
echo   3. Tencent Cloud
echo   4. Douban
echo   5. Official PyPI (slow in China)
echo.
set /p mirror="Enter your choice (1-5, default=1): "

if "!mirror!"=="" set mirror=1

if "!mirror!"=="1" (
    set MIRROR_URL=https://pypi.tuna.tsinghua.edu.cn/simple
    set MIRROR_NAME=Tsinghua University
)
if "!mirror!"=="2" (
    set MIRROR_URL=https://mirrors.aliyun.com/pypi/simple
    set MIRROR_NAME=Aliyun
)
if "!mirror!"=="3" (
    set MIRROR_URL=https://mirrors.cloud.tencent.com/pypi/simple
    set MIRROR_NAME=Tencent Cloud
)
if "!mirror!"=="4" (
    set MIRROR_URL=https://pypi.doubanio.com/simple
    set MIRROR_NAME=Douban
)
if "!mirror!"=="5" (
    set MIRROR_URL=https://pypi.org/simple
    set MIRROR_NAME=Official PyPI
)

echo.
echo [INFO] Using mirror: !MIRROR_NAME!
echo [INFO] Mirror URL: !MIRROR_URL!
echo.

REM Detect Python version and select requirements file
python -c "import sys; exit(0 if sys.version_info >= (3, 12) else 1)" >nul 2>&1
if errorlevel 1 (
    set REQ_FILE=requirements_release.txt
    echo [INFO] Python version ^< 3.12, using requirements_release.txt
) else (
    set REQ_FILE=requirements_py312.txt
    echo [INFO] Python 3.12+ detected, using requirements_py312.txt
)
echo.

REM Upgrade pip
echo [STEP 2] Upgrading pip...
python -m pip install --upgrade pip -i !MIRROR_URL!
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)
echo.

REM Install dependencies
echo [STEP 3] Installing dependencies...
echo [INFO] Using: !REQ_FILE!
echo --------------------------------------------------------
echo.
echo This may take a few minutes, please wait...
echo.

pip install -r !REQ_FILE! -i !MIRROR_URL!

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed!
    echo.
    echo Trying alternative mirror sources...
    echo.
    
    REM Try alternative mirrors
    echo [RETRY 1] Trying Aliyun mirror...
    pip install -r requirements_release.txt -i https://mirrors.aliyun.com/pypi/simple
    
    if errorlevel 1 (
        echo [RETRY 2] Trying Tencent mirror...
        pip install -r requirements_release.txt -i https://mirrors.cloud.tencent.com/pypi/simple
        
        if errorlevel 1 (
            echo.
            echo [ERROR] All mirrors failed!
            echo.
            echo Possible reasons:
            echo   1. Network connection issues
            echo   2. Firewall blocking
            echo   3. Proxy settings needed
            echo.
            echo Solutions:
            echo   - Check network connection
            echo   - Try running as Administrator
            echo   - Disable VPN/Proxy temporarily
            echo   - Contact your network administrator
            echo.
            pause
            exit /b 1
        )
    )
)

echo.
echo --------------------------------------------------------
echo.
echo [SUCCESS] Dependencies installed successfully!
echo.
echo Next step: Run "start_app.bat" to start the system
echo.
pause
