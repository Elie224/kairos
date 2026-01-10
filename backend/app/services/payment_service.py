"""
Service pour les paiements Stripe
Intégration complète avec Stripe pour abonnements
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
try:
    import stripe
except ImportError:
    stripe = None
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Stripe non installé - fonctionnalités de paiement désactivées")
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialiser Stripe si disponible
if stripe:
    stripe.api_key = getattr(settings, 'stripe_secret_key', None)
    if not stripe.api_key:
        logger.warning("STRIPE_SECRET_KEY non configuré - Fonctionnalités de paiement désactivées")
else:
    logger.warning("Stripe non installé - Installez avec: pip install stripe")


class PaymentService:
    """Service de paiement Stripe"""
    
    @staticmethod
    async def create_checkout_session(
        user_id: str,
        plan: str,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Crée une session de checkout Stripe pour un abonnement
        """
        try:
            if not stripe:
                raise ValueError("Stripe non installé. Installez avec: pip install stripe")
            if not stripe.api_key:
                raise ValueError("Stripe non configuré (STRIPE_SECRET_KEY manquant)")
            
            # Prix selon le plan (en centimes)
            prices = {
                "premium": {
                    "price_id": getattr(settings, 'stripe_premium_price_id', 'price_premium'),
                    "amount": 1999,  # 19.99€
                    "currency": "eur"
                },
                "enterprise": {
                    "price_id": getattr(settings, 'stripe_enterprise_price_id', 'price_enterprise'),
                    "amount": 4999,  # 49.99€
                    "currency": "eur"
                }
            }
            
            if plan not in prices:
                raise ValueError(f"Plan {plan} non valide")
            
            price_info = prices[plan]
            
            # Créer la session de checkout
            checkout_session = stripe.checkout.Session.create(
                customer_email=None,  # Sera rempli par l'utilisateur
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': price_info['currency'],
                        'product_data': {
                            'name': f'Kaïros {plan.capitalize()}',
                            'description': f'Abonnement {plan.capitalize()} à Kaïros'
                        },
                        'unit_amount': price_info['amount'],
                        'recurring': {
                            'interval': 'month'
                        }
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': user_id,
                    'plan': plan
                },
                subscription_data={
                    'metadata': {
                        'user_id': user_id,
                        'plan': plan
                    }
                }
            )
            
            return {
                "session_id": checkout_session.id,
                "url": checkout_session.url,
                "plan": plan,
                "amount": price_info['amount'] / 100  # Convertir en euros
            }
            
        except Exception as e:
            if stripe and hasattr(stripe, 'error') and isinstance(e, stripe.error.StripeError):
                logger.error(f"Erreur Stripe: {e}", exc_info=True)
                raise ValueError(f"Erreur de paiement: {str(e)}")
            logger.error(f"Erreur lors de la création de session: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la création de session: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def handle_webhook(payload: bytes, signature: str) -> Dict[str, Any]:
        """
        Traite un webhook Stripe
        """
        try:
            if not stripe:
                return {"status": "ignored", "reason": "stripe_not_installed"}
            
            webhook_secret = getattr(settings, 'stripe_webhook_secret', None)
            if not webhook_secret:
                logger.warning("STRIPE_WEBHOOK_SECRET non configuré")
                return {"status": "ignored", "reason": "webhook_secret_not_configured"}
            
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            # Gérer les événements
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                await PaymentService._handle_subscription_created(session)
            elif event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                await PaymentService._handle_subscription_updated(subscription)
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                await PaymentService._handle_subscription_cancelled(subscription)
            elif event['type'] == 'invoice.payment_succeeded':
                invoice = event['data']['object']
                await PaymentService._handle_payment_succeeded(invoice)
            elif event['type'] == 'invoice.payment_failed':
                invoice = event['data']['object']
                await PaymentService._handle_payment_failed(invoice)
            
            return {"status": "processed", "event_type": event['type']}
            
        except ValueError as e:
            logger.error(f"Erreur webhook: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Erreur traitement webhook: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    async def _handle_subscription_created(session: Dict[str, Any]):
        """Gère la création d'un abonnement"""
        try:
            user_id = session['metadata'].get('user_id')
            plan = session['metadata'].get('plan')
            subscription_id = session.get('subscription')
            
            if user_id and plan:
                from app.repositories.subscription_repository import SubscriptionRepository
                await SubscriptionRepository.create_subscription({
                    "user_id": user_id,
                    "plan": plan,
                    "stripe_subscription_id": subscription_id,
                    "stripe_customer_id": session.get('customer'),
                    "status": "active",
                    "start_date": datetime.now(timezone.utc),
                    "auto_renew": True,
                    "created_at": datetime.now(timezone.utc)
                })
                logger.info(f"Abonnement créé pour utilisateur {user_id}, plan {plan}")
        except Exception as e:
            logger.error(f"Erreur lors de la création d'abonnement: {e}", exc_info=True)
    
    @staticmethod
    async def _handle_subscription_updated(subscription: Dict[str, Any]):
        """Gère la mise à jour d'un abonnement"""
        try:
            subscription_id = subscription.get('id')
            status = subscription.get('status')
            
            from app.repositories.subscription_repository import SubscriptionRepository
            await SubscriptionRepository.update_by_stripe_id(
                subscription_id,
                {"status": status}
            )
            logger.info(f"Abonnement {subscription_id} mis à jour: {status}")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour: {e}", exc_info=True)
    
    @staticmethod
    async def _handle_subscription_cancelled(subscription: Dict[str, Any]):
        """Gère l'annulation d'un abonnement"""
        try:
            subscription_id = subscription.get('id')
            
            from app.repositories.subscription_repository import SubscriptionRepository
            await SubscriptionRepository.update_by_stripe_id(
                subscription_id,
                {
                    "status": "cancelled",
                    "end_date": datetime.now(timezone.utc)
                }
            )
            logger.info(f"Abonnement {subscription_id} annulé")
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation: {e}", exc_info=True)
    
    @staticmethod
    async def _handle_payment_succeeded(invoice: Dict[str, Any]):
        """Gère un paiement réussi"""
        try:
            subscription_id = invoice.get('subscription')
            if subscription_id:
                from app.repositories.subscription_repository import SubscriptionRepository
                await SubscriptionRepository.update_by_stripe_id(
                    subscription_id,
                    {"last_payment_date": datetime.now(timezone.utc)}
                )
                logger.info(f"Paiement réussi pour abonnement {subscription_id}")
        except Exception as e:
            logger.error(f"Erreur lors du traitement du paiement: {e}", exc_info=True)
    
    @staticmethod
    async def _handle_payment_failed(invoice: Dict[str, Any]):
        """Gère un échec de paiement"""
        try:
            subscription_id = invoice.get('subscription')
            if subscription_id:
                from app.repositories.subscription_repository import SubscriptionRepository
                await SubscriptionRepository.update_by_stripe_id(
                    subscription_id,
                    {"status": "payment_failed"}
                )
                logger.warning(f"Échec de paiement pour abonnement {subscription_id}")
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'échec: {e}", exc_info=True)
    
    @staticmethod
    async def cancel_subscription(user_id: str) -> bool:
        """
        Annule un abonnement
        """
        try:
            from app.repositories.subscription_repository import SubscriptionRepository
            subscription = await SubscriptionRepository.get_active_subscription(user_id)
            
            if not subscription:
                return False
            
            stripe_subscription_id = subscription.get('stripe_subscription_id')
            if stripe_subscription_id and stripe:
                stripe.Subscription.modify(
                    stripe_subscription_id,
                    cancel_at_period_end=True
                )
            
            await SubscriptionRepository.update_by_stripe_id(
                stripe_subscription_id,
                {"auto_renew": False}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'annulation: {e}", exc_info=True)
            return False

