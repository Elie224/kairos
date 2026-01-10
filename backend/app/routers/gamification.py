"""
Routeur pour la gamification avancée
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.models.gamification import Quest, UserQuest, LeaderboardEntry, Challenge
from app.models import Subject, Difficulty
from app.services.gamification_service import GamificationService
from app.utils.permissions import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/quests", response_model=List[Quest])
async def get_personalized_quests(
    limit: int = Query(5, ge=1, le=20),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère les quêtes personnalisées pour l'utilisateur
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        quests = await GamificationService.generate_personalized_quests(
            user_id=user_id,
            limit=limit
        )
        return quests
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des quêtes: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/quests/{quest_id}/progress", response_model=UserQuest)
async def update_quest_progress(
    quest_id: str,
    progress_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Met à jour la progression d'une quête
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        user_quest = await GamificationService.update_quest_progress(
            user_id=user_id,
            quest_id=quest_id,
            progress_data=progress_data
        )
        return user_quest
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    leaderboard_type: str = Query("points", pattern="^(points|modules|streak)$"),
    subject: Optional[Subject] = Query(None),
    limit: int = Query(100, ge=1, le=500)
):
    """
    Récupère un classement intelligent
    """
    try:
        entries = await GamificationService.get_leaderboard(
            leaderboard_type=leaderboard_type,
            subject=subject,
            limit=limit
        )
        return entries
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du classement: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/challenges", response_model=Challenge, status_code=status.HTTP_201_CREATED)
async def create_challenge(
    title: str,
    description: str,
    target: dict,
    difficulty: Difficulty,
    deadline_days: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(get_current_user)
):
    """
    Crée un défi personnalisé
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        challenge = await GamificationService.create_personalized_challenge(
            user_id=user_id,
            title=title,
            description=description,
            target=target,
            difficulty=difficulty,
            deadline_days=deadline_days
        )
        return challenge
    except Exception as e:
        logger.error(f"Erreur lors de la création du défi: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )











