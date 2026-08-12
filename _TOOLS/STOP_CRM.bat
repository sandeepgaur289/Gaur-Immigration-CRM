@echo off
title GAUR PORTAL - Stop
echo Closing GAUR PORTAL server...
taskkill /FI "WINDOWTITLE eq GAUR CRM SERVER*" /T /F >nul 2>&1
echo Done.
timeout /t 2 /nobreak >nul
