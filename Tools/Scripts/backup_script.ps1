# Simple version of the backup script
Write-Host "Starting backup process..." -ForegroundColor Green

$repoPath = "D:\Jammin eats"
$backupBasePath = "D:\Jammin eats\Backups"

# Create timestamp and backup directory
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$backupPath = Join-Path -Path $backupBasePath -ChildPath $timestamp
New-Item -ItemType Directory -Path $backupPath -Force

# Copy files
Copy-Item -Path "$repoPath\*" -Destination $backupPath -Recurse -Force

Write-Host "Backup complete!" -ForegroundColor Green