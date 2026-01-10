"""
Routeur pour la conformité RGPD
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from app.services.gdpr_service import GDPRService
from app.utils.permissions import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/export-data", response_model=Dict[str, Any])
async def export_user_data(
    current_user: dict = Depends(get_current_user)
):
    """
    Exporte toutes les données de l'utilisateur connecté
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        export_data = await GDPRService.export_user_data(user_id)
        
        # Retourner en JSON avec headers appropriés
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Type": "application/json",
                "Content-Disposition": f'attachment; filename="user_data_{user_id}.json"'
            }
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'export: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.delete("/delete-data", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_data(
    current_user: dict = Depends(get_current_user)
):
    """
    Supprime toutes les données de l'utilisateur (droit à l'oubli)
    """
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        
        success = await GDPRService.delete_user_data(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la suppression"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )











