@echo off
echo Fixing remaining LucideIcons references...

powershell -Command "(Get-Content 'lib\screens\buyer_app\notification_screen.dart') -replace 'LucideIcons\.chevronLeft', 'Icons.chevron_left' -replace 'LucideIcons\.settings', 'Icons.settings' -replace 'LucideIcons\.inbox', 'Icons.inbox' -replace 'LucideIcons\.trash2', 'Icons.delete_outline' -replace 'LucideIcons\.shield', 'Icons.shield' | Set-Content 'lib\screens\buyer_app\notification_screen.dart'"

powershell -Command "(Get-Content 'lib\screens\buyer_app\orders_screen.dart') -replace 'LucideIcons\.inbox', 'Icons.inbox' -replace 'LucideIcons\.chevronRight', 'Icons.chevron_right' -replace 'LucideIcons\.truck', 'Icons.local_shipping' -replace 'LucideIcons\.undo2', 'Icons.undo' -replace 'LucideIcons\.helpCircle', 'Icons.help_outline' | Set-Content 'lib\screens\buyer_app\orders_screen.dart'"

echo Done!
pause
