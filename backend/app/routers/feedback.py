"""
Routeur pour le feedback utilisateur
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional
from app.models.feedback import Feedback
from app.services.feedback_service import FeedbackService
from app.utils.security import InputSanitizer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", status_code=201)
async def create_feedback(
    feedback: Feedback
):
    """Crée un nouveau feedback (route publique)"""
    try:
        feedback_data = feedback.dict()
        # Utiliser un user_id par défaut car auth supprimée
        feedback_data["user_id"] = "anonymous"
        
        # Sanitizer les champs
        if "question" in feedback_data:
            feedback_data["question"] = InputSanitizer.sanitize_string(
                feedback_data["question"], max_length=1000
            )
        if "response" in feedback_data:
            feedback_data["response"] = InputSanitizer.sanitize_string(
                feedback_data["response"], max_length=5000
            )
        if "comment" in feedback_data and feedback_data["comment"]:
            feedback_data["comment"] = InputSanitizer.sanitize_string(
                feedback_data["comment"], max_length=500
            )
        
        result = await FeedbackService.create_feedback(feedback_data)
        
        # Enregistrer la métrique Prometheus
        try:
            from app.utils.prometheus_metrics import MetricsCollector
            MetricsCollector.record_user_feedback(
                feedback_data.get("feedback_type", "unknown")
            )
        except Exception:
            pass  # Prometheus optionnel
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la création du feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du feedback"
        )


@router.get("/")
async def get_my_feedback(
    limit: int = 100
):
    """Récupère tous les feedbacks (route publique)"""
    try:
        # Retourner tous les feedbacks car auth supprimée
        from app.repositories.feedback_repository import FeedbackRepository
        return await FeedbackRepository.find_all(limit=limit)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des feedbacks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des feedbacks"
        )


@router.get("/stats")
async def get_feedback_stats(
    model: Optional[str] = None
):
    """Récupère les statistiques de feedback (route publique)"""
    try:
        # Retourner les stats globales car auth supprimée
        return await FeedbackService.get_stats("anonymous", model)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des stats"
        )
