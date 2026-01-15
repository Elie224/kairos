"""
Service pour la gestion de la progression - Business logic
"""
from typing import Dict, Any, Optional
from app.repositories.progress_repository import ProgressRepository
from app.models import ProgressCreate
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ProgressService:
    """Service pour la gestion de la progression"""
    
    @staticmethod
    async def get_user_progress(user_id: str, module_id: Optional[str] = None, limit: int = 100) -> list:
        """Récupère la progression d'un utilisateur"""
        try:
            # Valider user_id
            if not user_id:
                logger.warning("get_user_progress appelé avec user_id vide")
                return []
            
            if module_id:
                try:
                    progress = await ProgressRepository.find_by_user_and_module(user_id, module_id)
                    return [progress] if progress else []
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération de la progression pour module {module_id}: {e}", exc_info=True)
                    return []
            
            try:
                return await ProgressRepository.find_by_user(user_id, limit)
            except ConnectionError as ce:
                logger.warning(f"Base de données indisponible lors de la récupération de la progression: {ce}")
                # Retourner une liste vide au lieu de lever une exception
                return []
            except Exception as e:
                logger.error(f"Erreur dans ProgressService.get_user_progress: {e}", exc_info=True)
                # Renvoyer une liste vide afin de ne pas bloquer l'UI en cas d'erreur mineure
                return []
        except Exception as e:
            logger.error(f"Erreur inattendue dans get_user_progress: {e}", exc_info=True)
            return []
    
    @staticmethod
    async def get_module_progress(user_id: str, module_id: str) -> Optional[Dict[str, Any]]:
        """Récupère la progression d'un utilisateur pour un module spécifique"""
        return await ProgressRepository.find_by_user_and_module(user_id, module_id)
    
    @staticmethod
    async def get_user_progress_for_module(user_id: str, module_id: str) -> Optional[Dict[str, Any]]:
        """Récupère la progression d'un utilisateur pour un module"""
        return await ProgressRepository.find_by_user_and_module(user_id, module_id)
    
    @staticmethod
    async def create_or_update_progress(
        user_id: str,
        progress_data: ProgressCreate
    ) -> Dict[str, Any]:
        """Crée ou met à jour une entrée de progression"""
        existing = await ProgressRepository.find_by_user_and_module(
            user_id,
            progress_data.module_id
        )
        
        progress_dict = {
            "completed": progress_data.completed,
            "time_spent": progress_data.time_spent,
        }
        
        if progress_data.score is not None:
            progress_dict["score"] = progress_data.score
        
        if progress_data.completed:
            progress_dict["completed_at"] = datetime.now(timezone.utc)
            # Vérifier et attribuer des badges
            try:
                from app.services.badge_service import BadgeService
                await BadgeService.check_and_award_badges(user_id)
            except Exception as e:
                logger.warning(f"Erreur lors de l'attribution des badges: {e}")
        
        # Toujours utiliser upsert pour éviter les race conditions
        # Cela garantit une opération atomique même si l'entrée n'existe pas encore
        if not existing:
            progress_dict["attempts"] = 1
            progress_dict["started_at"] = datetime.now(timezone.utc)
        else:
            progress_dict["attempts"] = existing.get("attempts", 0) + 1
        
        progress_dict["updated_at"] = datetime.now(timezone.utc)
        
        # Utiliser upsert pour garantir l'atomicité
        return await ProgressRepository.upsert(user_id, progress_data.module_id, progress_dict)
    
    @staticmethod
    async def get_progress_stats(user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques de progression d'un utilisateur (OPTIMISÉ - une seule requête d'agrégation)"""
        try:
            # Valider user_id
            if not user_id:
                logger.warning("get_progress_stats appelé avec user_id vide")
                return {
                    "total_modules": 0,
                    "completed_modules": 0,
                    "completion_rate": 0,
                    "total_time_spent": 0,
                    "average_score": None
                }
            
            from app.database import get_database
            from app.utils.security import InputSanitizer
            
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                return {
                    "total_modules": 0,
                    "completed_modules": 0,
                    "completion_rate": 0,
                    "total_time_spent": 0,
                    "average_score": None
                }
            
            db = get_database()
            if db is None:
                return {
                    "total_modules": 0,
                    "completed_modules": 0,
                    "completion_rate": 0,
                    "total_time_spent": 0,
                    "average_score": None
                }
            
            # OPTIMISATION: Une seule requête d'agrégation pour toutes les stats (beaucoup plus rapide)
            # Au lieu de 4 requêtes séparées, on fait tout en une seule
            pipeline = [
                {"$match": {"user_id": sanitized_user_id}},
                {"$group": {
                    "_id": None,
                    "completed_modules": {
                        "$sum": {"$cond": [{"$eq": ["$completed", True]}, 1, 0]}
                    },
                    "total_time_spent": {
                        "$sum": {"$ifNull": ["$time_spent", 0]}
                    },
                    "average_score": {
                        "$avg": {
                            "$cond": [
                                {"$and": [
                                    {"$ne": ["$score", None]},
                                    {"$type": ["$score", "number"]}
                                ]},
                                "$score",
                                None
                            ]
                        }
                    },
                    "scores_count": {
                        "$sum": {
                            "$cond": [
                                {"$and": [
                                    {"$ne": ["$score", None]},
                                    {"$type": ["$score", "number"]}
                                ]},
                                1,
                                0
                            ]
                        }
                    }
                }}
            ]
            
            # Exécuter l'agrégation optimisée
            result = await db.progress.aggregate(pipeline, allowDiskUse=True).to_list(length=1)
            
            # Récupérer les résultats
            if result and result[0]:
                stats = result[0]
                completed_modules = stats.get("completed_modules", 0) or 0
                total_time = stats.get("total_time_spent", 0) or 0
                avg_score = stats.get("average_score")
                scores_count = stats.get("scores_count", 0) or 0
                
                # Si aucun score, avg_score est None
                if scores_count == 0:
                    avg_score = None
            else:
                completed_modules = 0
                total_time = 0
                avg_score = None
            
            # Compter le total de modules disponibles (cette requête peut être mise en cache séparément)
            # OPTIMISATION: Utiliser count_documents avec projection vide pour performance
            total_modules_available = await db.modules.count_documents({})
            
            # Calculer le taux de complétion
            completion_rate = (completed_modules / total_modules_available * 100) if total_modules_available > 0 else 0
            
            return {
                "total_modules": total_modules_available,
                "completed_modules": completed_modules,
                "completion_rate": round(completion_rate, 2),
                "total_time_spent": int(total_time),
                "average_score": round(avg_score, 2) if avg_score is not None else None
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques de progression: {e}", exc_info=True)
            # Retourner des valeurs par défaut en cas d'erreur
            return {
                "total_modules": 0,
                "completed_modules": 0,
                "completion_rate": 0,
                "total_time_spent": 0,
                "average_score": None
            }
    
    @staticmethod
    async def update_progress_time(user_id: str, module_id: str, time_spent: int) -> Dict[str, Any]:
        """Met à jour le temps passé sur un module"""
        existing = await ProgressRepository.find_by_user_and_module(user_id, module_id)
        
        if existing:
            update_data = {
                "time_spent": existing.get("time_spent", 0) + time_spent,
                "updated_at": datetime.now(timezone.utc)
            }
            # Utiliser upsert pour éviter les problèmes
            return await ProgressRepository.upsert(user_id, module_id, update_data)
        else:
            progress_data = {
                "user_id": user_id,
                "module_id": module_id,
                "time_spent": time_spent,
                "completed": False,
                "started_at": datetime.now(timezone.utc),
                "attempts": 1
            }
            return await ProgressRepository.create(progress_data)


