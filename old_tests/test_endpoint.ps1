$loginResponse = Invoke-WebRequest -Uri "http://localhost:5000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"carttest123@example.com","password":"Test@12345"}'

$token = ($loginResponse.Content | ConvertFrom-Json).tokens.access_token
Write-Host "Token: $token"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host "`nTesting GET /api/v1/buyer/cart:"
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/v1/buyer/cart" `
  -Method GET `
  -Headers $headers

Write-Host "Status: $($response.StatusCode)"
Write-Host "Response: $($response.Content)"
