<#
.SYNOPSIS
    A build and utility script for the Project Dashboard application,
    designed to be the PowerShell equivalent of the project's Makefile.
.DESCRIPTION
    This script provides functions to automate common development tasks such
    as setting up the virtual environment, installing dependencies, running
    tests, and cleaning up the project directory.

    To see available commands: Get-Help .\build.ps1 -Full
.EXAMPLE
    .\build.ps1 -Install
    Installs dependencies and sets up the virtual environment.
.EXAMPLE
    .\build.ps1 -Test
    Runs the pytest test suite.
.EXAMPLE
    .\build.ps1 -Clean
    Removes build artifacts and cache directories.
#>
[CmdletBinding()]
param (
    [Switch]$Install,
    [Switch]$Test,
    [Switch]$Clean
)

# --- Script Configuration ---
$VenvName = ".venv"
$VenvPath = Join-Path -Path $PSScriptRoot -ChildPath $VenvName
$PythonPath = Join-Path -Path $VenvPath -ChildPath "Scripts\python.exe"
$RequirementsFile = Join-Path -Path $PSScriptRoot -ChildPath "requirements.txt"

# --- Helper Functions ---
function Invoke-Install {
    Write-Host ">>> Setting up environment..."
    if (-not (Test-Path -Path $VenvPath)) {
        Write-Host ">>> Creating virtual environment..."
        python3 -m venv $VenvName
    }

    Write-Host ">>> Installing dependencies from requirements.txt..."
    & $PythonPath -m pip install -r $RequirementsFile
    Write-Host "Installation complete."
}

function Invoke-Test {
    Write-Host ">>> Running tests..."
    if (-not (Test-Path -Path $PythonPath)) {
        Write-Error "Virtual environment not found. Please run '.\build.ps1 -Install' first."
        return
    }
    & $PythonPath -m pytest
}

function Invoke-Clean {
    Write-Host ">>> Cleaning up..."
    Get-ChildItem -Path $PSScriptRoot -Recurse -Include "__pycache__", ".pytest_cache", ".mypy_cache" -Directory | Remove-Item -Recurse -Force
    Write-Host "Cleanup complete."
}


# --- Main Execution Logic ---
if ($Install) {
    Invoke-Install
}
elseif ($Test) {
    Invoke-Test
}
elseif ($Clean) {
    Invoke-Clean
}
else {
    # Default action: Show help
    Get-Help -Name $MyInvocation.MyCommand.Path -Full
}