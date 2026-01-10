"""
Repository pour les parcours d'apprentissage
"""
from typing import Optional, Dict, Any, List
from app.database import get_database
from app.schemas import serialize_doc
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PathwayRepository:
    """Repository pour gérer les parcours"""
    
    @staticmethod
    async def create(pathway_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau parcours"""
        try:
            db = get_database()
            result = await db.pathways.insert_one(pathway_data)
            if result.inserted_id:
                created = await db.pathways.find_one({"_id": result.inserted_id})
                return serialize_doc(created)
            raise ValueError("Échec de la création du parcours")
        except Exception as e:
            logger.error(f"Erreur lors de la création du parcours: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def find_by_id(pathway_id: str) -> Optional[Dict[str, Any]]:
        """Trouve un parcours par ID"""
        try:
            db = get_database()
            if not ObjectId.is_valid(pathway_id):
                return None
            pathway = await db.pathways.find_one({"_id": ObjectId(pathway_id)})
            return serialize_doc(pathway) if pathway else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche du parcours: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def find_all(
        subject: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Récupère tous les parcours avec filtres"""
        try:
            db = get_database()
            query = {}
            
            if subject:
                query["subject"] = subject
            if status:
                query["status"] = status
            
            cursor = db.pathways.find(query).skip(skip).limit(limit).sort("created_at", -1)
            pathways = await cursor.to_list(length=limit)
            return [serialize_doc(p) for p in pathways]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des parcours: {e}", exc_info=True)
            return []
    
    @staticmethod
    async def update(pathway_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un parcours"""
        try:
            db = get_database()
            if not ObjectId.is_valid(pathway_id):
                return None
            
            update_data["updated_at"] = update_data.get("updated_at")
            
            result = await db.pathways.update_one(
                {"_id": ObjectId(pathway_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                updated = await db.pathways.find_one({"_id": ObjectId(pathway_id)})
                return serialize_doc(updated)
            
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du parcours: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def delete(pathway_id: str) -> bool:
        """Supprime un parcours"""
        try:
            db = get_database()
            if not ObjectId.is_valid(pathway_id):
                return False
            
            result = await db.pathways.delete_one({"_id": ObjectId(pathway_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du parcours: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def find_by_user(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère les parcours d'un utilisateur"""
        try:
            db = get_database()
            cursor = db.pathways.find({"created_by": user_id}).limit(limit).sort("created_at", -1)
            pathways = await cursor.to_list(length=limit)
            return [serialize_doc(p) for p in pathways]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des parcours utilisateur: {e}", exc_info=True)
            return []











