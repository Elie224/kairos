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
        logger.info("ℹ️  Module redis non installé - Cache désactivé (optionnel)")
        logger.info("   Pour activer Redis, installez: pip install redis[hiredis]")
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
            logger.info(f"ℹ️  Redis non accessible à {settings.redis_url} - Cache désactivé (optionnel)")
            logger.info("   Pour activer Redis et améliorer les performances:")
            logger.info("   1. Sur Render: Créez un service Redis et configurez REDIS_URL")
            logger.info("   2. Localement (Docker): docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine")
            logger.info("   3. Localement (Windows): Démarrez le service Redis")
            logger.info("   4. Vérifiez REDIS_URL dans .env: REDIS_URL=redis://localhost:6379/0")
            logger.info("   Consultez backend/DEMARRER_REDIS.md pour plus d'informations")
        else:
            logger.info(f"ℹ️  Erreur lors de l'initialisation Redis: {error_msg}")
            logger.info(f"   Redis URL configurée: {settings.redis_url}")
            logger.info("   Le cache ne sera pas disponible (Redis est optionnel)")
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
        logger.info(f"ℹ️  Erreur lors de la fermeture Redis (non critique): {e}")
