# Script PowerShell pour redémarrer le backend en libérant le port 8000 si nécessaire

Write-Host "🔄 Redémarrage du backend..." -ForegroundColor Cyan

# Vérifier si le port 8000 est utilisé
$portInUse = netstat -ano | findstr :8000 | findstr LISTENING

if ($portInUse) {
    Write-Host "⚠️  Le port 8000 est déjà utilisé. Libération du port..." -ForegroundColor Yellow
    
    # Extraire le PID du processus qui utilise le port
    $pid = ($portInUse -split '\s+')[-1]
    
    if ($pid -and $pid -ne "0") {
        Write-Host "   Arrêt du processus PID: $pid" -ForegroundColor Yellow
        taskkill /F /PID $pid 2>$null
        Start-Sleep -Seconds 2
        Write-Host "✅ Port 8000 libéré" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Le port 8000 est libre" -ForegroundColor Green
}

# Attendre un peu pour être sûr que le port est libéré
Start-Sleep -Seconds 1

# Vérifier que Python existe
if (-not (Test-Path ".\venv\Scripts\python.exe")) {
    Write-Host "❌ Python non trouvé dans venv\Scripts\python.exe" -ForegroundColor Red
    exit 1
}

# Démarrer le backend dans une nouvelle fenêtre
Write-Host "🚀 Démarrage du backend..." -ForegroundColor Cyan
$backendPath = (Get-Location).Path
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host '✅ Backend démarré sur http://localhost:8000' -ForegroundColor Green; .\venv\Scripts\python.exe main.py"

Write-Host "✅ Backend démarré dans une nouvelle fenêtre PowerShell" -ForegroundColor Green
Write-Host "   Accédez à http://localhost:8000/docs pour voir la documentation API" -ForegroundColor Cyan
