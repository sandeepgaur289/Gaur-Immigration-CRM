@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
title GAUR CRM - CENTRAL SERVER v2.1

cls
echo ============================================================
echo        GAUR PORTAL - CENTRAL SHARED SERVER v2.1
echo ============================================================
echo.
echo IMPORTANT:
echo   RUN THIS FILE ON ONLY ONE MAIN COMPUTER.
echo   All MD / GM / Reception / AM users must connect to THIS PC.
echo.

set "OLDVENV=%LOCALAPPDATA%\GaurCRM\venv"
set "NEWVENV=%LOCALAPPDATA%\GaurCRM_v2\venv"
set "PY="

if exist "%OLDVENV%\Scripts\python.exe" set "PY=%OLDVENV%\Scripts\python.exe"
if not defined PY if exist "%NEWVENV%\Scripts\python.exe" set "PY=%NEWVENV%\Scripts\python.exe"

if not defined PY (
  where py >nul 2>&1
  if not errorlevel 1 (
    set "PYBASE=py -3"
  ) else (
    where python >nul 2>&1
    if errorlevel 1 (
      echo [ERROR] Python not found on SERVER computer.
      pause
      exit /b 1
    )
    set "PYBASE=python"
  )
  echo Creating shared CRM runtime...
  %PYBASE% -m venv "%NEWVENV%"
  if errorlevel 1 goto FAIL
  set "PY=%NEWVENV%\Scripts\python.exe"
)

echo Checking server components...
"%PY%" -c "import flask,openpyxl,xlrd,werkzeug,waitress" >nul 2>&1
if errorlevel 1 (
  echo Installing server components once...
  "%PY%" -m pip install --disable-pip-version-check -r "%~dp0requirements.txt"
  if errorlevel 1 goto FAIL
)

echo Checking application...
"%PY%" -m py_compile "%~dp0app.py"
if errorlevel 1 goto FAIL

echo.
echo Detecting LAN IP...
set "LANIP="
for /f "delims=" %%i in ('powershell -NoProfile -Command "$ips=Get-NetIPAddress -AddressFamily IPv4 ^| Where-Object {$_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254.*'} ^| Sort-Object InterfaceMetric; $ip=$ips ^| Select-Object -First 1 -ExpandProperty IPAddress; if($ip){$ip}"') do set "LANIP=%%i"

echo.
echo ============================================================
echo SERVER COMPUTER URL:
echo   http://127.0.0.1:5050
echo.
if defined LANIP (
  echo OTHER OFFICE COMPUTERS MUST USE:
  echo   http://!LANIP!:5050
  echo.
  >"%~dp0SERVER_ADDRESS.txt" echo http://!LANIP!:5050
) else (
  echo LAN IP was not detected automatically.
  echo Run ipconfig and use the IPv4 address with :5050
)
echo ============================================================
echo.
echo DO NOT run another CRM server on GM / Reception / AM computers.
echo They should use 2_CLIENT_CONNECT.bat only.
echo.
echo KEEP THIS WINDOW OPEN.
echo.

start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:5050'"

"%PY%" "%~dp0app.py"
set "RC=%ERRORLEVEL%"

echo.
echo CENTRAL SERVER STOPPED - EXIT CODE %RC%
pause
exit /b %RC%

:FAIL
echo.
echo CENTRAL SERVER STARTUP FAILED.
pause
exit /b 1
