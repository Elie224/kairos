"""
Repository pour la gestion de la progression
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.database import get_database
from app.schemas import serialize_doc
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ProgressRepository:
    """Repository pour les opérations CRUD sur la progression"""
    
    @staticmethod
    async def find_by_user(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Récupère toute la progression d'un utilisateur"""
        try:
            from app.utils.security import InputSanitizer
            # Sanitize user_id and limit
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                logger.warning(f"Tentative de récupération de la progression avec user_id invalide: {user_id}")
                return []
            if not isinstance(limit, int):
                try:
                    limit = int(limit)
                except Exception:
                    limit = 100

            logger.debug(f"ProgressRepository.find_by_user: user_id={sanitized_user_id}, limit={limit}")
            db = get_database()
            # Limiter à 50 par défaut pour la performance
            actual_limit = min(limit, 50)
            cursor = db.progress.find(
                {"user_id": sanitized_user_id},
                {"_id": 1, "module_id": 1, "completed": 1, "score": 1, "time_spent": 1, "started_at": 1, "completed_at": 1}
            ).sort("started_at", -1).limit(actual_limit)
            progress_list = await cursor.to_list(length=actual_limit)
            return [serialize_doc(p) for p in progress_list]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de la progression: {e}")
            raise
    
    @staticmethod
    async def find_by_user_and_module(user_id: str, module_id: str) -> Optional[Dict[str, Any]]:
        """Trouve la progression d'un utilisateur pour un module spécifique"""
        try:
            from app.utils.security import InputSanitizer
            from bson import ObjectId
            
            # Valider le module_id (doit être un ObjectId)
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_module_id:
                logger.warning(f"Module ID invalide: {module_id}")
                return None
            
            # user_id est une string simple, pas un ObjectId
            # On le nettoie pour éviter les injections mais on le garde comme string
            sanitized_user_id = InputSanitizer.sanitize_string(user_id) if isinstance(user_id, str) else str(user_id)
            
            db = get_database()
            progress = await db.progress.find_one({
                "user_id": sanitized_user_id,
                "module_id": ObjectId(sanitized_module_id)
            })
            return serialize_doc(progress) if progress else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de progression: {e}")
            raise
    
    @staticmethod
    async def create(progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une nouvelle entrée de progression"""
        try:
            from app.utils.security import InputSanitizer
            
            # Valider et convertir le module_id en ObjectId
            if "module_id" in progress_data:
                sanitized_module_id = InputSanitizer.sanitize_object_id(progress_data["module_id"])
                if sanitized_module_id:
                    progress_data["module_id"] = ObjectId(sanitized_module_id)
                else:
                    raise ValueError(f"Module ID invalide: {progress_data.get('module_id')}")
            
            # user_id reste une string simple
            if "user_id" in progress_data:
                progress_data["user_id"] = InputSanitizer.sanitize_string(str(progress_data["user_id"]))
            
            # S'assurer que les dates sont en UTC
            if "started_at" in progress_data and isinstance(progress_data["started_at"], datetime):
                if progress_data["started_at"].tzinfo is None:
                    progress_data["started_at"] = progress_data["started_at"].replace(tzinfo=timezone.utc)
            if "completed_at" in progress_data and isinstance(progress_data["completed_at"], datetime):
                if progress_data["completed_at"].tzinfo is None:
                    progress_data["completed_at"] = progress_data["completed_at"].replace(tzinfo=timezone.utc)
            
            db = get_database()
            result = await db.progress.insert_one(progress_data)
            progress_data["_id"] = result.inserted_id
            return serialize_doc(progress_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création de la progression: {e}")
            raise
    
    @staticmethod
    async def update(progress_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour une entrée de progression"""
        try:
            from app.utils.security import InputSanitizer
            # Valider l'ObjectId avant utilisation
            sanitized_id = InputSanitizer.sanitize_object_id(progress_id)
            if not sanitized_id:
                return None
            
            db = get_database()
            await db.progress.update_one(
                {"_id": ObjectId(sanitized_id)},
                {"$set": update_data}
            )
            updated = await db.progress.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(updated) if updated else None
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la progression: {e}")
            raise
    
    @staticmethod
    async def upsert(user_id: str, module_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée ou met à jour une entrée de progression (avec transaction atomique)"""
        try:
            from app.utils.security import InputSanitizer
            # Valider le module_id (doit être un ObjectId)
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_module_id:
                raise ValueError("ID de module invalide")
            
            # user_id peut être une string simple, pas forcément un ObjectId
            # On le garde tel quel mais on le nettoie pour éviter les injections
            if not user_id:
                raise ValueError("ID d'utilisateur requis")
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if isinstance(user_id, str) else str(user_id)
            if not sanitized_user_id or len(sanitized_user_id.strip()) == 0:
                raise ValueError(f"ID d'utilisateur invalide après sanitization: {user_id}")
            
            db = get_database()
            
            # Utiliser find_one_and_update avec upsert=True pour opération atomique
            # Cela évite les race conditions et garantit l'atomicité
            update_data = {
                **progress_data,
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Retirer started_at de update_data si présent car il sera géré par $setOnInsert
            started_at_value = update_data.pop("started_at", None)
            
            from bson import ObjectId
            
            from pymongo import ReturnDocument
            
            # Construire l'opération de mise à jour
            update_operation = {
                "$set": update_data
            }
            
            # $setOnInsert ne s'exécute que lors de l'insertion
            # Utiliser la valeur fournie ou la date actuelle
            set_on_insert = {
                "user_id": sanitized_user_id,
                "module_id": ObjectId(sanitized_module_id),
                "started_at": started_at_value if started_at_value else datetime.now(timezone.utc)
            }
            update_operation["$setOnInsert"] = set_on_insert
            
            result = await db.progress.find_one_and_update(
                {
                    "user_id": sanitized_user_id,
                    "module_id": ObjectId(sanitized_module_id)
                },
                update_operation,
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            
            return serialize_doc(result)
        except Exception as e:
            logger.error(f"Erreur lors de l'upsert de la progression: {e}")
            raise
    
    @staticmethod
    async def count_completed(user_id: str) -> int:
        """Compte le nombre de modules complétés par un utilisateur"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                logger.warning(f"Tentative de comptage avec user_id invalide: {user_id}")
                return 0
            db = get_database()
            return await db.progress.count_documents({
                "user_id": sanitized_user_id,
                "completed": True
            })
        except Exception as e:
            logger.error(f"Erreur lors du comptage des modules complétés: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def count_total(user_id: str) -> int:
        """Compte le nombre total de modules commencés par un utilisateur"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                logger.warning(f"Tentative de comptage avec user_id invalide: {user_id}")
                return 0
            db = get_database()
            return await db.progress.count_documents({"user_id": sanitized_user_id})
        except Exception as e:
            logger.error(f"Erreur lors du comptage total: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_total_time_spent(user_id: str) -> int:
        """Calcule le temps total passé en apprentissage (optimisé avec agrégation MongoDB)"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                logger.warning(f"Tentative de calcul du temps avec user_id invalide: {user_id}")
                return 0
            logger.debug(f"get_total_time_spent called with user_id={sanitized_user_id}")
            db = get_database()
            # Utiliser allowDiskUse pour les grandes collections
            pipeline = [
                {"$match": {"user_id": sanitized_user_id}},
                {"$group": {
                    "_id": None,
                    "total_time": {"$sum": {"$ifNull": ["$time_spent", 0]}}
                }}
            ]
            result = await db.progress.aggregate(pipeline, allowDiskUse=True).to_list(length=1)
            return result[0]["total_time"] if result else 0
        except Exception as e:
            logger.error(f"Erreur lors du calcul du temps total: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_average_score(user_id: str) -> Optional[float]:
        """Calcule la moyenne des scores (optimisé avec agrégation MongoDB)"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                logger.warning(f"Tentative de calcul de la moyenne avec user_id invalide: {user_id}")
                return None
            logger.debug(f"get_average_score called with user_id={sanitized_user_id}")
            db = get_database()
            pipeline = [
                {"$match": {
                    "user_id": sanitized_user_id,
                    "score": {"$exists": True, "$ne": None, "$type": "number"}
                }},
                {"$group": {
                    "_id": None,
                    "average_score": {"$avg": "$score"},
                    "count": {"$sum": 1}
                }}
            ]
            result = await db.progress.aggregate(pipeline, allowDiskUse=True).to_list(length=1)
            if result and result[0].get("count", 0) > 0:
                return result[0]["average_score"]
            return None
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la moyenne: {e}", exc_info=True)
            raise

