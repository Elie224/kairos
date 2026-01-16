"""
Routeur pour les badges et récompenses
"""
from fastapi import APIRouter, Depends
from typing import List
from app.models import Badge
from app.services.badge_service import BadgeService
from app.utils.permissions import get_current_user

router = APIRouter()


@router.get("/", response_model=List[Badge])
async def get_user_badges(
    current_user: dict = Depends(get_current_user)
):
    """Récupère tous les badges de l'utilisateur"""
    return await BadgeService.get_user_badges(str(current_user["id"]))


@router.get("/count")
async def get_badge_count(
    current_user: dict = Depends(get_current_user)
):
    """Compte le nombre de badges de l'utilisateur"""
    count = await BadgeService.get_user_badge_count(str(current_user["id"]))
    return {"count": count}

