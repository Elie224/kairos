"""
Circuit Breaker Pattern pour protéger contre les pannes en cascade
Protège les appels aux services externes (OpenAI, MongoDB, etc.)
"""
import asyncio
import logging
from enum import Enum
from typing import Callable, TypeVar, Optional
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """États du circuit breaker"""
    CLOSED = "closed"  # Normal, les requêtes passent
    OPEN = "open"  # Panne détectée, toutes les requêtes sont bloquées
    HALF_OPEN = "half_open"  # Test de récupération, une seule requête est autorisée


class CircuitBreaker:
    """Circuit breaker pour protéger les appels aux services externes"""
    
    def __init__(
        self,
        failure_threshold: int = 5,  # Nombre d'échecs avant ouverture
        success_threshold: int = 2,  # Nombre de succès pour fermer
        timeout: float = 60.0,  # Temps avant de passer en half-open (secondes)
        expected_exception: tuple = (Exception,)
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> T:
        """Exécute une fonction avec protection circuit breaker"""
        async with self._lock:
            # Vérifier l'état du circuit
            if self.state == CircuitState.OPEN:
                # Vérifier si on peut passer en half-open
                if self.last_failure_time and \
                   (datetime.now() - self.last_failure_time).total_seconds() >= self.timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    logger.info(f"Circuit breaker: Passage en HALF_OPEN pour {func.__name__}")
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker is OPEN. Service unavailable. "
                        f"Retry after {self.timeout} seconds."
                    )
            
            # Exécuter la fonction
            try:
                result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
                
                # Succès
                await self._on_success()
                return result
                
            except self.expected_exception as e:
                # Échec
                await self._on_failure()
                raise e
    
    async def _on_success(self):
        """Gère un succès"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker: Circuit CLOSED (service recovered)")
        elif self.state == CircuitState.CLOSED:
            # Réinitialiser le compteur d'échecs en cas de succès
            self.failure_count = 0
    
    async def _on_failure(self):
        """Gère un échec"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            # Retour en OPEN si échec en half-open
            self.state = CircuitState.OPEN
            self.success_count = 0
            logger.warning("Circuit breaker: Retour en OPEN (service still failing)")
        elif self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            # Passer en OPEN si seuil d'échecs atteint
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker: Circuit OPENED after {self.failure_count} failures. "
                f"Service unavailable for {self.timeout} seconds."
            )
    
    def reset(self):
        """Réinitialise le circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        logger.info("Circuit breaker: Reset to CLOSED")


class CircuitBreakerOpenError(Exception):
    """Exception levée quand le circuit breaker est ouvert"""
    pass


# Circuit breakers globaux pour les services externes
openai_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    success_threshold=2,
    timeout=60.0,
    expected_exception=(Exception,)
)

mongodb_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    success_threshold=1,
    timeout=30.0,
    expected_exception=(ConnectionError, TimeoutError, Exception)
)


def circuit_breaker(circuit: CircuitBreaker):
    """Décorateur pour appliquer un circuit breaker à une fonction"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await circuit.call(func, *args, **kwargs)
        return wrapper
    return decorator
