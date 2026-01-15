"""
Routeur pour la mémoire pédagogique utilisateur
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from app.services.pedagogical_memory_service import PedagogicalMemoryService
from app.utils.permissions import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pedagogical-memory", tags=["Pedagogical Memory"])


@router.get("/")
async def get_my_memory(current_user: dict = Depends(get_current_user)):
    """Récupère la mémoire pédagogique de l'utilisateur actuel"""
    try:
        if not current_user or not current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        memory = await PedagogicalMemoryService.get_memory(current_user["id"])
        if not memory:
            return {
                "user_id": current_user["id"],
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
    subject: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupère le niveau d'un utilisateur pour une matière"""
    try:
        if not current_user or not current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        level = await PedagogicalMemoryService.get_subject_level(current_user["id"], subject)
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
    limit: int = 5,
    current_user: dict = Depends(get_current_user)
):
    """Récupère les erreurs fréquentes d'un utilisateur"""
    try:
        if not current_user or not current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        errors = await PedagogicalMemoryService.get_frequent_errors(current_user["id"], limit)
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
    error_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Enregistre une erreur dans la mémoire pédagogique"""
    try:
        if not current_user or not current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        await PedagogicalMemoryService.record_error(current_user["id"], concept, error_type)
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
    confidence_score: float = 0.5,
    current_user: dict = Depends(get_current_user)
):
    """Met à jour le niveau d'un utilisateur pour une matière"""
    try:
        if not current_user or not current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        if level not in ["beginner", "intermediate", "advanced"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le niveau doit être 'beginner', 'intermediate' ou 'advanced'"
            )
        
        await PedagogicalMemoryService.update_level(
            current_user["id"], subject, level, confidence_score
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
