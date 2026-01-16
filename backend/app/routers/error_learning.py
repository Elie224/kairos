"""
Routeur pour le mode "Apprendre par l'erreur"
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.services.error_analysis_service import ErrorAnalysisService
# Authentification supprimée - toutes les routes sont publiques
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_error(
    user_answer: str,
    correct_answer: str,
    question: str,
    module_id: str = None,
):
    """
    Analyse une erreur et génère une explication ciblée
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        # Récupérer le contexte du module si fourni
        module_context = None
        if module_id:
            from app.repositories.module_repository import ModuleRepository
            module = await ModuleRepository.find_by_id(module_id)
            if module:
                module_context = {
                    "title": module.get("title"),
                    "subject": module.get("subject"),
                    "learning_objectives": module.get("learning_objectives", [])
                }
        
        analysis = await ErrorAnalysisService.analyze_error(
            user_answer=user_answer,
            correct_answer=correct_answer,
            question=question,
            module_context=module_context
        )
        
        return analysis
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse d'erreur: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )











