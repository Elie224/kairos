"""
Routeur pour la mémoire pédagogique utilisateur
"""
from fastapi import APIRouter, HTTPException, status
from typing import Optional
from app.services.pedagogical_memory_service import PedagogicalMemoryService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pedagogical-memory", tags=["Pedagogical Memory"])


@router.get("/")
async def get_my_memory():
    """Récupère la mémoire pédagogique (route publique)"""
    try:
        # Utiliser un user_id par défaut car auth supprimée
        memory = await PedagogicalMemoryService.get_memory("anonymous")
        if not memory:
            return {
                "user_id": "anonymous",
                "subject_levels": {},
                "error_history": [],
                "learning_style": {
                    "preferred_format": "balanced",
                    "detail_level": "medium",
                    "examples_preference": True,
                    "visual_aids_preference": True
                }
            }
        return memory
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la mémoire: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de la mémoire"
        )


@router.get("/subject/{subject}/level")
async def get_subject_level(
    subject: str
):
    """Récupère le niveau pour une matière (route publique)"""
    try:
        # Utiliser un user_id par défaut car auth supprimée
        level = await PedagogicalMemoryService.get_subject_level("anonymous", subject)
        return {"subject": subject, "level": level}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du niveau: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération du niveau"
        )


@router.get("/errors/frequent")
async def get_frequent_errors(
    limit: int = 5
):
    """Récupère les erreurs fréquentes (route publique)"""
    try:
        # Utiliser un user_id par défaut car auth supprimée
        errors = await PedagogicalMemoryService.get_frequent_errors("anonymous", limit)
        return {"errors": errors}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des erreurs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des erreurs"
        )


@router.post("/errors")
async def record_error(
    concept: str,
    error_type: str
):
    """Enregistre une erreur dans la mémoire pédagogique (route publique)"""
    try:
        # Utiliser un user_id par défaut car auth supprimée
        await PedagogicalMemoryService.record_error("anonymous", concept, error_type)
        return {"message": "Erreur enregistrée"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement d'erreur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de l'enregistrement d'erreur"
        )


@router.put("/subject/{subject}/level")
async def update_subject_level(
    subject: str,
    level: str,
    confidence_score: float = 0.5
):
    """Met à jour le niveau pour une matière (route publique)"""
    try:
        if level not in ["beginner", "intermediate", "advanced"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le niveau doit être 'beginner', 'intermediate' ou 'advanced'"
            )
        
        # Utiliser un user_id par défaut car auth supprimée
        await PedagogicalMemoryService.update_level(
            "anonymous", subject, level, confidence_score
        )
        return {"message": "Niveau mis à jour", "subject": subject, "level": level}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du niveau: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du niveau"
        )
