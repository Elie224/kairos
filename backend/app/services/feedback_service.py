"""
Service pour la gestion du feedback utilisateur
"""
from typing import Dict, Any, Optional
from app.repositories.feedback_repository import FeedbackRepository
from app.models.feedback import Feedback
import logging

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service pour la gestion du feedback"""
    
    @staticmethod
    async def create_feedback(feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau feedback"""
        try:
            return await FeedbackRepository.create(feedback_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création du feedback: {e}")
            raise
    
    @staticmethod
    async def get_user_feedback(user_id: str, limit: int = 100) -> list:
        """Récupère les feedbacks d'un utilisateur"""
        try:
            return await FeedbackRepository.find_by_user(user_id, limit)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des feedbacks: {e}")
            return []
    
    @staticmethod
    async def get_stats(user_id: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """Récupère les statistiques de feedback"""
        try:
            return await FeedbackRepository.get_stats(user_id, model)
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return {
                "useful": 0,
                "not_useful": 0,
                "total": 0,
                "avg_rating": 0.0
            }
