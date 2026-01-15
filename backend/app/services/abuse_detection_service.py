"""
Service de détection d'abus pour protéger contre les abus IA
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from app.utils.cache import get_redis
import logging
import re

logger = logging.getLogger(__name__)


class AbuseDetectionService:
    """Service pour détecter les abus (prompt hacking, flood, etc.)"""
    
    # Patterns de prompt hacking
    PROMPT_HACKING_PATTERNS = [
        r'ignore\s+(previous|all|above)',
        r'forget\s+(everything|all|previous)',
        r'you\s+are\s+now',
        r'new\s+instructions',
        r'system\s+prompt',
        r'roleplay',
        r'pretend\s+to\s+be',
        r'act\s+as\s+if',
        r'disregard',
        r'override',
    ]
    
    @staticmethod
    async def detect_prompt_hacking(message: str) -> bool:
        """Détecte les tentatives de prompt hacking"""
        try:
            message_lower = message.lower()
            for pattern in AbuseDetectionService.PROMPT_HACKING_PATTERNS:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    logger.warning(f"Prompt hacking détecté: {pattern} dans le message")
                    return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la détection de prompt hacking: {e}")
            return False
    
    @staticmethod
    async def detect_flood(user_id: str, endpoint: str, window_seconds: int = 60) -> bool:
        """Détecte un flood de requêtes"""
        try:
            redis = get_redis()
            if not redis:
                # Sans Redis, on ne peut pas détecter le flood efficacement
                return False
            
            key = f"abuse:flood:{user_id}:{endpoint}"
            current_count = await redis.incr(key)
            
            if current_count == 1:
                # Première requête, définir l'expiration
                await redis.expire(key, window_seconds)
            
            # Seuil de flood (ex: 20 requêtes par minute)
            flood_threshold = 20
            if current_count > flood_threshold:
                logger.warning(f"Flood détecté pour utilisateur {user_id} sur {endpoint}: {current_count} requêtes")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la détection de flood: {e}")
            return False
    
    @staticmethod
    async def detect_abnormal_usage(user_id: str, endpoint: str) -> bool:
        """Détecte un usage anormal"""
        try:
            redis = get_redis()
            if not redis:
                return False
            
            # Vérifier le nombre de requêtes dans les dernières 24h
            key_24h = f"abuse:usage_24h:{user_id}:{endpoint}"
            count_24h = await redis.get(key_24h)
            count_24h = int(count_24h) if count_24h else 0
            
            # Seuil d'usage anormal (ex: 1000 requêtes par jour)
            abnormal_threshold = 1000
            if count_24h > abnormal_threshold:
                logger.warning(f"Usage anormal détecté pour utilisateur {user_id}: {count_24h} requêtes en 24h")
                return True
            
            # Incrémenter le compteur 24h
            await redis.incr(key_24h)
            if count_24h == 0:
                await redis.expire(key_24h, 86400)  # 24 heures
            
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la détection d'usage anormal: {e}")
            return False
    
    @staticmethod
    async def check_abuse(user_id: str, message: str, endpoint: str) -> Dict[str, Any]:
        """Vérifie tous les types d'abus"""
        try:
            results = {
                "is_abuse": False,
                "abuse_types": [],
                "should_block": False
            }
            
            # Détecter prompt hacking
            if await AbuseDetectionService.detect_prompt_hacking(message):
                results["is_abuse"] = True
                results["abuse_types"].append("prompt_hacking")
                results["should_block"] = True
            
            # Détecter flood
            if await AbuseDetectionService.detect_flood(user_id, endpoint):
                results["is_abuse"] = True
                results["abuse_types"].append("flood")
                results["should_block"] = True
            
            # Détecter usage anormal
            if await AbuseDetectionService.detect_abnormal_usage(user_id, endpoint):
                results["is_abuse"] = True
                results["abuse_types"].append("abnormal_usage")
                # Usage anormal ne bloque pas immédiatement, juste un warning
            
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'abus: {e}")
            return {
                "is_abuse": False,
                "abuse_types": [],
                "should_block": False
            }
    
    @staticmethod
    async def block_user_temporarily(user_id: str, duration_seconds: int = 300):
        """Bloque un utilisateur temporairement"""
        try:
            redis = get_redis()
            if not redis:
                return False
            
            key = f"abuse:blocked:{user_id}"
            await redis.setex(key, duration_seconds, "1")
            logger.warning(f"Utilisateur {user_id} bloqué temporairement pour {duration_seconds} secondes")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du blocage utilisateur: {e}")
            return False
    
    @staticmethod
    async def is_user_blocked(user_id: str) -> bool:
        """Vérifie si un utilisateur est bloqué"""
        try:
            redis = get_redis()
            if not redis:
                return False
            
            key = f"abuse:blocked:{user_id}"
            blocked = await redis.get(key)
            return blocked is not None
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du blocage: {e}")
            return False
