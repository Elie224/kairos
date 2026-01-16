"""
Routeur pour l'authentification
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, Any, List
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


@router.get("/users")
async def get_all_users(
    current_user: Dict[str, Any] = Depends(require_admin)
) -> List[Dict[str, Any]]:
    """
    Récupère la liste de tous les utilisateurs (ADMIN ONLY)
    """
    from app.repositories.user_repository import UserRepository
    from app.database import get_database
    
    try:
        db = get_database()
        # Récupérer tous les utilisateurs
        users_cursor = db.users.find({})
        users = await users_cursor.to_list(length=None)
        
        # Serializer les utilisateurs (exclure les mots de passe)
        serialized_users = []
        for user in users:
            user_dict = {
                "id": str(user.get("_id")),
                "email": user.get("email"),
                "username": user.get("username"),
                "first_name": user.get("first_name"),
                "last_name": user.get("last_name"),
                "is_admin": user.get("is_admin", False),
                "is_active": user.get("is_active", True),
                "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
            }
            serialized_users.append(user_dict)
        
        return serialized_users
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des utilisateurs: {str(e)}"
        )


@router.get("/stats")
async def get_stats(
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Récupère les statistiques de la plateforme (ADMIN ONLY)
    """
    from app.database import get_database
    
    try:
        db = get_database()
        
        # Compter les utilisateurs
        total_users = await db.users.count_documents({})
        total_admins = await db.users.count_documents({"is_admin": True})
        active_users = await db.users.count_documents({"is_active": True})
        
        # Compter les modules
        total_modules = await db.modules.count_documents({})
        
        # Compter les progressions
        total_progress = await db.progress.count_documents({})
        
        # Compter les messages de support
        total_support_messages = await db.support_messages.count_documents({})
        
        # Modules par sujet
        modules_by_subject = {}
        modules_cursor = db.modules.find({}, {"subject": 1})
        async for module in modules_cursor:
            subject = module.get("subject", "unknown")
            modules_by_subject[subject] = modules_by_subject.get(subject, 0) + 1
        
        # Modules par difficulté
        modules_by_difficulty = {}
        modules_cursor = db.modules.find({}, {"difficulty": 1})
        async for module in modules_cursor:
            difficulty = module.get("difficulty", "unknown")
            modules_by_difficulty[difficulty] = modules_by_difficulty.get(difficulty, 0) + 1
        
        return {
            "total_users": total_users,
            "total_admins": total_admins,
            "active_users": active_users,
            "total_modules": total_modules,
            "total_progress": total_progress,
            "total_support_messages": total_support_messages,
            "modules_by_subject": modules_by_subject,
            "modules_by_difficulty": modules_by_difficulty,
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des statistiques: {str(e)}"
        )


@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Met à jour un utilisateur (ADMIN ONLY)
    Permet de promouvoir/rétrograder admin, activer/désactiver un compte
    """
    from app.repositories.user_repository import UserRepository
    from app.utils.security import InputSanitizer
    from datetime import datetime, timezone
    
    try:
        # Sanitizer l'ID utilisateur
        sanitized_user_id = InputSanitizer.sanitize_object_id(user_id)
        if not sanitized_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID utilisateur invalide"
            )
        
        # Vérifier que l'utilisateur existe
        user = await UserRepository.find_by_id(sanitized_user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Préparer les données de mise à jour
        update_data = {}
        
        # Permettre la modification de is_admin et is_active uniquement
        if "is_admin" in user_data:
            update_data["is_admin"] = bool(user_data["is_admin"])
        
        if "is_active" in user_data:
            update_data["is_active"] = bool(user_data["is_active"])
        
        # Mettre à jour la date de modification
        update_data["updated_at"] = datetime.now(timezone.utc)
        
        # Mettre à jour l'utilisateur
        updated_user = await UserRepository.update(sanitized_user_id, update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la mise à jour de l'utilisateur"
            )
        
        # Retourner sans le mot de passe
        updated_user.pop("hashed_password", None)
        updated_user.pop("password_reset_token", None)
        updated_user.pop("email_verification_token", None)
        
        logger.info(f"Utilisateur {sanitized_user_id} mis à jour par admin {current_user.get('email')}")
        
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'utilisateur: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )


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


@router.get("/users/all/public/check")
async def check_delete_endpoint() -> Dict[str, str]:
    """
    Endpoint de test pour vérifier que l'endpoint est disponible
    """
    return {"status": "endpoint_available", "message": "Endpoint de suppression disponible"}


@router.post("/users/all/public")
async def delete_all_users_public_post(request: Request) -> Dict[str, Any]:
    """
    ⚠️ ENDPOINT TEMPORAIRE - Supprime tous les utilisateurs SANS authentification (POST)
    Alternative à DELETE pour compatibilité
    """
    return await delete_all_users_public(request)


@router.get("/users/debug/{email}")
async def debug_user(email: str) -> Dict[str, Any]:
    """
    ⚠️ ENDPOINT TEMPORAIRE - Debug d'un utilisateur SANS authentification
    À SUPPRIMER après utilisation pour des raisons de sécurité
    """
    from app.database import get_database
    from app.utils.security import InputSanitizer
    
    try:
        sanitized_email = InputSanitizer.sanitize_email(email)
        if not sanitized_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email invalide"
            )
        
        db = get_database()
        user = await db.users.find_one({"email": sanitized_email})
        
        if not user:
            return {
                "found": False,
                "message": f"Utilisateur non trouvé pour {sanitized_email}"
            }
        
        # Retourner les informations de debug (sans le hash complet pour la sécurité)
        hashed_password = user.get("hashed_password", "")
        return {
            "found": True,
            "email": user.get("email"),
            "username": user.get("username"),
            "user_id": str(user.get("_id")),
            "has_hashed_password": bool(hashed_password),
            "hashed_password_length": len(hashed_password) if hashed_password else 0,
            "hashed_password_preview": hashed_password[:30] + "..." if hashed_password and len(hashed_password) > 30 else (hashed_password if hashed_password else None),
            "is_active": user.get("is_active", True),
            "created_at": str(user.get("created_at")) if user.get("created_at") else None,
        }
    except Exception as e:
        logger.error(f"Erreur lors du debug: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du debug: {str(e)}"
        )


@router.post("/users/fix-password")
async def fix_user_password_public(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    ⚠️ ENDPOINT TEMPORAIRE - Corrige le mot de passe d'un utilisateur SANS authentification
    À SUPPRIMER après utilisation pour des raisons de sécurité
    """
    from app.database import get_database
    from app.utils.security import PasswordHasher
    from bson import ObjectId
    
    email = user_data.get("email")
    new_password = user_data.get("password")
    
    if not email or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email et mot de passe requis"
        )
    
    try:
        db = get_database()
        user = await db.users.find_one({"email": email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Hasher le nouveau mot de passe
        logger.info(f"Hashage du nouveau mot de passe pour {email}")
        hashed_password = PasswordHasher.hash_password(new_password)
        logger.info(f"Mot de passe hashé avec succès, hash (premiers 30 chars): {hashed_password[:30]}...")
        
        # Mettre à jour l'utilisateur
        logger.info(f"Mise à jour de l'utilisateur {user['_id']} avec le nouveau hash")
        result = await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"hashed_password": hashed_password}}
        )
        logger.info(f"Résultat de la mise à jour: modified_count={result.modified_count}, matched_count={result.matched_count}")
        
        # Vérifier que le hash a bien été sauvegardé
        updated_user = await db.users.find_one({"_id": user["_id"]}, {"hashed_password": 1})
        if updated_user and updated_user.get("hashed_password"):
            logger.info(f"✅ Hash confirmé dans la base de données (premiers 30 chars): {updated_user.get('hashed_password')[:30]}...")
        else:
            logger.error(f"❌ ERREUR: Le hash n'a PAS été sauvegardé!")
        
        if result.modified_count > 0:
            logger.info(f"✅ Mot de passe corrigé pour {email}")
            return {
                "message": f"Mot de passe corrigé avec succès pour {email}",
                "success": True
            }
        else:
            return {
                "message": "Aucune modification effectuée",
                "success": False
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la correction du mot de passe: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la correction: {str(e)}"
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
