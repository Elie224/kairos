"""
Métriques Prometheus pour monitoring de l'application
"""
from prometheus_client import Counter, Histogram, Gauge, Summary
import time
from typing import Optional

# Métriques de performance
request_duration = Histogram(
    'http_request_duration_seconds',
    'Durée des requêtes HTTP en secondes',
    ['method', 'endpoint', 'status_code'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

request_count = Counter(
    'http_requests_total',
    'Nombre total de requêtes HTTP',
    ['method', 'endpoint', 'status_code']
)

active_requests = Gauge(
    'http_active_requests',
    'Nombre de requêtes actives en cours'
)

# Métriques base de données
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Durée des requêtes base de données en secondes',
    ['operation', 'collection'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

db_connection_pool_size = Gauge(
    'db_connection_pool_size',
    'Taille du pool de connexions MongoDB',
    ['state']  # active, idle, total
)

# Métriques IA
ai_requests_total = Counter(
    'ai_requests_total',
    'Nombre total de requêtes IA',
    ['model', 'endpoint', 'status']
)

ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'Durée des requêtes IA en secondes',
    ['model'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

ai_tokens_used = Counter(
    'ai_tokens_used_total',
    'Nombre total de tokens utilisés',
    ['model', 'type']  # type: prompt, completion
)

ai_cost_eur = Counter(
    'ai_cost_eur_total',
    'Coût total en EUR des requêtes IA',
    ['model']
)

ai_errors_total = Counter(
    'ai_errors_total',
    'Nombre total d\'erreurs IA',
    ['model', 'error_type']
)

# Métriques cache
cache_hits = Counter(
    'cache_hits_total',
    'Nombre de hits de cache',
    ['cache_type']
)

cache_misses = Counter(
    'cache_misses_total',
    'Nombre de misses de cache',
    ['cache_type']
)

cache_size = Gauge(
    'cache_size_bytes',
    'Taille du cache en bytes',
    ['cache_type']
)

# Métriques utilisateurs
active_users = Gauge(
    'active_users_total',
    'Nombre d\'utilisateurs actifs'
)

user_registrations = Counter(
    'user_registrations_total',
    'Nombre total d\'inscriptions',
    ['status']  # success, failed
)

user_logins = Counter(
    'user_logins_total',
    'Nombre total de connexions',
    ['status']  # success, failed
)

# Métriques business
modules_completed = Counter(
    'modules_completed_total',
    'Nombre total de modules complétés',
    ['subject', 'difficulty']
)

exams_passed = Counter(
    'exams_passed_total',
    'Nombre total d\'examens réussis',
    ['subject']
)

quiz_attempts = Counter(
    'quiz_attempts_total',
    'Nombre total de tentatives de quiz',
    ['subject', 'result']  # passed, failed
)


class MetricsCollector:
    """Collecteur de métriques pour l'application"""
    
    @staticmethod
    def record_request(method: str, endpoint: str, status_code: int, duration: float):
        """Enregistre une requête HTTP"""
        request_duration.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).observe(duration)
        
        request_count.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
    
    @staticmethod
    def record_db_query(operation: str, collection: str, duration: float):
        """Enregistre une requête base de données"""
        db_query_duration.labels(
            operation=operation,
            collection=collection
        ).observe(duration)
    
    @staticmethod
    def record_ai_request(
        model: str,
        endpoint: str,
        duration: float,
        tokens_prompt: int = 0,
        tokens_completion: int = 0,
        cost_eur: float = 0.0,
        status: str = 'success'
    ):
        """Enregistre une requête IA"""
        ai_requests_total.labels(
            model=model,
            endpoint=endpoint,
            status=status
        ).inc()
        
        ai_request_duration.labels(model=model).observe(duration)
        
        if tokens_prompt > 0:
            ai_tokens_used.labels(model=model, type='prompt').inc(tokens_prompt)
        
        if tokens_completion > 0:
            ai_tokens_used.labels(model=model, type='completion').inc(tokens_completion)
        
        if cost_eur > 0:
            ai_cost_eur.labels(model=model).inc(cost_eur)
        
        if status != 'success':
            ai_errors_total.labels(model=model, error_type=status).inc()
    
    @staticmethod
    def record_cache_hit(cache_type: str):
        """Enregistre un hit de cache"""
        cache_hits.labels(cache_type=cache_type).inc()
    
    @staticmethod
    def record_cache_miss(cache_type: str):
        """Enregistre un miss de cache"""
        cache_misses.labels(cache_type=cache_type).inc()
    
    @staticmethod
    def record_user_registration(status: str):
        """Enregistre une inscription"""
        user_registrations.labels(status=status).inc()
    
    @staticmethod
    def record_user_login(status: str):
        """Enregistre une connexion"""
        user_logins.labels(status=status).inc()
    
    @staticmethod
    def record_module_completed(subject: str, difficulty: str):
        """Enregistre un module complété"""
        modules_completed.labels(subject=subject, difficulty=difficulty).inc()
    
    @staticmethod
    def record_exam_passed(subject: str):
        """Enregistre un examen réussi"""
        exams_passed.labels(subject=subject).inc()
    
    @staticmethod
    def record_quiz_attempt(subject: str, result: str):
        """Enregistre une tentative de quiz"""
        quiz_attempts.labels(subject=subject, result=result).inc()
    
    @staticmethod
    def record_user_feedback(feedback_type: str):
        """Enregistre un feedback utilisateur"""
        user_feedback.labels(feedback_type=feedback_type).inc()
    
    @staticmethod
    def set_active_users(count: int):
        """Définit le nombre d'utilisateurs actifs"""
        active_users.set(count)
    
    @staticmethod
    def set_db_connection_pool_size(state: str, size: int):
        """Définit la taille du pool de connexions"""
        db_connection_pool_size.labels(state=state).set(size)
    
    @staticmethod
    def set_cache_size(cache_type: str, size_bytes: int):
        """Définit la taille du cache"""
        cache_size.labels(cache_type=cache_type).set(size_bytes)
    
    @staticmethod
    def increment_active_requests():
        """Incrémente le nombre de requêtes actives"""
        active_requests.inc()
    
    @staticmethod
    def decrement_active_requests():
        """Décrémente le nombre de requêtes actives"""
        active_requests.dec()
