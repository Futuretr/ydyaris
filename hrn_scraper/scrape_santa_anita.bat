@echo off
echo Scraping Santa Anita for 2025-09-27...
echo.

REM Set Python path
set PYTHON_PATH="C:\Users\emir\AppData\Local\Programs\Python\Python313\python.exe"

REM Check if Python is available
%PYTHON_PATH% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed at the expected path!
    echo Expected: %PYTHON_PATH%
    pause
    exit /b 1
)

echo You can modify this file to scrape different tracks/dates
echo Current settings: santa-anita, 2025-09-27
echo.

%PYTHON_PATH% single_track_scraper.py santa-anita 2025-09-27

echo.
echo Scraping completed!
echo Check the generated JSON file for results.
echo.
pause