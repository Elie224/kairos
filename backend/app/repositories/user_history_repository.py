"""
Repository pour l'historique utilisateur (MongoDB)
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.database import get_database
from app.models.user_history import HistoryEntry, Subject
import logging

logger = logging.getLogger(__name__)


class UserHistoryRepository:
    """Repository pour gérer l'historique utilisateur"""
    
    @staticmethod
    async def create_entry(entry: HistoryEntry) -> Dict[str, Any]:
        """Crée une entrée dans l'historique"""
        try:
            db = get_database()
            entry_dict = entry.dict()
            entry_dict["created_at"] = datetime.now(timezone.utc)
            
            result = await db.user_history.insert_one(entry_dict)
            entry_dict["_id"] = result.inserted_id
            entry_dict["id"] = str(result.inserted_id)
            return entry_dict
        except Exception as e:
            logger.error(f"Erreur création entrée historique: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_user_history(
        user_id: str,
        subject: Optional[Subject] = None,
        module_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Récupère l'historique d'un utilisateur"""
        try:
            db = get_database()
            query = {"user_id": user_id}
            
            if subject:
                query["subject"] = subject.value
            
            if module_id:
                query["module_id"] = module_id
            
            if start_date:
                query["created_at"] = {"$gte": start_date}
            
            if end_date:
                if "created_at" in query:
                    query["created_at"]["$lte"] = end_date
                else:
                    query["created_at"] = {"$lte": end_date}
            
            cursor = db.user_history.find(query).sort("created_at", -1).skip(offset).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Convertir ObjectId en string
            for result in results:
                result["id"] = str(result["_id"])
                del result["_id"]
            
            return results
        except Exception as e:
            logger.error(f"Erreur récupération historique: {e}", exc_info=True)
            return []
    
    @staticmethod
    async def find_exact_match(user_id: str, question: str) -> Optional[Dict[str, Any]]:
        """Trouve une question exactement identique"""
        try:
            db = get_database()
            # Normaliser la question (minuscules, espaces)
            normalized = " ".join(question.lower().split())
            
            result = await db.user_history.find_one({
                "user_id": user_id,
                "question": {"$regex": f"^{normalized}$", "$options": "i"}
            }, sort=[("created_at", -1)])
            
            if result:
                result["id"] = str(result["_id"])
                del result["_id"]
                return result
            
            return None
        except Exception as e:
            logger.error(f"Erreur recherche correspondance exacte: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def find_similar_questions(
        user_id: Optional[str],
        question: str,
        threshold: float = 0.8,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Trouve des questions similaires en utilisant une recherche textuelle MongoDB
        Pour une vraie similarité sémantique, on pourrait utiliser des embeddings
        """
        try:
            db = get_database()
            normalized = " ".join(question.lower().split())
            
            # Recherche textuelle MongoDB (basique)
            # Pour une vraie similarité sémantique, utiliser des embeddings vectoriels
            query = {
                "$text": {"$search": normalized}
            }
            
            if user_id:
                query["user_id"] = user_id
            
            cursor = db.user_history.find(query).limit(limit)
            results = await cursor.to_list(length=limit)
            
            # Convertir ObjectId en string
            for result in results:
                result["id"] = str(result["_id"])
                del result["_id"]
            
            return results
        except Exception as e:
            logger.debug(f"Recherche similaire non disponible (index textuel manquant): {e}")
            # Fallback: recherche par mots-clés
            return await UserHistoryRepository._find_by_keywords(user_id, question, limit)
    
    @staticmethod
    async def _find_by_keywords(
        user_id: Optional[str],
        question: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Recherche par mots-clés (fallback)"""
        try:
            db = get_database()
            # Extraire les mots-clés (mots de 4+ caractères)
            words = [w.lower() for w in question.split() if len(w) >= 4]
            
            if not words:
                return []
            
            query = {
                "question": {"$regex": "|".join(words), "$options": "i"}
            }
            
            if user_id:
                query["user_id"] = user_id
            
            cursor = db.user_history.find(query).sort("created_at", -1).limit(limit)
            results = await cursor.to_list(length=limit)
            
            for result in results:
                result["id"] = str(result["_id"])
                del result["_id"]
            
            return results
        except Exception as e:
            logger.error(f"Erreur recherche par mots-clés: {e}", exc_info=True)
            return []
    
    @staticmethod
    async def get_stats(user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques de l'historique utilisateur"""
        try:
            db = get_database()
            
            # Stats globales
            total_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_questions": {"$sum": 1},
                    "total_tokens": {"$sum": "$tokens_used"},
                    "total_cost": {"$sum": "$cost_eur"}
                }}
            ]
            
            total_stats = await db.user_history.aggregate(total_pipeline).to_list(length=1)
            
            # Stats par matière
            subject_pipeline = [
                {"$match": {"user_id": user_id, "subject": {"$exists": True}}},
                {"$group": {
                    "_id": "$subject",
                    "count": {"$sum": 1}
                }}
            ]
            
            subject_stats = await db.user_history.aggregate(subject_pipeline).to_list(length=100)
            by_subject = {stat["_id"]: stat["count"] for stat in subject_stats}
            
            # Stats par modèle
            model_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$model_used",
                    "count": {"$sum": 1}
                }}
            ]
            
            model_stats = await db.user_history.aggregate(model_pipeline).to_list(length=100)
            by_model = {stat["_id"]: stat["count"] for stat in model_stats}
            
            # Questions les plus posées
            frequent_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$question",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            frequent_questions = await db.user_history.aggregate(frequent_pipeline).to_list(length=10)
            most_asked = [
                {"question": q["_id"], "count": q["count"]}
                for q in frequent_questions
            ]
            
            total = total_stats[0] if total_stats else {
                "total_questions": 0,
                "total_tokens": 0,
                "total_cost": 0.0
            }
            
            return {
                "total_questions": total.get("total_questions", 0),
                "total_tokens": total.get("total_tokens", 0),
                "total_cost_eur": total.get("total_cost", 0.0),
                "by_subject": by_subject,
                "by_model": by_model,
                "most_asked_questions": most_asked
            }
        except Exception as e:
            logger.error(f"Erreur récupération stats: {e}", exc_info=True)
            return {
                "total_questions": 0,
                "total_tokens": 0,
                "total_cost_eur": 0.0,
                "by_subject": {},
                "by_model": {},
                "most_asked_questions": []
            }
    
    @staticmethod
    async def delete_user_history(user_id: str) -> int:
        """Supprime tout l'historique d'un utilisateur (RGPD)"""
        try:
            db = get_database()
            result = await db.user_history.delete_many({"user_id": user_id})
            return result.deleted_count
        except Exception as e:
            logger.error(f"Erreur suppression historique: {e}", exc_info=True)
            return 0











