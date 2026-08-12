@echo off
setlocal
title GAUR PORTAL - Repair Runtime
set "CRM_HOME=%LOCALAPPDATA%\GaurCRM"
echo This resets ONLY the shared Python runtime.
echo Your CRM database and employee/lead data are NOT deleted.
echo.
if exist "%CRM_HOME%\venv" rmdir /S /Q "%CRM_HOME%\venv"
del /Q "%CRM_HOME%\requirements_v1_6_2.ok" >nul 2>&1
echo Runtime reset complete.
echo Double-click START_CRM_FAST.bat.
pause
