# Setup script for production Tailwind CSS

Write-Host "Setting up Tailwind CSS for production..." -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is installed
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js is not installed!" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After installing Node.js, run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Node.js found: $(node --version)" -ForegroundColor Green

# Check if npm is installed
if (!(Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: npm is not installed!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ npm found: $(npm --version)" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing Tailwind CSS dependencies..." -ForegroundColor Cyan
npm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Build CSS
Write-Host "Building production CSS..." -ForegroundColor Cyan
npm run build:css

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to build CSS!" -ForegroundColor Red
    exit 1
}

Write-Host "✓ CSS built successfully" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the dashboard:" -ForegroundColor Cyan
Write-Host "  .venv\Scripts\python.exe dashboard.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "To rebuild CSS after changes:" -ForegroundColor Cyan
Write-Host "  npm run build:css" -ForegroundColor Yellow
Write-Host ""
Write-Host "To watch for changes (auto-rebuild):" -ForegroundColor Cyan
Write-Host "  npm run watch:css" -ForegroundColor Yellow
Write-Host ""
