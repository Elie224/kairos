"""
Repository pour la gestion des Ressources de cours
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.database import get_database
from app.schemas import serialize_doc
from app.utils.security import InputSanitizer
import logging

logger = logging.getLogger(__name__)


class ResourceRepository:
    """Repository pour les opérations CRUD sur les ressources"""

    @staticmethod
    async def find_by_module_id(module_id: str) -> List[Dict[str, Any]]:
        """Récupère toutes les ressources d'un module"""
        try:
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_module_id:
                return []

            db = get_database()
            cursor = db.resources.find({"module_id": ObjectId(sanitized_module_id)}).sort("created_at", -1)
            resources = await cursor.to_list(length=100)
            return [serialize_doc(resource) for resource in resources]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des ressources: {e}")
            raise

    @staticmethod
    async def find_by_id(resource_id: str) -> Optional[Dict[str, Any]]:
        """Trouve une ressource par son ID"""
        try:
            sanitized_id = InputSanitizer.sanitize_object_id(resource_id)
            if not sanitized_id:
                return None

            db = get_database()
            resource = await db.resources.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(resource) if resource else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de la ressource: {e}")
            raise

    @staticmethod
    async def create(resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une nouvelle ressource"""
        try:
            db = get_database()
            # Convertir module_id en ObjectId si c'est une string
            if "module_id" in resource_data:
                if isinstance(resource_data["module_id"], str):
                    sanitized_module_id = InputSanitizer.sanitize_object_id(resource_data["module_id"])
                    if sanitized_module_id:
                        resource_data["module_id"] = ObjectId(sanitized_module_id)
                    else:
                        raise ValueError("ID de module invalide")
                elif isinstance(resource_data["module_id"], ObjectId):
                    # Déjà un ObjectId, pas besoin de conversion
                    pass
            
            result = await db.resources.insert_one(resource_data)
            created_resource = await db.resources.find_one({"_id": result.inserted_id})
            return serialize_doc(created_resource)
        except Exception as e:
            logger.error(f"Erreur lors de la création de la ressource: {e}")
            raise

    @staticmethod
    async def update(resource_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour une ressource"""
        try:
            sanitized_id = InputSanitizer.sanitize_object_id(resource_id)
            if not sanitized_id:
                return None

            db = get_database()
            result = await db.resources.update_one(
                {"_id": ObjectId(sanitized_id)},
                {"$set": update_data}
            )
            if result.modified_count == 0:
                return None
            updated_resource = await db.resources.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(updated_resource) if updated_resource else None
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la ressource: {e}")
            raise

    @staticmethod
    async def delete(resource_id: str) -> bool:
        """Supprime une ressource"""
        try:
            sanitized_id = InputSanitizer.sanitize_object_id(resource_id)
            if not sanitized_id:
                return False

            db = get_database()
            result = await db.resources.delete_one({"_id": ObjectId(sanitized_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la ressource: {e}")
            raise

