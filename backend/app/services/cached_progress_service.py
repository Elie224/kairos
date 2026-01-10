"""
Service de progression avec cache Redis pour optimiser les performances
"""
from typing import Dict, Any, Optional, List
from app.services.progress_service import ProgressService
from app.utils.cache_decorator import cache_result, invalidate_cache
from app.models import ProgressCreate
import logging

logger = logging.getLogger(__name__)


class CachedProgressService:
    """Service de progression avec cache Redis"""
    
    @staticmethod
    @cache_result(ttl=300, key_prefix="cache:progress:user", include_user=True)  # 5 minutes
    async def get_user_progress(user_id: str, module_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Récupère la progression d'un utilisateur avec cache"""
        try:
            logger.debug(f"get_user_progress called with user_id={user_id}, module_id={module_id}, limit={limit}")
            result = await ProgressService.get_user_progress(user_id, module_id, limit)
            # S'assurer que le résultat est une liste
            if not isinstance(result, list):
                logger.warning(f"get_user_progress a retourné un type inattendu: {type(result)}")
                return []
            return result
        except Exception as e:
            logger.error(f"Erreur dans CachedProgressService.get_user_progress: {e}", exc_info=True)
            # Retourner une liste vide en cas d'erreur
            return []
    
    @staticmethod
    @cache_result(ttl=300, key_prefix="cache:progress:module", include_user=True)  # 5 minutes
    async def get_module_progress(user_id: str, module_id: str) -> Optional[Dict[str, Any]]:
        """Récupère la progression d'un module avec cache"""
        return await ProgressService.get_module_progress(user_id, module_id)
    
    @staticmethod
    async def create_or_update_progress(
        user_id: str,
        progress_data: ProgressCreate
    ) -> Dict[str, Any]:
        """Crée ou met à jour une progression et invalide le cache"""
        result = await ProgressService.create_or_update_progress(user_id, progress_data)
        # Invalider le cache pour cet utilisateur
        await invalidate_cache(f"cache:progress:*{user_id}*")
        return result
    
    @staticmethod
    @cache_result(ttl=300, key_prefix="cache:progress:stats", include_user=True)  # 5 minutes
    async def get_progress_stats(user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques avec cache"""
        return await ProgressService.get_progress_stats(user_id)
    
    @staticmethod
    async def update_progress_time(user_id: str, module_id: str, time_spent: int) -> Dict[str, Any]:
        """Met à jour le temps passé et invalide le cache"""
        result = await ProgressService.update_progress_time(user_id, module_id, time_spent)
        await invalidate_cache(f"cache:progress:*{user_id}*")
        return result

