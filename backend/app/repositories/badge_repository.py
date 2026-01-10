"""
Repository pour les badges et récompenses
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_database
from app.models import BadgeType
from app.schemas import serialize_doc
import logging

logger = logging.getLogger(__name__)


class BadgeRepository:
    """Repository pour la gestion des badges"""
    
    @staticmethod
    async def create(user_id: str, badge_type: BadgeType, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Crée un nouveau badge"""
        db = get_database()
        badge_doc = {
            "user_id": user_id,
            "badge_type": badge_type.value,
            "earned_at": datetime.utcnow(),
            "metadata": metadata or {}
        }
        result = await db.badges.insert_one(badge_doc)
        badge_doc["_id"] = result.inserted_id
        return serialize_doc(badge_doc)
    
    @staticmethod
    async def find_by_user(user_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les badges d'un utilisateur"""
        db = get_database()
        cursor = db.badges.find({"user_id": user_id}).sort("earned_at", -1)
        badges = await cursor.to_list(length=100)
        return [serialize_doc(badge) for badge in badges]
    
    @staticmethod
    async def find_by_user_and_type(user_id: str, badge_type: BadgeType) -> Optional[Dict[str, Any]]:
        """Vérifie si un utilisateur a un badge spécifique"""
        db = get_database()
        badge = await db.badges.find_one({
            "user_id": user_id,
            "badge_type": badge_type.value
        })
        return serialize_doc(badge) if badge else None
    
    @staticmethod
    async def count_by_user(user_id: str) -> int:
        """Compte le nombre de badges d'un utilisateur"""
        db = get_database()
        return await db.badges.count_documents({"user_id": user_id})

