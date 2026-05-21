# Comprehensive LucideIcons to Material Icons replacement script

$replacements = @{
    'LucideIcons.zap' = 'Icons.flash_on'
    'LucideIcons.share2' = 'Icons.share'
    'LucideIcons.pause' = 'Icons.pause'
    'LucideIcons.chevronUp' = 'Icons.keyboard_arrow_up'
    'LucideIcons.chevronDown' = 'Icons.keyboard_arrow_down'
    'LucideIcons.chevronRight' = 'Icons.chevron_right'
    'LucideIcons.chevronLeft' = 'Icons.chevron_left'
    'LucideIcons.truck' = 'Icons.local_shipping'
    'LucideIcons.scanLine' = 'Icons.qr_code_scanner'
    'LucideIcons.badgeCheck' = 'Icons.verified'
    'LucideIcons.undo2' = 'Icons.undo'
    'LucideIcons.mapPin' = 'Icons.location_on'
    'LucideIcons.phone' = 'Icons.phone'
    'LucideIcons.expand' = 'Icons.open_in_full'
    'LucideIcons.receipt' = 'Icons.receipt_long'
    'LucideIcons.rotateCw' = 'Icons.refresh'
    'LucideIcons.globe' = 'Icons.public'
    'LucideIcons.briefcase' = 'Icons.work'
    'LucideIcons.building2' = 'Icons.business'
    'LucideIcons.circle' = 'Icons.circle_outlined'
    'LucideIcons.shield' = 'Icons.shield'
    'LucideIcons.helpCircle' = 'Icons.help_outline'
    'LucideIcons.edit' = 'Icons.edit'
    'LucideIcons.logOut' = 'Icons.logout'
    'LucideIcons.trash2' = 'Icons.delete_outline'
}

$files = Get-ChildItem -Path "lib" -Filter "*.dart" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $modified = $false
    
    foreach ($old in $replacements.Keys) {
        $new = $replacements[$old]
        if ($content -match [regex]::Escape($old)) {
            $content = $content -replace [regex]::Escape($old), $new
            $modified = $true
            Write-Host "Replaced $old with $new in $($file.Name)" -ForegroundColor Green
        }
    }
    
    if ($modified) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
    }
}

Write-Host "`nReplacement complete!" -ForegroundColor Cyan
