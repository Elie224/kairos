"""
Middleware CSRF (Cross-Site Request Forgery) Protection
Protège contre les attaques CSRF en validant les tokens CSRF
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import secrets
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    """Middleware pour protéger contre les attaques CSRF"""
    
    # Méthodes HTTP qui nécessitent une protection CSRF
    PROTECTED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    
    # Endpoints exemptés de la protection CSRF (API publiques, webhooks, etc.)
    EXEMPT_PATHS = {
        "/api/health",
        "/api/docs",
        "/api/openapi.json",
        "/api/redoc",
        "/",  # Health check
    }
    
    def __init__(self, app):
        super().__init__(app)
        self.secret_key = getattr(settings, 'csrf_secret_key', secrets.token_urlsafe(32))
    
    def _is_exempt(self, path: str) -> bool:
        """Vérifie si un chemin est exempté de la protection CSRF"""
        return any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS)
    
    def _get_csrf_token(self, request: Request) -> Optional[str]:
        """Récupère le token CSRF depuis les headers ou cookies"""
        # Vérifier d'abord le header (préféré pour les API)
        token = request.headers.get("X-CSRF-Token")
        if token:
            return token
        
        # Vérifier ensuite le cookie (pour les formulaires HTML)
        token = request.cookies.get("csrf_token")
        return token
    
    def _validate_csrf_token(self, request: Request, token: Optional[str]) -> bool:
        """Valide le token CSRF"""
        if not token:
            return False
        
        # En production, implémenter une validation plus stricte
        # Pour l'instant, vérifier que le token existe et a la bonne longueur
        if len(token) < 32:
            return False
        
        # TODO: Implémenter une validation plus robuste avec signature
        # Pour l'instant, accepter tout token de longueur suffisante
        return True
    
    async def dispatch(self, request: Request, call_next):
        # Ne pas protéger les méthodes GET, HEAD, OPTIONS
        if request.method not in self.PROTECTED_METHODS:
            return await call_next(request)
        
        # Ne pas protéger les endpoints exemptés
        if self._is_exempt(request.url.path):
            return await call_next(request)
        
        # Récupérer le token CSRF
        csrf_token = self._get_csrf_token(request)
        
        # Valider le token
        if not self._validate_csrf_token(request, csrf_token):
            logger.warning(
                f"Tentative de requête CSRF bloquée: {request.method} {request.url.path} "
                f"depuis {request.client.host if request.client else 'unknown'}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token CSRF manquant ou invalide. Veuillez rafraîchir la page."
            )
        
        # Continuer avec la requête
        response = await call_next(request)
        
        # Ajouter le token CSRF dans les cookies pour les prochaines requêtes
        # (seulement pour les réponses HTML)
        if "text/html" in response.headers.get("Content-Type", ""):
            if "csrf_token" not in request.cookies:
                # Générer un nouveau token CSRF
                new_token = secrets.token_urlsafe(32)
                response.set_cookie(
                    key="csrf_token",
                    value=new_token,
                    httponly=False,  # Accessible via JavaScript pour les headers
                    samesite="strict",
                    secure=not settings.debug,  # Secure seulement en production
                    max_age=3600 * 24,  # 24 heures
                )
        
        return response
