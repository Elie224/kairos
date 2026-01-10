"""
Configuration de l'application
"""
from pydantic_settings import BaseSettings
from typing import Optional
import secrets
import os

class Settings(BaseSettings):
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db_name: str = os.getenv("MONGODB_DB_NAME", "kaïros")
    # Timeout MongoDB en millisecondes (5 secondes par défaut)
    mongodb_timeout_ms: int = int(os.getenv("MONGODB_TIMEOUT_MS", "5000"))
    
    # Sécurité JWT - OBLIGATOIRE en production
    secret_key: str = os.getenv("SECRET_KEY", "")
    algorithm: str = "HS256"
    
    # Rate limiting général
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst_size: int = 10
    
    # Rate limiting pour endpoints IA (plus restrictif)
    ai_rate_limit_per_minute: int = 10
    ai_rate_limit_per_hour: int = 50
    
    # OpenAI - GPT-5.2, GPT-5-mini, GPT-5-nano
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    # Optional HTTP proxy for OpenAI requests, e.g. "http://proxy:3128"
    openai_proxy: Optional[str] = None
    openai_model: str = "gpt-5-mini"  # Modèle par défaut (GPT-5-mini)
    gpt_5_2_model: str = "gpt-5.2"  # Expert - Raisonnement complexe (Examens, TD avancés, TP ML)
    gpt_5_mini_model: str = "gpt-5-mini"  # Principal - Pédagogique (TD standards, quiz, explications)
    gpt_5_nano_model: str = "gpt-5-nano"  # Rapide - Économique (QCM, flash-cards, vérifications)
    
    # PostgreSQL
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: str = os.getenv("POSTGRES_PORT", "5432")
    postgres_db: str = os.getenv("POSTGRES_DB", "eduverse")
    
    # Environnement
    environment: str = os.getenv("ENVIRONMENT", "development")
    # Redis (optional) for rate limiting and cache
    redis_url: Optional[str] = os.getenv("REDIS_URL", None)
    
    # Sécurité supplémentaire
    enable_csrf: bool = os.getenv("ENABLE_CSRF", "false").lower() == "true"
    allowed_hosts: list[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    # Frontend URL pour les liens dans les emails
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Stripe Configuration
    stripe_secret_key: Optional[str] = os.getenv("STRIPE_SECRET_KEY", None)
    stripe_webhook_secret: Optional[str] = os.getenv("STRIPE_WEBHOOK_SECRET", None)
    stripe_premium_price_id: Optional[str] = os.getenv("STRIPE_PREMIUM_PRICE_ID", None)
    stripe_enterprise_price_id: Optional[str] = os.getenv("STRIPE_ENTERPRISE_PRICE_ID", None)
    
    # AI Cost Guard Configuration
    ai_monthly_token_limit: int = int(os.getenv("AI_MONTHLY_TOKEN_LIMIT", "10000000"))  # 10M tokens/mois
    ai_monthly_cost_limit_eur: float = float(os.getenv("AI_MONTHLY_COST_LIMIT_EUR", "50.0"))  # 50€/mois max
    
    @property
    def is_production(self) -> bool:
        """Vérifie si on est en production"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Vérifie si on est en développement"""
        return self.environment.lower() == "development"
    
    def get_csp_policy(self) -> str:
        """Retourne la politique CSP selon l'environnement"""
        if self.is_production:
            # CSP strict pour production (sans unsafe-inline/unsafe-eval)
            return (
                "default-src 'self'; "
                "script-src 'self'; "  # Pas de unsafe-inline en prod
                "style-src 'self'; "  # Pas de unsafe-inline en prod
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
        else:
            # CSP plus permissif pour développement
            return (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'; "
                "frame-src 'self' blob: data:; "  # Autoriser les iframes pour les PDFs (blob:)
                "frame-ancestors 'self'; "  # Permettre l'embedding dans la même origine
                "base-uri 'self'; "
                "form-action 'self';"
            )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignorer les champs extra dans .env (compatibilité)

settings = Settings()

# Validation de la configuration en production
if settings.is_production:
    if not settings.secret_key or len(settings.secret_key) < 32:
        raise ValueError(
            "SECRET_KEY est obligatoire en production et doit contenir au moins 32 caractères. "
            "Configurez SECRET_KEY dans les variables d'environnement."
        )
    
    if settings.mongodb_url == "mongodb://localhost:27017":
        import warnings
        warnings.warn(
            "ATTENTION: MongoDB URL par défaut utilisée en production! "
            "Configurez MONGODB_URL dans les variables d'environnement.",
            UserWarning
        )
    
    # Vérifier que la clé secrète n'est pas la valeur par défaut
    if settings.secret_key == secrets.token_urlsafe(32):
        # Si c'est une nouvelle clé générée, c'est un problème
        import warnings
        warnings.warn(
            "ATTENTION: Une nouvelle SECRET_KEY a été générée. "
            "Tous les tokens JWT existants seront invalides. "
            "Configurez SECRET_KEY dans les variables d'environnement.",
            UserWarning
        )

