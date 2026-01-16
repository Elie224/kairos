"""
Routeur pour les abonnements et monétisation
Intégration complète Stripe
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from typing import Dict, Any, Optional
from app.models.subscription import SubscriptionPlan, PlanLimits, Subscription
from app.services.subscription_service import SubscriptionService
from app.services.payment_service import PaymentService
# Authentification supprimée - toutes les routes sont publiques
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/plans/{plan}", response_model=PlanLimits)
async def get_plan_limits(plan: SubscriptionPlan):
    """
    Récupère les limites d'un plan
    """
    try:
        limits = SubscriptionService.get_plan_limits(plan)
        return limits
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/my-plan", response_model=Dict[str, Any])
async def get_my_plan(
):
    """
    Récupère le plan actuel de l'utilisateur
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        plan = await SubscriptionService.get_user_plan(user_id)
        limits = SubscriptionService.get_plan_limits(plan)
        
        from app.repositories.subscription_repository import SubscriptionRepository
        subscription = await SubscriptionRepository.get_active_subscription(user_id)
        
        return {
            "plan": plan.value,
            "limits": limits.dict(),
            "subscription": subscription,
            "is_premium": plan != SubscriptionPlan.FREE
        }
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/checkout", response_model=Dict[str, Any])
async def create_checkout_session(
    plan: SubscriptionPlan,
    success_url: str,
    cancel_url: str,
):
    """
    Crée une session de checkout Stripe pour un abonnement
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        if plan == SubscriptionPlan.FREE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le plan gratuit ne nécessite pas de paiement"
            )
        
        session = await PaymentService.create_checkout_session(
            user_id=user_id,
            plan=plan.value,
            success_url=success_url,
            cancel_url=cancel_url
        )
        
        return session
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """
    Webhook Stripe pour gérer les événements de paiement
    """
    try:
        payload = await request.body()
        
        result = await PaymentService.handle_webhook(
            payload=payload,
            signature=stripe_signature
        )
        
        return result
    except ValueError as e:
        logger.error(f"Erreur webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erreur traitement webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.post("/cancel", response_model=Dict[str, Any])
async def cancel_subscription(
):
    """
    Annule l'abonnement de l'utilisateur
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        success = await PaymentService.cancel_subscription(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Aucun abonnement actif trouvé"
            )
        
        return {
            "success": True,
            "message": "Abonnement annulé. Il restera actif jusqu'à la fin de la période payée."
        }
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/check-ai-limit", response_model=Dict[str, Any])
async def check_ai_limit(
):
    """
    Vérifie les limites IA de l'utilisateur
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        limits = await SubscriptionService.check_ai_limit(user_id)
        return limits
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )


@router.get("/check-feature/{feature}", response_model=Dict[str, bool])
async def check_feature_access(
    feature: str,
):
    """
    Vérifie si l'utilisateur peut accéder à une fonctionnalité
    """
    try:
        user_id = "anonymous"  # Auth supprimée
        
        can_access = await SubscriptionService.can_access_feature(user_id, feature)
        return {"can_access": can_access}
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur: {str(e)}"
        )

