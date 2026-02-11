Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🔧 FIX MOTOR/PYMONGO COMPATIBILITY                   ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Navigate to project root
Set-Location "d:\Projects\Personal\New folder\omnisales-ai"

Write-Host "Step 1: Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

Write-Host "✅ Virtual environment activated`n" -ForegroundColor Green

Write-Host "Step 2: Uninstalling incompatible packages..." -ForegroundColor Yellow
pip uninstall motor pymongo -y

Write-Host "`nStep 3: Installing compatible versions..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt

Write-Host "`n╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ INSTALLATION COMPLETE!                    ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Now you can run:" -ForegroundColor Cyan
Write-Host "  python load_products.py" -ForegroundColor Yellow
Write-Host "  uvicorn app.main:app --reload`n" -ForegroundColor Yellow
