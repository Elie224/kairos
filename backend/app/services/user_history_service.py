"""
Service pour gérer l'historique utilisateur et le cache intelligent
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from app.repositories.user_history_repository import UserHistoryRepository
from app.models.user_history import HistoryEntry, Subject, SimilarQuestionRequest, SimilarQuestionResponse
from app.services.semantic_cache import SemanticCache
import logging
import hashlib

logger = logging.getLogger(__name__)


class UserHistoryService:
    """Service pour gérer l'historique utilisateur et le cache"""
    
    # TTL du cache Redis pour les réponses (30 jours)
    CACHE_TTL_DAYS = 30
    
    @staticmethod
    def _get_cache_key(user_id: str, question: str) -> str:
        """Génère une clé de cache pour une question utilisateur"""
        normalized = " ".join(question.lower().split())
        hash_obj = hashlib.md5(f"{user_id}:{normalized}".encode())
        return f"user_history:{hash_obj.hexdigest()}"
    
    @staticmethod
    async def get_cached_answer(
        user_id: str,
        question: str,
        check_history: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Récupère une réponse depuis le cache ou l'historique
        
        Args:
            user_id: ID de l'utilisateur
            question: Question posée
            check_history: Si True, vérifie aussi l'historique MongoDB
        
        Returns:
            {"answer": str, "cached": bool, "source": str} ou None
        """
        # 1. Vérifier le cache Redis (rapide)
        cache_key = UserHistoryService._get_cache_key(user_id, question)
        try:
            from app.utils.cache import get_redis
            redis_client = get_redis()
            if redis_client:
                cached = await redis_client.get(cache_key)
                if cached:
                    import json
                    data = json.loads(cached)
                    logger.debug(f"Cache HIT pour utilisateur {user_id}")
                    return {
                        "answer": data.get("answer"),
                        "cached": True,
                        "source": "redis_cache",
                        "model_used": data.get("model_used", "gpt-5-mini"),
                        "created_at": data.get("created_at")
                    }
        except Exception as e:
            logger.debug(f"Cache Redis non disponible: {e}")
        
        # 2. Vérifier l'historique MongoDB (si activé)
        if check_history:
            try:
                exact_match = await UserHistoryRepository.find_exact_match(user_id, question)
                if exact_match:
                    logger.debug(f"Historique HIT pour utilisateur {user_id}")
                    # Remettre en cache Redis
                    await UserHistoryService._cache_answer(user_id, question, exact_match["answer"], exact_match.get("model_used", "gpt-5-mini"))
                    return {
                        "answer": exact_match["answer"],
                        "cached": True,
                        "source": "user_history",
                        "model_used": exact_match.get("model_used", "gpt-5-mini"),
                        "created_at": exact_match.get("created_at")
                    }
            except Exception as e:
                logger.warning(f"Erreur vérification historique: {e}")
        
        return None
    
    @staticmethod
    async def _cache_answer(
        user_id: str,
        question: str,
        answer: str,
        model_used: str = "gpt-5-mini"
    ) -> bool:
        """Met en cache une réponse dans Redis"""
        try:
            from app.utils.cache import get_redis
            redis_client = get_redis()
            if redis_client:
                cache_key = UserHistoryService._get_cache_key(user_id, question)
                cache_data = {
                    "answer": answer,
                    "model_used": model_used,
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                import json
                ttl_seconds = UserHistoryService.CACHE_TTL_DAYS * 24 * 3600
                await redis_client.setex(cache_key, ttl_seconds, json.dumps(cache_data))
                return True
        except Exception as e:
            logger.debug(f"Erreur mise en cache Redis: {e}")
        return False
    
    @staticmethod
    async def store_answer(
        user_id: str,
        question: str,
        answer: str,
        model_used: str = "gpt-5-mini",
        subject: Optional[Subject] = None,
        module_id: Optional[str] = None,
        tokens_used: Optional[int] = None,
        cost_eur: Optional[float] = None,
        language: str = "fr",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Stocke une réponse dans l'historique et le cache
        
        Returns:
            Entrée créée dans l'historique
        """
        # 1. Créer l'entrée d'historique
        entry = HistoryEntry(
            user_id=user_id,
            question=question,
            answer=answer,
            subject=subject,
            module_id=module_id,
            model_used=model_used,
            tokens_used=tokens_used,
            cost_eur=cost_eur,
            language=language,
            metadata=metadata
        )
        
        # 2. Sauvegarder dans MongoDB
        try:
            stored_entry = await UserHistoryRepository.create_entry(entry)
        except Exception as e:
            logger.error(f"Erreur sauvegarde historique: {e}", exc_info=True)
            stored_entry = entry.dict()
        
        # 3. Mettre en cache Redis
        await UserHistoryService._cache_answer(user_id, question, answer, model_used)
        
        # 4. Mettre aussi dans le cache sémantique (pour réutilisation globale)
        await SemanticCache.set(question, model_used, answer, "default", module_id)
        
        return stored_entry
    
    @staticmethod
    async def get_user_history(
        user_id: str,
        subject: Optional[Subject] = None,
        module_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Récupère l'historique d'un utilisateur"""
        return await UserHistoryRepository.get_user_history(
            user_id=user_id,
            subject=subject,
            module_id=module_id,
            limit=limit,
            offset=offset
        )
    
    @staticmethod
    async def find_similar_questions(
        request: SimilarQuestionRequest
    ) -> SimilarQuestionResponse:
        """
        Trouve des questions similaires dans l'historique
        
        Returns:
            Questions similaires trouvées
        """
        # 1. Vérifier correspondance exacte
        if request.user_id:
            exact_match = await UserHistoryRepository.find_exact_match(
                request.user_id,
                request.question
            )
            if exact_match:
                return SimilarQuestionResponse(
                    question=request.question,
                    similar_questions=[],
                    found_exact_match=True,
                    exact_match_answer=exact_match["answer"]
                )
        
        # 2. Rechercher questions similaires
        similar = await UserHistoryRepository.find_similar_questions(
            user_id=request.user_id,
            question=request.question,
            threshold=request.threshold
        )
        
        similar_questions = [
            {
                "question": q["question"],
                "answer": q["answer"],
                "created_at": q.get("created_at"),
                "subject": q.get("subject")
            }
            for q in similar
        ]
        
        return SimilarQuestionResponse(
            question=request.question,
            similar_questions=similar_questions,
            found_exact_match=False
        )
    
    @staticmethod
    async def get_stats(user_id: str) -> Dict[str, Any]:
        """Récupère les statistiques de l'historique utilisateur"""
        return await UserHistoryRepository.get_stats(user_id)
    
    @staticmethod
    async def delete_user_history(user_id: str) -> Dict[str, Any]:
        """Supprime tout l'historique d'un utilisateur (RGPD)"""
        deleted_count = await UserHistoryRepository.delete_user_history(user_id)
        
        # Invalider aussi le cache Redis
        try:
            from app.utils.cache import get_redis
            redis_client = get_redis()
            if redis_client:
                # Supprimer toutes les clés de cache de l'utilisateur
                pattern = f"user_history:*"
                keys = await redis_client.keys(pattern)
                if keys:
                    await redis_client.delete(*keys)
        except Exception as e:
            logger.warning(f"Erreur invalidation cache: {e}")
        
        return {
            "deleted_count": deleted_count,
            "message": f"Historique supprimé: {deleted_count} entrées"
        }











