"""
Routeur pour l'Avatar IA Enseignant
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any
from app.services.avatar_service import AvatarService
# Authentification supprimée - toutes les routes sont publiques
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate-script", response_model=Dict[str, Any])
async def generate_explanation_script(
    content: str,
    explanation_type: str = Query("step_by_step", pattern="^(visual|textual|step_by_step)$"),
):
    """
    Génère un script d'explication pour l'avatar
    """
    try:
        script = await AvatarService.generate_explanation_script(
            content=content,
            explanation_type=explanation_type
        )
        return script
    except Exception as e:
        logger.error(f"Erreur lors de la génération de script: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/speech-config", response_model=Dict[str, Any])
async def get_speech_config(
    text: str,
    language: str = Query("fr", pattern="^(fr|en)$"),
):
    """
    Récupère la configuration pour la synthèse vocale
    """
    try:
        config = await AvatarService.generate_speech_audio(
            text=text,
            language=language
        )
        return config
    except Exception as e:
        logger.error(f"Erreur lors de la génération de config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/config", response_model=Dict[str, Any])
async def get_avatar_config(
    avatar_type: str = Query("default", pattern="^(default|female)$")
):
    """
    Récupère la configuration de l'avatar
    """
    try:
        config = AvatarService.get_avatar_config(avatar_type=avatar_type)
        return config
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )











