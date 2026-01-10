"""
Routeur pour Learning Analytics avancé
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.services.learning_analytics_service import LearningAnalyticsService
from app.utils.permissions import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dropout-risk", response_model=Dict[str, Any])
async def get_dropout_risk(
    current_user: dict = Depends(get_current_user)
):
    """
    Détecte le risque de décrochage pour l'utilisateur connecté
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        risk_analysis = await LearningAnalyticsService.detect_dropout_risk(user_id)
        return risk_analysis
    except Exception as e:
        logger.error(f"Erreur lors de la détection de décrochage: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )


@router.get("/success-prediction/{module_id}", response_model=Dict[str, Any])
async def predict_success(
    module_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Prédit la probabilité de réussite pour un module
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        prediction = await LearningAnalyticsService.predict_success(user_id, module_id)
        return prediction
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la prédiction: {str(e)}"
        )


@router.get("/difficulty-heatmap", response_model=Dict[str, Any])
async def get_difficulty_heatmap(
    current_user: dict = Depends(get_current_user)
):
    """
    Génère une heatmap des difficultés par notion
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        heatmap = await LearningAnalyticsService.generate_difficulty_heatmap(user_id)
        return heatmap
    except Exception as e:
        logger.error(f"Erreur lors de la génération de heatmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )











