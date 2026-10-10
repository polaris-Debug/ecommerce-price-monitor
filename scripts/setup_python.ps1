param(
    [switch]$Production,
    [switch]$Playwright
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

$pythonExe = "python"
$pythonArgs = @()
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = "py"
    $pythonArgs = @("-3.11")
} else {
    $pythonExe = "python"
}

$versionOutput = & $pythonExe @pythonArgs --version 2>&1
if ($LASTEXITCODE -ne 0 -or $versionOutput -notmatch "Python 3\.11") {
    throw "Python 3.11 is required. Install it from https://www.python.org/downloads/ and rerun this script."
}

& $pythonExe @pythonArgs -m venv --upgrade (Join-Path $repoRoot ".venv")
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create the .venv virtual environment."
}

$pythonInterpreter = Join-Path $repoRoot ".venv\Scripts\python.exe"
$requirements = if ($Production) { "requirements.txt" } else { "requirements-dev.txt" }
$requirementsPath = Join-Path $repoRoot $requirements

$env:PIP_NO_INDEX = $null
if ($env:HTTP_PROXY -eq "http://127.0.0.1:9") { $env:HTTP_PROXY = $null }
if ($env:HTTPS_PROXY -eq "http://127.0.0.1:9") { $env:HTTPS_PROXY = $null }
if ($env:ALL_PROXY -eq "http://127.0.0.1:9") { $env:ALL_PROXY = $null }

& $pythonInterpreter -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip."
}

& $pythonInterpreter -m pip install -r $requirementsPath
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install Python dependencies."
}

if ($Playwright) {
    & $pythonInterpreter -m pip install -r (Join-Path $repoRoot "requirements-playwright.txt")
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install Playwright dependencies."
    }
}

if (-not (Test-Path (Join-Path $repoRoot ".env"))) {
    Copy-Item (Join-Path $repoRoot ".env.example") (Join-Path $repoRoot ".env")
}

Write-Host "Python environment ready. Activate it with: .\.venv\Scripts\Activate.ps1"
