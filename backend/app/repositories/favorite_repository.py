"""
Repository pour les favoris
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_database
from app.schemas import serialize_doc
import logging

logger = logging.getLogger(__name__)


class FavoriteRepository:
    """Repository pour la gestion des favoris"""
    
    @staticmethod
    async def create(user_id: str, module_id: str) -> Dict[str, Any]:
        """Ajoute un module aux favoris"""
        db = get_database()
        
        # Vérifier si déjà en favoris
        existing = await db.favorites.find_one({
            "user_id": user_id,
            "module_id": module_id
        })
        if existing:
            return serialize_doc(existing)
        
        favorite_doc = {
            "user_id": user_id,
            "module_id": module_id,
            "created_at": datetime.utcnow()
        }
        result = await db.favorites.insert_one(favorite_doc)
        favorite_doc["_id"] = result.inserted_id
        return serialize_doc(favorite_doc)
    
    @staticmethod
    async def delete(user_id: str, module_id: str) -> bool:
        """Retire un module des favoris"""
        db = get_database()
        result = await db.favorites.delete_one({
            "user_id": user_id,
            "module_id": module_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    async def find_by_user(user_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les favoris d'un utilisateur"""
        db = get_database()
        cursor = db.favorites.find({"user_id": user_id}).sort("created_at", -1)
        favorites = await cursor.to_list(length=100)
        return [serialize_doc(fav) for fav in favorites]
    
    @staticmethod
    async def is_favorite(user_id: str, module_id: str) -> bool:
        """Vérifie si un module est en favoris"""
        db = get_database()
        favorite = await db.favorites.find_one({
            "user_id": user_id,
            "module_id": module_id
        })
        return favorite is not None

