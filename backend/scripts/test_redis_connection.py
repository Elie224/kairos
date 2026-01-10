"""
Script pour tester la connexion Redis
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_redis():
    """Teste la connexion Redis"""
    try:
        from app.utils.cache import init_redis, get_redis
        
        logger.info("=" * 60)
        logger.info("TEST DE CONNEXION REDIS")
        logger.info("=" * 60)
        logger.info("")
        
        # Initialiser Redis
        logger.info("Initialisation de Redis...")
        await init_redis()
        
        # Obtenir le client Redis
        redis = get_redis()
        
        if redis:
            logger.info("OK: Client Redis obtenu")
            logger.info("")
            
            # Tester la connexion
            logger.info("Test de connexion (PING)...")
            result = await redis.ping()
            
            if result:
                logger.info("OK: Redis repond (PONG)")
                logger.info("")
                
                # Tester une écriture/lecture
                logger.info("Test d'ecriture/lecture...")
                await redis.set("test_key", "test_value", ex=10)
                value = await redis.get("test_key")
                
                # Gérer le cas où value est bytes ou str
                if value:
                    if isinstance(value, bytes):
                        value_str = value.decode()
                    else:
                        value_str = str(value)
                    
                    if value_str == "test_value":
                        logger.info("OK: Ecriture et lecture reussies")
                        logger.info("")
                        
                        # Nettoyer
                        await redis.delete("test_key")
                        
                        logger.info("=" * 60)
                        logger.info("SUCCES: Redis fonctionne correctement!")
                        logger.info("=" * 60)
                        logger.info("")
                        logger.info("Configuration:")
                        logger.info("  URL: redis://localhost:6379/0")
                        logger.info("  Status: Connecte et operationnel")
                        return True
                    else:
                        logger.error("ERREUR: Valeur incorrecte")
                        return False
                else:
                    logger.error("ERREUR: Probleme d'ecriture/lecture")
                    return False
            else:
                logger.error("ERREUR: Redis ne repond pas")
                return False
        else:
            logger.error("ERREUR: Impossible d'obtenir le client Redis")
            logger.error("")
            logger.error("Verifiez:")
            logger.error("  1. Que Redis est demarre: docker ps | findstr redis")
            logger.error("  2. Que REDIS_URL est configure dans .env")
            logger.error("  3. Que le port 6379 n'est pas bloque")
            return False
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"ERREUR: {error_msg}")
        logger.error("")
        logger.error("Verifiez que Redis est demarre:")
        logger.error("  docker ps | findstr redis")
        logger.error("")
        logger.error("Ou demarrez Redis:")
        logger.error("  docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_redis())
    sys.exit(0 if success else 1)
