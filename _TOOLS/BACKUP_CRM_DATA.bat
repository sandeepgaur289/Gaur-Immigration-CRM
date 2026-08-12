@echo off
setlocal
cd /d "%~dp0"
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set dt=%%I
if not defined dt set dt=backup
set stamp=%dt:~0,8%_%dt:~8,6%
set dest=BACKUP_%stamp%
mkdir "%dest%" >nul 2>&1
if exist mini_crm.db copy /Y mini_crm.db "%dest%\mini_crm.db" >nul
if exist uploads xcopy uploads "%dest%\uploads\" /E /I /Y >nul
if exist "%dest%\mini_crm.db" (
 echo Backup created: %dest%
) else (
 echo No mini_crm.db found yet. Start the CRM once first.
)
pause
