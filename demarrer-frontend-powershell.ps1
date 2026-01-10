# Script PowerShell pour démarrer le frontend
# Contourne le problème de politique d'exécution

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage du Frontend Kaïros" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Contourner la politique d'exécution pour cette session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Ajouter Node.js au PATH
$env:PATH += ";C:\Program Files\nodejs"

# Vérifier Node.js
Write-Host "Vérification de Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js trouvé : $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js non trouvé!" -ForegroundColor Red
    Write-Host "Veuillez installer Node.js depuis: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Se placer dans le dossier frontend
Set-Location "frontend"

# Vérifier si node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host ""
    Write-Host "Installation des dépendances npm (cela peut prendre quelques minutes)..." -ForegroundColor Yellow
    
    # Utiliser npm.cmd au lieu de npm pour contourner la politique
    & "C:\Program Files\nodejs\npm.cmd" install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erreur lors de l'installation des dépendances" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Dépendances installées avec succès!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage du serveur de développement..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Le frontend sera accessible sur: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur." -ForegroundColor Yellow
Write-Host ""

# Démarrer le serveur en utilisant npm.cmd
& "C:\Program Files\nodejs\npm.cmd" run dev
