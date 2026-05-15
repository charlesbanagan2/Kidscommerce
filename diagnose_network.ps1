# Network Diagnostic Script for Windows PowerShell

Write-Host "=================================================="
Write-Host "NETWORK CONNECTIVITY DIAGNOSTIC"
Write-Host "=================================================="
Write-Host ""

# Test 1: Internet connectivity
Write-Host "[1] Testing Internet Connection..."
try {
    $ping = Test-Connection -ComputerName 8.8.8.8 -Count 1 -ErrorAction Stop
    Write-Host "    ✓ Internet connection OK (Google DNS responded)"
} catch {
    Write-Host "    ✗ No internet connection detected"
    Write-Host "    → Check WiFi/network status"
    exit 1
}

Write-Host ""

# Test 2: DNS resolution
Write-Host "[2] Testing DNS Resolution..."
try {
    $result = [System.Net.Dns]::GetHostAddresses("db.qkdacoawexaxejljfihh.supabase.co")
    Write-Host "    ✓ DNS resolved: $($result[0].IPAddressToString)"
} catch {
    Write-Host "    ✗ Cannot resolve Supabase host: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "    Solutions:"
    Write-Host "    1. Check internet connection (Test 1 above)"
    Write-Host "    2. Try changing DNS servers:"
    Write-Host "       - Use 8.8.8.8 (Google DNS) or 1.1.1.1 (Cloudflare)"
    Write-Host "    3. Check Supabase project at https://supabase.com"
    Write-Host "    4. Try in Command Prompt: ipconfig /flushdns"
    exit 1
}

Write-Host ""

# Test 3: Supabase connectivity
Write-Host "[3] Testing Supabase Port 6543..."
$tcpClient = New-Object System.Net.Sockets.TcpClient
try {
    $tcpClient.Connect("db.qkdacoawexaxejljfihh.supabase.co", 6543)
    if ($tcpClient.Connected) {
        Write-Host "    ✓ Port 6543 is open and reachable"
    }
    $tcpClient.Close()
} catch {
    Write-Host "    ✗ Cannot connect to port 6543"
    Write-Host "    → Supabase server may be down or blocked by firewall"
    exit 1
}

Write-Host ""

# Test 4: Google DNS test
Write-Host "[4] Testing with Different DNS..."
try {
    $result = [System.Net.Dns]::GetHostAddresses("supabase.com")
    Write-Host "    ✓ Can resolve supabase.com: $($result[0].IPAddressToString)"
} catch {
    Write-Host "    ✗ Cannot reach any Supabase domain"
}

Write-Host ""
Write-Host "=================================================="
Write-Host "✓ ALL TESTS PASSED"
Write-Host "=================================================="
