@echo off
cd /d "%~dp0"
echo Run this ONCE on the MAIN SERVER computer.
echo Windows will ask for Administrator permission.
powershell -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File ""%~dp0enable_central_firewall.ps1""'"
pause
