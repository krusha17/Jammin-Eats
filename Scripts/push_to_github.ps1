# Navigate to your project folder
Set-Location "D:\Jammin eats\WorkingCopy"

# Step 1: Stage all changes
Write-Host "Adding all changes..." -ForegroundColor Yellow
git add .

# Step 2: Commit your changes
# 👉 Change the commit message below!
$commitMsg = Read-Host "Enter your commit message"
git commit -m "$commitMsg"


# Step 3: Push changes to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Green
git push origin main

Write-Host "✅ Push complete!" -ForegroundColor Green
