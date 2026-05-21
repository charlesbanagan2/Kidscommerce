@echo off
echo Reverting to last working state...
git reset --hard c72657d
git push origin main --force
echo Done! Website should be back to working state.
pause
