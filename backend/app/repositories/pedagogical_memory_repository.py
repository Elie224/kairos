"""
Repository pour la mémoire pédagogique utilisateur
"""
from typing import Optional, Dict, Any
from app.database import get_database
from app.schemas import serialize_doc
from app.models.pedagogical_memory import PedagogicalMemory
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class PedagogicalMemoryRepository:
    """Repository pour les opérations CRUD sur la mémoire pédagogique"""
    
    @staticmethod
    async def find_by_user(user_id: str) -> Optional[Dict[str, Any]]:
        """Trouve la mémoire pédagogique d'un utilisateur"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                return None
            
            db = get_database()
            memory = await db.pedagogical_memory.find_one({"user_id": sanitized_user_id})
            return serialize_doc(memory) if memory else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de la mémoire pédagogique: {e}")
            return None
    
    @staticmethod
    async def create(memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une nouvelle mémoire pédagogique"""
        try:
            from app.utils.security import InputSanitizer
            if "user_id" in memory_data:
                memory_data["user_id"] = InputSanitizer.sanitize_string(str(memory_data["user_id"]))
            
            memory_data["created_at"] = datetime.now(timezone.utc)
            memory_data["updated_at"] = datetime.now(timezone.utc)
            
            db = get_database()
            result = await db.pedagogical_memory.insert_one(memory_data)
            memory_data["_id"] = result.inserted_id
            return serialize_doc(memory_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création de la mémoire pédagogique: {e}")
            raise
    
    @staticmethod
    async def update(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour la mémoire pédagogique"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                return None
            
            update_data["updated_at"] = datetime.now(timezone.utc)
            
            db = get_database()
            await db.pedagogical_memory.update_one(
                {"user_id": sanitized_user_id},
                {"$set": update_data},
                upsert=True
            )
            return await PedagogicalMemoryRepository.find_by_user(sanitized_user_id)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la mémoire pédagogique: {e}")
            raise
    
    @staticmethod
    async def add_error(user_id: str, concept: str, error_type: str):
        """Ajoute une erreur à l'historique"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                return
            
            db = get_database()
            memory = await db.pedagogical_memory.find_one({"user_id": sanitized_user_id})
            
            if not memory:
                # Créer la mémoire si elle n'existe pas
                await db.pedagogical_memory.insert_one({
                    "user_id": sanitized_user_id,
                    "error_history": [],
                    "subject_levels": {},
                    "learning_style": {},
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                })
                memory = await db.pedagogical_memory.find_one({"user_id": sanitized_user_id})
            
            # Trouver ou créer l'entrée d'erreur pour ce concept
            error_history = memory.get("error_history", [])
            error_entry = None
            for entry in error_history:
                if entry.get("concept") == concept:
                    error_entry = entry
                    break
            
            if error_entry:
                # Mettre à jour l'entrée existante
                error_entry["error_count"] = error_entry.get("error_count", 0) + 1
                error_entry["last_error_at"] = datetime.now(timezone.utc)
                if error_type not in error_entry.get("error_types", []):
                    error_entry.setdefault("error_types", []).append(error_type)
            else:
                # Créer une nouvelle entrée
                error_history.append({
                    "concept": concept,
                    "error_count": 1,
                    "last_error_at": datetime.now(timezone.utc),
                    "error_types": [error_type]
                })
            
            await db.pedagogical_memory.update_one(
                {"user_id": sanitized_user_id},
                {
                    "$set": {
                        "error_history": error_history,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout d'erreur à la mémoire: {e}")
    
    @staticmethod
    async def update_subject_level(user_id: str, subject: str, level: str, confidence_score: float):
        """Met à jour le niveau d'une matière"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                return
            
            db = get_database()
            memory = await db.pedagogical_memory.find_one({"user_id": sanitized_user_id})
            
            if not memory:
                await db.pedagogical_memory.insert_one({
                    "user_id": sanitized_user_id,
                    "subject_levels": {},
                    "error_history": [],
                    "learning_style": {},
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                })
                memory = await db.pedagogical_memory.find_one({"user_id": sanitized_user_id})
            
            subject_levels = memory.get("subject_levels", {})
            subject_levels[subject] = {
                "subject": subject,
                "level": level,
                "confidence_score": confidence_score,
                "last_assessed_at": datetime.now(timezone.utc)
            }
            
            await db.pedagogical_memory.update_one(
                {"user_id": sanitized_user_id},
                {
                    "$set": {
                        "subject_levels": subject_levels,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du niveau: {e}")
