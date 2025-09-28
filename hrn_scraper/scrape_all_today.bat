@echo off
echo Scraping ALL tracks for today...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please run install_packages.bat first
    pause
    exit /b 1
)

echo Starting scrape for all tracks...
echo This may take several minutes depending on the number of tracks.
echo.

python hrn_scraper.py

echo.
echo Scraping completed!
echo Check the generated JSON and CSV files for results.
echo.
pause