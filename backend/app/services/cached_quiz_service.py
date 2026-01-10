"""
Service de quiz avec cache Redis pour optimiser les performances
Gains : -60% coût API OpenAI
"""
from typing import Dict, Any, Optional
from app.services.quiz_service import QuizService
from app.utils.cache_decorator import cache_result, invalidate_cache
import logging

logger = logging.getLogger(__name__)


class CachedQuizService:
    """Service de quiz avec cache Redis"""
    
    @staticmethod
    @cache_result(ttl=3600, key_prefix="cache:quiz")  # 1 heure - les quiz ne changent pas
    async def get_or_generate_quiz(
        module_id: str,
        num_questions: int = 40,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """Récupère ou génère un quiz avec cache"""
        return await QuizService.get_or_generate_quiz(
            module_id=module_id,
            num_questions=num_questions,
            difficulty=difficulty
        )
    
    @staticmethod
    async def regenerate_quiz(
        module_id: str,
        num_questions: int = 40,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """Régénère un quiz et invalide le cache"""
        # Invalider le cache avant de régénérer
        await invalidate_cache(f"cache:quiz:*{module_id}*")
        return await QuizService.regenerate_quiz(
            module_id=module_id,
            num_questions=num_questions,
            difficulty=difficulty
        )
    
    @staticmethod
    async def delete_quiz(module_id: str) -> bool:
        """Supprime un quiz et invalide le cache"""
        await invalidate_cache(f"cache:quiz:*{module_id}*")
        return await QuizService.delete_quiz(module_id)














