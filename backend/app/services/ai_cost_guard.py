"""
AI Cost Guard - Protection contre les coûts excessifs OpenAI
Plafonds par utilisateur, plafond mensuel global, fallback automatique
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from app.database import get_database
from app.config import settings
from app.utils.model_mapper import map_to_real_model, get_model_cost
import logging

logger = logging.getLogger(__name__)


class AICostGuard:
    """Garde-fou pour les coûts OpenAI"""
    
    # Plafonds par défaut
    DEFAULT_USER_DAILY_TOKENS = 100000  # 100k tokens/jour par utilisateur
    DEFAULT_MONTHLY_TOKENS = 10000000   # 10M tokens/mois global
    DEFAULT_MONTHLY_COST_EUR = 50.0     # 50€/mois max
    
    @staticmethod
    async def check_user_limit(user_id: str, estimated_tokens: int) -> Dict[str, Any]:
        """
        Vérifie si l'utilisateur peut faire une requête
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "remaining_tokens": int,
                "fallback_model": Optional[str]
            }
        """
        try:
            db = get_database()
            today = datetime.now(timezone.utc).date()
            
            # Récupérer les limites de l'utilisateur (depuis subscription ou défaut)
            from app.services.subscription_service import SubscriptionService
            plan = await SubscriptionService.get_user_plan(user_id)
            
            # Limites selon le plan
            daily_limit = AICostGuard._get_daily_limit(plan)
            
            # Compter les tokens utilisés aujourd'hui
            start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            
            daily_usage = await db.ai_usage.aggregate([
                {
                    "$match": {
                        "user_id": user_id,
                        "created_at": {"$gte": start_of_day}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_tokens": {"$sum": "$tokens_used"}
                    }
                }
            ]).to_list(length=1)
            
            tokens_used_today = daily_usage[0].get("total_tokens", 0) if daily_usage else 0
            remaining_tokens = max(0, daily_limit - tokens_used_today)
            
            # Vérifier si la requête est autorisée
            if tokens_used_today + estimated_tokens > daily_limit:
                # Suggérer un modèle moins cher (mapper vers le vrai modèle)
                fallback_model = map_to_real_model("gpt-5-mini") if estimated_tokens > 0 else None
                
                return {
                    "allowed": False,
                    "reason": f"Limite quotidienne atteinte ({tokens_used_today}/{daily_limit} tokens)",
                    "remaining_tokens": remaining_tokens,
                    "fallback_model": fallback_model,
                    "suggestion": f"Utilisez {fallback_model} ou attendez demain" if fallback_model else "Attendez demain"
                }
            
            return {
                "allowed": True,
                "reason": "OK",
                "remaining_tokens": remaining_tokens - estimated_tokens,
                "fallback_model": None
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification limite utilisateur: {e}", exc_info=True)
            # En cas d'erreur, autoriser (fail open pour ne pas bloquer)
            return {
                "allowed": True,
                "reason": "Erreur vérification, autorisé par sécurité",
                "remaining_tokens": 100000,
                "fallback_model": None
            }
    
    @staticmethod
    async def check_global_limit(estimated_tokens: int, model: str) -> Dict[str, Any]:
        """
        Vérifie le plafond mensuel global
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "estimated_cost": float,
                "monthly_cost": float,
                "fallback_model": Optional[str]
            }
        """
        try:
            db = get_database()
            now = datetime.now(timezone.utc)
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Récupérer les limites globales depuis la config
            monthly_token_limit = getattr(settings, 'ai_monthly_token_limit', AICostGuard.DEFAULT_MONTHLY_TOKENS)
            monthly_cost_limit = getattr(settings, 'ai_monthly_cost_limit_eur', AICostGuard.DEFAULT_MONTHLY_COST_EUR)
            
            # Calculer le coût estimé de cette requête (utiliser la fonction utilitaire)
            model_cost_per_million = get_model_cost(model)
            estimated_cost = (estimated_tokens / 1_000_000) * model_cost_per_million
            
            # Compter les tokens et coûts du mois
            monthly_usage = await db.ai_usage.aggregate([
                {
                    "$match": {
                        "created_at": {"$gte": start_of_month}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_tokens": {"$sum": "$tokens_used"},
                        "total_cost": {"$sum": "$cost_eur"}
                    }
                }
            ]).to_list(length=1)
            
            if monthly_usage:
                monthly_tokens = monthly_usage[0].get("total_tokens", 0)
                monthly_cost = monthly_usage[0].get("total_cost", 0.0)
            else:
                monthly_tokens = 0
                monthly_cost = 0.0
            
            # Vérifier les limites
            if monthly_tokens + estimated_tokens > monthly_token_limit:
                fallback_model = map_to_real_model("gpt-5-mini")
                return {
                    "allowed": False,
                    "reason": f"Plafond mensuel de tokens atteint ({monthly_tokens}/{monthly_token_limit})",
                    "estimated_cost": estimated_cost,
                    "monthly_cost": monthly_cost,
                    "fallback_model": fallback_model
                }
            
            if monthly_cost + estimated_cost > monthly_cost_limit:
                fallback_model = map_to_real_model("gpt-5-mini")
                return {
                    "allowed": False,
                    "reason": f"Plafond mensuel de coût atteint ({monthly_cost:.2f}€/{monthly_cost_limit}€)",
                    "estimated_cost": estimated_cost,
                    "monthly_cost": monthly_cost,
                    "fallback_model": fallback_model
                }
            
            return {
                "allowed": True,
                "reason": "OK",
                "estimated_cost": estimated_cost,
                "monthly_cost": monthly_cost + estimated_cost,
                "fallback_model": None
            }
            
        except Exception as e:
            logger.error(f"Erreur vérification limite globale: {e}", exc_info=True)
            return {
                "allowed": True,
                "reason": "Erreur vérification, autorisé par sécurité",
                "estimated_cost": 0.0,
                "monthly_cost": 0.0,
                "fallback_model": None
            }
    
    @staticmethod
    async def record_usage(
        user_id: str,
        model: str,
        tokens_used: int,
        cost_eur: float
    ) -> None:
        """Enregistre l'utilisation IA pour le suivi des coûts"""
        try:
            db = get_database()
            await db.ai_usage.insert_one({
                "user_id": user_id,
                "model": model,
                "tokens_used": tokens_used,
                "cost_eur": cost_eur,
                "created_at": datetime.now(timezone.utc)
            })
        except Exception as e:
            logger.error(f"Erreur enregistrement usage: {e}", exc_info=True)
    
    @staticmethod
    async def estimate_tokens(message: str, context: Optional[str] = None) -> int:
        """
        Estime le nombre de tokens pour une requête
        Approximation: ~4 caractères = 1 token
        """
        total_chars = len(message)
        if context:
            total_chars += len(context)
        
        # Ajouter ~20% pour les tokens système et formatage
        estimated = int((total_chars / 4) * 1.2)
        return max(estimated, 10)  # Minimum 10 tokens
    
    @staticmethod
    def _get_daily_limit(plan) -> int:
        """Retourne la limite quotidienne selon le plan"""
        from app.models.subscription import SubscriptionPlan
        
        limits = {
            SubscriptionPlan.FREE: 50000,      # 50k tokens/jour
            SubscriptionPlan.PREMIUM: 200000,  # 200k tokens/jour
            SubscriptionPlan.ENTERPRISE: -1    # Illimité
        }
        
        return limits.get(plan, 50000)
    
    @staticmethod
    async def get_user_stats(user_id: str) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation de l'utilisateur"""
        try:
            db = get_database()
            today = datetime.now(timezone.utc).date()
            start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Stats du jour
            daily_stats = await db.ai_usage.aggregate([
                {
                    "$match": {
                        "user_id": user_id,
                        "created_at": {"$gte": start_of_day}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_tokens": {"$sum": "$tokens_used"},
                        "total_cost": {"$sum": "$cost_eur"},
                        "requests": {"$sum": 1}
                    }
                }
            ]).to_list(length=1)
            
            # Stats du mois
            monthly_stats = await db.ai_usage.aggregate([
                {
                    "$match": {
                        "user_id": user_id,
                        "created_at": {"$gte": start_of_month}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_tokens": {"$sum": "$tokens_used"},
                        "total_cost": {"$sum": "$cost_eur"},
                        "requests": {"$sum": 1}
                    }
                }
            ]).to_list(length=1)
            
            from app.services.subscription_service import SubscriptionService
            plan = await SubscriptionService.get_user_plan(user_id)
            daily_limit = AICostGuard._get_daily_limit(plan)
            
            daily = daily_stats[0] if daily_stats else {"total_tokens": 0, "total_cost": 0.0, "requests": 0}
            monthly = monthly_stats[0] if monthly_stats else {"total_tokens": 0, "total_cost": 0.0, "requests": 0}
            
            return {
                "daily": {
                    "tokens_used": daily["total_tokens"],
                    "tokens_limit": daily_limit,
                    "cost_eur": daily["total_cost"],
                    "requests": daily["requests"]
                },
                "monthly": {
                    "tokens_used": monthly["total_tokens"],
                    "cost_eur": monthly["total_cost"],
                    "requests": monthly["requests"]
                },
                "plan": plan.value
            }
            
        except Exception as e:
            logger.error(f"Erreur récupération stats: {e}", exc_info=True)
            return {
                "daily": {"tokens_used": 0, "tokens_limit": 50000, "cost_eur": 0.0, "requests": 0},
                "monthly": {"tokens_used": 0, "cost_eur": 0.0, "requests": 0},
                "plan": "free"
            }











