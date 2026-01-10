"""
Repository pour la gestion des Travaux Dirigés (TD)
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.database import get_database
from app.schemas import serialize_doc
from app.utils.security import InputSanitizer
import logging
import logging

logger = logging.getLogger(__name__)


class TDRepository:
    """Repository pour les opérations CRUD sur les TD"""

    @staticmethod
    async def find_by_module_id(module_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les TD d'un module"""
        try:
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_module_id:
                return []

            db = get_database()
            cursor = db.tds.find({"module_id": ObjectId(sanitized_module_id)}).sort("created_at", 1)
            tds = await cursor.to_list(length=100)
            return [serialize_doc(td) for td in tds]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des TD: {e}")
            raise

    @staticmethod
    async def find_by_id(td_id: str) -> Optional[Dict[str, Any]]:
        """Trouve un TD par son ID"""
        try:
            sanitized_id = InputSanitizer.sanitize_object_id(td_id)
            if not sanitized_id:
                return None

            db = get_database()
            td = await db.tds.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(td) if td else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche du TD: {e}")
            raise

    @staticmethod
    async def create(td_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau TD"""
        try:
            from datetime import datetime, timezone
            
            logger.info(f"📝 TDRepository.create: Début de la création du TD")
            
            # Valider et convertir le module_id en ObjectId
            if "module_id" in td_data:
                sanitized_module_id = InputSanitizer.sanitize_object_id(td_data["module_id"])
                if sanitized_module_id:
                    td_data["module_id"] = ObjectId(sanitized_module_id)
                    logger.info(f"📝 TDRepository.create: module_id converti en ObjectId: {sanitized_module_id}")
                else:
                    raise ValueError(f"Module ID invalide: {td_data.get('module_id')}")

            td_data["created_at"] = datetime.now(timezone.utc)
            td_data["updated_at"] = datetime.now(timezone.utc)
            logger.info(f"📝 TDRepository.create: Dates ajoutées")

            db = get_database()
            logger.info(f"📝 TDRepository.create: Base de données obtenue, insertion en cours...")
            result = await db.tds.insert_one(td_data)
            logger.info(f"✅ TDRepository.create: Insertion réussie, ID: {result.inserted_id}")
            td_data["_id"] = result.inserted_id
            logger.info(f"📝 TDRepository.create: Début de la sérialisation du TD...")
            try:
                # Sérialisation manuelle pour éviter les problèmes de récursion
                # Convertir les exercices en listes simples
                exercises = td_data.get("exercises", [])
                exercises_serialized = []
                for ex in exercises:
                    if isinstance(ex, dict):
                        exercises_serialized.append(ex)
                    else:
                        # Si c'est un objet, convertir en dict
                        exercises_serialized.append(ex.__dict__ if hasattr(ex, '__dict__') else str(ex))
                
                serialized = {
                    "id": str(td_data["_id"]),
                    "module_id": str(td_data["module_id"]) if isinstance(td_data.get("module_id"), ObjectId) else td_data.get("module_id"),
                    "title": str(td_data.get("title", "")),
                    "description": str(td_data.get("description", "")),
                    "exercises": exercises_serialized,
                    "estimated_time": int(td_data.get("estimated_time", 60)),
                    "pdf_url": td_data.get("pdf_url"),  # Inclure pdf_url si présent
                    "created_at": td_data.get("created_at").isoformat() if isinstance(td_data.get("created_at"), datetime) else str(td_data.get("created_at", "")),
                    "updated_at": td_data.get("updated_at").isoformat() if isinstance(td_data.get("updated_at"), datetime) else str(td_data.get("updated_at", ""))
                }
                logger.info(f"✅ TDRepository.create: TD sérialisé avec succès ({len(exercises_serialized)} exercices), retour du résultat")
                return serialized
            except Exception as ser_error:
                logger.error(f"❌ Erreur lors de la sérialisation du TD: {ser_error}", exc_info=True)
                # Retourner quand même le TD avec l'ID converti manuellement
                td_data_copy = td_data.copy()
                td_data_copy["id"] = str(td_data_copy["_id"])
                del td_data_copy["_id"]
                if isinstance(td_data_copy.get("module_id"), ObjectId):
                    td_data_copy["module_id"] = str(td_data_copy["module_id"])
                logger.info(f"⚠️ TDRepository.create: Retour du TD sans sérialisation complète")
                return td_data_copy
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création du TD: {e}", exc_info=True)
            raise

    @staticmethod
    async def update(td_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un TD"""
        try:
            from datetime import datetime, timezone
            
            sanitized_id = InputSanitizer.sanitize_object_id(td_id)
            if not sanitized_id:
                return None

            update_data["updated_at"] = datetime.now(timezone.utc)

            db = get_database()
            await db.tds.update_one(
                {"_id": ObjectId(sanitized_id)},
                {"$set": update_data}
            )
            updated = await db.tds.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(updated) if updated else None
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du TD: {e}")
            raise

    @staticmethod
    async def delete(td_id: str) -> bool:
        """Supprime un TD"""
        try:
            sanitized_id = InputSanitizer.sanitize_object_id(td_id)
            if not sanitized_id:
                return False

            db = get_database()
            result = await db.tds.delete_one({"_id": ObjectId(sanitized_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du TD: {e}")
            raise














