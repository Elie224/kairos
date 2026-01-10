"""
Repository pour la gestion des Travaux Pratiques (TP)
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.database import get_database
from app.schemas import serialize_doc
from app.utils.security import InputSanitizer
import logging

logger = logging.getLogger(__name__)


class TPRepository:
    """Repository pour les opérations CRUD sur les TP"""

    @staticmethod
    async def find_by_module_id(module_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les TP d'un module"""
        try:
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_module_id:
                return []

            db = get_database()
            cursor = db.tps.find({"module_id": ObjectId(sanitized_module_id)}).sort("created_at", 1)
            tps = await cursor.to_list(length=100)
            return [serialize_doc(tp) for tp in tps]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des TP: {e}")
            raise

    @staticmethod
    async def find_by_id(tp_id: str) -> Optional[Dict[str, Any]]:
        """Trouve un TP par son ID"""
        try:
            sanitized_id = InputSanitizer.sanitize_object_id(tp_id)
            if not sanitized_id:
                return None

            db = get_database()
            tp = await db.tps.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(tp) if tp else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche du TP: {e}")
            raise

    @staticmethod
    async def create(tp_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau TP"""
        try:
            from datetime import datetime, timezone
            
            logger.info(f"📝 TPRepository.create: Début de la création du TP")
            
            # Valider et convertir le module_id en ObjectId
            if "module_id" in tp_data:
                sanitized_module_id = InputSanitizer.sanitize_object_id(tp_data["module_id"])
                if sanitized_module_id:
                    tp_data["module_id"] = ObjectId(sanitized_module_id)
                    logger.info(f"📝 TPRepository.create: module_id converti en ObjectId")
                else:
                    raise ValueError(f"Module ID invalide: {tp_data.get('module_id')}")
            
            tp_data["created_at"] = datetime.now(timezone.utc)
            tp_data["updated_at"] = datetime.now(timezone.utc)
            logger.info(f"📝 TPRepository.create: Dates ajoutées")
            
            db = get_database()
            logger.info(f"📝 TPRepository.create: Base de données obtenue, insertion en cours...")
            result = await db.tps.insert_one(tp_data)
            logger.info(f"✅ TPRepository.create: Insertion réussie, ID: {result.inserted_id}")
            tp_data["_id"] = result.inserted_id
            
            logger.info(f"📝 TPRepository.create: Début de la sérialisation du TP...")
            try:
                # Sérialisation manuelle pour éviter les problèmes de récursion
                # Convertir les steps en listes simples
                steps = tp_data.get("steps", [])
                steps_serialized = []
                for step in steps:
                    if isinstance(step, dict):
                        steps_serialized.append(step)
                    else:
                        steps_serialized.append(step.__dict__ if hasattr(step, '__dict__') else str(step))
                
                serialized = {
                    "id": str(tp_data["_id"]),
                    "module_id": str(tp_data["module_id"]) if isinstance(tp_data.get("module_id"), ObjectId) else tp_data.get("module_id"),
                    "title": str(tp_data.get("title", "")),
                    "description": str(tp_data.get("description", "")),
                    "objectives": tp_data.get("objectives", []),
                    "steps": steps_serialized,
                    "estimated_time": int(tp_data.get("estimated_time", 90)),
                    "materials_needed": tp_data.get("materials_needed", []),
                    "programming_language": tp_data.get("programming_language"),  # Inclure programming_language si présent
                    "pdf_url": tp_data.get("pdf_url"),  # Inclure pdf_url si présent
                    "created_at": tp_data.get("created_at").isoformat() if isinstance(tp_data.get("created_at"), datetime) else str(tp_data.get("created_at", "")),
                    "updated_at": tp_data.get("updated_at").isoformat() if isinstance(tp_data.get("updated_at"), datetime) else str(tp_data.get("updated_at", ""))
                }
                logger.info(f"✅ TPRepository.create: TP sérialisé avec succès ({len(steps_serialized)} étapes), retour du résultat")
                return serialized
            except Exception as ser_error:
                logger.error(f"❌ Erreur lors de la sérialisation du TP: {ser_error}", exc_info=True)
                # Retourner quand même le TP avec l'ID converti manuellement
                tp_data_copy = tp_data.copy()
                tp_data_copy["id"] = str(tp_data_copy["_id"])
                del tp_data_copy["_id"]
                if isinstance(tp_data_copy.get("module_id"), ObjectId):
                    tp_data_copy["module_id"] = str(tp_data_copy["module_id"])
                logger.info(f"⚠️ TPRepository.create: Retour du TP sans sérialisation complète")
                return tp_data_copy
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création du TP: {e}", exc_info=True)
            raise

    @staticmethod
    async def update(tp_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un TP"""
        try:
            from datetime import datetime, timezone
            
            sanitized_id = InputSanitizer.sanitize_object_id(tp_id)
            if not sanitized_id:
                return None

            update_data["updated_at"] = datetime.now(timezone.utc)

            db = get_database()
            await db.tps.update_one(
                {"_id": ObjectId(sanitized_id)},
                {"$set": update_data}
            )
            updated = await db.tps.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(updated) if updated else None
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du TP: {e}")
            raise

    @staticmethod
    async def delete(tp_id: str) -> bool:
        """Supprime un TP"""
        try:
            sanitized_id = InputSanitizer.sanitize_object_id(tp_id)
            if not sanitized_id:
                return False

            db = get_database()
            result = await db.tps.delete_one({"_id": ObjectId(sanitized_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du TP: {e}")
            raise














