# Script pour nettoyer l'historique Git et pousser proprement
Write-Host "=== NETTOYAGE HISTORIQUE GIT ===" -ForegroundColor Cyan

# Supprimer le repository local et recommencer proprement
Write-Host "Suppression de .git..." -ForegroundColor Yellow
Remove-Item -Recurse -Force .git -ErrorAction SilentlyContinue

Write-Host "Initialisation Git propre..." -ForegroundColor Cyan
git init

Write-Host "Configuration Git..." -ForegroundColor Cyan
git config user.name "Elie224"
git config user.email "elie224@users.noreply.github.com"

Write-Host "Verification securite..." -ForegroundColor Cyan
# S'assurer que le fichier update_openai_key.py n'a pas de clé hardcodée
$content = Get-Content "backend/scripts/update_openai_key.py" -Raw
if ($content -match 'sk-proj-[A-Za-z0-9_-]+') {
    Write-Host "ERREUR: Clé API encore presente dans update_openai_key.py" -ForegroundColor Red
    exit 1
}

Write-Host "OK - Aucune clé API hardcodée trouvée" -ForegroundColor Green

Write-Host "Ajout des fichiers..." -ForegroundColor Cyan
git add .

Write-Host "Creation du commit..." -ForegroundColor Cyan
git commit -m "Initial commit - Preparation deploiement Render

- Configuration Render (.render.yaml)
- Variables d'environnement (env.example)  
- Script de build backend
- Documentation deploiement complete
- Securite: aucune cle API hardcodee"

Write-Host "Branche main..." -ForegroundColor Cyan
git branch -M main

Write-Host "Configuration remote..." -ForegroundColor Cyan
git remote add origin https://github.com/Elie224/kairos.git 2>&1 | Out-Null
git remote set-url origin https://github.com/Elie224/kairos.git 2>&1 | Out-Null

Write-Host ""
Write-Host "=== PUSH VERS GITHUB ===" -ForegroundColor Cyan
Write-Host "GitHub va demander authentification" -ForegroundColor Yellow
Write-Host ""

git push -u origin main --force

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== SUCCES ===" -ForegroundColor Green
    Write-Host "Repository: https://github.com/Elie224/kairos" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "=== ERREUR ===" -ForegroundColor Red
    Write-Host "Verifiez vos identifiants GitHub" -ForegroundColor Yellow
}
