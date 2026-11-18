# Firestore Setup Script
Write-Host "=== Firebase Firestore Setup ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking firebase-admin..." -ForegroundColor Yellow
$check = python -c "import firebase_admin; print('OK')" 2>&1
if ($check -notlike "*OK*") {
    python -m pip install firebase-admin
}
Write-Host "firebase-admin installed" -ForegroundColor Green
Write-Host ""

Write-Host "=== Step 1: Get Service Account Key ===" -ForegroundColor Cyan
Write-Host "1. Open: https://console.firebase.google.com/project/nova-ticket-app/settings/serviceaccounts/adminsdk"
Write-Host "2. Click Generate new private key"
Write-Host "3. Save as: service-account.json in repo root"
Write-Host ""
Write-Host "Press Enter when ready..." -ForegroundColor Yellow
Read-Host

$saPath = Join-Path (Join-Path $PSScriptRoot "..") "service-account.json"
if (-not (Test-Path $saPath)) {
    Write-Host "service-account.json not found at $saPath" -ForegroundColor Red
    exit 1
}
Write-Host "Found service-account.json" -ForegroundColor Green
Write-Host ""

Write-Host "=== Step 2: Set Environment Variable ===" -ForegroundColor Cyan
$env:GOOGLE_APPLICATION_CREDENTIALS = $saPath
Write-Host "Set GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Green
Write-Host ""

Write-Host "=== Step 3: Migrate Data ===" -ForegroundColor Cyan
python (Join-Path $PSScriptRoot "migrate_to_firestore.py")

if ($LASTEXITCODE -eq 0) {
    Write-Host "Migration complete!" -ForegroundColor Green
    Write-Host ""
    
    $env:FIRESTORE_ENABLED = "1"
    
    $envPath = Join-Path (Join-Path $PSScriptRoot "..") ".env"
    if (Test-Path $envPath) {
        $content = Get-Content $envPath -Raw
        if ($content -notmatch "FIRESTORE_ENABLED") {
            Add-Content $envPath "`n# Firestore`nFIRESTORE_ENABLED=1"
            Write-Host "Added to .env" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "=== Setup Complete! ===" -ForegroundColor Green
    Write-Host "Data is now persistent in Firestore" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To test:" -ForegroundColor Yellow
    Write-Host "  Set env vars then run dashboard.py"
    Write-Host ""
} else {
    Write-Host "Migration failed" -ForegroundColor Red
}
