"""
Repository pour la gestion des quiz
"""
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.database import get_database
from app.schemas import serialize_doc
import logging

logger = logging.getLogger(__name__)


class QuizRepository:
    """Repository pour les opérations CRUD sur les quiz"""
    
    @staticmethod
    async def find_by_module_id(module_id: str) -> Optional[Dict[str, Any]]:
        """Trouve le quiz d'un module"""
        try:
            from app.utils.security import InputSanitizer
            # Valider l'ObjectId
            sanitized_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_id:
                return None
            
            db = get_database()
            quiz = await db.quizzes.find_one({"module_id": sanitized_id})
            return serialize_doc(quiz) if quiz else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche du quiz: {e}")
            raise
    
    @staticmethod
    async def create(quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau quiz"""
        try:
            db = get_database()
            result = await db.quizzes.insert_one(quiz_data)
            quiz_data["_id"] = result.inserted_id
            return serialize_doc(quiz_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création du quiz: {e}")
            raise
    
    @staticmethod
    async def update(module_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un quiz existant"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_id:
                return None
            
            db = get_database()
            await db.quizzes.update_one(
                {"module_id": sanitized_id},
                {"$set": update_data}
            )
            return await QuizRepository.find_by_module_id(sanitized_id)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du quiz: {e}")
            raise
    
    @staticmethod
    async def delete(module_id: str) -> bool:
        """Supprime le quiz d'un module"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_id:
                return False
            
            db = get_database()
            result = await db.quizzes.delete_one({"module_id": sanitized_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du quiz: {e}")
            raise
    
    @staticmethod
    async def exists(module_id: str) -> bool:
        """Vérifie si un quiz existe pour un module"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_id:
                return False
            
            db = get_database()
            count = await db.quizzes.count_documents({"module_id": sanitized_id})
            return count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de l'existence du quiz: {e}")
            return False
    
    @staticmethod
    async def create_attempt(attempt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée une nouvelle tentative de quiz"""
        try:
            db = get_database()
            result = await db.quiz_attempts.insert_one(attempt_data)
            attempt_data["_id"] = result.inserted_id
            return serialize_doc(attempt_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création de la tentative de quiz: {e}")
            raise
    
    @staticmethod
    async def find_attempts_by_user_and_module(user_id: str, module_id: str) -> List[Dict[str, Any]]:
        """Trouve toutes les tentatives de quiz d'un utilisateur pour un module"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_object_id(user_id)
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_user_id or not sanitized_module_id:
                return []
            
            db = get_database()
            cursor = db.quiz_attempts.find({
                "user_id": sanitized_user_id,
                "module_id": sanitized_module_id
            }).sort("completed_at", -1)  # Plus récent en premier
            
            attempts = []
            async for attempt in cursor:
                attempts.append(serialize_doc(attempt))
            return attempts
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des tentatives: {e}")
            return []
    
    @staticmethod
    async def get_statistics(user_id: str, module_id: str) -> Optional[Dict[str, Any]]:
        """Calcule les statistiques de quiz pour un utilisateur et un module"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_object_id(user_id)
            sanitized_module_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_user_id or not sanitized_module_id:
                return None
            
            db = get_database()
            attempts = await QuizRepository.find_attempts_by_user_and_module(sanitized_user_id, sanitized_module_id)
            
            if not attempts:
                return None
            
            total_attempts = len(attempts)
            scores = [attempt.get("score", 0) for attempt in attempts]
            best_score = max(scores) if scores else 0
            average_score = sum(scores) / len(scores) if scores else 0
            total_time_spent = sum(attempt.get("time_spent", 0) for attempt in attempts)
            last_attempt_at = attempts[0].get("completed_at") if attempts else None
            
            return {
                "module_id": sanitized_module_id,
                "total_attempts": total_attempts,
                "best_score": best_score,
                "average_score": average_score,
                "last_attempt_at": last_attempt_at,
                "total_time_spent": total_time_spent
            }
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            return None









