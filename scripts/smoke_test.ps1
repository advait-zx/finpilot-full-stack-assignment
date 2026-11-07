$ErrorActionPreference = "Stop"
$api = "http://localhost:8000"
Write-Host "Checking health..."
$health = Invoke-RestMethod "$api/health"
$health | ConvertTo-Json -Depth 5

Write-Host "Logging in as viewer..."
$body = @{ username = "viewer"; password = "viewer123" } | ConvertTo-Json
$login = Invoke-RestMethod -Method Post -Uri "$api/api/v1/auth/login" -ContentType "application/json" -Body $body
if (-not $login.access_token) { throw "Login did not return an access token" }
Write-Host "Login OK. Role: $($login.role)"

Write-Host "Smoke test passed."
