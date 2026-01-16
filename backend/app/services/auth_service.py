"""
Service d'authentification
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.utils.security import PasswordHasher, InputSanitizer
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service pour l'authentification des utilisateurs"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(hours=24)
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
        
        if not settings.secret_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SECRET_KEY non configurée"
            )
        
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Vérifie et décode un token JWT"""
        try:
            if not settings.secret_key:
                return None
            
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authentifie un utilisateur avec email et mot de passe"""
        try:
            logger.info(f"authenticate_user appelé avec email: {email}")
            # Sanitizer l'email
            sanitized_email = InputSanitizer.sanitize_email(email)
            logger.info(f"Email après sanitization: {sanitized_email}")
            if not sanitized_email:
                logger.warning(f"Email invalide après sanitization: {email}")
                return None
            
            # Trouver l'utilisateur
            logger.info(f"Recherche de l'utilisateur avec email: {sanitized_email}")
            user = await UserRepository.find_by_email(sanitized_email)
            if not user:
                logger.warning(f"Utilisateur non trouvé pour email: {sanitized_email} (email original: {email})")
                # Essayer de trouver tous les utilisateurs pour debug
                try:
                    from app.database import get_database
                    db = get_database()
                    all_users = await db.users.find({}, {"email": 1, "username": 1}).to_list(length=10)
                    logger.info(f"Utilisateurs dans la base de données: {[u.get('email') for u in all_users]}")
                except Exception as e:
                    logger.error(f"Erreur lors de la récupération des utilisateurs pour debug: {e}")
                return None
            
            # Vérifier le mot de passe
            hashed_password = user.get("hashed_password")
            logger.info(f"Récupération du hash: hashed_password présent={bool(hashed_password)}, type={type(hashed_password) if hashed_password else None}")
            if not hashed_password:
                logger.warning(f"Utilisateur sans mot de passe hashé: {user.get('id')}, email: {sanitized_email}")
                logger.warning(f"Clés disponibles dans user: {list(user.keys())}")
                return None
            
            logger.info(f"Vérification du mot de passe pour email: {sanitized_email}, user_id: {user.get('id')}")
            logger.info(f"Hash stocké (premiers 30 chars): {hashed_password[:30]}...")
            logger.info(f"Longueur du hash: {len(hashed_password)}")
            password_valid = PasswordHasher.verify_password(password, hashed_password)
            logger.info(f"Résultat de la vérification du mot de passe: {password_valid}")
            if not password_valid:
                logger.warning(f"Mot de passe incorrect pour email: {sanitized_email}, user_id: {user.get('id')}")
                logger.warning(f"Tentative de vérification avec mot de passe de longueur: {len(password)}")
                return None
            
            # Retourner l'utilisateur sans le mot de passe
            user.pop("hashed_password", None)
            user.pop("password_reset_token", None)
            user.pop("email_verification_token", None)
            
            return user
        except Exception as e:
            logger.error(f"Erreur lors de l'authentification: {e}")
            return None
    
    @staticmethod
    async def register_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enregistre un nouvel utilisateur"""
        try:
            # Valider et sanitizer les données
            email = InputSanitizer.sanitize_email(user_data.get("email", ""))
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email invalide"
                )
            
            username = user_data.get("username", "").strip()
            if not username or len(username) < 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le nom d'utilisateur doit contenir au moins 3 caractères"
                )
            
            password = user_data.get("password", "")
            if not password or len(password) < 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le mot de passe doit contenir au moins 6 caractères"
                )
            
            # Vérifier si l'email existe déjà
            existing_user = await UserRepository.find_by_email(email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cet email est déjà utilisé"
                )
            
            # Vérifier si le username existe déjà
            existing_username = await UserRepository.find_by_username(username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce nom d'utilisateur est déjà utilisé"
                )
            
            # Hasher le mot de passe
            logger.info(f"Hashage du mot de passe pour email: {email}, username: {username}")
            hashed_password = PasswordHasher.hash_password(password)
            logger.info(f"Mot de passe hashé avec succès pour email: {email}, hash (premiers 20 chars): {hashed_password[:20]}...")
            
            # Créer l'utilisateur
            user_dict = {
                "email": email,
                "username": username,
                "hashed_password": hashed_password,
                "first_name": user_data.get("first_name", "").strip(),
                "last_name": user_data.get("last_name", "").strip(),
                "date_of_birth": user_data.get("date_of_birth"),
                "country": user_data.get("country", "").strip(),
                "phone": user_data.get("phone", "").strip(),
                "is_active": True,
                "is_admin": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            logger.info(f"Appel de UserRepository.create avec user_dict contenant hashed_password: {bool(user_dict.get('hashed_password'))}")
            user = await UserRepository.create(user_dict)
            logger.info(f"Utilisateur créé retourné par UserRepository.create: id={user.get('id')}, email={user.get('email')}, has_hashed_password={bool(user.get('hashed_password'))}")
            
            # Retourner sans le mot de passe (mais seulement pour la réponse, pas pour la base de données)
            response_user = user.copy()
            response_user.pop("hashed_password", None)
            response_user.pop("password_reset_token", None)
            response_user.pop("email_verification_token", None)
            
            logger.info(f"Inscription terminée avec succès pour user_id: {user.get('id')}, email: {user.get('email')}")
            return response_user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de l'inscription: {str(e)}"
            )
