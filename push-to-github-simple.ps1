# Script simplifie pour pousser sur GitHub
# Repository: kairos | Utilisateur: Elie224

Write-Host "=== PUSH VERS GITHUB ===" -ForegroundColor Cyan
Write-Host "Repository: kairos" -ForegroundColor Yellow
Write-Host "Utilisateur: Elie224" -ForegroundColor Yellow
Write-Host ""

# Configuration Git
Write-Host "[1/8] Configuration Git..." -ForegroundColor Cyan
git config user.name "Elie224" 2>&1 | Out-Null
git config user.email "elie224@users.noreply.github.com" 2>&1 | Out-Null
Write-Host "OK" -ForegroundColor Green

# Vérifier/Initialiser Git
Write-Host "[2/8] Initialisation Git..." -ForegroundColor Cyan
if (-not (Test-Path ".git")) {
    git init | Out-Null
}
Write-Host "OK" -ForegroundColor Green

# Vérifier sécurité
Write-Host "[3/8] Verification securite..." -ForegroundColor Cyan
if (Test-Path ".env") {
    git rm --cached .env 2>&1 | Out-Null
    if (-not (Get-Content .gitignore | Select-String -Pattern "^\.env$")) {
        Add-Content .gitignore "`n.env"
    }
}
Write-Host "OK" -ForegroundColor Green

# Ajouter fichiers
Write-Host "[4/8] Ajout des fichiers..." -ForegroundColor Cyan
git add . 2>&1 | Out-Null
Write-Host "OK" -ForegroundColor Green

# Créer commit
Write-Host "[5/8] Creation du commit..." -ForegroundColor Cyan
git commit -m "Initial commit - Preparation deploiement Render" 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Aucun changement ou commit deja cree" -ForegroundColor Yellow
} else {
    Write-Host "OK" -ForegroundColor Green
}

# Renommer branche
Write-Host "[6/8] Branche main..." -ForegroundColor Cyan
git branch -M main 2>&1 | Out-Null
Write-Host "OK" -ForegroundColor Green

# Configurer remote
Write-Host "[7/8] Configuration remote GitHub..." -ForegroundColor Cyan
$remoteExists = git remote get-url origin 2>&1
if ($LASTEXITCODE -ne 0) {
    git remote add origin https://github.com/Elie224/kairos.git 2>&1 | Out-Null
} else {
    git remote set-url origin https://github.com/Elie224/kairos.git 2>&1 | Out-Null
}
Write-Host "OK" -ForegroundColor Green
Write-Host "Remote: https://github.com/Elie224/kairos.git" -ForegroundColor Gray

# Push
Write-Host "[8/8] Push vers GitHub..." -ForegroundColor Cyan
Write-Host ""
Write-Host "GitHub va demander authentification:" -ForegroundColor Yellow
Write-Host "- Option 1: Navigateur (recommandé)" -ForegroundColor White
Write-Host "- Option 2: Token personnel GitHub" -ForegroundColor White
Write-Host ""
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCCES ===" -ForegroundColor Green
    Write-Host "Repository: https://github.com/Elie224/kairos" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "=== ERREUR ===" -ForegroundColor Red
    Write-Host "Verifiez:" -ForegroundColor Yellow
    Write-Host "1. Le repository existe: https://github.com/Elie224/kairos" -ForegroundColor White
    Write-Host "2. Vos identifiants GitHub" -ForegroundColor White
}
