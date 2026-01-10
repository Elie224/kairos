"""
Middleware pour limiter la taille des requêtes
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

# Limites de taille (en bytes)
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB pour les requêtes générales
MAX_MODULE_CONTENT_SIZE = 5 * 1024 * 1024  # 5MB pour le contenu de module


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware pour limiter la taille des requêtes"""
    
    async def dispatch(self, request: Request, call_next):
        # Vérifier la taille du Content-Length si présent
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                size = int(content_length)
                
                # Limite générale
                if size > MAX_REQUEST_SIZE:
                    logger.warning(
                        f"Requête trop volumineuse rejetée: {size} bytes "
                        f"(max: {MAX_REQUEST_SIZE} bytes) depuis {request.client.host if request.client else 'unknown'}"
                    )
                    return Response(
                        content='{"detail": "Requête trop volumineuse. Taille maximale: 10MB"}',
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        media_type="application/json"
                    )
                
                # Limite spécifique pour la création de modules
                if request.url.path == "/api/modules/" and request.method == "POST":
                    if size > MAX_MODULE_CONTENT_SIZE:
                        logger.warning(
                            f"Contenu de module trop volumineux rejeté: {size} bytes "
                            f"(max: {MAX_MODULE_CONTENT_SIZE} bytes)"
                        )
                        return Response(
                            content='{"detail": "Le contenu du module est trop volumineux. Taille maximale: 5MB. Considérez stocker les assets lourds dans un object storage."}',
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            media_type="application/json"
                        )
            except ValueError:
                # Content-Length invalide, continuer (sera géré par FastAPI)
                pass
        
        response = await call_next(request)
        return response

