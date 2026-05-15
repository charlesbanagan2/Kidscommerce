# Read the file
$lines = Get-Content 'c:\Users\mnban\OneDrive\Desktop\kids\backend\app.py'

# Remove lines 19901-19965 (the duplicate endpoint)
$before = $lines[0..19900]
$after = @()

# Combine
$newContent = $before + $after

# Write back
$newContent | Set-Content 'c:\Users\mnban\OneDrive\Desktop\kids\backend\app.py' -Encoding UTF8

Write-Output "Removed duplicate forgot-password endpoint (lines 19901-19965)"
Write-Output "New total lines: $($newContent.Count)"
