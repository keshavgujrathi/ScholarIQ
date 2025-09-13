<#
.SYNOPSIS
    Sets up the development environment for ScholarIQ.
.DESCRIPTION
    This script creates a Python virtual environment and installs all required dependencies.
#>

param (
    [switch]$Dev = $false,
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"
$venvPath = "../.venv"
$requirementsFile = "../requirements.txt"
$devRequirementsFile = "../requirements-dev.txt"

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

Write-Host "=== Setting up ScholarIQ Development Environment ===" -ForegroundColor Cyan

# Check Python version
$pythonVersion = python --version
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8 or higher and try again."
    exit 1
}

$pythonVersion = $pythonVersion -replace "Python ", ""
$pythonMajorVersion = [int]($pythonVersion.Split(".")[0])
$pythonMinorVersion = [int]($pythonVersion.Split(".")[1])

if ($pythonMajorVersion -lt 3 -or ($pythonMajorVersion -eq 3 -and $pythonMinorVersion -lt 8)) {
    Write-Error "Python 3.8 or higher is required. Found Python $pythonVersion"
    exit 1
}

Write-Host "✓ Using Python $pythonVersion" -ForegroundColor Green

# Create virtual environment
if (Test-Path $venvPath) {
    if ($Force) {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Path $venvPath -Recurse -Force
    } else {
        Write-Host "Virtual environment already exists at $venvPath" -ForegroundColor Yellow
        Write-Host "Use -Force to recreate it" -ForegroundColor Yellow
        $useExisting = Read-Host "Use existing virtual environment? (y/n)"
        if ($useExisting -ne 'y') {
            exit 0
        }
    }
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath..." -ForegroundColor Cyan
    python -m venv $venvPath
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
    
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    $activateScript = Join-Path $venvPath "Scripts\activate"
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
. $activateScript

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to upgrade pip"
    exit 1
}

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Cyan
pip install -r $requirementsFile

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install requirements"
    exit 1
}

# Install dev requirements if requested
if ($Dev) {
    Write-Host "Installing development requirements..." -ForegroundColor Cyan
    pip install -r $devRequirementsFile
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install development requirements"
        exit 1
    }
}

# Install pre-commit hooks if available
if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
    Write-Host "Installing pre-commit hooks..." -ForegroundColor Cyan
    pre-commit install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Failed to install pre-commit hooks"
    } else {
        Write-Host "✓ Pre-commit hooks installed" -ForegroundColor Green
    }
}

# Create .env file if it doesn't exist
$envExampleFile = "../.env.example"
$envFile = "../.env"

if (-not (Test-Path $envFile) -and (Test-Path $envExampleFile)) {
    Write-Host "Creating .env file from example..." -ForegroundColor Cyan
    Copy-Item -Path $envExampleFile -Destination $envFile
    Write-Host "✓ .env file created. Please update it with your configuration." -ForegroundColor Green
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "  .\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "`nTo deactivate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "  deactivate" -ForegroundColor White

if (-not $isAdmin) {
    Write-Host "`nNote: Some operations may require administrator privileges." -ForegroundColor Yellow
}

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Update the .env file with your configuration" -ForegroundColor White
Write-Host "2. Run 'python -m scripts.manage_db reset' to initialize the database" -ForegroundColor White
Write-Host "3. Run 'uvicorn app.main:app --reload' to start the development server" -ForegroundColor White
