"""
Modèles pour les abonnements et monétisation
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SubscriptionPlan(str, Enum):
    """Plans d'abonnement"""
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, Enum):
    """Statut d'abonnement"""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"


class Subscription(BaseModel):
    """Modèle d'abonnement"""
    id: str
    user_id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    auto_renew: bool = True
    payment_method: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
        use_enum_values = True


class PlanLimits(BaseModel):
    """Limites d'un plan"""
    plan: SubscriptionPlan
    ai_requests_per_month: int
    modules_access: str  # "all" ou liste de IDs
    features: List[str]
    max_storage_gb: int
    priority_support: bool











