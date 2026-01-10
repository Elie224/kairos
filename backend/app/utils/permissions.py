"""
Utilitaires pour la gestion des permissions et rôles
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any
from app.services.auth_service import AuthService
import logging

logger = logging.getLogger(__name__)

# OAuth2 scheme pour l'authentification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Récupère l'utilisateur actuel depuis le token"""
    return await AuthService.get_current_user_from_token(token)


async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dépendance FastAPI qui vérifie que l'utilisateur est admin.
    À utiliser dans les endpoints qui nécessitent des permissions admin.
    
    Usage:
        @router.post("/admin-only")
        async def admin_endpoint(admin_user: dict = Depends(require_admin)):
            ...
    """
    if not current_user.get("is_admin", False):
        logger.warning(f"Tentative d'accès admin par un utilisateur non-admin: {current_user.get('id')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé: cette opération nécessite des permissions administrateur"
        )
    return current_user


def is_admin(user: Dict[str, Any]) -> bool:
    """Vérifie si un utilisateur est admin"""
    return user.get("is_admin", False)


def require_admin_sync(user: Dict[str, Any]) -> None:
    """
    Vérifie de manière synchrone si un utilisateur est admin.
    Lève une exception si ce n'est pas le cas.
    """
    if not is_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé: cette opération nécessite des permissions administrateur"
        )

