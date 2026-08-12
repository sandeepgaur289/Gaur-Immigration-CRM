@echo off
setlocal
set "CRM_HOME=%LOCALAPPDATA%\GaurCRM_v2"
echo This repairs ONLY the Python runtime. It does NOT delete CRM database or uploads.
if exist "%CRM_HOME%\venv" rmdir /s /q "%CRM_HOME%\venv"
if exist "%CRM_HOME%\requirements_v2_0_1.ok" del /q "%CRM_HOME%\requirements_v2_0_1.ok"
echo Runtime reset complete. Now run START_CRM.bat again.
pause
