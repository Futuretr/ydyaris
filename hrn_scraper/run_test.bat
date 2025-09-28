@echo off
echo Testing Horse Racing Nation Scraper...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please run install_packages.bat first
    pause
    exit /b 1
)

echo Running test script...
python test_scraper.py

echo.
echo Test completed! Check the output above for results.
echo If test_results.json was created, the scraper is working properly.
echo.
pause