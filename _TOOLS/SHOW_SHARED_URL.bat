@echo off
title GAUR PORTAL - Shared URL
echo.
echo Use one of these URLs on OTHER computers:
echo.
powershell -NoProfile -Command "Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike '127.*' -and $_.PrefixOrigin -ne 'WellKnown'} | ForEach-Object { Write-Host ('http://' + $_.IPAddress + ':5050') -ForegroundColor Cyan }"
echo.
echo IMPORTANT: 127.0.0.1 is ONLY for this computer.
pause
