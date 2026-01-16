"""
Routeur pour les laboratoires virtuels interactifs
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any
from app.services.lab_simulation_service import LabSimulationService
# Authentification supprimée - toutes les routes sont publiques
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/config/{module_id}", response_model=Dict[str, Any])
async def get_simulation_config(
    module_id: str,
    simulation_type: str = Query("physics", pattern="^(physics|chemistry)$"),
):
    """
    Récupère la configuration de simulation pour un module
    """
    try:
        config = await LabSimulationService.get_simulation_config(
            module_id=module_id,
            simulation_type=simulation_type
        )
        return config
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/calculate/{module_id}", response_model=Dict[str, Any])
async def calculate_simulation(
    module_id: str,
    parameters: Dict[str, Any],
    simulation_type: str = Query("physics", pattern="^(physics|chemistry)$"),
):
    """
    Calcule les résultats d'une simulation avec paramètres donnés
    """
    try:
        results = await LabSimulationService.calculate_simulation(
            module_id=module_id,
            parameters=parameters,
            simulation_type=simulation_type
        )
        return results
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors du calcul: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )











