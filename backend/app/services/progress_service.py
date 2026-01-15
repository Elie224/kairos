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
        """Récupère les statistiques de progression d'un utilisateur"""
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
            
            # Obtenir le nombre total de modules disponibles dans la base de données
            total_modules_available = 0
            try:
                from app.database import get_database
                db = get_database()
                if db is not None:
                    total_modules_available = await db.modules.count_documents({})
            except Exception as db_error:
                logger.warning(f"Erreur lors du comptage des modules: {db_error}")
                total_modules_available = 0
            
            # Obtenir les statistiques de progression de l'utilisateur avec gestion d'erreur individuelle
            completed_modules = 0
            total_time = 0
            avg_score = None
            
            try:
                completed_modules = await ProgressRepository.count_completed(user_id) or 0
            except Exception as e:
                logger.warning(f"Erreur lors du comptage des modules complétés: {e}")
                completed_modules = 0
            
            try:
                total_time = await ProgressRepository.get_total_time_spent(user_id) or 0
            except Exception as e:
                logger.warning(f"Erreur lors du calcul du temps total: {e}")
                total_time = 0
            
            try:
                avg_score = await ProgressRepository.get_average_score(user_id)
            except Exception as e:
                logger.warning(f"Erreur lors du calcul de la moyenne: {e}")
                avg_score = None
            
            # Utiliser le nombre total de modules disponibles pour le calcul du taux de complétion
            completion_rate = (completed_modules / total_modules_available * 100) if total_modules_available > 0 else 0
            
            return {
                "total_modules": total_modules_available,  # Nombre total de modules disponibles
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


