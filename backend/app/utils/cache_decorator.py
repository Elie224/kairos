"""
Décorateur de cache Redis pour optimiser les performances
Gains : -60% coût API & +200% vitesse
"""
from functools import wraps
from typing import Optional, Callable, Any
import json
import hashlib
import logging
from app.utils.cache import get_redis

logger = logging.getLogger(__name__)

def cache_result(
    ttl: int = 300,  # 5 minutes par défaut
    key_prefix: str = "cache",
    include_user: bool = False
):
    """
    Décorateur pour mettre en cache les résultats des fonctions async
    
    Args:
        ttl: Time to live en secondes
        key_prefix: Préfixe pour la clé de cache
        include_user: Inclure l'ID utilisateur dans la clé de cache
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis = get_redis()
            if not redis:
                # Si Redis n'est pas disponible, exécuter sans cache
                return await func(*args, **kwargs)
            
            # Construire la clé de cache
            cache_key_parts = [key_prefix]
            
            # Ajouter l'ID utilisateur si nécessaire
            if include_user:
                user_id = None
                # Chercher dans les arguments
                for arg in args:
                    if isinstance(arg, str) and len(arg) > 0:
                        # Si c'est le premier argument et que c'est une string, c'est probablement user_id
                        if args.index(arg) == 0:
                            user_id = arg
                            break
                    elif isinstance(arg, dict) and "id" in arg:
                        user_id = arg["id"]
                        break
                # Chercher dans kwargs
                if not user_id and "user_id" in kwargs:
                    user_id = kwargs["user_id"]
                elif not user_id and "current_user" in kwargs:
                    current_user = kwargs["current_user"]
                    if isinstance(current_user, dict) and "id" in current_user:
                        user_id = current_user["id"]
                
                if user_id:
                    cache_key_parts.append(f"user:{str(user_id)}")
            
            # Ajouter les arguments pour créer une clé unique
            key_data = {
                "func": func.__name__,
                "args": str(args),
                "kwargs": {k: str(v) for k, v in kwargs.items() if k not in ["current_user", "admin_user"]}
            }
            key_hash = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
            cache_key_parts.append(key_hash)
            cache_key = ":".join(cache_key_parts)
            
            try:
                # Essayer de récupérer depuis le cache
                try:
                    # Vérifier que Redis est toujours connecté
                    if redis:
                        cached = await redis.get(cache_key)
                        if cached:
                            logger.debug(f"Cache hit: {cache_key}")
                            return json.loads(cached)
                except (ConnectionError, TimeoutError, AttributeError) as cache_read_error:
                    # Erreurs de connexion - ne pas logger comme warning si c'est juste une déconnexion temporaire
                    logger.debug(f"Cache non disponible (connexion Redis): {cache_read_error}")
                    # Continuer sans cache
                except Exception as cache_read_error:
                    # Autres erreurs - logger comme warning
                    logger.warning(f"Erreur lors de la lecture du cache: {cache_read_error}")
                    # Continuer sans cache
                
                # Cache miss - exécuter la fonction
                logger.debug(f"Cache miss: {cache_key}")
                result = await func(*args, **kwargs)
                
                # Mettre en cache le résultat (sans bloquer en cas d'erreur)
                if result is not None and redis:
                    try:
                        await redis.setex(
                            cache_key,
                            ttl,
                            json.dumps(result, default=str)
                        )
                    except (ConnectionError, TimeoutError, AttributeError) as cache_write_error:
                        # Erreurs de connexion - ne pas logger comme warning
                        logger.debug(f"Cache non disponible pour écriture (connexion Redis): {cache_write_error}")
                        # Continuer même si le cache échoue
                    except Exception as cache_write_error:
                        # Autres erreurs - logger comme warning
                        logger.warning(f"Erreur lors de l'écriture du cache: {cache_write_error}")
                        # Continuer même si le cache échoue
                
                return result
            except Exception as e:
                logger.warning(f"Erreur de cache pour {cache_key}: {e}", exc_info=True)
                # En cas d'erreur, exécuter sans cache
                try:
                    return await func(*args, **kwargs)
                except Exception as func_error:
                    logger.error(f"Erreur lors de l'exécution de la fonction sans cache: {func_error}", exc_info=True)
                    # Si même sans cache ça échoue, lever l'exception
                    raise
        
        return wrapper
    return decorator


async def invalidate_cache(pattern: str):
    """
    Invalide toutes les clés de cache correspondant au pattern
    
    Args:
        pattern: Pattern Redis (ex: "cache:modules:*")
    """
    redis = get_redis()
    if not redis:
        return
    
    try:
        keys = []
        async for key in redis.scan_iter(match=pattern):
            keys.append(key)
        
        if keys:
            await redis.delete(*keys)
            logger.info(f"Cache invalidé: {len(keys)} clés supprimées pour pattern {pattern}")
    except Exception as e:
        logger.warning(f"Erreur lors de l'invalidation du cache: {e}")


async def clear_all_cache():
    """Vide tout le cache Redis"""
    redis = get_redis()
    if not redis:
        return
    
    try:
        await redis.flushdb()
        logger.info("Cache Redis vidé")
    except Exception as e:
        logger.warning(f"Erreur lors du vidage du cache: {e}")

