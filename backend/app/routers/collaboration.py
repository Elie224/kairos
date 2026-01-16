"""
Routeur pour la collaboration intelligente
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from app.services.collaboration_service import CollaborationService
# Authentification supprimée - toutes les routes sont publiques
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/groups", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_smart_group(
    user_ids: List[str],
    module_id: str,
    group_size: int = 4,
):
    """
    Crée un groupe intelligent avec répartition automatique des rôles
    """
    try:
        # Auth supprimée - pas de vérification d'utilisateur
        
        group = await CollaborationService.create_smart_group(
            user_ids=user_ids,
            module_id=module_id,
            group_size=group_size
        )
        return group
    except Exception as e:
        logger.error(f"Erreur lors de la création du groupe: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/groups/{group_id}/feedback", response_model=Dict[str, Any])
async def get_group_feedback(
    group_id: str,
    work_submitted: Dict[str, Any],
):
    """
    Génère un feedback collectif pour le groupe
    """
    try:
        feedback = await CollaborationService.generate_group_feedback(
            group_id=group_id,
            work_submitted=work_submitted
        )
        return feedback
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la génération de feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )











