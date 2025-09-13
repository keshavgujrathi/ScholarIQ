<#
.SYNOPSIS
    Starts the ScholarIQ development server.
.DESCRIPTION
    This script starts the Uvicorn development server with hot-reload enabled.
    It also ensures the virtual environment is activated and dependencies are installed.
#>

param (
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8000,
    [int]$Workers = 1,
    [switch]$NoReload = $false,
    [switch]$Debug = $false
)

$ErrorActionPreference = "Stop"
$venvPath = ".\.venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

# Check if virtual environment exists
if (-not (Test-Path $activateScript)) {
    Write-Host "Virtual environment not found at $venvPath" -ForegroundColor Yellow
    Write-Host "Running setup script..." -ForegroundColor Cyan
    
    # Run the setup script
    $setupScript = Join-Path $PSScriptRoot "setup_environment.ps1"
    if (-not (Test-Path $setupScript)) {
        Write-Error "Setup script not found at $setupScript"
        exit 1
    }
    
    & $setupScript -Dev
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to set up the development environment"
        exit 1
    }
    
    # Reactivate the virtual environment
    . $activateScript
}

# Activate virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    . $activateScript
}

# Install dependencies if needed
$missingDeps = pip freeze | Select-String -Pattern "^uvicorn=" -Quiet -NotMatch
if ($missingDeps) {
    Write-Host "Installing missing dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies"
        exit 1
    }
}

# Set environment variables
$env:APP_ENV = "development"
if ($Debug) {
    $env:DEBUG = "true"
    $env:LOG_LEVEL = "DEBUG"
} else {
    $env:DEBUG = "false"
    $env:LOG_LEVEL = "INFO"
}

# Build Uvicorn command
$uvicornArgs = @(
    "app.main:app",
    "--host", $HostAddress,
    "--port", $Port.ToString(),
    "--workers", $Workers.ToString()
)

if (-not $NoReload) {
    $uvicornArgs += "--reload"
}

if ($Debug) {
    $uvicornArgs += "--log-level debug"
}

# Start the server
Write-Host "Starting development server on http://${HostAddress}:${Port}" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Cyan

uvicorn @uvicornArgs

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start the development server"
    exit 1
}
