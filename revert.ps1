# Revert to last working state
Write-Host "Reverting to last working commit..." -ForegroundColor Yellow

# Reset to commit before image changes
git reset --hard c72657d

# Force push to GitHub
git push origin main --force

Write-Host "Done! Website reverted to working state." -ForegroundColor Green
Write-Host "Wait 5-10 minutes for Render to deploy." -ForegroundColor Cyan
