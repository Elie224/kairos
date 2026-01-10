"""
Repository pour la gestion des validations de module
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.database import get_database
from app.schemas import serialize_doc
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ValidationRepository:
    """Repository pour les opérations CRUD sur les validations de module"""

    @staticmethod
    async def find_by_id(validation_id: str) -> Optional[Dict[str, Any]]:
        """Trouve une validation par son ID"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_id = InputSanitizer.sanitize_object_id(validation_id)
            if not sanitized_id:
                return None

            db = get_database()
            validation = await db.module_validations.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(validation) if validation else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de la validation: {e}")
            raise

    @staticmethod
    async def find_by_user_and_module(user_id: str, module_id: str) -> Optional[Dict[str, Any]]:
        """Trouve la validation d'un module pour un utilisateur"""
        try:
            from app.utils.security import InputSanitizer
            
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_module_id:
                return None

            # user_id est une string simple
            sanitized_user_id = InputSanitizer.sanitize_string(user_id) if isinstance(user_id, str) else str(user_id)

            db = get_database()
            validation = await db.module_validations.find_one({
                "user_id": sanitized_user_id,
                "module_id": ObjectId(sanitized_module_id)
            })
            return serialize_doc(validation) if validation else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de la validation: {e}")
            raise

    @staticmethod
    async def find_by_user(user_id: str) -> List[Dict[str, Any]]:
        """Trouve toutes les validations d'un utilisateur"""
        try:
            db = get_database()
            cursor = db.module_validations.find({"user_id": user_id}).sort("validated_at", -1)
            validations = await cursor.to_list(length=100)
            return [serialize_doc(validation) for validation in validations]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des validations: {e}")
            raise

    @staticmethod
    async def create(validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une nouvelle validation de module"""
        try:
            from app.utils.security import InputSanitizer
            
            # Valider et convertir le module_id en ObjectId
            if "module_id" in validation_data:
                sanitized_module_id = InputSanitizer.sanitize_object_id(validation_data["module_id"])
                if sanitized_module_id:
                    validation_data["module_id"] = ObjectId(sanitized_module_id)
                else:
                    raise ValueError(f"Module ID invalide: {validation_data.get('module_id')}")
            
            # user_id reste une string simple
            if "user_id" in validation_data:
                validation_data["user_id"] = InputSanitizer.sanitize_string(str(validation_data["user_id"]))
            
            db = get_database()
            validation_data["validated_at"] = datetime.now(timezone.utc)
            result = await db.module_validations.insert_one(validation_data)
            validation_data["_id"] = result.inserted_id
            return serialize_doc(validation_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création de la validation: {e}")
            raise

    @staticmethod
    async def exists(user_id: str, module_id: str) -> bool:
        """Vérifie si un module est déjà validé pour un utilisateur"""
        try:
            from app.utils.security import InputSanitizer
            
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_module_id:
                return False

            # user_id est une string simple
            sanitized_user_id = InputSanitizer.sanitize_string(user_id) if isinstance(user_id, str) else str(user_id)

            db = get_database()
            count = await db.module_validations.count_documents({
                "user_id": sanitized_user_id,
                "module_id": ObjectId(sanitized_module_id)
            })
            return count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la validation: {e}")
            return False

    @staticmethod
    async def get_validated_modules(user_id: str) -> List[str]:
        """Récupère la liste des modules validés par un utilisateur (optimisé avec projection)"""
        try:
            db = get_database()
            # Projection pour récupérer seulement module_id (plus rapide)
            cursor = db.module_validations.find(
                {"user_id": user_id},
                {"module_id": 1, "_id": 0}  # Seulement module_id
            ).limit(100)  # Limiter à 100 résultats
            validations = await cursor.to_list(length=100)
            return [validation.get("module_id") for validation in validations if validation.get("module_id")]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modules validés: {e}")
            return []

