"""
Routeur pour la génération automatique d'exercices TD/TP
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any
from app.models import Difficulty
from app.services.exercise_generator_service import ExerciseGeneratorService
# Authentification supprimée - toutes les routes sont publiques
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/td/{module_id}", response_model=List[Dict[str, Any]])
async def generate_td_exercises(
    module_id: str,
    num_exercises: int = Query(5, ge=1, le=20),
    difficulty: Difficulty = Query(None),
):
    """
    Génère automatiquement des exercices de TD pour un module
    """
    try:
        exercises = await ExerciseGeneratorService.generate_td_exercises(
            module_id=module_id,
            num_exercises=num_exercises,
            difficulty=difficulty
        )
        return exercises
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la génération d'exercices TD: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )


@router.post("/tp/{module_id}", response_model=List[Dict[str, Any]])
async def generate_tp_steps(
    module_id: str,
    num_steps: int = Query(5, ge=1, le=15),
):
    """
    Génère automatiquement des étapes de TP pour un module
    """
    try:
        steps = await ExerciseGeneratorService.generate_tp_steps(
            module_id=module_id,
            num_steps=num_steps
        )
        return steps
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la génération d'étapes TP: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )


@router.post("/solution", response_model=Dict[str, Any])
async def generate_solution(
    exercise: Dict[str, Any],
    exercise_type: str = Query("td", pattern="^(td|tp)$"),
):
    """
    Génère une solution détaillée pour un exercice
    """
    try:
        solution = await ExerciseGeneratorService.generate_solution(
            exercise=exercise,
            exercise_type=exercise_type
        )
        return solution
    except Exception as e:
        logger.error(f"Erreur lors de la génération de solution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )











