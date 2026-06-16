# AI Scam Detector - Quick Start Script for PowerShell

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   AI Scam Detector - Starting Application" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Run Flask app
Write-Host "Starting Flask app..." -ForegroundColor Green
Write-Host ""
python app.py

Read-Host "Press Enter to close"
