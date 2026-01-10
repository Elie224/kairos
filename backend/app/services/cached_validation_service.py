"""
Service de validation avec cache Redis pour optimiser les performances
"""
from typing import List
from app.services.validation_service import ValidationService
from app.utils.cache_decorator import cache_result, invalidate_cache
import logging

logger = logging.getLogger(__name__)


class CachedValidationService:
    """Service de validation avec cache Redis"""
    
    @staticmethod
    @cache_result(ttl=600, key_prefix="cache:validations:user", include_user=True)  # 10 minutes
    async def get_user_validations(user_id: str) -> List[dict]:
        """Récupère les validations avec cache"""
        return await ValidationService.get_user_validations(user_id)
    
    @staticmethod
    @cache_result(ttl=600, key_prefix="cache:validations:modules", include_user=True)  # 10 minutes
    async def get_validated_modules(user_id: str) -> List[str]:
        """Récupère les modules validés avec cache"""
        return await ValidationService.get_validated_modules(user_id)
    
    @staticmethod
    @cache_result(ttl=300, key_prefix="cache:validations:module", include_user=True)  # 5 minutes
    async def get_module_validation(user_id: str, module_id: str):
        """Récupère la validation d'un module avec cache"""
        return await ValidationService.get_module_validation(user_id, module_id)
    
    @staticmethod
    async def validate_module(user_id: str, module_id: str, exam_attempt_id: str, score: float) -> bool:
        """Valide un module et invalide le cache"""
        result = await ValidationService.validate_module(user_id, module_id, exam_attempt_id, score)
        await invalidate_cache(f"cache:validations:*{user_id}*")
        return result














