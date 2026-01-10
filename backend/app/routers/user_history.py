"""
Routeur pour l'historique utilisateur et le cache intelligent
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from app.models.user_history import (
    HistoryQuery, HistoryStats, SimilarQuestionRequest, SimilarQuestionResponse
)
from app.services.user_history_service import UserHistoryService
from app.utils.permissions import get_current_user
from app.models.user_history import Subject

router = APIRouter()


@router.get("/history", response_model=List[dict])
async def get_history(
    subject: Optional[Subject] = Query(None),
    module_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère l'historique de l'utilisateur connecté
    """
    user_id = current_user["id"]
    history = await UserHistoryService.get_user_history(
        user_id=user_id,
        subject=subject,
        module_id=module_id,
        limit=limit,
        offset=offset
    )
    return history


@router.get("/stats", response_model=dict)
async def get_history_stats(current_user: dict = Depends(get_current_user)):
    """
    Récupère les statistiques de l'historique utilisateur
    """
    user_id = current_user["id"]
    stats = await UserHistoryService.get_stats(user_id)
    return stats


@router.post("/similar", response_model=SimilarQuestionResponse)
async def find_similar_questions(
    request: SimilarQuestionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Trouve des questions similaires dans l'historique
    """
    if not request.user_id:
        request.user_id = current_user["id"]
    
    result = await UserHistoryService.find_similar_questions(request)
    return result


@router.delete("/history", response_model=dict)
async def delete_history(current_user: dict = Depends(get_current_user)):
    """
    Supprime tout l'historique de l'utilisateur (RGPD)
    """
    user_id = current_user["id"]
    result = await UserHistoryService.delete_user_history(user_id)
    return result


@router.get("/cache/stats", response_model=dict)
async def get_cache_stats(current_user: dict = Depends(get_current_user)):
    """
    Récupère les statistiques du cache pour l'utilisateur
    """
    from app.services.semantic_cache import SemanticCache
    stats = await SemanticCache.get_stats()
    return stats











