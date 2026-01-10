"""
Redis cache utility for rate-limiting and login attempts
"""
from typing import Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Lazy import redis to avoid requiring it when not configured
redis_client = None

async def init_redis(app=None):
    global redis_client
    if not settings.redis_url:
        logger.info("Redis URL not configured; skipping Redis initialization")
        return
    
    try:
        import redis.asyncio as redis
        logger.info(f"Tentative de connexion Redis à {settings.redis_url}...")
        redis_client = await redis.from_url(
            settings.redis_url, 
            encoding='utf-8', 
            decode_responses=True,
            socket_connect_timeout=5,  # Timeout de connexion de 5 secondes
            socket_timeout=5,  # Timeout socket de 5 secondes
            retry_on_timeout=True,
            health_check_interval=30  # Vérifier la santé de la connexion toutes les 30s
        )
        # Test de connexion
        await redis_client.ping()
        logger.info("✅ Redis connecté avec succès")
    except ImportError:
        logger.warning("⚠️  Module redis non installé")
        logger.warning("   Installez avec: pip install redis[hiredis]")
        redis_client = None
    except Exception as e:
        error_msg = str(e)
        # Détecter les erreurs de connexion spécifiques
        is_connection_error = (
            "connection refused" in error_msg.lower() or
            "connection error" in error_msg.lower() or
            "error 22" in error_msg.lower() or
            "cannot connect" in error_msg.lower() or
            "refused" in error_msg.lower()
        )
        
        if is_connection_error:
            logger.warning(f"⚠️  Erreur de connexion Redis: {error_msg}")
            logger.warning(f"   Redis n'est pas accessible à {settings.redis_url}")
            logger.warning("   Solutions:")
            logger.warning("   1. Démarrez Redis:")
            logger.warning("      - Docker: docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine")
            logger.warning("      - Windows: Démarrez le service Redis")
            logger.warning("      - Script: python scripts/start_redis.ps1 (Windows) ou ./scripts/start_redis.sh (Linux/Mac)")
            logger.warning("   2. Vérifiez REDIS_URL dans .env: REDIS_URL=redis://localhost:6379/0")
            logger.warning("   3. Vérifiez que le port 6379 n'est pas bloqué par un firewall")
            logger.warning("   Consultez backend/DEMARRER_REDIS.md pour plus d'informations")
        else:
            logger.warning(f"⚠️  Erreur lors de l'initialisation Redis: {error_msg}")
            logger.warning(f"   Redis URL configurée: {settings.redis_url}")
            logger.warning("   Le cache ne sera pas disponible - performance réduite")
        redis_client = None

def get_redis():
    return redis_client


async def close_redis():
    global redis_client
    try:
        if redis_client:
            await redis_client.aclose()
            redis_client = None
            logger.info("Redis connection closed")
    except Exception as e:
        logger.warning(f"Error closing Redis: {e}")
