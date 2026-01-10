# Script de démarrage simple du frontend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage du Frontend Kaïros" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Se déplacer dans le dossier frontend
Set-Location "frontend"

# Vérifier si node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "Installation des dépendances npm..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur lors de l'installation des dépendances" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Démarrage du serveur de développement..." -ForegroundColor Yellow
Write-Host "Le frontend sera accessible sur: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur." -ForegroundColor Yellow
Write-Host ""

# Démarrer le serveur
npm run dev


