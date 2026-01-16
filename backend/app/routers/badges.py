"""
Routeur pour les badges et récompenses
"""
from fastapi import APIRouter, Depends
from typing import List
from app.models import Badge
# Authentification supprimée - toutes les routes sont publiques
from app.services.badge_service import BadgeService

router = APIRouter()


@router.get("/", response_model=List[Badge])
async def get_user_badges(current_user: dict = Depends(get_current_user)):
    """Récupère tous les badges de l'utilisateur"""
    return await BadgeService.get_user_badges("anonymous")  # Auth supprimée


@router.get("/count")
async def get_badge_count(current_user: dict = Depends(get_current_user)):
    """Compte le nombre de badges de l'utilisateur"""
    count = await BadgeService.get_badge_count("anonymous")  # Auth supprimée
    return {"count": count}

