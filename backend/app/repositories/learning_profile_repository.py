"""
Repository pour les profils d'apprentissage adaptatif
"""
from typing import Optional, Dict, Any, List
from app.database import get_database
from app.schemas import serialize_doc
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class LearningProfileRepository:
    """Repository pour gérer les profils d'apprentissage"""
    
    @staticmethod
    async def create_or_update(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée ou met à jour un profil d'apprentissage"""
        try:
            db = get_database()
            user_id = profile_data.get("user_id")
            
            if not user_id:
                raise ValueError("user_id est requis")
            
            # Vérifier si le profil existe déjà
            existing = await db.learning_profiles.find_one({"user_id": user_id})
            
            if existing:
                # Mettre à jour
                profile_data.pop("user_id", None)  # Ne pas mettre à jour user_id
                profile_data.pop("created_at", None)  # Ne pas modifier created_at
                result = await db.learning_profiles.update_one(
                    {"user_id": user_id},
                    {"$set": profile_data}
                )
                if result.modified_count > 0:
                    updated = await db.learning_profiles.find_one({"user_id": user_id})
                    return serialize_doc(updated)
            else:
                # Créer nouveau profil
                result = await db.learning_profiles.insert_one(profile_data)
                if result.inserted_id:
                    created = await db.learning_profiles.find_one({"_id": result.inserted_id})
                    return serialize_doc(created)
            
            return serialize_doc(existing) if existing else None
            
        except Exception as e:
            logger.error(f"Erreur lors de la création/mise à jour du profil: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def find_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Trouve un profil par user_id"""
        try:
            db = get_database()
            profile = await db.learning_profiles.find_one({"user_id": user_id})
            return serialize_doc(profile) if profile else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche du profil: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def update(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un profil"""
        try:
            db = get_database()
            update_data["updated_at"] = update_data.get("updated_at")
            
            result = await db.learning_profiles.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated = await db.learning_profiles.find_one({"user_id": user_id})
                return serialize_doc(updated)
            
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du profil: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def add_difficulty_adjustment(
        user_id: str,
        adjustment_data: Dict[str, Any]
    ) -> bool:
        """Ajoute un ajustement de difficulté à l'historique"""
        try:
            db = get_database()
            result = await db.learning_profiles.update_one(
                {"user_id": user_id},
                {
                    "$push": {"difficulty_history": adjustment_data},
                    "$inc": {"adaptation_frequency": 1}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de l'ajustement: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def update_subject_performance(
        user_id: str,
        subject: str,
        performance_data: Dict[str, Any]
    ) -> bool:
        """Met à jour les performances pour une matière"""
        try:
            db = get_database()
            result = await db.learning_profiles.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        f"subject_performance.{subject}": performance_data
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des performances: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def find_all(limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Récupère tous les profils (pour admin)"""
        try:
            db = get_database()
            cursor = db.learning_profiles.find().skip(skip).limit(limit)
            profiles = await cursor.to_list(length=limit)
            return [serialize_doc(p) for p in profiles]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des profils: {e}", exc_info=True)
            return []











