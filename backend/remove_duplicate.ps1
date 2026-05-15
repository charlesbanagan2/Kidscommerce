# Read the file
$lines = Get-Content 'c:\Users\mnban\OneDrive\Desktop\kids\backend\app.py'

# Remove lines 19966-20040 (the duplicate endpoint)
$before = $lines[0..19965]
# Line 20040 is the last line, so we're done
$after = @()

# Combine
$newContent = $before + $after

# Write back
$newContent | Set-Content 'c:\Users\mnban\OneDrive\Desktop\kids\backend\app.py' -Encoding UTF8

Write-Output "Removed duplicate reset-password endpoint (lines 19966-20040)"
Write-Output "New total lines: $($newContent.Count)"
