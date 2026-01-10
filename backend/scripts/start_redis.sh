#!/bin/bash
# Script bash pour démarrer Redis avec Docker
# Usage: ./scripts/start_redis.sh

echo "========================================"
echo "Démarrage de Redis pour Kaïros"
echo "========================================"
echo ""

# Vérifier si Docker est disponible
if ! command -v docker &> /dev/null; then
    echo "[ERREUR] Docker n'est pas installé ou non accessible"
    echo "Installez Docker depuis: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "[OK] Docker est installé"

# Vérifier si Redis est déjà démarré
if docker ps --filter "name=kairos-redis" --format "{{.Names}}" | grep -q "kairos-redis"; then
    echo "[INFO] Redis est déjà démarré (kairos-redis)"
    echo ""
    echo "Pour tester la connexion:"
    echo "  docker exec -it kairos-redis redis-cli ping"
    exit 0
fi

# Vérifier si le conteneur existe mais est arrêté
if docker ps -a --filter "name=kairos-redis" --format "{{.Names}}" | grep -q "kairos-redis"; then
    echo "[INFO] Conteneur Redis existe mais est arrêté"
    echo "Démarrage du conteneur existant..."
    docker start kairos-redis
    if [ $? -eq 0 ]; then
        echo "[OK] Redis démarré avec succès"
    else
        echo "[ERREUR] Impossible de démarrer Redis"
        exit 1
    fi
else
    echo "Création et démarrage d'un nouveau conteneur Redis..."
    docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine
    if [ $? -eq 0 ]; then
        echo "[OK] Redis démarré avec succès"
    else
        echo "[ERREUR] Impossible de démarrer Redis"
        echo "Vérifiez que le port 6379 n'est pas déjà utilisé"
        exit 1
    fi
fi

echo ""
echo "Attente de 2 secondes pour que Redis soit prêt..."
sleep 2

# Tester la connexion
echo ""
echo "Test de connexion Redis..."
PING_RESULT=$(docker exec kairos-redis redis-cli ping 2>&1)

if [ "$PING_RESULT" = "PONG" ]; then
    echo "[OK] Redis répond correctement (PONG)"
else
    echo "[ATTENTION] Redis ne répond pas correctement: $PING_RESULT"
fi

echo ""
echo "========================================"
echo "Redis est prêt!"
echo "========================================"
echo ""
echo "Configuration dans .env:"
echo "  REDIS_URL=redis://localhost:6379/0"
echo ""
echo "Commandes utiles:"
echo "  Voir les logs: docker logs kairos-redis"
echo "  Arrêter: docker stop kairos-redis"
echo "  Redémarrer: docker restart kairos-redis"
echo "  CLI Redis: docker exec -it kairos-redis redis-cli"








