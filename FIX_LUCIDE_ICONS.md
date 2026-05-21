# Fix Lucide Icons Issue - Quick Solution

## Problem
lucide_icons 0.257.0 is incompatible with current Flutter SDK (tries to extend final class IconData)

## Quick Solution Options

### Option 1: Use Material Icons (Recommended - Already started)
We already removed lucide_icons from buyer_home_screen.dart. Need to do the same for all other files.

**Files that need lucide_icons removed:**
1. wishlist_screen.dart
2. product_chat_screen.dart  
3. store_detail_screen.dart
4. rating_screen.dart
5. return_refund_screen.dart
6. product_detail_screen.dart
7. order_detail.dart
8. orders_screen.dart
9. notification_screen.dart
10. profile_screen.dart
11. submit_review_screen.dart
12. product_card_widget.dart
13. modern_snackbar.dart

### Option 2: Downgrade Flutter SDK (Not Recommended)
Downgrade to an older Flutter SDK that doesn't have IconData as final.

### Option 3: Use Alternative Icon Package
Use `flutter_icons` or `font_awesome_flutter` instead.

## Recommended Action: Bulk Replace Script

Run this PowerShell script in mobile_app directory:

```powershell
# Icon mapping
$iconMap = @{
    'LucideIcons.shoppingCart' = 'Icons.shopping_cart_outlined'
    'LucideIcons.bell' = 'Icons.notifications_outlined'
    'LucideIcons.search' = 'Icons.search'
    'LucideIcons.trendingUp' = 'Icons.trending_up'
    'LucideIcons.zap' = 'Icons.flash_on'
    'LucideIcons.star' = 'Icons.star'
    'LucideIcons.chevronRight' = 'Icons.chevron_right'
    'LucideIcons.image' = 'Icons.image'
    'LucideIcons.package' = 'Icons.inventory_2_outlined'
    'LucideIcons.heart' = 'Icons.favorite'
    'LucideIcons.heartOff' = 'Icons.favorite_border'
    'LucideIcons.shoppingBag' = 'Icons.shopping_bag_outlined'
    'LucideIcons.arrowLeft' = 'Icons.arrow_back'
    'LucideIcons.store' = 'Icons.store'
    'LucideIcons.messageCircle' = 'Icons.chat_bubble_outline'
    'LucideIcons.user' = 'Icons.person'
    'LucideIcons.send' = 'Icons.send'
    'LucideIcons.x' = 'Icons.close'
    'LucideIcons.users' = 'Icons.people'
    'LucideIcons.imageOff' = 'Icons.broken_image'
    'LucideIcons.checkCircle' = 'Icons.check_circle'
    'LucideIcons.alertCircle' = 'Icons.error'
    'LucideIcons.bike' = 'Icons.pedal_bike'
    'LucideIcons.checkCircle2' = 'Icons.check_circle_outline'
    'LucideIcons.clipboardList' = 'Icons.assignment'
    'LucideIcons.layoutGrid' = 'Icons.grid_view'
    'LucideIcons.tag' = 'Icons.local_offer'
    'LucideIcons.messageSquare' = 'Icons.message'
    'LucideIcons.camera' = 'Icons.camera_alt'
    'LucideIcons.play' = 'Icons.play_arrow'
    'LucideIcons.video' = 'Icons.videocam'
    'LucideIcons.shieldCheck' = 'Icons.verified_user'
    'LucideIcons.check' = 'Icons.check'
    'LucideIcons.packageSearch' = 'Icons.search'
    'LucideIcons.minus' = 'Icons.remove'
    'LucideIcons.plus' = 'Icons.add'
    'LucideIcons.info' = 'Icons.info'
    'LucideIcons.fileText' = 'Icons.description'
    'LucideIcons.imagePlus' = 'Icons.add_photo_alternate'
    'LucideIcons.creditCard' = 'Icons.credit_card'
    'LucideIcons.wallet' = 'Icons.account_balance_wallet'
    'LucideIcons.refreshCcw' = 'Icons.refresh'
    'LucideIcons.alertTriangle' = 'Icons.warning'
    'LucideIcons.home' = 'Icons.home'
    'LucideIcons.hash' = 'Icons.tag'
    'LucideIcons.clock' = 'Icons.access_time'
    'LucideIcons.calendar' = 'Icons.calendar_today'
    'LucideIcons.arrowRight' = 'Icons.arrow_forward'
}

# Get all dart files
$files = Get-ChildItem -Path "lib" -Filter "*.dart" -Recurse

foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw
    $modified = $false
    
    # Remove lucide_icons import
    if ($content -match "import 'package:lucide_icons/lucide_icons.dart';") {
        $content = $content -replace "import 'package:lucide_icons/lucide_icons.dart';", ""
        $modified = $true
    }
    
    # Replace all icon references
    foreach ($key in $iconMap.Keys) {
        if ($content -match [regex]::Escape($key)) {
            $content = $content -replace [regex]::Escape($key), $iconMap[$key]
            $modified = $true
        }
    }
    
    if ($modified) {
        Set-Content -Path $file.FullName -Value $content
        Write-Host "Updated: $($file.Name)"
    }
}

Write-Host "Done! Run 'flutter pub get' and then 'flutter run'"
```

Save this as `fix_icons.ps1` and run it.

## Manual Quick Fix (If script doesn't work)

Just temporarily disable the problematic screens by commenting them out in routes, then fix them one by one later.

For now, to get the app running:
1. Keep buyer_home_screen.dart (already fixed)
2. Comment out imports of other screens that use lucide_icons
3. Build and test the main flow
4. Fix other screens gradually

## Status
- ✅ buyer_home_screen.dart - Fixed
- ⚠️ 13 other files - Need fixing
