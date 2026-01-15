"""
Middleware pour la gestion centralisée des erreurs
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Gère les erreurs de validation"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Erreur de validation: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Erreur de validation des données",
            "errors": errors
        },
        headers={"Content-Encoding": "identity"}  # Désactiver la compression pour éviter les problèmes GZip
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Gère les exceptions HTTP"""
    # Les erreurs 401 (non authentifié) sont normales et ne doivent pas être loggées comme warnings
    if exc.status_code == 401:
        logger.debug(f"Utilisateur non authentifié: {request.method} {request.url.path}")
    elif exc.status_code == 404:
        logger.debug(f"Ressource non trouvée: {request.method} {request.url.path}")
    else:
        logger.warning(f"Exception HTTP {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        },
        headers={"Content-Encoding": "identity"}  # Désactiver la compression pour éviter les problèmes GZip
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Gère les exceptions générales"""
    import traceback
    error_trace = traceback.format_exc()
    
    # Logger les détails complets (toujours en interne) - masquer les informations sensibles
    error_type = type(exc).__name__
    error_message = str(exc)
    
    # Masquer les chemins de fichiers et autres informations sensibles dans les logs
    safe_error_message = error_message
    if settings.is_production:
        # En production, ne pas logger les chemins de fichiers complets
        import re
        safe_error_message = re.sub(r'/[^\s]+', '[PATH]', safe_error_message)
        safe_error_message = re.sub(r'[A-Z]:\\[^\s]+', '[PATH]', safe_error_message)
    
    logger.error(f"Erreur inattendue [{error_type}]: {safe_error_message}")
    logger.error(f"Traceback: {error_trace}")
    logger.error(f"URL: {request.url.path}")  # Ne logger que le path, pas les query params
    logger.error(f"Method: {request.method}")
    
    # Ne jamais exposer les détails de l'erreur en production
    if settings.is_production:
        # Message générique en production
        detail_message = "Une erreur interne s'est produite. Veuillez réessayer plus tard."
        
        # Messages spécifiques mais génériques selon le type d'erreur
        if any(keyword in error_type.lower() for keyword in ['connection', 'timeout', 'network']):
            detail_message = "Erreur de connexion. Veuillez vérifier votre connexion réseau et réessayer."
        elif any(keyword in error_message.lower() for keyword in ['mongodb', 'database', 'connection']):
            detail_message = "Service temporairement indisponible. Veuillez réessayer plus tard."
        elif 'validation' in error_type.lower() or 'value' in error_type.lower():
            detail_message = "Données invalides. Veuillez vérifier vos informations."
    else:
        # En développement, donner plus de détails mais toujours sécurisés
        detail_message = f"Erreur serveur [{error_type}]: {safe_error_message}"
        if any(keyword in error_message.lower() for keyword in ['mongodb', 'database', 'connection']):
            detail_message = "Erreur de connexion à la base de données. Vérifiez que MongoDB est démarré."
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail_message,
            "status_code": 500
        },
        headers={"Content-Encoding": "identity"}  # Désactiver la compression pour éviter les problèmes GZip
    )


