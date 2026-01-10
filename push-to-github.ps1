# Script pour pousser le code sur GitHub de manière sécurisée
# Repository: kairos
# Utilisateur: Elie224

Write-Host "🚀 Préparation du push sur GitHub..." -ForegroundColor Cyan
Write-Host "Repository: kairos" -ForegroundColor Yellow
Write-Host "Utilisateur: Elie224" -ForegroundColor Yellow
Write-Host ""

# Se placer dans le dossier du projet
$projectPath = "C:\Users\KOURO\OneDrive\Desktop\Kairós"
Set-Location $projectPath

# 1. Vérifier que Git est installé
Write-Host "📋 Vérification de Git..." -ForegroundColor Cyan
$gitVersion = git --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git n'est pas installé. Veuillez l'installer depuis https://git-scm.com/downloads" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Git trouvé: $gitVersion" -ForegroundColor Green

# 2. Configurer Git (si pas déjà fait)
Write-Host ""
Write-Host "📋 Configuration Git..." -ForegroundColor Cyan
git config user.name "Elie224"
git config user.email "elie224@users.noreply.github.com"
Write-Host "✅ Git configuré" -ForegroundColor Green

# 3. Vérifier si Git est initialisé
Write-Host ""
Write-Host "📋 Vérification du repository Git..." -ForegroundColor Cyan
if (-not (Test-Path ".git")) {
    Write-Host "⚠️  Git n'est pas initialisé. Initialisation..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Git initialisé" -ForegroundColor Green
}

# 4. Vérifier les fichiers sensibles
Write-Host ""
Write-Host "🔒 Vérification de la sécurité..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "⚠️  ATTENTION: Fichier .env trouvé !" -ForegroundColor Yellow
    Write-Host "   Vérification qu'il est dans .gitignore..." -ForegroundColor Yellow
    git check-ignore .env 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERREUR: .env n'est pas dans .gitignore !" -ForegroundColor Red
        Write-Host "   Suppression de .env du cache Git..." -ForegroundColor Yellow
        git rm --cached .env 2>&1 | Out-Null
        Add-Content -Path ".gitignore" -Value "`n.env" -Force
        Write-Host "✅ .env ajouté au .gitignore" -ForegroundColor Green
    } else {
        Write-Host "✅ .env est bien dans .gitignore" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Aucun fichier .env trouvé" -ForegroundColor Green
}

# 5. Vérifier le .gitignore
Write-Host ""
Write-Host "📋 Vérification du .gitignore..." -ForegroundColor Cyan
if (Test-Path ".gitignore") {
    Write-Host "✅ .gitignore présent" -ForegroundColor Green
} else {
    Write-Host "❌ ERREUR: .gitignore manquant !" -ForegroundColor Red
    exit 1
}

# 6. Vérifier qu'aucun fichier sensible n'est tracké
Write-Host ""
Write-Host "🔍 Recherche de fichiers sensibles..." -ForegroundColor Cyan
$sensitiveFiles = @(".env", "venv", "node_modules", "*.log")
$found = $false
foreach ($pattern in $sensitiveFiles) {
    $files = git ls-files $pattern 2>&1
    if ($files -and $LASTEXITCODE -eq 0) {
        Write-Host "⚠️  ATTENTION: Fichiers sensibles trouvés: $files" -ForegroundColor Yellow
        $found = $true
    }
}
if (-not $found) {
    Write-Host "✅ Aucun fichier sensible trouvé" -ForegroundColor Green
}

# 7. Ajouter tous les fichiers (sauf ceux dans .gitignore)
Write-Host ""
Write-Host "📦 Ajout des fichiers au repository..." -ForegroundColor Cyan
git add .
Write-Host "✅ Fichiers ajoutés" -ForegroundColor Green

# 8. Vérifier ce qui a été ajouté
Write-Host ""
Write-Host "📋 Fichiers à commiter:" -ForegroundColor Cyan
git status --short | Select-Object -First 20
$totalFiles = (git status --short).Count
Write-Host "   Total: $totalFiles fichiers" -ForegroundColor Yellow

# 9. Créer le commit
Write-Host ""
Write-Host "💾 Création du commit..." -ForegroundColor Cyan
$commitMessage = @"
Initial commit - Préparation déploiement Render

- Configuration Render (.render.yaml)
- Variables d'environnement (env.example)
- Script de build backend
- Documentation déploiement complète
- Sécurité: clés et secrets sécurisés
"@
git commit -m $commitMessage
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Commit créé avec succès" -ForegroundColor Green
} else {
    Write-Host "⚠️  Aucun changement à commiter (ou commit déjà créé)" -ForegroundColor Yellow
}

# 10. Renommer la branche en main (si nécessaire)
Write-Host ""
Write-Host "📋 Vérification de la branche..." -ForegroundColor Cyan
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "   Renommage de la branche '$currentBranch' en 'main'..." -ForegroundColor Yellow
    git branch -M main
    Write-Host "✅ Branche renommée en 'main'" -ForegroundColor Green
} else {
    Write-Host "✅ Branche déjà 'main'" -ForegroundColor Green
}

# 11. Ajouter le remote GitHub
Write-Host ""
Write-Host "🔗 Configuration du remote GitHub..." -ForegroundColor Cyan
$remoteUrl = "https://github.com/Elie224/kairos.git"
$existingRemote = git remote get-url origin 2>&1
if ($LASTEXITCODE -eq 0) {
    if ($existingRemote -ne $remoteUrl) {
        Write-Host "   Mise à jour du remote..." -ForegroundColor Yellow
        git remote set-url origin $remoteUrl
        Write-Host "✅ Remote mis à jour" -ForegroundColor Green
    } else {
        Write-Host "✅ Remote déjà configuré correctement" -ForegroundColor Green
    }
} else {
    Write-Host "   Ajout du remote GitHub..." -ForegroundColor Yellow
    git remote add origin $remoteUrl
    Write-Host "✅ Remote ajouté" -ForegroundColor Green
}

# 12. Vérifier le remote
Write-Host ""
Write-Host "📋 Vérification du remote:" -ForegroundColor Cyan
git remote -v

# 13. Pousser sur GitHub
Write-Host ""
Write-Host "🚀 Pousser le code sur GitHub..." -ForegroundColor Cyan
Write-Host "   Repository: $remoteUrl" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  GitHub va demander vos identifiants:" -ForegroundColor Yellow
Write-Host "   - Option 1: Authentification par navigateur (recommandé)" -ForegroundColor White
Write-Host "   - Option 2: Utiliser un token personnel GitHub" -ForegroundColor White
Write-Host ""
$confirm = Read-Host "Continuer ? (O/N)"
if ($confirm -ne "O" -and $confirm -ne "o") {
    Write-Host "❌ Push annulé par l'utilisateur" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "⏳ Pousser le code..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Code poussé sur GitHub avec succès !" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Repository: https://github.com/Elie224/kairos" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📚 Prochaine étape: Suivre DEPLOIEMENT_RENDER.md pour déployer sur Render" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors du push. Vérifiez les messages d'erreur ci-dessus." -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Solutions possibles:" -ForegroundColor Yellow
    Write-Host "   1. Vérifier que le repository GitHub existe: https://github.com/Elie224/kairos" -ForegroundColor White
    Write-Host "   2. Vérifier vos identifiants GitHub" -ForegroundColor White
    Write-Host "   3. Utiliser un token personnel si l'authentification échoue" -ForegroundColor White
    exit 1
}
