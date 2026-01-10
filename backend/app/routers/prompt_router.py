"""
Routeur pour les statistiques et configuration du Prompt Router
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional
from app.services.prompt_router_service import PromptRouterService
from app.utils.permissions import get_current_user

router = APIRouter()


@router.get("/stats", response_model=Dict[str, Any])
async def get_router_stats(current_user: dict = Depends(get_current_user)):
    """
    Récupère les statistiques du Prompt Router
    """
    return PromptRouterService.get_category_stats()


@router.post("/classify")
async def classify_message(
    message: str,
    context: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Classifie un message pour tester le système
    """
    category = await PromptRouterService.classify_request(message, context)
    model = PromptRouterService.CATEGORY_TO_MODEL.get(category, "gpt-5-mini")
    
    category_names = {
        1: "Explication simple / aide rapide",
        2: "Exercice standard / quiz",
        3: "Raisonnement complexe / TD / TP",
        4: "Analyse approfondie / diagnostic pédagogique"
    }
    
    return {
        "message": message,
        "category": category,
        "category_name": category_names.get(category, "Inconnue"),
        "recommended_model": model
    }

