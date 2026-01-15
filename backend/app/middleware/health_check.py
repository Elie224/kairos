"""
Middleware pour les health checks améliorés
Fournit des informations détaillées sur l'état de l'application
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging
import time
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware pour améliorer les health checks"""
    
    async def dispatch(self, request: Request, call_next):
        # Intercepter les requêtes vers /health et /api/health
        if request.url.path in ["/health", "/api/health"]:
            return await self._handle_health_check(request)
        
        return await call_next(request)
    
    async def _handle_health_check(self, request: Request) -> Response:
        """Gère les health checks avec informations détaillées"""
        health_status: Dict[str, Any] = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {}
        }
        
        # Vérifier MongoDB
        try:
            from app.database import get_database
            db = get_database()
            if db is not None:
                await db.client.admin.command('ping')
                health_status["services"]["mongodb"] = {
                    "status": "healthy",
                    "response_time_ms": 0  # TODO: Mesurer le temps de réponse
                }
            else:
                health_status["services"]["mongodb"] = {
                    "status": "unavailable",
                    "error": "Database not initialized"
                }
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["services"]["mongodb"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["status"] = "unhealthy"
        
        # Vérifier Redis (optionnel)
        try:
            from app.utils.cache import get_redis
            redis = get_redis()
            if redis:
                start = time.time()
                await redis.ping()
                response_time = (time.time() - start) * 1000
                health_status["services"]["redis"] = {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2)
                }
            else:
                health_status["services"]["redis"] = {
                    "status": "not_configured",
                    "message": "Redis is optional"
                }
        except Exception as e:
            health_status["services"]["redis"] = {
                "status": "unavailable",
                "error": str(e)
            }
            # Redis est optionnel, ne pas marquer comme unhealthy
        
        # Déterminer le code de statut HTTP
        if health_status["status"] == "healthy":
            status_code = 200
        elif health_status["status"] == "degraded":
            status_code = 200  # Toujours 200, mais avec status "degraded"
        else:
            status_code = 503  # Service Unavailable
        
        return JSONResponse(
            content=health_status,
            status_code=status_code,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
