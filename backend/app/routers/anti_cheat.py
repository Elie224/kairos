"""
Routeur pour la détection de triche et plagiat
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from app.services.cheating_detector import CheatingDetector
# Authentification supprimée - toutes les routes sont publiques
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/plagiarism-check", response_model=Dict[str, Any])
async def check_plagiarism(
    user_answer: str,
    question: str,
    other_answers: List[str],
):
    """
    Vérifie la similarité avec d'autres réponses (détection plagiat)
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        plagiarism_check = await CheatingDetector.detect_plagiarism(
            user_answer=user_answer,
            other_answers=other_answers,
            question=question
        )
        
        return plagiarism_check
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de plagiat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la vérification: {str(e)}"
        )


@router.post("/behavior-analysis", response_model=Dict[str, Any])
async def analyze_behavior(
    answer_times: List[float],
    scores: List[float],
    average_time: float,
):
    """
    Analyse les anomalies comportementales
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        analysis = await CheatingDetector.analyze_behavior_anomalies(
            user_id=user_id,
            answer_times=answer_times,
            scores=scores,
            average_time=average_time
        )
        
        return analysis
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse comportementale: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )


@router.get("/suspicious-users", response_model=List[Dict[str, Any]])
async def get_suspicious_users(
):
    """
    Récupère la liste des utilisateurs suspects (admin seulement)
    """
    try:
        # À implémenter : récupérer tous les utilisateurs avec score de risque élevé
        # Pour l'instant, retourner liste vide
        return []
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs suspects: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )











