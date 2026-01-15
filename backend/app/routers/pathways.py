"""
Routeur pour les parcours d'apprentissage intelligents
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.models.pathway import (
    Pathway,
    PathwayCreate,
    PathwayRecommendation,
    PrerequisiteAnalysis
)
from app.models import Subject, Difficulty
from app.services.pathway_generator_service import PathwayGeneratorService
from app.services.prerequisite_detector import PrerequisiteDetector
from app.repositories.pathway_repository import PathwayRepository
# Authentification supprimée - toutes les routes sont publiques
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=Pathway, status_code=status.HTTP_201_CREATED)
async def generate_pathway(
    subject: Subject,
    target_level: Difficulty,
    learning_objectives: Optional[List[str]] = None,
):
    """
    Génère automatiquement un parcours d'apprentissage personnalisé (route publique)
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        pathway = await PathwayGeneratorService.generate_pathway(
            subject=subject,
            target_level=target_level,
            user_id=user_id,
            learning_objectives=learning_objectives
        )
        
        return pathway
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de la génération du parcours: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )


@router.get("/recommendations", response_model=List[PathwayRecommendation])
async def get_pathway_recommendations(
    limit: int = Query(5, ge=1, le=20),
):
    """
    Recommande des parcours (route publique)
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        recommendations = await PathwayGeneratorService.recommend_pathways(
            user_id=user_id,
            limit=limit
        )
        
        return recommendations
    except Exception as e:
        logger.error(f"Erreur lors de la génération de recommandations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la génération: {str(e)}"
        )


@router.get("/", response_model=List[Pathway])
async def get_pathways(
    subject: Optional[Subject] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Récupère la liste des parcours avec filtres optionnels
    """
    try:
        pathways = await PathwayRepository.find_all(
            subject=subject.value if subject else None,
            status=status,
            limit=limit,
            skip=skip
        )
        return [Pathway(**p) for p in pathways]
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des parcours: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération: {str(e)}"
        )


@router.get("/{pathway_id}", response_model=Pathway)
async def get_pathway(pathway_id: str):
    """
    Récupère un parcours spécifique
    """
    pathway_data = await PathwayRepository.find_by_id(pathway_id)
    if not pathway_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcours non trouvé"
        )
    return Pathway(**pathway_data)


@router.post("/", response_model=Pathway, status_code=status.HTTP_201_CREATED)
async def create_pathway(
    pathway_data: PathwayCreate,
):
    """
    Crée un nouveau parcours (route publique)
    """
    try:
        from datetime import datetime, timezone
        pathway_dict = {
            **pathway_data.dict(),
            "status": "draft",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        saved_pathway = await PathwayRepository.create(pathway_dict)
        return Pathway(**saved_pathway)
    except Exception as e:
        logger.error(f"Erreur lors de la création du parcours: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création: {str(e)}"
        )


@router.get("/prerequisites/{module_id}", response_model=PrerequisiteAnalysis)
async def analyze_prerequisites(
    module_id: str,
):
    """
    Analyse les prérequis d'un module (route publique)
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        analysis = await PrerequisiteDetector.analyze_prerequisites(
            module_id=module_id,
            user_id=user_id
        )
        
        return analysis
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des prérequis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'analyse: {str(e)}"
        )











