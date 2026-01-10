# Script de démarrage simple du backend
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage du Backend Kaïros" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Se déplacer dans le dossier backend
Set-Location "backend"

# Vérifier si l'environnement virtuel existe
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "✅ Environnement virtuel trouvé" -ForegroundColor Green
    
    # Activer et démarrer
    Write-Host "Démarrage du serveur FastAPI..." -ForegroundColor Yellow
    Write-Host "Le serveur sera accessible sur: http://localhost:8000" -ForegroundColor Green
    Write-Host "Documentation API: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host ""
    Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur." -ForegroundColor Yellow
    Write-Host ""
    
    # Démarrer le serveur
    & "venv\Scripts\python.exe" main.py
} else {
    Write-Host "❌ Environnement virtuel non trouvé" -ForegroundColor Red
    Write-Host "Création de l'environnement virtuel..." -ForegroundColor Yellow
    
    # Créer l'environnement virtuel
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur lors de la création de l'environnement virtuel" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Installation des dépendances..." -ForegroundColor Yellow
    & "venv\Scripts\pip.exe" install -r requirements.txt
    
    Write-Host "Démarrage du serveur..." -ForegroundColor Yellow
    & "venv\Scripts\python.exe" main.py
}


