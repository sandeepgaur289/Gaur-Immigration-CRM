$rule = Get-NetFirewallRule -DisplayName "GAUR CRM Central Server 5050" -ErrorAction SilentlyContinue
if (-not $rule) {
    New-NetFirewallRule -DisplayName "GAUR CRM Central Server 5050" -Direction Inbound -Protocol TCP -LocalPort 5050 -Action Allow -Profile Private
}
Write-Host ""
Write-Host "GAUR CRM network access enabled on TCP port 5050." -ForegroundColor Green
Read-Host "Press Enter"
