# Script de démarrage du backend Kaïros
# Ce script active l'environnement virtuel Python et démarre le serveur FastAPI

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage du Backend Kaïros" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si on est dans le bon répertoire
$backendPath = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path $backendPath)) {
    Write-Host "Erreur: Le dossier 'backend' n'existe pas dans le répertoire actuel." -ForegroundColor Red
    Write-Host "Répertoire actuel: $PSScriptRoot" -ForegroundColor Yellow
    exit 1
}

# Se déplacer dans le dossier backend
Set-Location $backendPath
Write-Host "Répertoire: $backendPath" -ForegroundColor Green

# Vérifier si l'environnement virtuel existe et s'il est valide
$venvPath = Join-Path $backendPath "venv"
$venvPythonPath = Join-Path $venvPath "Scripts\python.exe"
$venvCorrupted = $false

if (Test-Path $venvPath) {
    # Vérifier si le venv est corrompu (contient des références à un autre chemin)
    if (Test-Path $venvPythonPath) {
        # Vérifier si python.exe existe et fonctionne
        try {
            $pythonVersion = & $venvPythonPath --version 2>&1
            if ($LASTEXITCODE -ne 0) {
                $venvCorrupted = $true
            }
        } catch {
            $venvCorrupted = $true
        }
    } else {
        $venvCorrupted = $true
    }
    
    # Vérifier les scripts pip et uvicorn pour des chemins incorrects
    $pipScript = Join-Path $venvPath "Scripts\pip.exe"
    if (Test-Path $pipScript) {
        $pipContent = Get-Content $pipScript -Raw -ErrorAction SilentlyContinue
        if ($pipContent -and $pipContent -match "EduVerse") {
            Write-Host "⚠️  Environnement virtuel corrompu détecté (références à EduVerse)." -ForegroundColor Yellow
            $venvCorrupted = $true
        }
    }
}

if (-not (Test-Path $venvPath) -or $venvCorrupted) {
    if ($venvCorrupted) {
        Write-Host "Suppression de l'environnement virtuel corrompu..." -ForegroundColor Yellow
        Remove-Item -Path $venvPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    Write-Host "⚠️  Création d'un nouvel environnement virtuel..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur: Impossible de créer l'environnement virtuel." -ForegroundColor Red
        Write-Host "Vérifiez que Python est installé et accessible." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "✅ Environnement virtuel créé." -ForegroundColor Green
}

# Activer l'environnement virtuel
Write-Host "Activation de l'environnement virtuel..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "Erreur: Script d'activation non trouvé à $activateScript" -ForegroundColor Red
    exit 1
}

# Utiliser python.exe du venv directement pour éviter les problèmes de launcher
$pythonExe = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "Erreur: python.exe non trouvé dans l'environnement virtuel." -ForegroundColor Red
    exit 1
}

# Vérifier si les dépendances sont installées
Write-Host "Vérification des dépendances..." -ForegroundColor Yellow
$requirementsPath = Join-Path $backendPath "requirements.txt"
if (Test-Path $requirementsPath) {
    Write-Host "Installation/mise à jour des dépendances..." -ForegroundColor Yellow
    & $pythonExe -m pip install -q --upgrade pip
    & $pythonExe -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Erreur lors de l'installation des dépendances. Continuons quand même..." -ForegroundColor Yellow
    } else {
        Write-Host "✅ Dépendances installées." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage du serveur FastAPI..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Le serveur sera accessible sur: http://localhost:8000" -ForegroundColor Green
Write-Host "Documentation API: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Appuyez sur Ctrl+C pour arrêter le serveur." -ForegroundColor Yellow
Write-Host ""

# Démarrer le serveur avec uvicorn en utilisant python -m pour éviter les problèmes de launcher
try {
    & $pythonExe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
} catch {
    Write-Host "Erreur lors du démarrage du serveur: $_" -ForegroundColor Red
    exit 1
}

