@echo off
echo Installing Python packages...
echo.

REM Set Python path
set PYTHON_PATH="C:\Users\emir\AppData\Local\Programs\Python\Python313\python.exe"
set PIP_PATH="C:\Users\emir\AppData\Local\Programs\Python\Python313\Scripts\pip.exe"

REM Check if Python is installed
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed at the expected path!
    echo Expected: %PYTHON_PATH%
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found, installing required packages...
%PIP_PATH% install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Package installation failed!
    echo Try running as Administrator or check your internet connection
    pause
    exit /b 1
)

echo.
echo SUCCESS: All packages installed successfully!
echo You can now run the scraper scripts.
echo.
pause