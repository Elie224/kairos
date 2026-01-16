"""
Routeur pour Learning Analytics avancé
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.services.learning_analytics_service import LearningAnalyticsService
# Authentification supprimée - toutes les routes sont publiques
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dropout-risk", response_model=Dict[str, Any])
async def get_dropout_risk(
):
    """
    Détecte le risque de décrochage pour l'utilisateur connecté
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
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
):
    """
    Prédit la probabilité de réussite pour un module
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
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
):
    """
    Génère une heatmap des difficultés par notion
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        heatmap = await LearningAnalyticsService.generate_difficulty_heatmap(user_id)
        return heatmap
    except Exception as e:
        logger.error(f"Erreur lors de la génération de heatmap: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )











