# Script de démarrage de Redis pour Kaïros
# Ce script démarre Redis dans un conteneur Docker

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Démarrage de Redis pour Kaïros" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Docker est installé
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker détecté: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur: Docker n'est pas installé ou n'est pas dans le PATH." -ForegroundColor Red
    Write-Host "   Installez Docker Desktop depuis: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    exit 1
}

# Vérifier si Docker est en cours d'exécution
try {
    docker ps 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erreur: Docker n'est pas en cours d'exécution." -ForegroundColor Red
        Write-Host "   Démarrez Docker Desktop et réessayez." -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Erreur: Impossible de se connecter à Docker." -ForegroundColor Red
    Write-Host "   Assurez-vous que Docker Desktop est démarré." -ForegroundColor Yellow
    exit 1
}

$containerName = "kairos-redis"
$port = 6379

# Vérifier si le conteneur existe déjà
$existingContainer = docker ps -a --filter "name=$containerName" --format "{{.Names}}" 2>&1

if ($existingContainer -eq $containerName) {
    Write-Host "📦 Conteneur Redis existant trouvé: $containerName" -ForegroundColor Yellow
    
    # Vérifier si le conteneur est en cours d'exécution
    $runningContainer = docker ps --filter "name=$containerName" --format "{{.Names}}" 2>&1
    
    if ($runningContainer -eq $containerName) {
        Write-Host "✅ Redis est déjà en cours d'exécution!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Informations du conteneur:" -ForegroundColor Cyan
        docker ps --filter "name=$containerName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        Write-Host ""
        Write-Host "Pour tester Redis:" -ForegroundColor Yellow
        Write-Host "  docker exec -it $containerName redis-cli ping" -ForegroundColor White
        Write-Host ""
        Write-Host "Pour arrêter Redis:" -ForegroundColor Yellow
        Write-Host "  docker stop $containerName" -ForegroundColor White
        exit 0
    } else {
        Write-Host "🔄 Redémarrage du conteneur Redis..." -ForegroundColor Yellow
        docker start $containerName 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Redis redémarré avec succès!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Erreur lors du redémarrage. Suppression et recréation..." -ForegroundColor Yellow
            docker rm -f $containerName 2>&1 | Out-Null
        }
    }
}

# Si le conteneur n'existe pas ou a été supprimé, le créer
$runningContainer = docker ps --filter "name=$containerName" --format "{{.Names}}" 2>&1
if ($runningContainer -ne $containerName) {
    Write-Host "🚀 Création et démarrage du conteneur Redis..." -ForegroundColor Yellow
    Write-Host ""
    
    # Vérifier si le port est déjà utilisé
    $portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Host "⚠️  Attention: Le port $port est déjà utilisé." -ForegroundColor Yellow
        Write-Host "   Vérification des processus utilisant le port $port..." -ForegroundColor Yellow
        $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($process) {
            Write-Host "   Processus trouvé: PID $($process.OwningProcess)" -ForegroundColor Yellow
        }
    }
    
    # Créer et démarrer le conteneur Redis
    Write-Host "Configuration Redis:" -ForegroundColor Cyan
    Write-Host "  - Nom du conteneur: $containerName" -ForegroundColor White
    Write-Host "  - Port: $port" -ForegroundColor White
    Write-Host "  - Image: redis:7-alpine" -ForegroundColor White
    Write-Host "  - Persistance: activée (appendonly)" -ForegroundColor White
    Write-Host "  - Mémoire max: 256MB" -ForegroundColor White
    Write-Host ""
    
    docker run -d `
        -p ${port}:6379 `
        --name $containerName `
        --restart unless-stopped `
        redis:7-alpine `
        redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Redis démarré avec succès!" -ForegroundColor Green
        Write-Host ""
        
        # Attendre quelques secondes pour que Redis démarre complètement
        Write-Host "⏳ Attente du démarrage complet de Redis..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        
        # Tester la connexion
        Write-Host "🔍 Test de connexion Redis..." -ForegroundColor Yellow
        $pingResult = docker exec $containerName redis-cli ping 2>&1
        
        if ($pingResult -eq "PONG") {
            Write-Host "✅ Redis répond correctement (PONG)!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Redis a démarré mais le test ping a échoué." -ForegroundColor Yellow
            Write-Host "   Résultat: $pingResult" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Erreur lors du démarrage de Redis." -ForegroundColor Red
        Write-Host "   Vérifiez les logs avec: docker logs $containerName" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Redis est prêt!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Informations de connexion:" -ForegroundColor Cyan
Write-Host "  URL: redis://localhost:$port/0" -ForegroundColor White
Write-Host "  Host: localhost" -ForegroundColor White
Write-Host "  Port: $port" -ForegroundColor White
Write-Host ""
Write-Host "Commandes utiles:" -ForegroundColor Cyan
Write-Host "  Tester Redis:     docker exec -it $containerName redis-cli ping" -ForegroundColor White
Write-Host "  Accéder au CLI:   docker exec -it $containerName redis-cli" -ForegroundColor White
Write-Host "  Voir les logs:    docker logs $containerName" -ForegroundColor White
Write-Host "  Arrêter Redis:    docker stop $containerName" -ForegroundColor White
Write-Host "  Redémarrer:      docker restart $containerName" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  N'oubliez pas de configurer REDIS_URL dans backend/.env:" -ForegroundColor Yellow
Write-Host "   REDIS_URL=redis://localhost:$port/0" -ForegroundColor White
Write-Host ""

