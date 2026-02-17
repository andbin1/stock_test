@echo off
setlocal enabledelayedexpansion

title Installing Dependencies...

echo ========================================================
echo    Dependency Installer
echo ========================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.8+
    echo Download: https://www.python.org/downloads/
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
    echo [WARNING] Python version might be too old
    echo This system requires Python 3.8+
    echo.
    set /p continue="Continue anyway? (Y/N): "
    if /i "!continue!" == "Y" (
        echo Continuing...
    ) else (
        echo Installation cancelled.
        pause
        exit /b 1
    )
)

REM Detect Python version
python -c "import sys; sys.exit(0 if sys.version_info[0] == 3 and sys.version_info[1] >= 12 else 1)" >nul 2>&1
if errorlevel 1 (
    set REQ_FILE=requirements_release.txt
    echo [INFO] Using requirements_release.txt
) else (
    set REQ_FILE=requirements_py312.txt
    echo [INFO] Using requirements_py312.txt for Python 3.12+
)
echo.

REM Select mirror
echo [STEP 1] Select pip mirror:
echo.
echo   1. Tsinghua University (recommended)
echo   2. Aliyun
echo   3. Tencent Cloud
echo   4. Douban
echo   5. Official PyPI
echo.
set /p mirror="Enter choice (1-5, default=1): "

if "!mirror!" == "" set mirror=1

if "!mirror!" == "1" (
    set MIRROR_URL=https://pypi.tuna.tsinghua.edu.cn/simple
    set MIRROR_NAME=Tsinghua
)
if "!mirror!" == "2" (
    set MIRROR_URL=https://mirrors.aliyun.com/pypi/simple
    set MIRROR_NAME=Aliyun
)
if "!mirror!" == "3" (
    set MIRROR_URL=https://mirrors.cloud.tencent.com/pypi/simple
    set MIRROR_NAME=Tencent
)
if "!mirror!" == "4" (
    set MIRROR_URL=https://pypi.doubanio.com/simple
    set MIRROR_NAME=Douban
)
if "!mirror!" == "5" (
    set MIRROR_URL=https://pypi.org/simple
    set MIRROR_NAME=Official
)

echo.
echo [INFO] Using mirror: !MIRROR_NAME!
echo.

REM Upgrade pip
echo [STEP 2] Upgrading pip...
python -m pip install --upgrade pip -i !MIRROR_URL!
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing...
)
echo.

REM Install dependencies
echo [STEP 3] Installing dependencies...
echo [INFO] Using: !REQ_FILE!
echo --------------------------------------------------------
echo.
echo Please wait...
echo.

pip install -r !REQ_FILE! -i !MIRROR_URL!

if errorlevel 1 (
    echo.
    echo [ERROR] Installation failed!
    echo.
    echo Trying alternative mirrors...
    echo.

    echo [RETRY 1] Trying Aliyun...
    pip install -r !REQ_FILE! -i https://mirrors.aliyun.com/pypi/simple

    if errorlevel 1 (
        echo [RETRY 2] Trying Tencent...
        pip install -r !REQ_FILE! -i https://mirrors.cloud.tencent.com/pypi/simple

        if errorlevel 1 (
            echo.
            echo [ERROR] All mirrors failed!
            echo.
            echo Possible reasons:
            echo   - Network connection issues
            echo   - Firewall blocking
            echo.
            pause
            exit /b 1
        )
    )
)

echo.
echo --------------------------------------------------------
echo.
echo [SUCCESS] Dependencies installed!
echo.
echo Next: Run start_app.bat
echo.
pause
