@echo off
echo Starting Chrome with remote debugging for Instagram Bot...
echo.
echo This will open Chrome. Please log into Instagram in the browser window.
echo Then go back to the bot and click "Connect to Existing Browser"
echo.
pause

REM Find Chrome executable
set CHROME_PATH=
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
) else if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    set CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe
)

if "%CHROME_PATH%"=="" (
    echo Chrome not found! Please start Chrome manually with:
    echo chrome.exe --remote-debugging-port=9222
    pause
    exit /b 1
)

REM Start Chrome with remote debugging
start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%TEMP%\chrome_debug"

echo.
echo Chrome started! Please log into Instagram.
echo Then go to the bot and click "Connect to Existing Browser"
echo.
pause
