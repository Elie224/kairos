# Script de migration PostgreSQL pour Kaïros
# Crée toutes les tables dans la base de données eduverse

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Migration PostgreSQL - Kaïros" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que l'environnement virtuel existe
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "❌ Erreur: Environnement virtuel introuvable!" -ForegroundColor Red
    Write-Host "   Créez l'environnement virtuel avec: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
& "venv\Scripts\python.exe" --version | Out-Null

# Vérifier que le fichier .env existe
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Fichier .env introuvable!" -ForegroundColor Yellow
    Write-Host "   Création d'un fichier .env avec les valeurs par défaut..." -ForegroundColor Yellow
    Write-Host ""
    
    $envContent = @"
# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Fichier .env créé. Veuillez le modifier avec vos paramètres PostgreSQL." -ForegroundColor Green
    Write-Host ""
    Write-Host "Appuyez sur Entrée pour continuer avec les valeurs par défaut..." -ForegroundColor Yellow
    Read-Host
}

# Exécuter les migrations
Write-Host "Exécution des migrations PostgreSQL..." -ForegroundColor Yellow
Write-Host ""

& "venv\Scripts\python.exe" scripts\migrate_postgres.py create

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migration terminée avec succès!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Tables créées dans PostgreSQL:" -ForegroundColor Cyan
    Write-Host "  - users" -ForegroundColor White
    Write-Host "  - courses" -ForegroundColor White
    Write-Host "  - modules" -ForegroundColor White
    Write-Host "  - enrollments" -ForegroundColor White
    Write-Host "  - user_progress" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors de la migration!" -ForegroundColor Red
    Write-Host "   Vérifiez:" -ForegroundColor Yellow
    Write-Host "   1. Que PostgreSQL 18 est démarré" -ForegroundColor Yellow
    Write-Host "   2. Que la base de données 'eduverse' existe" -ForegroundColor Yellow
    Write-Host "   3. Que les paramètres dans .env sont corrects" -ForegroundColor Yellow
    exit 1
}
