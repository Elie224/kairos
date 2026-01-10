"""
Repository pour la collaboration
"""
from typing import Optional, Dict, Any, List
from app.database import get_database
from app.schemas import serialize_doc
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class CollaborationRepository:
    """Repository pour collaboration"""
    
    @staticmethod
    async def create_group(group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un groupe"""
        try:
            db = get_database()
            result = await db.collaboration_groups.insert_one(group_data)
            if result.inserted_id:
                created = await db.collaboration_groups.find_one({"_id": result.inserted_id})
                return serialize_doc(created)
            raise ValueError("Échec création groupe")
        except Exception as e:
            logger.error(f"Erreur création groupe: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_group(group_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un groupe"""
        try:
            db = get_database()
            if not ObjectId.is_valid(group_id):
                return None
            group = await db.collaboration_groups.find_one({"_id": ObjectId(group_id)})
            return serialize_doc(group) if group else None
        except Exception as e:
            logger.error(f"Erreur récupération groupe: {e}", exc_info=True)
            return None











