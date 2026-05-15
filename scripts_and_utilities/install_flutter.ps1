# Flutter and Dart Installation Script for Windows
# Run this script as Administrator in PowerShell

Write-Host "=== Flutter and Dart Installation Script ===" -ForegroundColor Green
Write-Host "This script will install Flutter SDK and configure your environment" -ForegroundColor Yellow
Write-Host ""

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Please run this script as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# Step 1: Download Flutter SDK
Write-Host "Step 1: Downloading Flutter SDK..." -ForegroundColor Cyan
$flutterUrl = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.19.6-stable.zip"
$flutterZip = "C:\flutter.zip"
$flutterDir = "C:\flutter"

try {
    # Create Flutter directory if it doesn't exist
    if (!(Test-Path $flutterDir)) {
        New-Item -ItemType Directory -Path $flutterDir -Force
        Write-Host "Created Flutter directory: $flutterDir" -ForegroundColor Green
    }
    
    # Download Flutter
    Write-Host "Downloading Flutter SDK (this may take a few minutes)..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $flutterUrl -OutFile $flutterZip -UseBasicParsing
    Write-Host "Flutter SDK downloaded successfully!" -ForegroundColor Green
}
catch {
    Write-Host "Failed to download Flutter SDK: $_" -ForegroundColor Red
    Write-Host "Please download manually from: https://flutter.dev/docs/get-started/install/windows" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# Step 2: Extract Flutter SDK
Write-Host "Step 2: Extracting Flutter SDK..." -ForegroundColor Cyan
try {
    Expand-Archive -Path $flutterZip -Destination "C:\" -Force
    Write-Host "Flutter SDK extracted successfully!" -ForegroundColor Green
    
    # Clean up zip file
    Remove-Item $flutterZip -Force
}
catch {
    Write-Host "Failed to extract Flutter SDK: $_" -ForegroundColor Red
    Write-Host "Please extract manually to C:\flutter" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit
}

# Step 3: Add Flutter to PATH
Write-Host "Step 3: Adding Flutter to PATH..." -ForegroundColor Cyan
try {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*C:\flutter\bin*") {
        $newPath = $currentPath + ";C:\flutter\bin"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Host "Flutter added to PATH successfully!" -ForegroundColor Green
    } else {
        Write-Host "Flutter already in PATH" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Failed to add Flutter to PATH: $_" -ForegroundColor Red
    Write-Host "Please add C:\flutter\bin to PATH manually" -ForegroundColor Yellow
}

# Step 4: Verify Flutter Installation
Write-Host "Step 4: Verifying Flutter installation..." -ForegroundColor Cyan
try {
    # Refresh environment variables
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    
    # Test Flutter command
    $flutterVersion = & flutter --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Flutter installation verified!" -ForegroundColor Green
        Write-Host $flutterVersion -ForegroundColor White
    } else {
        Write-Host "Flutter command not working yet. Please restart PowerShell and run 'flutter --version'" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Flutter verification failed. Please restart PowerShell and try again." -ForegroundColor Yellow
}

# Step 5: Run Flutter Doctor
Write-Host "Step 5: Running Flutter Doctor..." -ForegroundColor Cyan
Write-Host "This will check what components are needed..." -ForegroundColor Yellow

try {
    & flutter doctor
}
catch {
    Write-Host "Flutter doctor failed. Please run 'flutter doctor' manually after setup." -ForegroundColor Yellow
}

# Step 6: Install Android Studio (Manual Step)
Write-Host "Step 6: Android Studio Installation" -ForegroundColor Cyan
Write-Host "Please complete these manual steps:" -ForegroundColor Yellow
Write-Host "1. Download Android Studio from: https://developer.android.com/studio" -ForegroundColor White
Write-Host "2. Install Android Studio with default settings" -ForegroundColor White
Write-Host "3. Open Android Studio > File > Settings > Plugins" -ForegroundColor White
Write-Host "4. Search for 'Flutter' and install the plugin" -ForegroundColor White
Write-Host "5. Restart Android Studio" -ForegroundColor White
Write-Host "6. Create an Android Virtual Device (AVD)" -ForegroundColor White
Write-Host "7. Run 'flutter doctor --android-licenses' and accept all licenses" -ForegroundColor White

# Step 7: Test Your App
Write-Host "Step 7: Ready to run your app!" -ForegroundColor Cyan
Write-Host "Once Android Studio is set up, run these commands:" -ForegroundColor Yellow
Write-Host "cd mobile_app" -ForegroundColor White
Write-Host "flutter pub get" -ForegroundColor White
Write-Host "flutter run" -ForegroundColor White

Write-Host ""
Write-Host "=== Installation Complete! ===" -ForegroundColor Green
Write-Host "Please restart PowerShell to use Flutter commands" -ForegroundColor Yellow
Write-Host "Then follow the Android Studio setup steps above" -ForegroundColor Yellow
Read-Host "Press Enter to exit"
