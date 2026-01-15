"""
Routeur d'authentification - Refactorisé avec services
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from app.models import UserCreate, User, UserUpdate
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.utils.permissions import require_admin, get_current_user
from jose import JWTError, jwt
from app.config import settings
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Inscription d'un nouvel utilisateur"""
    from app.utils.logging_utils import mask_email
    logger.info(f"Début de l'inscription pour: {mask_email(user_data.email)}")
    return await AuthService.register_user(user_data)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    """Connexion et génération du token avec protection contre brute force"""
    # Extraire l'IP du client pour le lockout
    client_ip = None
    if request:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                client_ip = real_ip
            elif hasattr(request, 'client') and request.client:
                client_ip = request.client.host
    
    # Logger pour debug
    logger.info(f"Tentative de connexion pour: {form_data.username}")
    
    try:
        result = await AuthService.login_user(form_data.username, form_data.password, client_ip)
        logger.info(f"Connexion réussie pour: {form_data.username}")
        return result
    except HTTPException as e:
        logger.warning(f"Échec de connexion pour {form_data.username}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la connexion: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur lors de la connexion"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Rafraîchit un token d'accès avec un refresh token"""
    try:
        # Décoder le refresh token
        payload = jwt.decode(
            request.refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        # Vérifier que c'est bien un refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide: ce n'est pas un refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide: identifiant utilisateur manquant"
            )
        
        # Vérifier que l'utilisateur existe toujours
        user = await AuthService.get_current_user_from_token(
            jwt.encode(
                {"sub": user_id, "type": "access"},
                settings.secret_key,
                algorithm=settings.algorithm
            )
        )
        
        # Créer un nouveau token d'accès
        from datetime import timedelta
        access_token = AuthService.create_access_token(
            data={"sub": user_id, "username": user.get("username")},
            expires_delta=timedelta(hours=1)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou expiré"
        )


@router.get("/me", response_model=User)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """Récupère les informations de l'utilisateur connecté"""
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non authentifié"
            )
        return current_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des informations utilisateur"
        )


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Demande de réinitialisation de mot de passe"""
    return await AuthService.request_password_reset(request.email)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Réinitialise le mot de passe avec un token"""
    return await AuthService.reset_password(request.token, request.new_password)


@router.put("/me", response_model=User)
async def update_user(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Met à jour les informations de l'utilisateur connecté"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non authentifié"
        )
    return await AuthService.update_user(user_id, user_update)


# Endpoints admin pour la gestion des utilisateurs
@router.get("/users", response_model=List[User])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    admin_user: dict = Depends(require_admin)
):
    """Récupère tous les utilisateurs (admin seulement)"""
    return await UserRepository.find_all(skip=skip, limit=limit)


class AdminUserUpdate(BaseModel):
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None


@router.put("/users/{user_id}", response_model=User)
async def update_user_admin(
    user_id: str,
    user_update: AdminUserUpdate,
    admin_user: dict = Depends(require_admin)
):
    """Met à jour un utilisateur (admin seulement)"""
    from app.utils.security import InputSanitizer
    sanitized_id = InputSanitizer.sanitize_object_id(user_id)
    if not sanitized_id:
        raise HTTPException(status_code=400, detail="ID utilisateur invalide")
    
    # Empêcher un admin de se rétrograder lui-même
    if admin_user.get("id") == sanitized_id and user_update.is_admin is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas vous rétrograder vous-même"
        )
    
    update_data = {}
    if user_update.is_admin is not None:
        update_data["is_admin"] = user_update.is_admin
    if user_update.is_active is not None:
        update_data["is_active"] = user_update.is_active
    
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
    
    updated_user = await UserRepository.update(sanitized_id, update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return updated_user


@router.post("/initialize-main-admin")
async def initialize_main_admin():
    """
    Endpoint d'initialisation pour promouvoir kouroumaelisee@gmail.com comme admin principal.
    Peut être appelé une seule fois lors de la première installation.
    """
    MAIN_ADMIN_EMAIL = "kouroumaelisee@gmail.com"
    
    from app.utils.security import InputSanitizer
    from app.repositories.user_repository import UserRepository
    from app.database import get_database
    from bson import ObjectId
    
    # Trouver l'utilisateur par email
    user = await UserRepository.find_by_email(MAIN_ADMIN_EMAIL)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec l'email '{MAIN_ADMIN_EMAIL}' non trouvé. Veuillez d'abord créer un compte avec cet email."
        )
    
    # Vérifier si déjà admin
    if user.get("is_admin", False):
        return {
            "message": f"L'utilisateur '{MAIN_ADMIN_EMAIL}' est déjà administrateur",
            "user": {
                "id": user.get("id"),
                "email": user.get("email"),
                "username": user.get("username"),
                "is_admin": True
            }
        }
    
    # Promouvoir en admin
    db = get_database()
    sanitized_id = InputSanitizer.sanitize_object_id(user["id"])
    
    if not sanitized_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID utilisateur invalide"
        )
    
    result = await db.users.update_one(
        {"_id": ObjectId(sanitized_id)},
        {"$set": {"is_admin": True}}
    )
    
    if result.modified_count > 0:
        # Récupérer l'utilisateur mis à jour
        updated_user = await UserRepository.find_by_id(sanitized_id)
        logger.info(f"✅ Utilisateur '{MAIN_ADMIN_EMAIL}' promu administrateur avec succès")
        return {
            "message": f"Utilisateur '{MAIN_ADMIN_EMAIL}' promu administrateur avec succès",
            "user": {
                "id": updated_user.get("id"),
                "email": updated_user.get("email"),
                "username": updated_user.get("username"),
                "is_admin": updated_user.get("is_admin", True)
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de la promotion"
        )


@router.post("/promote-admin-by-email")
async def promote_admin_by_email(
    email: str = Form(...),
    secret_key: str = Form(...)
):
    """
    Endpoint temporaire pour promouvoir un utilisateur en admin par email.
    Utilise une clé secrète pour la sécurité.
    À SUPPRIMER après la promotion initiale.
    """
    # Clé secrète temporaire - À CHANGER/SUPPRIMER après utilisation
    EXPECTED_SECRET = "TEMPORARY_ADMIN_PROMOTION_KEY_2024"
    
    if secret_key != EXPECTED_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé secrète invalide"
        )
    
    from app.utils.security import InputSanitizer
    from app.repositories.user_repository import UserRepository
    from bson import ObjectId
    
    # Trouver l'utilisateur par email
    user = await UserRepository.find_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec l'email '{email}' non trouvé"
        )
    
    # Vérifier si déjà admin
    if user.get("is_admin", False):
        return {
            "message": f"L'utilisateur '{email}' est déjà administrateur",
            "user": user
        }
    
    # Promouvoir en admin
    from app.database import get_database
    db = get_database()
    sanitized_id = InputSanitizer.sanitize_object_id(user["id"])
    
    result = await db.users.update_one(
        {"_id": ObjectId(sanitized_id)},
        {"$set": {"is_admin": True}}
    )
    
    if result.modified_count > 0:
        # Récupérer l'utilisateur mis à jour
        updated_user = await UserRepository.find_by_id(sanitized_id)
        return {
            "message": f"Utilisateur '{email}' promu administrateur avec succès",
            "user": updated_user
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de la promotion"
        )


@router.get("/stats")
async def get_stats(admin_user: dict = Depends(require_admin)):
    """Récupère les statistiques de l'application (admin seulement)"""
    from app.database import get_database
    from app.repositories.module_repository import ModuleRepository
    
    db = get_database()
    
    stats = {
        "total_users": await UserRepository.count(),
        "total_admins": await db.users.count_documents({"is_admin": True}),
        "active_users": await db.users.count_documents({"is_active": True}),
        "total_modules": await db.modules.count_documents({}),
        "total_progress": await db.progress.count_documents({}),
        "total_support_messages": await db.support_messages.count_documents({}),
    }
    
    # Statistiques par matière
    subjects = ["physics", "chemistry", "mathematics", "english", "computer_science"]
    stats["modules_by_subject"] = {}
    for subject in subjects:
        count = await db.modules.count_documents({"subject": subject})
        stats["modules_by_subject"][subject] = count
    
    # Statistiques par difficulté
    difficulties = ["beginner", "intermediate", "advanced"]
    stats["modules_by_difficulty"] = {}
    for difficulty in difficulties:
        count = await db.modules.count_documents({"difficulty": difficulty})
        stats["modules_by_difficulty"][difficulty] = count
    
    return stats



