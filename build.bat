@echo off

echo.
echo ========================================
echo   File Nexus Suite - PyInstaller Build
echo ========================================
echo.

python -m PyInstaller --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PyInstaller is not installed.
    echo         Run: pip install pyinstaller
    echo.
    pause
    exit /b 1
)

python build_pyinstaller.py

echo.
pause
