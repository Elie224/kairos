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
        
        # Logger les requêtes lentes (> 1 seconde)
        if process_time > 1.0:
            logger.warning(
                f"Requête lente: {request.method} {request.url.path} "
                f"en {process_time:.2f}s"
            )
        
        # Ajouter des headers de performance
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = str(id(request))
        
        return response














