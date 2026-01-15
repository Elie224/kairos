"""
Routeur pour l'IA pédagogique adaptative
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.models.adaptive_learning import (
    AdaptiveDiagnostic,
    LearningProfile,
    AdaptiveRecommendation,
    DifficultyAdjustment,
    AdaptiveContentRequest,
    AdaptiveContentResponse
)
from app.services.adaptive_learning_service import AdaptiveLearningService
# Authentification supprimée - toutes les routes sont publiques
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/diagnostic", response_model=AdaptiveDiagnostic, status_code=status.HTTP_201_CREATED)
async def run_diagnostic(
    diagnostic_answers: Dict[str, Any],
    current_user: dict = Depends()
):
    """
    Exécute un diagnostic initial pour déterminer le niveau et le profil de l'apprenant
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        diagnostic = await AdaptiveLearningService.run_initial_diagnostic(
            user_id=user_id,
            diagnostic_answers=diagnostic_answers
        )
        
        return diagnostic
    except Exception as e:
        logger.error(f"Erreur lors du diagnostic: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du diagnostic: {str(e)}"
        )


@router.get("/profile", response_model=LearningProfile)
async def get_profile(current_user: dict = Depends()):
    """
    Récupère le profil d'apprentissage de l' (route publique) connecté
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        profile = await AdaptiveLearningService.get_learning_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profil d'apprentissage non trouvé. Exécutez d'abord un diagnostic."
            )
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du profil: {str(e)}"
        )


@router.post("/adapt-difficulty/{module_id}", response_model=DifficultyAdjustment)
async def adapt_difficulty(
    module_id: str,
    performance_data: Dict[str, Any],
    current_user: dict = Depends()
):
    """
    Adapte la difficulté d'un module basé sur les performances de l'utilisateur
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        adjustment = await AdaptiveLearningService.adapt_difficulty(
            user_id=user_id,
            module_id=module_id,
            performance_data=performance_data
        )
        
        return adjustment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'adaptation de difficulté: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'adaptation: {str(e)}"
        )


@router.post("/adaptive-content", response_model=AdaptiveContentResponse)
async def get_adaptive_content(
    request: AdaptiveContentRequest,
    current_user: dict = Depends()
):
    """
    Génère du contenu adapté selon le profil de l'utilisateur
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        # S'assurer que le user_id correspond
        request.user_id = user_id
        
        content = await AdaptiveLearningService.generate_adaptive_content(request)
        return content
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la génération de contenu adaptatif: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )


@router.get("/recommendations", response_model=List[AdaptiveRecommendation])
async def get_recommendations(
    limit: int = 5,
    current_user: dict = Depends()
):
    """
    Génère des recommandations adaptatives pour l'utilisateur
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        recommendations = await AdaptiveLearningService.get_recommendations(
            user_id=user_id,
            limit=limit
        )
        
        return recommendations
    except Exception as e:
        logger.error(f"Erreur lors de la génération de recommandations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )











