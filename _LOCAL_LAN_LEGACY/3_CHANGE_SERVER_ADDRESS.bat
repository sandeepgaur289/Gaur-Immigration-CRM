@echo off
set "CFG=%LOCALAPPDATA%\GaurCRM\central_server_url.txt"
if exist "%CFG%" del /q "%CFG%"
echo Saved server address removed.
echo Run 2_CLIENT_CONNECT.bat and enter the new server URL.
pause
