@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title GAUR CRM SERVER

echo ============================================
echo        GAUR PORTAL - IMMIGRATION CRM v2.0
echo ============================================
echo.

where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found.
  echo Please install Python 3.11+ and enable "Add Python to PATH".
  pause
  exit /b 1
)

set "CRM_HOME=%LOCALAPPDATA%\GaurCRM"
set "VENV=%CRM_HOME%\venv"
set "PY=%VENV%\Scripts\python.exe"
set "REQMARK=%CRM_HOME%\requirements_v1_6_3.ok"

if not exist "%CRM_HOME%" mkdir "%CRM_HOME%"

if not exist "%PY%" (
  echo First-time setup: creating shared CRM runtime...
  python -m venv "%VENV%"
  if errorlevel 1 (
    echo [ERROR] Could not create CRM runtime.
    pause
    exit /b 1
  )
)

if not exist "%REQMARK%" (
  echo First-time setup: installing required components...
  "%PY%" -m pip install --disable-pip-version-check -q -r requirements.txt
  if errorlevel 1 (
    echo [ERROR] Required components could not be installed.
    pause
    exit /b 1
  )
  echo ready>"%REQMARK%"
)

echo Detecting this computer's LAN address...
for /f "delims=" %%i in ('powershell -NoProfile -Command "$ip=(Get-NetIPAddress -AddressFamily IPv4 ^| Where-Object {$_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown'} ^| Sort-Object InterfaceMetric ^| Select-Object -First 1 -ExpandProperty IPAddress); if($ip){$ip}else{'NOT_FOUND'}"') do set "LANIP=%%i"

echo Starting GAUR PORTAL...
start "GAUR CRM SERVER" /MIN "%PY%" app.py

echo Waiting for server...
set /a tries=0
:WAIT_SERVER
"%PY%" -c "import urllib.request,sys; exec('try:\\n urllib.request.urlopen(\"http://127.0.0.1:5050\",timeout=1)\\nexcept Exception:\\n sys.exit(1)')" >nul 2>&1
if not errorlevel 1 goto SERVER_READY

set /a tries+=1
if !tries! GEQ 30 (
  echo.
  echo [ERROR] Server did not start within 30 seconds.
  pause
  exit /b 1
)
timeout /t 1 /nobreak >nul
goto WAIT_SERVER

:SERVER_READY
echo.
echo ============================================
echo GAUR PORTAL IS RUNNING
echo ============================================
echo This computer:
echo   http://127.0.0.1:5050
echo.
if /I not "!LANIP!"=="NOT_FOUND" (
  echo OTHER COMPUTERS ON SAME WIFI/LAN:
  echo   http://!LANIP!:5050
  echo.
  echo Share ONLY the LAN URL above with other office computers.
) else (
  echo LAN IP could not be detected automatically.
  echo Run SHOW_SHARED_URL.bat
)
echo ============================================
echo.
start "" "http://127.0.0.1:5050"
echo Keep this server computer ON while other computers use the CRM.
pause
