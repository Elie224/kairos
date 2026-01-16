"""
Middleware de sécurité pour protéger l'application
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from app.config import settings
import time
import asyncio
import logging
from typing import Dict, List
from collections import defaultdict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware pour ajouter des en-têtes de sécurité HTTP"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # En-têtes de sécurité
        security_headers = {
            # Empêche le MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            # Active la protection XSS du navigateur
            "X-XSS-Protection": "1; mode=block",
            # Permettre l'embedding dans la même origine (pour les PDFs)
            "X-Frame-Options": "SAMEORIGIN",
            # Politique de référent strict
            "Referrer-Policy": "strict-origin-when-cross-origin",
            # Content Security Policy (CSP) - Dynamique selon l'environnement
            "Content-Security-Policy": settings.get_csp_policy(),
            # Permissions Policy (anciennement Feature Policy)
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "accelerometer=()"
            ),
            # Strict Transport Security (HSTS) - seulement en HTTPS
            # "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        }
        
        # Ajouter les en-têtes à la réponse
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware pour limiter le taux de requêtes (rate limiting)"""
    
    def __init__(self, app, requests_per_minute: int = 120, burst_size: int = 20):
        super().__init__(app)
        # En développement, être plus permissif pour localhost
        import os
        is_dev = os.getenv("ENVIRONMENT", "development").lower() == "development"
        # Augmenter les limites pour éviter de bloquer les utilisateurs légitimes
        self.requests_per_minute = requests_per_minute * (3 if is_dev else 1)  # 3x plus permissif en dev
        self.burst_size = burst_size * (5 if is_dev else 1)  # 5x plus permissif en dev
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, datetime] = {}
        self.block_duration = timedelta(minutes=1 if is_dev else 2)  # Blocage plus court (2 min au lieu de 5)
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrait l'IP réelle du client"""
        # Vérifier les headers de proxy
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
                # Débloquer après expiration
                del self.blocked_ips[ip]
        return False
    
    def _check_rate_limit(self, ip: str, requests_per_minute: int = None, burst_size: int = None) -> tuple[bool, str]:
        """Vérifie si la requête dépasse la limite"""
        # Utiliser les limites par défaut si non spécifiées
        if requests_per_minute is None:
            requests_per_minute = self.requests_per_minute
        if burst_size is None:
            burst_size = self.burst_size
            
        now = time.time()
        minute_ago = now - 60
        
        # Nettoyer les anciennes requêtes
        self.requests[ip] = [req_time for req_time in self.requests[ip] if req_time > minute_ago]
        
        # Vérifier le burst (nombre de requêtes simultanées)
        recent_requests = [req_time for req_time in self.requests[ip] if req_time > now - 1]
        if len(recent_requests) > burst_size:
            # En développement, être plus tolérant pour localhost
            import os
            is_dev = os.getenv("ENVIRONMENT", "development").lower() == "development"
            if is_dev and ip in ["127.0.0.1", "localhost", "::1"]:
                # En dev, permettre jusqu'à 2x le burst_size pour localhost
                if len(recent_requests) > burst_size * 2:
                    logger.warning(f"IP {ip} bloquée pour burst excessif (dev mode, limite: {burst_size * 2})")
                    self.blocked_ips[ip] = datetime.now() + timedelta(seconds=30)  # Blocage très court en dev
                    return False, "Trop de requêtes simultanées. Veuillez patienter."
            else:
                # Bloquer l'IP temporairement
                self.blocked_ips[ip] = datetime.now() + self.block_duration
                logger.warning(f"IP {ip} bloquée pour burst excessif (limite: {burst_size})")
                return False, "Trop de requêtes simultanées. Veuillez patienter."
        
        # Vérifier le taux par minute
        if len(self.requests[ip]) >= requests_per_minute:
            # Bloquer l'IP temporairement
            self.blocked_ips[ip] = datetime.now() + self.block_duration
            logger.warning(f"IP {ip} bloquée pour dépassement de limite")
            return False, f"Limite de {self.requests_per_minute} requêtes par minute atteinte."
        
        # Ajouter la requête actuelle
        self.requests[ip].append(now)
        return True, ""
    
    async def dispatch(self, request: Request, call_next):
        # Ne pas limiter les endpoints de santé et l'endpoint de suppression des utilisateurs (temporaire)
        excluded_paths = [
            "/health", "/", "/api/health", 
            "/api/auth/users/all/public", 
            "/api/auth/users/all/public/check", 
            "/api/auth/users/fix-password",
            "/api/auth/me",  # Endpoint de vérification d'authentification - doit être accessible
            "/api/auth/login",  # Login doit être accessible
            "/api/auth/register",  # Register doit être accessible
            "/api/auth/users/set-admin",  # Endpoint supprimé - exclure pour éviter les blocages
        ]
        
        # Exclure les endpoints de lecture (GET) courants utilisés par le dashboard
        # Ces endpoints sont moins critiques et peuvent être appelés fréquemment
        read_only_endpoints = [
            "/api/progress",
            "/api/validations",
            "/api/modules",
            "/api/badges",
            "/api/recommendations",
            "/api/favorites",
        ]
        
        # Vérifier si c'est un endpoint exclu
        is_excluded = (
            request.url.path in excluded_paths or 
            request.url.path.startswith("/api/auth/users/debug/") or
            request.url.path.startswith("/api/auth/users/set-admin") or  # Exclure même les variantes
            (request.method == "GET" and any(request.url.path.startswith(endpoint) for endpoint in read_only_endpoints))
        )
        
        if is_excluded:
            # Débloquer l'IP si elle était bloquée pour cet endpoint spécifique
            ip = self._get_client_ip(request)
            if ip in self.blocked_ips:
                logger.info(f"Déblocage automatique de l'IP {ip} pour l'accès à {request.url.path}")
                del self.blocked_ips[ip]
            if ip in self.requests:
                # Réinitialiser seulement partiellement pour les endpoints de lecture
                if request.method == "GET" and any(request.url.path.startswith(endpoint) for endpoint in read_only_endpoints):
                    # Garder seulement les 5 dernières requêtes pour éviter l'accumulation
                    self.requests[ip] = self.requests[ip][-5:]
                else:
                    # Réinitialiser complètement pour les autres endpoints exclus
                    self.requests[ip] = []
            return await call_next(request)
        
        ip = self._get_client_ip(request)
        
        # En développement, être plus permissif pour localhost
        import os
        is_dev = os.getenv("ENVIRONMENT", "development").lower() == "development"
        if is_dev and ip in ["127.0.0.1", "localhost", "::1"]:
            # Réinitialiser le compteur pour localhost en dev
            if ip in self.blocked_ips:
                del self.blocked_ips[ip]
            if ip in self.requests:
                # Garder seulement les 10 dernières requêtes pour éviter l'accumulation
                self.requests[ip] = self.requests[ip][-10:]
        
        # Vérifier si la requête est authentifiée (présence d'un token Bearer)
        is_authenticated = False
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            is_authenticated = True
            # Pour les requêtes authentifiées, augmenter les limites
            # En production, on peut être plus permissif pour les utilisateurs authentifiés
            effective_requests_per_minute = self.requests_per_minute * 2  # 2x plus de marge pour les utilisateurs authentifiés
            effective_burst_size = self.burst_size * 2
        else:
            effective_requests_per_minute = self.requests_per_minute
            effective_burst_size = self.burst_size
        
        # Vérifier si l'IP est bloquée
        if self._is_blocked(ip):
            # Pour les utilisateurs authentifiés, réduire le temps de blocage ou débloquer
            if is_authenticated:
                # Vérifier si le blocage peut être réduit
                if ip in self.blocked_ips:
                    time_remaining = (self.blocked_ips[ip] - datetime.now()).total_seconds()
                    if time_remaining > 30:  # Si plus de 30 secondes restantes
                        # Réduire le blocage à 30 secondes pour les utilisateurs authentifiés
                        self.blocked_ips[ip] = datetime.now() + timedelta(seconds=30)
                        logger.info(f"Blocage réduit pour utilisateur authentifié: {ip} (30 secondes)")
                        # Ne pas bloquer, laisser passer après réduction
                    else:
                        # Si moins de 30 secondes, débloquer complètement pour les utilisateurs authentifiés
                        logger.info(f"Déblocage automatique pour utilisateur authentifié: {ip}")
                        del self.blocked_ips[ip]
                        # Laisser passer la requête
            else:
                # Pour les utilisateurs non authentifiés, vérifier si c'est un endpoint important
                # Si oui, débloquer temporairement
                important_paths = ["/api/progress", "/api/validations", "/api/modules"]
                if any(request.url.path.startswith(path) for path in important_paths):
                    logger.info(f"Déblocage temporaire pour endpoint important: {ip} -> {request.url.path}")
                    del self.blocked_ips[ip]
                    # Laisser passer
                else:
                    return StarletteResponse(
                        content='{"detail": "IP temporairement bloquée. Veuillez réessayer plus tard."}',
                        status_code=429,
                        media_type="application/json",
                        headers={"Retry-After": "120"}
                    )
        
        # Vérifier le rate limit avec les limites ajustées pour les utilisateurs authentifiés
        allowed, message = self._check_rate_limit(ip, effective_requests_per_minute, effective_burst_size)
        if not allowed:
            retry_after = "30" if is_authenticated else "60"
            return StarletteResponse(
                content=f'{{"detail": "{message}"}}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": retry_after}
            )
        
        response = await call_next(request)
        return response


class AIRateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware pour limiter le taux de requêtes sur les endpoints IA"""
    
    def __init__(self, app, requests_per_minute: int = 10, requests_per_hour: int = 50):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_minute: Dict[str, List[float]] = defaultdict(list)
        self.requests_hour: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: Dict[str, datetime] = {}
        self.block_duration = timedelta(minutes=10)
    
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
    
    async def _check_rate_limit(self, ip: str) -> tuple[bool, str]:
        """Vérifie si la requête dépasse la limite pour les endpoints IA"""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        
        # Prefer using Redis for IA rate limits
        try:
            from app.utils.cache import get_redis
            redis = get_redis()
        except Exception:
            redis = None

        if redis:
            try:
                minute_key = f"airate:minute:{ip}"
                hour_key = f"airate:hour:{ip}"
                # Increment minute counter
                mcount = await redis.incr(minute_key)
                if mcount == 1:
                    await redis.expire(minute_key, 60)
                if mcount > self.requests_per_minute:
                    await redis.set(f"airate:blocked:{ip}", 1, ex=int(self.block_duration.total_seconds()))
                    logger.warning(f"IP {ip} blocked for IA minute limit (redis)")
                    return False, f"Limite de {self.requests_per_minute} requêtes IA par minute atteinte."
                # Increment hour counter
                hcount = await redis.incr(hour_key)
                if hcount == 1:
                    await redis.expire(hour_key, 3600)
                if hcount > self.requests_per_hour:
                    await redis.set(f"airate:blocked:{ip}", 1, ex=int(self.block_duration.total_seconds()))
                    logger.warning(f"IP {ip} blocked for IA hour limit (redis)")
                    return False, f"Limite de {self.requests_per_hour} requêtes IA par heure atteinte."
                return True, ""
            except Exception:
                pass

        # Nettoyer les anciennes requêtes
        self.requests_minute[ip] = [req_time for req_time in self.requests_minute[ip] if req_time > minute_ago]
        self.requests_hour[ip] = [req_time for req_time in self.requests_hour[ip] if req_time > hour_ago]
        
        # Vérifier la limite par minute
        if len(self.requests_minute[ip]) >= self.requests_per_minute:
            self.blocked_ips[ip] = datetime.now() + self.block_duration
            logger.warning(f"IP {ip} bloquée pour dépassement de limite IA (minute)")
            return False, f"Limite de {self.requests_per_minute} requêtes IA par minute atteinte."
        
        # Vérifier la limite par heure
        if len(self.requests_hour[ip]) >= self.requests_per_hour:
            self.blocked_ips[ip] = datetime.now() + self.block_duration
            logger.warning(f"IP {ip} bloquée pour dépassement de limite IA (heure)")
            return False, f"Limite de {self.requests_per_hour} requêtes IA par heure atteinte."
        
        # Ajouter la requête actuelle
        self.requests_minute[ip].append(now)
        self.requests_hour[ip].append(now)
        return True, ""
    
    async def dispatch(self, request: Request, call_next):
        # Appliquer uniquement aux endpoints IA
        if not request.url.path.startswith("/api/ai/"):
            return await call_next(request)
        
        ip = self._get_client_ip(request)
        
        # Vérifier si l'IP est bloquée (memory based)
        if self._is_blocked(ip):
            return StarletteResponse(
                content='{"detail": "IP temporairement bloquée pour abus des endpoints IA. Veuillez réessayer plus tard."}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "600"}
            )
        # Vérifier si bloquée côté Redis
        try:
            from app.utils.cache import get_redis
            redis = get_redis()
        except Exception:
            redis = None
        if redis:
            try:
                if await redis.get(f"airate:blocked:{ip}"):
                    return StarletteResponse(
                        content='{"detail": "IP temporairement bloquée pour abus des endpoints IA. Veuillez réessayer plus tard."}',
                        status_code=429,
                        media_type="application/json",
                        headers={"Retry-After": "600"}
                    )
            except Exception:
                pass
        
        # Vérifier le rate limit
        allowed, message = await self._check_rate_limit(ip)
        if not allowed:
            return StarletteResponse(
                content=f'{{"detail": "{message}"}}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60"}
            )
        
        response = await call_next(request)
        return response


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour logger les événements de sécurité"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")
        
        # Logger les tentatives d'accès aux endpoints sensibles
        sensitive_paths = ["/api/auth/login", "/api/auth/register", "/api/auth/"]
        if any(path in request.url.path for path in sensitive_paths):
            logger.info(f"Tentative d'accès: {request.method} {request.url.path} depuis {ip}")
        
        response = await call_next(request)
        
        # Logger les erreurs de sécurité (401 est normal pour les utilisateurs non connectés)
        if response.status_code == 401:
            # Ne logger qu'en DEBUG - les 401 sont normaux (utilisateur non connecté)
            logger.debug(f"Accès non authentifié: {request.method} {request.url.path} depuis {ip}")
        elif response.status_code == 403:
            logger.warning(f"Accès interdit: {request.method} {request.url.path} depuis {ip}")
        elif response.status_code == 429:
            logger.warning(f"Rate limit dépassé: {request.method} {request.url.path} depuis {ip}")
        
        # Logger les requêtes suspectes (seuil augmenté pour éviter les faux positifs)
        duration = time.time() - start_time
        # Routes qui peuvent être lentes normalement
        slow_allowed_routes = ['/api/auth/login', '/api/auth/register', '/api/ai/chat', '/api/exams/generate']
        is_slow_allowed = any(request.url.path.startswith(route) for route in slow_allowed_routes)
        
        if duration > 10 and not is_slow_allowed:  # Seuil augmenté à 10s pour éviter les faux positifs
            logger.warning(f"Requête très lente détectée: {request.method} {request.url.path} ({duration:.2f}s) depuis {ip}")
        
        # Détecter les user agents suspects
        suspicious_agents = ["curl", "wget", "python-requests", "scanner", "bot"]
        if any(agent.lower() in user_agent.lower() for agent in suspicious_agents):
            logger.info(f"User agent suspect: {user_agent} depuis {ip}")
        
        return response

