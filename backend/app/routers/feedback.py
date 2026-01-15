"""
Routeur pour le feedback utilisateur
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.models.feedback import Feedback
from app.services.feedback_service import FeedbackService
from app.utils.permissions import get_current_user
from app.utils.security import InputSanitizer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("/", status_code=201)
async def create_feedback(
    feedback: Feedback,
    current_user: dict = Depends(get_current_user)
):
    """Crée un nouveau feedback"""
    try:
        if not current_user or not current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        feedback_data = feedback.dict()
        feedback_data["user_id"] = current_user["id"]
        
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
    current_user: dict = Depends(get_current_user),
    limit: int = 100
):
    """Récupère les feedbacks de l'utilisateur actuel"""
    try:
        if not current_user or not current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        return await FeedbackService.get_user_feedback(current_user["id"], limit)
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
    current_user: dict = Depends(get_current_user),
    model: Optional[str] = None
):
    """Récupère les statistiques de feedback"""
    try:
        if not current_user or not current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        return await FeedbackService.get_stats(current_user["id"], model)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des stats"
        )
