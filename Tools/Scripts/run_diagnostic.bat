@echo off
echo Running PowerShell Diagnostic Tool...
echo This will create a log file on your desktop.
powershell.exe -ExecutionPolicy Bypass -Command "& {$logFile = \"$env:USERPROFILE\Desktop\powershell_diagnostic.log\"; \"Diagnostic run started at $(Get-Date)\" | Out-File -FilePath $logFile; \"PowerShell Version:\" | Out-File -FilePath $logFile -Append; $PSVersionTable | Out-String | Out-File -FilePath $logFile -Append; \"Execution Policy:\" | Out-File -FilePath $logFile -Append; Get-ExecutionPolicy -List | Out-File -FilePath $logFile -Append; \"Checking paths:\" | Out-File -FilePath $logFile -Append; $repoPath = \"D:\Jammin eats\WorkingCopy\"; $backupPath = \"D:\Jammin eats\Backups\"; \"Repository path ($repoPath) exists: $(Test-Path -Path $repoPath)\" | Out-File -FilePath $logFile -Append; \"Backup path ($backupPath) exists: $(Test-Path -Path $backupPath)\" | Out-File -FilePath $logFile -Append; \"Checking Git:\" | Out-File -FilePath $logFile -Append; try { $gitVersion = git --version; \"Git version: $gitVersion\" | Out-File -FilePath $logFile -Append } catch { \"Git command failed: $_\" | Out-File -FilePath $logFile -Append }; \"Diagnostic completed. Log saved to $logFile\"; Write-Host \"Diagnostic complete. Log file saved to: $logFile\" -ForegroundColor Green;}"
echo.
echo If successful, the diagnostic log file has been created on your desktop.
echo Check the file "powershell_diagnostic.log" for detailed information.
echo.
pause