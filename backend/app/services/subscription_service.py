"""
Service pour les abonnements et monétisation
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from app.models.subscription import SubscriptionPlan, SubscriptionStatus, PlanLimits
from app.repositories.subscription_repository import SubscriptionRepository
import logging

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service d'abonnements"""
    
    @staticmethod
    def get_plan_limits(plan: SubscriptionPlan) -> PlanLimits:
        """Retourne les limites d'un plan"""
        limits_map = {
            SubscriptionPlan.FREE: PlanLimits(
                plan=SubscriptionPlan.FREE,
                ai_requests_per_month=50,
                modules_access="limited",
                features=["basic_modules", "basic_quiz"],
                max_storage_gb=1,
                priority_support=False
            ),
            SubscriptionPlan.PREMIUM: PlanLimits(
                plan=SubscriptionPlan.PREMIUM,
                ai_requests_per_month=500,
                modules_access="all",
                features=["all_modules", "ai_tutor", "virtual_labs", "advanced_analytics"],
                max_storage_gb=10,
                priority_support=True
            ),
            SubscriptionPlan.ENTERPRISE: PlanLimits(
                plan=SubscriptionPlan.ENTERPRISE,
                ai_requests_per_month=-1,  # Illimité
                modules_access="all",
                features=["all_features", "custom_content", "api_access"],
                max_storage_gb=100,
                priority_support=True
            )
        }
        
        return limits_map.get(plan, limits_map[SubscriptionPlan.FREE])
    
    @staticmethod
    async def get_user_plan(user_id: str) -> SubscriptionPlan:
        """Récupère le plan d'un utilisateur"""
        try:
            subscription = await SubscriptionRepository.get_active_subscription(user_id)
            if subscription:
                plan_str = subscription.get("plan", "free")
                return SubscriptionPlan(plan_str)
            return SubscriptionPlan.FREE
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du plan: {e}", exc_info=True)
            return SubscriptionPlan.FREE
    
    @staticmethod
    async def check_ai_limit(user_id: str) -> Dict[str, Any]:
        """
        Vérifie si l'utilisateur peut faire une requête IA
        Compte les requêtes du mois en cours
        """
        try:
            plan = await SubscriptionService.get_user_plan(user_id)
            limits = SubscriptionService.get_plan_limits(plan)
            
            # Si illimité
            if limits.ai_requests_per_month == -1:
                return {
                    "allowed": True,
                    "remaining": -1,
                    "limit": -1,
                    "plan": plan.value
                }
            
            # Compter les requêtes du mois en cours
            from app.database import get_database
            db = get_database()
            
            start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Compter les requêtes IA ce mois (à partir des logs ou collection dédiée)
            ai_requests_count = await db.ai_requests.count_documents({
                "user_id": user_id,
                "created_at": {"$gte": start_of_month}
            })
            
            remaining = max(0, limits.ai_requests_per_month - ai_requests_count)
            allowed = remaining > 0
            
            return {
                "allowed": allowed,
                "remaining": remaining,
                "limit": limits.ai_requests_per_month,
                "plan": plan.value,
                "used": ai_requests_count
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de limite: {e}", exc_info=True)
            # En cas d'erreur, autoriser (fail open)
            return {
                "allowed": True,
                "remaining": 50,
                "limit": 50,
                "plan": "free"
            }
    
    @staticmethod
    async def record_ai_request(user_id: str, endpoint: str) -> bool:
        """
        Enregistre une requête IA pour le comptage
        """
        try:
            from app.database import get_database
            db = get_database()
            
            await db.ai_requests.insert_one({
                "user_id": user_id,
                "endpoint": endpoint,
                "created_at": datetime.now(timezone.utc)
            })
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de requête: {e}", exc_info=True)
            return False
    
    @staticmethod
    async def can_access_feature(user_id: str, feature: str) -> bool:
        """
        Vérifie si l'utilisateur peut accéder à une fonctionnalité
        """
        try:
            plan = await SubscriptionService.get_user_plan(user_id)
            limits = SubscriptionService.get_plan_limits(plan)
            
            return feature in limits.features
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'accès: {e}", exc_info=True)
            # En cas d'erreur, refuser l'accès (fail closed)
            return False

