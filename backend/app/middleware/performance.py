"""
Middleware pour optimiser les performances
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import logging

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware pour logger les performances et ajouter des headers"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Ajouter des headers de performance
        response: Response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Routes qui peuvent être lentes normalement (ne pas logger comme warning)
        slow_allowed_routes = [
            '/api/auth/login',
            '/api/auth/register',
            '/api/ai/chat',
            '/api/ai/chat/stream',
            '/api/exams/generate',
            '/api/modules/',
        ]
        
        # Logger les requêtes lentes (> 2 secondes) sauf pour les routes autorisées
        if process_time > 2.0:
            # Vérifier si c'est une route autorisée à être lente
            is_slow_allowed = any(
                request.url.path.startswith(route) for route in slow_allowed_routes
            )
            
            if not is_slow_allowed:
                logger.warning(
                    f"Requête lente: {request.method} {request.url.path} "
                    f"en {process_time:.2f}s"
                )
            else:
                # Logger en INFO pour les routes autorisées (pour monitoring)
                logger.info(
                    f"Requête longue (normale): {request.method} {request.url.path} "
                    f"en {process_time:.2f}s"
                )
        
        # Ajouter des headers de performance
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = str(id(request))
        
        return response














