"""
Service pour la conformité RGPD avancée
Export données, droit à l'oubli automatisé
"""
from typing import Dict, Any, List
from datetime import datetime, timezone
from app.repositories.user_repository import UserRepository
from app.repositories.progress_repository import ProgressRepository as ProgressRepo
from app.repositories.learning_profile_repository import LearningProfileRepository
import logging
import json

logger = logging.getLogger(__name__)


class GDPRService:
    """Service RGPD"""
    
    @staticmethod
    async def export_user_data(user_id: str) -> Dict[str, Any]:
        """
        Exporte toutes les données d'un utilisateur
        """
        try:
            # Récupérer toutes les données utilisateur
            user = await UserRepository.find_by_id(user_id)
            progress = await ProgressRepo.find_by_user(user_id, limit=1000)
            profile = await LearningProfileRepository.find_by_user_id(user_id)
            
            export_data = {
                "user_id": user_id,
                "export_date": datetime.now(timezone.utc).isoformat(),
                "user_data": user,
                "progress_data": progress,
                "learning_profile": profile,
                "format": "json",
                "version": "1.0"
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'export: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def delete_user_data(user_id: str) -> bool:
        """
        Supprime toutes les données d'un utilisateur (droit à l'oubli)
        """
        try:
            # Supprimer progress
            from app.database import get_database
            db = get_database()
            await db.progress.delete_many({"user_id": user_id})
            
            # Supprimer learning profile
            await db.learning_profiles.delete_many({"user_id": user_id})
            
            # Supprimer user (anonymiser plutôt que supprimer pour logs)
            await UserRepository.anonymize_user(user_id)
            
            # Journaliser la suppression
            await GDPRService._log_deletion(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def _log_deletion(user_id: str):
        """Journalise une suppression"""
        try:
            from app.database import get_database
            db = get_database()
            await db.gdpr_logs.insert_one({
                "user_id": user_id,
                "action": "data_deletion",
                "timestamp": datetime.now(timezone.utc),
                "reason": "user_request"
            })
        except Exception as e:
            logger.error(f"Erreur journalisation: {e}", exc_info=True)











