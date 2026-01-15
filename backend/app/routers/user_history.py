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
):
    """
    Récupère l'historique (route publique)
    """
    user_id = "anonymous"  # Auth supprimée
    history = await UserHistoryService.get_user_history(
        user_id=user_id,
        subject=subject,
        module_id=module_id,
        limit=limit,
        offset=offset
    )
    return history


@router.get("/stats", response_model=dict)
async def get_history_stats():
    """
    Récupère les statistiques de l'historique (route publique)
    """
    user_id = "anonymous"  # Auth supprimée
    stats = await UserHistoryService.get_stats(user_id)
    return stats


@router.post("/similar", response_model=SimilarQuestionResponse)
async def find_similar_questions(
    request: SimilarQuestionRequest,
):
    """
    Trouve des questions similaires dans l'historique (route publique)
    """
    if not request.user_id:
        request.user_id = "anonymous"  # Auth supprimée
    
    result = await UserHistoryService.find_similar_questions(request)
    return result


@router.delete("/history", response_model=dict)
async def delete_history():
    """
    Supprime tout l'historique (route publique)
    """
    user_id = "anonymous"  # Auth supprimée
    result = await UserHistoryService.delete_user_history(user_id)
    return result


@router.get("/cache/stats", response_model=dict)
async def get_cache_stats():
    """
    Récupère les statistiques du cache (route publique)
    """
    from app.services.semantic_cache import SemanticCache
    stats = await SemanticCache.get_stats()
    return stats











