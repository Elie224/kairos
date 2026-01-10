"""
Service de modules avec cache Redis pour optimiser les performances
"""
from typing import List, Dict, Any, Optional
from app.services.module_service import ModuleService
from app.models import Subject, Difficulty
from app.utils.cache_decorator import cache_result, invalidate_cache
import logging

logger = logging.getLogger(__name__)


class CachedModuleService:
    """Service de modules avec cache Redis"""
    
    @staticmethod
    @cache_result(ttl=600, key_prefix="cache:modules:list")  # 10 minutes
    async def get_modules(
        subject: Optional[str] = None,
        difficulty: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Récupère les modules avec cache"""
        try:
            # Convertir les strings en enums si nécessaire
            subject_enum = None
            if subject:
                try:
                    subject_enum = Subject(subject)
                except ValueError:
                    logger.warning(f"Subject invalide: {subject}")
                    pass
            
            difficulty_enum = None
            if difficulty:
                try:
                    difficulty_enum = Difficulty(difficulty)
                except ValueError:
                    logger.warning(f"Difficulty invalide: {difficulty}")
                    pass
            
            result = await ModuleService.get_modules(
                subject=subject_enum,
                difficulty=difficulty_enum,
                search=search,
                skip=skip,
                limit=limit
            )
            return result or []
        except Exception as e:
            logger.error(f"Erreur dans CachedModuleService.get_modules: {e}", exc_info=True)
            # Retourner une liste vide en cas d'erreur
            return []
    
    @staticmethod
    @cache_result(ttl=1800, key_prefix="cache:modules:detail")  # 30 minutes
    async def get_module(module_id: str) -> Dict[str, Any]:
        """Récupère un module avec cache"""
        return await ModuleService.get_module(module_id)
    
    @staticmethod
    async def create_module(module_data) -> Dict[str, Any]:
        """Crée un module et invalide le cache"""
        result = await ModuleService.create_module(module_data)
        await invalidate_cache("cache:modules:*")
        return result
    
    @staticmethod
    async def update_module(module_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Met à jour un module et invalide le cache"""
        result = await ModuleService.update_module(module_id, update_data)
        await invalidate_cache("cache:modules:*")
        return result
    
    @staticmethod
    async def delete_module(module_id: str) -> bool:
        """Supprime un module et invalide le cache"""
        result = await ModuleService.delete_module(module_id)
        await invalidate_cache("cache:modules:*")
        return result

