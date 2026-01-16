"""
Routeur pour le suivi de progression - Refactorisé avec services
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from app.models import Progress, ProgressCreate
# Authentification supprimée - toutes les routes sont publiques
from app.services.progress_service import ProgressService
from app.services.cached_progress_service import CachedProgressService
from app.utils.security import InputSanitizer
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_user_progress(
    module_id: Optional[str] = Query(None, description="Filtrer par module"),
    limit: int = Query(100, description="Nombre maximum d'entrées retournées")
):
    """Récupère la progression (route publique)"""
    try:
        user_id = "anonymous"  # Auth supprimée
        if not user_id:
            logger.warning("GET /api/progress - user_id vide")
            return []
        
        logger.debug(f"GET /api/progress - user_id={user_id}, module_id={module_id}, limit={limit}")
        
        # Valider le module_id si fourni
        if module_id:
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_module_id:
                logger.warning(f"ID de module invalide: {module_id}")
                return []
            try:
                result = await CachedProgressService.get_user_progress(user_id, sanitized_module_id, limit)
                # S'assurer que le résultat est une liste
                if not isinstance(result, list):
                    logger.warning(f"get_user_progress a retourné un type inattendu: {type(result)}")
                    return []
                return result
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de la progression pour module {module_id}: {e}", exc_info=True)
                return []
        
        try:
            result = await CachedProgressService.get_user_progress(user_id, None, limit)
            # S'assurer que le résultat est une liste
            if not isinstance(result, list):
                logger.warning(f"get_user_progress a retourné un type inattendu: {type(result)}")
                return []
            return result
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la progression: {e}", exc_info=True)
            # Retourner une liste vide au lieu de lever une exception pour ne pas bloquer l'UI
            return []
    except HTTPException:
        raise
    except ConnectionError as ce:
        logger.error(f"Base de données indisponible lors de la récupération de la progression: {ce}", exc_info=True)
        # Retourner une liste vide au lieu de lever une exception
        return []
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la récupération de la progression: {e}", exc_info=True)
        # Retourner une liste vide au lieu de lever une exception pour ne pas bloquer l'UI
        return []


@router.post("/", response_model=Progress, status_code=201)
async def create_progress(progress_data: ProgressCreate):
    """Crée ou met à jour une entrée de progression"""
    # Valider le module_id
    sanitized_module_id = InputSanitizer.sanitize_object_id(progress_data.module_id)
    if not sanitized_module_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    # Créer une copie avec l'ID sanitizé
    progress_data.module_id = sanitized_module_id
    
    # Utiliser le service avec cache
    return await CachedProgressService.create_or_update_progress("anonymous", progress_data)  # Auth supprimée


@router.get("/stats")
async def get_progress_stats():
    """Récupère les statistiques de progression (route publique)"""
    try:
        user_id = "anonymous"  # Auth supprimée
        if not user_id:
            logger.warning("GET /api/progress/stats - user_id vide")
            return {
                "total_modules": 0,
                "completed_modules": 0,
                "completion_rate": 0,
                "total_time_spent": 0,
                "average_score": None
            }
        
        logger.debug(f"GET /api/progress/stats - user_id={user_id}")
        
        # Utiliser la méthode optimisée avec cache
        try:
            stats = await CachedProgressService.get_progress_stats(user_id)
        except Exception as service_error:
            logger.error(f"Erreur dans CachedProgressService.get_progress_stats: {service_error}", exc_info=True)
            # Si le service échoue, essayer directement sans cache
            try:
                from app.services.progress_service import ProgressService
                stats = await ProgressService.get_progress_stats(user_id)
            except Exception as direct_error:
                logger.error(f"Erreur dans ProgressService.get_progress_stats: {direct_error}", exc_info=True)
                stats = {
                    "total_modules": 0,
                    "completed_modules": 0,
                    "completion_rate": 0,
                    "total_time_spent": 0,
                    "average_score": None
                }
        
        # S'assurer que les valeurs sont correctement formatées et valides
        if not isinstance(stats, dict):
            logger.warning(f"Stats n'est pas un dictionnaire: {type(stats)}")
            stats = {}
        
        # Valider et formater les valeurs
        total_modules = int(stats.get("total_modules", 0) or 0)
        completed_modules = int(stats.get("completed_modules", 0) or 0)
        completion_rate = float(stats.get("completion_rate", 0) or 0)
        total_time_spent = int(stats.get("total_time_spent", 0) or 0)
        average_score = stats.get("average_score")
        
        # Valider average_score
        if average_score is not None:
            try:
                average_score = float(average_score)
                if average_score < 0 or average_score > 100:
                    average_score = None
            except (ValueError, TypeError):
                average_score = None
        
        return {
            "total_modules": total_modules,
            "completed_modules": completed_modules,
            "completion_rate": round(completion_rate, 2),
            "total_time_spent": total_time_spent,
            "average_score": round(average_score, 2) if average_score is not None else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}", exc_info=True)
        # Retourner des valeurs par défaut en cas d'erreur - NE JAMAIS LEVER D'EXCEPTION ICI
        return {
            "total_modules": 0,
            "completed_modules": 0,
            "completion_rate": 0,
            "total_time_spent": 0,
            "average_score": None
        }


@router.get("/{module_id}", response_model=Progress)
async def get_module_progress(
    module_id: str
):
    """Récupère la progression pour un module spécifique"""
    # Valider l'ObjectId
    sanitized_id = InputSanitizer.sanitize_object_id(module_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID de module invalide")
    
    progress = await CachedProgressService.get_module_progress("anonymous", sanitized_id)  # Auth supprimée
    if not progress:
        raise HTTPException(status_code=404, detail="Progression non trouvée")
    
    return progress





