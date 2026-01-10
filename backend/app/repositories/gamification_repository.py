"""
Repository pour la gamification
"""
from typing import Optional, Dict, Any, List
from app.database import get_database
from app.schemas import serialize_doc
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class GamificationRepository:
    """Repository pour gamification"""
    
    @staticmethod
    async def create_quest(quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une quête"""
        try:
            db = get_database()
            result = await db.quests.insert_one(quest_data)
            if result.inserted_id:
                created = await db.quests.find_one({"_id": result.inserted_id})
                return serialize_doc(created)
            raise ValueError("Échec création quête")
        except Exception as e:
            logger.error(f"Erreur création quête: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_quest(quest_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une quête"""
        try:
            db = get_database()
            if not ObjectId.is_valid(quest_id):
                return None
            quest = await db.quests.find_one({"_id": ObjectId(quest_id)})
            return serialize_doc(quest) if quest else None
        except Exception as e:
            logger.error(f"Erreur récupération quête: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def create_user_quest(user_quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une quête utilisateur"""
        try:
            db = get_database()
            result = await db.user_quests.insert_one(user_quest_data)
            if result.inserted_id:
                created = await db.user_quests.find_one({"_id": result.inserted_id})
                return serialize_doc(created)
            raise ValueError("Échec création quête utilisateur")
        except Exception as e:
            logger.error(f"Erreur création quête utilisateur: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_user_quest(user_id: str, quest_id: str) -> Optional[Dict[str, Any]]:
        """Récupère une quête utilisateur"""
        try:
            db = get_database()
            user_quest = await db.user_quests.find_one({
                "user_id": user_id,
                "quest_id": quest_id
            })
            return serialize_doc(user_quest) if user_quest else None
        except Exception as e:
            logger.error(f"Erreur récupération quête utilisateur: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def update_user_quest(
        user_id: str,
        quest_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Met à jour une quête utilisateur"""
        try:
            db = get_database()
            result = await db.user_quests.update_one(
                {"user_id": user_id, "quest_id": quest_id},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                updated = await db.user_quests.find_one({
                    "user_id": user_id,
                    "quest_id": quest_id
                })
                return serialize_doc(updated)
            return None
        except Exception as e:
            logger.error(f"Erreur mise à jour quête utilisateur: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_leaderboard(
        leaderboard_type: str = "points",
        subject: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Récupère un classement"""
        try:
            # Pour l'instant, retourner données basiques
            # À améliorer avec agrégation MongoDB
            return []
        except Exception as e:
            logger.error(f"Erreur récupération classement: {e}", exc_info=True)
            return []
    
    @staticmethod
    async def create_challenge(challenge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un défi"""
        try:
            db = get_database()
            result = await db.challenges.insert_one(challenge_data)
            if result.inserted_id:
                created = await db.challenges.find_one({"_id": result.inserted_id})
                return serialize_doc(created)
            raise ValueError("Échec création défi")
        except Exception as e:
            logger.error(f"Erreur création défi: {e}", exc_info=True)
            raise











