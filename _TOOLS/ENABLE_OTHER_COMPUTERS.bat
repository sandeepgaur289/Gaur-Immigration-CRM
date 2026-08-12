@echo off
cd /d "%~dp0"
title GAUR PORTAL - Enable Network Access
echo Windows will ask for Administrator permission.
echo Click YES to allow other office computers to connect.
echo.
powershell -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File ""%~dp0enable_firewall.ps1""'"
pause
