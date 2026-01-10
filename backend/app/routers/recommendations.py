"""
Routeur pour les recommandations personnalisées
"""
from fastapi import APIRouter, Depends, Query
from typing import List
from app.models import Module
from app.utils.permissions import get_current_user
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.get("/", response_model=List[Module])
async def get_recommendations(
    limit: int = Query(5, ge=1, le=20),
    current_user: dict = Depends(get_current_user)
):
    """Récupère les recommandations personnalisées pour l'utilisateur"""
    return await RecommendationService.get_recommendations(current_user["id"], limit)

