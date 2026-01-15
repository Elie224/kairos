"""
Repository pour le feedback utilisateur
"""
from typing import List, Dict, Any, Optional
from app.database import get_database
from app.schemas import serialize_doc
from app.models.feedback import Feedback
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class FeedbackRepository:
    """Repository pour les opérations CRUD sur le feedback"""
    
    @staticmethod
    async def create(feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau feedback"""
        try:
            from app.utils.security import InputSanitizer
            if "user_id" in feedback_data:
                feedback_data["user_id"] = InputSanitizer.sanitize_string(str(feedback_data["user_id"]))
            
            feedback_data["created_at"] = datetime.now(timezone.utc)
            
            db = get_database()
            result = await db.feedback.insert_one(feedback_data)
            feedback_data["_id"] = result.inserted_id
            return serialize_doc(feedback_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création du feedback: {e}")
            raise
    
    @staticmethod
    async def find_by_user(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Trouve tous les feedbacks d'un utilisateur"""
        try:
            from app.utils.security import InputSanitizer
            sanitized_user_id = InputSanitizer.sanitize_string(str(user_id)) if user_id else None
            if not sanitized_user_id:
                return []
            
            db = get_database()
            cursor = db.feedback.find({"user_id": sanitized_user_id}).sort("created_at", -1).limit(limit)
            feedbacks = await cursor.to_list(length=limit)
            return [serialize_doc(feedback) for feedback in feedbacks]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche des feedbacks: {e}")
            return []
    
    @staticmethod
    async def get_stats(user_id: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        """Récupère les statistiques de feedback"""
        try:
            db = get_database()
            query = {}
            if user_id:
                from app.utils.security import InputSanitizer
                sanitized_user_id = InputSanitizer.sanitize_string(str(user_id))
                if sanitized_user_id:
                    query["user_id"] = sanitized_user_id
            if model:
                query["model_used"] = model
            
            # Pipeline d'agrégation pour les stats
            pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$feedback_type",
                    "count": {"$sum": 1},
                    "avg_rating": {"$avg": "$rating"}
                }}
            ]
            
            results = await db.feedback.aggregate(pipeline, allowDiskUse=True).to_list(length=100)
            
            stats = {
                "useful": 0,
                "not_useful": 0,
                "total": 0,
                "avg_rating": 0.0
            }
            
            total_rating = 0
            rating_count = 0
            
            for result in results:
                feedback_type = result.get("_id", "unknown")
                count = result.get("count", 0)
                avg_rating = result.get("avg_rating")
                
                stats["total"] += count
                if feedback_type == "useful":
                    stats["useful"] = count
                elif feedback_type == "not_useful":
                    stats["not_useful"] = count
                
                if avg_rating:
                    total_rating += avg_rating * count
                    rating_count += count
            
            if rating_count > 0:
                stats["avg_rating"] = total_rating / rating_count
            
            return stats
        except Exception as e:
            logger.error(f"Erreur lors du calcul des stats: {e}")
            return {
                "useful": 0,
                "not_useful": 0,
                "total": 0,
                "avg_rating": 0.0
            }
