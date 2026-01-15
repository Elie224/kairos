"""
Cache ultra-rapide pour requêtes fréquentes
Utilise Redis si disponible, sinon cache en mémoire
"""
from typing import Optional, Any, Callable
import asyncio
import time
import hashlib
import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# Cache en mémoire (fallback si Redis n'est pas disponible)
_memory_cache: Dict[str, tuple] = {}
_cache_lock = asyncio.Lock()
_MAX_MEMORY_CACHE_SIZE = 1000  # Maximum 1000 entrées en mémoire


def _generate_cache_key(func_name: str, *args, **kwargs) -> str:
    """Génère une clé de cache unique"""
    # Créer une représentation stable des arguments
    key_data = {
        "func": func_name,
        "args": args,
        "kwargs": sorted(kwargs.items()) if kwargs else {}
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


async def _get_from_redis(key: str) -> Optional[Any]:
    """Récupère une valeur depuis Redis"""
    try:
        from app.utils.cache import get_redis
        redis = get_redis()
        if redis:
            value = await redis.get(key)
            if value:
                return json.loads(value)
    except Exception as e:
        logger.debug(f"Erreur Redis cache get: {e}")
    return None


async def _set_in_redis(key: str, value: Any, ttl: int = 300):
    """Stocke une valeur dans Redis avec TTL"""
    try:
        from app.utils.cache import get_redis
        redis = get_redis()
        if redis:
            await redis.setex(key, ttl, json.dumps(value, default=str))
            return True
    except Exception as e:
        logger.debug(f"Erreur Redis cache set: {e}")
    return False


async def _get_from_memory(key: str) -> Optional[Any]:
    """Récupère une valeur depuis le cache mémoire"""
    async with _cache_lock:
        if key in _memory_cache:
            value, expiry = _memory_cache[key]
            if time.time() < expiry:
                return value
            else:
                # Expiré, supprimer
                del _memory_cache[key]
    return None


async def _set_in_memory(key: str, value: Any, ttl: int = 300):
    """Stocke une valeur dans le cache mémoire"""
    async with _cache_lock:
        # Nettoyer le cache si trop plein
        if len(_memory_cache) >= _MAX_MEMORY_CACHE_SIZE:
            # Supprimer les 20% les plus anciens
            sorted_items = sorted(_memory_cache.items(), key=lambda x: x[1][1])
            to_remove = int(_MAX_MEMORY_CACHE_SIZE * 0.2)
            for k, _ in sorted_items[:to_remove]:
                del _memory_cache[k]
        
        expiry = time.time() + ttl
        _memory_cache[key] = (value, expiry)


async def fast_cache_get(key: str) -> Optional[Any]:
    """Récupère une valeur depuis le cache (Redis ou mémoire)"""
    # Essayer Redis d'abord
    value = await _get_from_redis(key)
    if value is not None:
        return value
    
    # Fallback sur mémoire
    return await _get_from_memory(key)


async def fast_cache_set(key: str, value: Any, ttl: int = 300):
    """Stocke une valeur dans le cache (Redis ou mémoire)"""
    # Essayer Redis d'abord
    redis_success = await _set_in_redis(key, value, ttl)
    
    # Toujours mettre en mémoire aussi (fallback)
    await _set_in_memory(key, value, ttl)
    
    return redis_success


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Décorateur pour mettre en cache les résultats de fonctions async
    
    Args:
        ttl: Time to live en secondes (défaut: 5 minutes)
        key_prefix: Préfixe pour la clé de cache
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Générer la clé de cache
            func_name = f"{key_prefix}.{func.__name__}" if key_prefix else func.__name__
            cache_key = _generate_cache_key(func_name, *args, **kwargs)
            
            # Essayer de récupérer depuis le cache
            cached_value = await fast_cache_get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {func_name}")
                return cached_value
            
            # Cache miss, exécuter la fonction
            logger.debug(f"Cache miss: {func_name}")
            result = await func(*args, **kwargs)
            
            # Mettre en cache
            await fast_cache_set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


async def invalidate_cache(pattern: str):
    """Invalide le cache pour un pattern donné"""
    try:
        from app.utils.cache import get_redis
        redis = get_redis()
        if redis:
            # Supprimer toutes les clés correspondant au pattern
            keys = await redis.keys(f"*{pattern}*")
            if keys:
                await redis.delete(*keys)
    except Exception:
        pass
    
    # Nettoyer aussi le cache mémoire
    async with _cache_lock:
        keys_to_remove = [k for k in _memory_cache.keys() if pattern in k]
        for k in keys_to_remove:
            del _memory_cache[k]
