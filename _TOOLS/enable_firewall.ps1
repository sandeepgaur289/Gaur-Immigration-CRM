New-NetFirewallRule -DisplayName "GAUR CRM Port 5050" -Direction Inbound -Protocol TCP -LocalPort 5050 -Action Allow -Profile Private -ErrorAction SilentlyContinue
Write-Host ""
Write-Host "Network access enabled for GAUR CRM on port 5050." -ForegroundColor Green
Write-Host "You can close this window."
Read-Host "Press Enter"
