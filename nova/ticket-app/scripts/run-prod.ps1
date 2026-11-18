param(
    [int]$Port = 5000,
    [string]$BindHost = "0.0.0.0"
)

Write-Host "Starting dashboard with waitress on $($BindHost):$Port..." -ForegroundColor Green

# Ensure we're in the repo root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

# Detect venv python
$VenvPython = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (Test-Path $VenvPython) {
    $Python = $VenvPython
} else {
    $Python = "python"
}

# Ensure dependencies installed
& $Python -m pip install -r requirements.txt | Write-Host

# Run waitress server (prefer venv exe)
$WaitressExe = Join-Path $RepoRoot ".venv\Scripts\waitress-serve.exe"
if (Test-Path $WaitressExe) {
    & $WaitressExe --host $BindHost --port $Port dashboard:app
} else {
    # Fallback to global PATH
    waitress-serve --host $BindHost --port $Port dashboard:app
}
