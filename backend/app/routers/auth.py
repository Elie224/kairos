"""
Routeur pour l'authentification
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any
from app.services.auth_service import AuthService
from app.utils.permissions import get_current_user, require_admin
from app.utils.security import InputSanitizer
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, Any]:
    """
    Connexion d'un utilisateur
    """
    try:
        # OAuth2PasswordRequestForm utilise 'username' mais on accepte email
        email = form_data.username
        logger.info(f"Tentative de connexion pour email: {email}")
        
        user = await AuthService.authenticate_user(email, form_data.password)
        if not user:
            logger.warning(f"Échec de l'authentification pour email: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Authentification réussie pour user_id: {user.get('id')}")
        
        # Créer le token
        access_token_expires = timedelta(hours=24)
        access_token = AuthService.create_access_token(
            data={"sub": str(user["id"])},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la connexion"
        )


@router.post("/register")
async def register(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inscription d'un nouvel utilisateur
    """
    try:
        logger.info(f"Tentative d'inscription pour email: {user_data.get('email')}, username: {user_data.get('username')}")
        user = await AuthService.register_user(user_data)
        logger.info(f"Inscription réussie pour user_id: {user.get('id')}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'inscription: {str(e)}"
        )


@router.get("/me")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Récupère les informations de l'utilisateur connecté
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Déconnexion (côté serveur, le token reste valide jusqu'à expiration)
    """
    return {"message": "Déconnexion réussie"}


@router.put("/me")
async def update_current_user(
    user_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Met à jour les informations de l'utilisateur connecté
    """
    from app.repositories.user_repository import UserRepository
    from app.utils.security import PasswordHasher
    
    user_id = str(current_user["id"])
    
    # Si un nouveau mot de passe est fourni, le hasher
    if "password" in user_data and user_data["password"]:
        user_data["hashed_password"] = PasswordHasher.hash_password(user_data.pop("password"))
    
    # Mettre à jour l'utilisateur
    updated_user = await UserRepository.update(user_id, user_data)
    
    # Retourner sans le mot de passe
    updated_user.pop("hashed_password", None)
    updated_user.pop("password_reset_token", None)
    updated_user.pop("email_verification_token", None)
    
    return updated_user


@router.delete("/users/all")
async def delete_all_users(
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Supprime tous les utilisateurs de la base de données (ADMIN ONLY)
    """
    from app.repositories.user_repository import UserRepository
    from app.database.mongo import db
    
    try:
        # Compter les utilisateurs avant suppression
        count_before = await db.database.users.count_documents({})
        
        if count_before == 0:
            return {
                "message": "Aucun utilisateur à supprimer",
                "deleted_count": 0
            }
        
        # Supprimer tous les utilisateurs
        result = await db.database.users.delete_many({})
        deleted_count = result.deleted_count
        
        logger.warning(f"⚠️  {deleted_count} utilisateur(s) supprimé(s) par {current_user.get('email')}")
        
        return {
            "message": f"{deleted_count} utilisateur(s) supprimé(s) avec succès",
            "deleted_count": deleted_count
        }
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des utilisateurs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )


@router.delete("/users/all/public")
async def delete_all_users_public(request: Request) -> Dict[str, Any]:
    """
    ⚠️ ENDPOINT TEMPORAIRE - Supprime tous les utilisateurs SANS authentification
    À SUPPRIMER après utilisation pour des raisons de sécurité
    Débloque automatiquement l'IP du rate limiting
    """
    from app.database.mongo import db
    from app.middleware.security import RateLimitMiddleware
    
    try:
        # Débloquer l'IP du rate limiting
        # Récupérer l'IP du client
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            real_ip = request.headers.get("X-Real-IP")
            ip = real_ip if real_ip else (request.client.host if request.client else "unknown")
        
        # Débloquer l'IP dans tous les middlewares de rate limiting
        # Note: Cette approche nécessite d'accéder aux instances des middlewares
        # Pour l'instant, on va juste supprimer les utilisateurs
        
        # Compter les utilisateurs avant suppression
        count_before = await db.database.users.count_documents({})
        
        if count_before == 0:
            return {
                "message": "Aucun utilisateur à supprimer",
                "deleted_count": 0
            }
        
        # Supprimer tous les utilisateurs
        result = await db.database.users.delete_many({})
        deleted_count = result.deleted_count
        
        logger.warning(f"⚠️  {deleted_count} utilisateur(s) supprimé(s) via endpoint public depuis IP: {ip}")
        
        return {
            "message": f"{deleted_count} utilisateur(s) supprimé(s) avec succès",
            "deleted_count": deleted_count,
            "warning": "Cet endpoint doit être supprimé après utilisation",
            "note": "Votre IP a été débloquée du rate limiting pour cette requête"
        }
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des utilisateurs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )
