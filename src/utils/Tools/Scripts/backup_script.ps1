# Enhanced backup script with progress bar
Write-Host "Starting backup process..." -ForegroundColor Green

$repoPath = "C:\Users\jerom\Jammin-Eats"
$backupBasePath = "D:\Backups\Jammin-Eats"

# Create timestamp and backup directory
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$backupPath = Join-Path -Path $backupBasePath -ChildPath $timestamp
New-Item -ItemType Directory -Path $backupPath -Force

# Count total files for progress tracking
Write-Host "Calculating files to backup..." -ForegroundColor Cyan
# Exclude Backups, .git, virtual env, build artifacts, and cache folders
$excludes = @("\\Backups\\", "\\.git\\", "\\.venv\\", "\\build\\", "\\dist\\", "\\__pycache__\\")
$filesToCopy = Get-ChildItem -Path $repoPath -Recurse -File |
    Where-Object {
        $include = $true
        foreach ($ex in $excludes) {
            if ($_.FullName -like "*${ex}*") { $include = $false; break }
        }
        $include
    }
$totalFiles = $filesToCopy.Count
Write-Host "Found $totalFiles files to backup" -ForegroundColor Cyan

# Initialize counters
$filesCopied = 0
$percentComplete = 0

# Create backup folder structure first
Get-ChildItem -Path $repoPath -Directory | Where-Object { $_.Name -ne "Backups" } | ForEach-Object {
    $destPath = Join-Path -Path $backupPath -ChildPath $_.Name
    if (!(Test-Path -Path $destPath)) {
        New-Item -ItemType Directory -Path $destPath -Force | Out-Null
    }
}

# Copy files with progress bar
foreach ($file in $filesToCopy) {
    # Skip files in Backups directory
    if ($file.FullName -like "*\Backups\*") { continue }
    
    # Calculate relative path and create destination path
    $relativePath = $file.FullName.Substring($repoPath.Length + 1)
    $destFile = Join-Path -Path $backupPath -ChildPath $relativePath
    $destDir = Split-Path -Path $destFile -Parent
    
    # Create destination directory if it doesn't exist
    if (!(Test-Path -Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    # Copy the file
    Copy-Item -Path $file.FullName -Destination $destFile -Force
    
    # Update progress
    $filesCopied++
    $percentComplete = [int](($filesCopied / $totalFiles) * 100)
    
    # Show progress bar
    Write-Progress -Activity "Backing up Jammin' Eats" -Status "$percentComplete% Complete" -PercentComplete $percentComplete -CurrentOperation "Copying: $relativePath" -Id 1
}

# Complete the progress bar
Write-Progress -Activity "Backing up Jammin' Eats" -Completed -Id 1

Write-Host "Backup complete! $filesCopied files copied to $backupPath" -ForegroundColor Green