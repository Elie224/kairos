# Script PowerShell pour démarrer Redis avec Docker
# Usage: .\scripts\start_redis.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Demarrage de Redis pour Kaïros" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Docker est disponible
try {
    docker --version | Out-Null
    Write-Host "[OK] Docker est installe" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Docker n'est pas installe ou non accessible" -ForegroundColor Red
    Write-Host "Installez Docker Desktop depuis: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Vérifier si Redis est déjà démarré
$redisRunning = docker ps --filter "name=kairos-redis" --format "{{.Names}}" | Select-String "kairos-redis"

if ($redisRunning) {
    Write-Host "[INFO] Redis est deja demarre (kairos-redis)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour tester la connexion:" -ForegroundColor Cyan
    Write-Host "  docker exec -it kairos-redis redis-cli ping" -ForegroundColor White
    exit 0
}

# Vérifier si le conteneur existe mais est arrêté
$redisExists = docker ps -a --filter "name=kairos-redis" --format "{{.Names}}" | Select-String "kairos-redis"

if ($redisExists) {
    Write-Host "[INFO] Conteneur Redis existe mais est arrete" -ForegroundColor Yellow
    Write-Host "Demarrage du conteneur existant..." -ForegroundColor Cyan
    docker start kairos-redis
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Redis demarre avec succes" -ForegroundColor Green
    } else {
        Write-Host "[ERREUR] Impossible de demarrer Redis" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Creation et demarrage d'un nouveau conteneur Redis..." -ForegroundColor Cyan
    docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Redis demarre avec succes" -ForegroundColor Green
    } else {
        Write-Host "[ERREUR] Impossible de demarrer Redis" -ForegroundColor Red
        Write-Host "Verifiez que le port 6379 n'est pas deja utilise" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "Attente de 2 secondes pour que Redis soit pret..." -ForegroundColor Cyan
Start-Sleep -Seconds 2

# Tester la connexion
Write-Host ""
Write-Host "Test de connexion Redis..." -ForegroundColor Cyan
$pingResult = docker exec kairos-redis redis-cli ping 2>&1

if ($pingResult -eq "PONG") {
    Write-Host "[OK] Redis repond correctement (PONG)" -ForegroundColor Green
} else {
    Write-Host "[ATTENTION] Redis ne repond pas correctement: $pingResult" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Redis est pret!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration dans .env:" -ForegroundColor Cyan
Write-Host "  REDIS_URL=redis://localhost:6379/0" -ForegroundColor White
Write-Host ""
Write-Host "Commandes utiles:" -ForegroundColor Cyan
Write-Host "  Voir les logs: docker logs kairos-redis" -ForegroundColor White
Write-Host "  Arreter: docker stop kairos-redis" -ForegroundColor White
Write-Host "  Redemarrer: docker restart kairos-redis" -ForegroundColor White
Write-Host "  CLI Redis: docker exec -it kairos-redis redis-cli" -ForegroundColor White








