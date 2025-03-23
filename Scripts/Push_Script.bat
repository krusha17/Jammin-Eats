cd "D:\Jammin eats\WorkingCopy"

REM echo Pulling latest changes from GitHub...
REM git pull origin main

echo Adding all changes...
git add .

echo Committing changes...
git commit -m "Added Push and DB schema to scripts, cleaned up folders and files :)"

echo Pushing to GitHub...
git push origin main

echo ✅ Push complete!

