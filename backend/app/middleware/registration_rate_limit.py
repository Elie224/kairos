"""
Middleware pour limiter le taux d'inscription (rate limiting spécifique)
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from typing import Dict, List
from collections import defaultdict
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)


class RegistrationRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware pour limiter le taux d'inscription (plus restrictif que le rate limiting général)"""
    
    def __init__(self, app, registrations_per_hour: int = 3, registrations_per_day: int = 5):
        super().__init__(app)
        self.registrations_per_hour = registrations_per_hour
        self.registrations_per_day = registrations_per_day
        self.hour_limits: Dict[str, List[float]] = defaultdict(list)
        self.day_limits: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, datetime] = {}
        self.block_duration = timedelta(hours=1)
        # En développement, ne bloquer que 15 minutes au lieu d'1 heure
        import os
        if os.getenv("ENVIRONMENT", "development").lower() == "development":
            self.block_duration = timedelta(minutes=15)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrait l'IP réelle du client"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _is_blocked(self, ip: str) -> bool:
        """Vérifie si l'IP est bloquée"""
        if ip in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip]:
                return True
            else:
                del self.blocked_ips[ip]
        return False
    
    async def dispatch(self, request: Request, call_next):
        # Appliquer seulement sur l'endpoint d'inscription
        if request.url.path != "/api/auth/register" or request.method != "POST":
            return await call_next(request)
        
        ip = self._get_client_ip(request)
        now = time.time()
        
        # Vérifier si l'IP est bloquée
        if self._is_blocked(ip):
            logger.warning(f"Tentative d'inscription depuis IP bloquée: {ip}")
            return StarletteResponse(
                content='{"detail": "Trop de tentatives d\'inscription. Veuillez réessayer plus tard."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": "3600"}  # 1 heure
            )
        
        # Nettoyer les anciennes entrées
        hour_ago = now - 3600
        day_ago = now - 86400
        
        self.hour_limits[ip] = [t for t in self.hour_limits[ip] if t > hour_ago]
        self.day_limits[ip] = [t for t in self.day_limits[ip] if t > day_ago]
        
        # Vérifier les limites
        if len(self.hour_limits[ip]) >= self.registrations_per_hour:
            # Bloquer l'IP temporairement
            self.blocked_ips[ip] = datetime.now() + self.block_duration
            logger.warning(f"IP {ip} bloquée pour trop d'inscriptions par heure")
            return StarletteResponse(
                content='{"detail": "Limite d\'inscriptions par heure atteinte. Veuillez réessayer plus tard."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": "3600"}
            )
        
        if len(self.day_limits[ip]) >= self.registrations_per_day:
            logger.warning(f"IP {ip} a atteint la limite d'inscriptions par jour")
            return StarletteResponse(
                content='{"detail": "Limite d\'inscriptions par jour atteinte. Veuillez réessayer demain."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": "86400"}  # 24 heures
            )
        
        # Enregistrer la tentative
        self.hour_limits[ip].append(now)
        self.day_limits[ip].append(now)
        
        response = await call_next(request)
        return response

