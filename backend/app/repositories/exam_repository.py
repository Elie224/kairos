"""
Repository pour la gestion des examens
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.database import get_database
from app.schemas import serialize_doc
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ExamRepository:
    """Repository pour les opérations CRUD sur les examens"""

    @staticmethod
    async def find_by_id(exam_id: str) -> Optional[Dict[str, Any]]:
        """Trouve un examen par son ID"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_id = InputSanitizer.sanitize_object_id(exam_id)
            if not sanitized_id:
                return None

            db = get_database()
            exam = await db.exams.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(exam) if exam else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de l'examen: {e}")
            raise

    @staticmethod
    async def find_by_module_id(module_id: str) -> Optional[Dict[str, Any]]:
        """Trouve l'examen d'un module"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_id:
                return None

            db = get_database()
            # Le module_id peut être stocké comme ObjectId ou string, chercher les deux
            exam = await db.exams.find_one({
                "$or": [
                    {"module_id": ObjectId(sanitized_id)},
                    {"module_id": sanitized_id}
                ]
            })
            return serialize_doc(exam) if exam else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de l'examen par module: {e}")
            raise

    @staticmethod
    async def create(exam_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau examen"""
        try:
            db = get_database()
            exam_data["created_at"] = datetime.now(timezone.utc)
            result = await db.exams.insert_one(exam_data)
            exam_data["_id"] = result.inserted_id
            serialized = serialize_doc(exam_data)
            # S'assurer que pdf_url est inclus s'il existe
            if "pdf_url" in exam_data:
                serialized["pdf_url"] = exam_data["pdf_url"]
            return serialized
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'examen: {e}")
            raise

    @staticmethod
    async def update(exam_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un examen existant"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_id = InputSanitizer.sanitize_object_id(exam_id)
            if not sanitized_id:
                return None

            db = get_database()
            update_data["updated_at"] = datetime.now(timezone.utc)
            await db.exams.update_one(
                {"_id": ObjectId(sanitized_id)},
                {"$set": update_data}
            )
            return await ExamRepository.find_by_id(sanitized_id)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'examen: {e}")
            raise

    @staticmethod
    async def list_all(limit: int = 100) -> List[Dict[str, Any]]:
        """Liste tous les examens"""
        try:
            db = get_database()
            cursor = db.exams.find().sort("created_at", -1).limit(limit)
            exams = await cursor.to_list(length=limit)
            return [serialize_doc(exam) for exam in exams]
        except Exception as e:
            logger.error(f"Erreur lors de la liste des examens: {e}")
            raise


class ExamAttemptRepository:
    """Repository pour les tentatives d'examen"""

    @staticmethod
    async def find_by_id(attempt_id: str) -> Optional[Dict[str, Any]]:
        """Trouve une tentative d'examen par son ID"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_id = InputSanitizer.sanitize_object_id(attempt_id)
            if not sanitized_id:
                return None

            db = get_database()
            attempt = await db.exam_attempts.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(attempt) if attempt else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de la tentative: {e}")
            raise

    @staticmethod
    async def find_by_user(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Trouve toutes les tentatives d'un utilisateur"""
        try:
            db = get_database()
            cursor = db.exam_attempts.find({"user_id": user_id}).sort("started_at", -1).limit(limit)
            attempts = await cursor.to_list(length=limit)
            return [serialize_doc(attempt) for attempt in attempts]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des tentatives: {e}")
            raise

    @staticmethod
    async def find_by_user_and_exam(user_id: str, exam_id: str) -> List[Dict[str, Any]]:
        """Trouve les tentatives d'un utilisateur pour un examen spécifique"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_exam_id = InputSanitizer.sanitize_object_id(exam_id)
            if not sanitized_exam_id:
                return []

            db = get_database()
            cursor = db.exam_attempts.find({
                "user_id": user_id,
                "exam_id": sanitized_exam_id
            }).sort("started_at", -1)
            attempts = await cursor.to_list(length=100)
            return [serialize_doc(attempt) for attempt in attempts]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des tentatives: {e}")
            raise

    @staticmethod
    async def find_by_user_and_module(user_id: str, module_id: str) -> List[Dict[str, Any]]:
        """Trouve les tentatives d'un utilisateur pour un module"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_module_id:
                return []

            db = get_database()
            cursor = db.exam_attempts.find({
                "user_id": user_id,
                "module_id": sanitized_module_id
            }).sort("started_at", -1)
            attempts = await cursor.to_list(length=100)
            return [serialize_doc(attempt) for attempt in attempts]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des tentatives: {e}")
            raise

    @staticmethod
    async def create(attempt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une nouvelle tentative d'examen"""
        try:
            db = get_database()
            attempt_data["started_at"] = datetime.now(timezone.utc)
            result = await db.exam_attempts.insert_one(attempt_data)
            attempt_data["_id"] = result.inserted_id
            return serialize_doc(attempt_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création de la tentative: {e}")
            raise

    @staticmethod
    async def update(attempt_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour une tentative d'examen"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_id = InputSanitizer.sanitize_object_id(attempt_id)
            if not sanitized_id:
                return None

            db = get_database()
            update_data["completed_at"] = datetime.now(timezone.utc)
            await db.exam_attempts.update_one(
                {"_id": ObjectId(sanitized_id)},
                {"$set": update_data}
            )
            return await ExamAttemptRepository.find_by_id(sanitized_id)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la tentative: {e}")
            raise

