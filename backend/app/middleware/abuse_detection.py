"""
Middleware pour la détection d'abus
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.services.abuse_detection_service import AbuseDetectionService
from app.utils.permissions import get_current_user_optional
import logging

logger = logging.getLogger(__name__)


class AbuseDetectionMiddleware(BaseHTTPMiddleware):
    """Middleware pour détecter et bloquer les abus"""
    
    # Endpoints IA à protéger
    AI_ENDPOINTS = [
        "/api/ai/chat",
        "/api/ai/chat/stream",
        "/api/ai/chat/vision",
        "/api/ai/generate",
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Vérifier seulement les endpoints IA
        if not any(request.url.path.startswith(endpoint) for endpoint in self.AI_ENDPOINTS):
            return await call_next(request)
        
        # Récupérer l'utilisateur (optionnel, peut être None pour les endpoints publics)
        try:
            user = await get_current_user_optional(request)
            user_id = user.get("id") if user else request.client.host  # Utiliser IP si pas d'utilisateur
        except Exception:
            user_id = request.client.host
        
        # Vérifier si l'utilisateur est bloqué
        if user_id:
            is_blocked = await AbuseDetectionService.is_user_blocked(str(user_id))
            if is_blocked:
                logger.warning(f"Requête bloquée - Utilisateur {user_id} est temporairement bloqué")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Vous avez été temporairement bloqué pour usage abusif. Veuillez réessayer plus tard."
                    }
                )
        
        # Pour les requêtes POST avec body, vérifier le prompt hacking
        if request.method == "POST":
            try:
                # Lire le body (attention: cela consomme le stream)
                body = await request.body()
                if body:
                    import json
                    try:
                        data = json.loads(body)
                        message = data.get("message", "") or data.get("question", "") or ""
                        
                        if message and user_id:
                            abuse_check = await AbuseDetectionService.check_abuse(
                                str(user_id),
                                message,
                                request.url.path
                            )
                            
                            if abuse_check.get("should_block"):
                                # Bloquer temporairement
                                await AbuseDetectionService.block_user_temporarily(str(user_id), 300)
                                
                                logger.warning(
                                    f"Abus détecté et bloqué - Utilisateur: {user_id}, "
                                    f"Types: {abuse_check.get('abuse_types')}"
                                )
                                
                                return JSONResponse(
                                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                    content={
                                        "detail": "Requête bloquée pour usage abusif détecté."
                                    }
                                )
                    except (json.JSONDecodeError, KeyError):
                        pass  # Body non-JSON ou pas de message, continuer
            except Exception as e:
                logger.debug(f"Erreur lors de la lecture du body pour détection d'abus: {e}")
                # Continuer même en cas d'erreur
        
        # Vérifier le flood même sans body
        if user_id:
            abuse_check = await AbuseDetectionService.check_abuse(
                str(user_id),
                "",
                request.url.path
            )
            
            if abuse_check.get("should_block"):
                await AbuseDetectionService.block_user_temporarily(str(user_id), 300)
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Trop de requêtes. Veuillez ralentir."
                    }
                )
        
        return await call_next(request)
