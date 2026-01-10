"""
Repository pour les abonnements
"""
from typing import Optional, Dict, Any
from app.database import get_database
from app.schemas import serialize_doc
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class SubscriptionRepository:
    """Repository pour abonnements"""
    
    @staticmethod
    async def create_subscription(subscription_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un abonnement"""
        try:
            db = get_database()
            result = await db.subscriptions.insert_one(subscription_data)
            if result.inserted_id:
                created = await db.subscriptions.find_one({"_id": result.inserted_id})
                return serialize_doc(created)
            raise ValueError("Échec création abonnement")
        except Exception as e:
            logger.error(f"Erreur création abonnement: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_active_subscription(user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère l'abonnement actif d'un utilisateur"""
        try:
            db = get_database()
            subscription = await db.subscriptions.find_one({
                "user_id": user_id,
                "status": {"$in": ["active", "trial"]}
            }, sort=[("created_at", -1)])
            return serialize_doc(subscription) if subscription else None
        except Exception as e:
            logger.error(f"Erreur récupération abonnement: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def update_by_stripe_id(
        stripe_subscription_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Met à jour un abonnement par son ID Stripe"""
        try:
            db = get_database()
            result = await db.subscriptions.update_one(
                {"stripe_subscription_id": stripe_subscription_id},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                updated = await db.subscriptions.find_one({
                    "stripe_subscription_id": stripe_subscription_id
                })
                return serialize_doc(updated)
            return None
        except Exception as e:
            logger.error(f"Erreur mise à jour abonnement: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère l'abonnement d'un utilisateur"""
        try:
            db = get_database()
            subscription = await db.subscriptions.find_one(
                {"user_id": user_id},
                sort=[("created_at", -1)]
            )
            return serialize_doc(subscription) if subscription else None
        except Exception as e:
            logger.error(f"Erreur récupération abonnement: {e}", exc_info=True)
            return None











