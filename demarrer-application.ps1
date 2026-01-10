# Script de démarrage pour l'application Kaïros
# PowerShell script pour démarrer MongoDB, Backend et Frontend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage de l'application Kaïros" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1 : Vérifier MongoDB
Write-Host "[1/4] Vérification de MongoDB..." -ForegroundColor Yellow
$mongoRunning = docker ps --filter "name=eduverse-mongodb" --format "{{.Names}}" 2>$null
if ($mongoRunning -eq "eduverse-mongodb") {
    Write-Host "✓ MongoDB est déjà démarré" -ForegroundColor Green
} else {
    Write-Host "⚠ MongoDB n'est pas démarré" -ForegroundColor Yellow
    Write-Host "  Démarrage de MongoDB..." -ForegroundColor Yellow
    docker start eduverse-mongodb 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Création du conteneur MongoDB..." -ForegroundColor Yellow
        docker run -d --name eduverse-mongodb -p 27017:27017 -v mongodb_data:/data/db mongo:7.0
        Start-Sleep -Seconds 5
    }
    Write-Host "✓ MongoDB démarré" -ForegroundColor Green
}

Write-Host ""

# Étape 2 : Démarrer le Backend
Write-Host "[2/4] Démarrage du Backend..." -ForegroundColor Yellow
$backendPath = Join-Path $PSScriptRoot "backend"
if (Test-Path $backendPath) {
    Write-Host "  Dossier backend trouvé" -ForegroundColor Green
    
    # Vérifier l'environnement virtuel
    $venvPath = Join-Path $backendPath "venv"
    if (-not (Test-Path $venvPath)) {
        Write-Host "  Création de l'environnement virtuel..." -ForegroundColor Yellow
        Set-Location $backendPath
        python -m venv venv
    }
    
    # Activer l'environnement virtuel et démarrer
    Write-Host "  Démarrage du serveur backend sur http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  (Ouvrez un nouveau terminal pour continuer)" -ForegroundColor Yellow
    
    $backendScript = @"
cd `"$backendPath`"
call venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
"@
    
    $backendScriptPath = Join-Path $env:TEMP "start-backend.bat"
    $backendScript | Out-File -FilePath $backendScriptPath -Encoding ASCII
    
    Start-Process cmd.exe -ArgumentList "/c", $backendScriptPath
} else {
    Write-Host "✗ Dossier backend non trouvé" -ForegroundColor Red
}

Write-Host ""

# Étape 3 : Démarrer le Frontend
Write-Host "[3/4] Démarrage du Frontend..." -ForegroundColor Yellow
$frontendPath = Join-Path $PSScriptRoot "frontend"
if (Test-Path $frontendPath) {
    Write-Host "  Dossier frontend trouvé" -ForegroundColor Green
    
    # Vérifier node_modules
    $nodeModulesPath = Join-Path $frontendPath "node_modules"
    if (-not (Test-Path $nodeModulesPath)) {
        Write-Host "  Installation des dépendances npm..." -ForegroundColor Yellow
        Set-Location $frontendPath
        npm install
    }
    
    Write-Host "  Démarrage du serveur frontend sur http://localhost:3000" -ForegroundColor Cyan
    
    $frontendScript = @"
cd `"$frontendPath`"
npm run dev
pause
"@
    
    $frontendScriptPath = Join-Path $env:TEMP "start-frontend.bat"
    $frontendScript | Out-File -FilePath $frontendScriptPath -Encoding ASCII
    
    Start-Process cmd.exe -ArgumentList "/c", $frontendScriptPath
} else {
    Write-Host "✗ Dossier frontend non trouvé" -ForegroundColor Red
}

Write-Host ""

# Étape 4 : Résumé
Write-Host "[4/4] Résumé" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ MongoDB: http://localhost:27017" -ForegroundColor Green
Write-Host "✓ Backend API: http://localhost:8000" -ForegroundColor Green
Write-Host "✓ Documentation API: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "✓ Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Les serveurs backend et frontend ont été démarrés dans des fenêtres séparées." -ForegroundColor Yellow
Write-Host "Appuyez sur Ctrl+C dans chaque fenêtre pour arrêter les serveurs." -ForegroundColor Yellow
Write-Host ""
Write-Host "Appuyez sur une touche pour fermer cette fenêtre..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")



