"""
Middleware Prometheus pour collecter les métriques
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from app.utils.prometheus_metrics import MetricsCollector

logger = logging.getLogger(__name__)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware pour collecter les métriques Prometheus"""
    
    async def dispatch(self, request: Request, call_next):
        # Ignorer les endpoints de métriques et health check
        if request.url.path in ['/metrics', '/health', '/api/health']:
            return await call_next(request)
        
        # Incrémenter les requêtes actives
        MetricsCollector.increment_active_requests()
        
        start_time = time.time()
        method = request.method
        endpoint = request.url.path
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            duration = time.time() - start_time
            
            # Enregistrer la métrique
            MetricsCollector.record_request(method, endpoint, status_code, duration)
            
            return response
        except Exception as e:
            status_code = 500
            duration = time.time() - start_time
            
            # Enregistrer l'erreur
            MetricsCollector.record_request(method, endpoint, status_code, duration)
            
            raise
        finally:
            # Décrémenter les requêtes actives
            MetricsCollector.decrement_active_requests()
