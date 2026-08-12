@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title GAUR CRM - CLIENT CONNECTOR

cls
echo ============================================================
echo             GAUR CRM - CLIENT CONNECTOR
echo ============================================================
echo.
echo This computer will NOT create its own database.
echo It will connect to the MAIN SERVER computer.
echo.

set "CFG=%LOCALAPPDATA%\GaurCRM\central_server_url.txt"
set "SERVERURL="

if exist "%CFG%" (
  set /p SERVERURL=<"%CFG%"
)

if defined SERVERURL goto HAVEURL

echo Enter the SERVER URL shown on the main computer.
echo Example: http://192.168.1.4:5050
echo.
set /p SERVERURL=Server URL: 

if not defined SERVERURL goto BAD
if not exist "%LOCALAPPDATA%\GaurCRM" mkdir "%LOCALAPPDATA%\GaurCRM"
>"%CFG%" echo %SERVERURL%

:HAVEURL
echo.
echo Connecting to:
echo   %SERVERURL%
echo.

powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing -Uri '%SERVERURL%' -TimeoutSec 4; exit 0 } catch { exit 1 }"
if errorlevel 1 (
  echo.
  echo [NOT CONNECTED]
  echo Please check:
  echo 1. Main SERVER computer is ON.
  echo 2. 1_SERVER_START.bat is running there.
  echo 3. Both computers are on the same office Wi-Fi/LAN.
  echo 4. Windows Firewall allows port 5050 on the server.
  echo.
  echo To change server address, delete:
  echo %CFG%
  pause
  exit /b 1
)

start "" "%SERVERURL%"
exit /b 0

:BAD
echo No server URL entered.
pause
