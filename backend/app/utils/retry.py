"""
Utilitaires pour retry avec backoff exponentiel
"""
import asyncio
import logging
from typing import Callable, TypeVar, Optional
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """
    Exécute une fonction avec retry et backoff exponentiel
    
    Args:
        func: Fonction à exécuter (doit être awaitable)
        max_retries: Nombre maximum de tentatives
        initial_delay: Délai initial en secondes
        max_delay: Délai maximum en secondes
        exponential_base: Base pour le calcul exponentiel
        exceptions: Tuple d'exceptions à capturer
    
    Returns:
        Résultat de la fonction
    
    Raises:
        La dernière exception si toutes les tentatives échouent
    """
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return await func()
        except exceptions as e:
            if attempt == max_retries - 1:
                # Dernière tentative échouée, lever l'exception
                logger.error(f"Toutes les tentatives ont échoué après {max_retries} essais: {e}")
                raise
            
            logger.warning(
                f"Tentative {attempt + 1}/{max_retries} échouée: {e}. "
                f"Réessai dans {delay:.2f} secondes..."
            )
            
            await asyncio.sleep(delay)
            delay = min(delay * exponential_base, max_delay)
    
    # Ne devrait jamais arriver ici, mais au cas où
    raise Exception("Erreur inattendue dans retry_with_backoff")


def retry_sync(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exceptions: tuple = (Exception,)
) -> T:
    """
    Version synchrone de retry_with_backoff
    
    Args:
        func: Fonction à exécuter
        max_retries: Nombre maximum de tentatives
        initial_delay: Délai initial en secondes
        exceptions: Tuple d'exceptions à capturer
    
    Returns:
        Résultat de la fonction
    """
    import time
    
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries - 1:
                logger.error(f"Toutes les tentatives ont échoué après {max_retries} essais: {e}")
                raise
            
            logger.warning(
                f"Tentative {attempt + 1}/{max_retries} échouée: {e}. "
                f"Réessai dans {delay:.2f} secondes..."
            )
            
            time.sleep(delay)
            delay = min(delay * 2, 60.0)
    
    raise Exception("Erreur inattendue dans retry_sync")

