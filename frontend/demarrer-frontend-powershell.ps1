# Script PowerShell pour démarrer le frontend
# Contourne les problèmes de politique d'exécution

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Demarrage du Frontend Kairos" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Node.js
try {
    $nodeVersion = node --version
    Write-Host "[OK] Node.js trouve: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Node.js n'est pas installe ou pas dans le PATH!" -ForegroundColor Red
    Write-Host "Installez Node.js depuis: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Vérifier si node_modules existe
if (-not (Test-Path "node_modules")) {
    Write-Host "Installation des dependances npm..." -ForegroundColor Yellow
    & npm.cmd install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERREUR] Echec de l'installation des dependances" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

Write-Host "Demarrage du serveur de developpement..." -ForegroundColor Yellow
Write-Host "Le frontend sera accessible sur: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arreter le serveur." -ForegroundColor Yellow
Write-Host ""

# Utiliser npm.cmd au lieu de npm pour éviter les problèmes PowerShell
& npm.cmd run dev
