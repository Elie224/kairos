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
            # Sanitizer l'email
            sanitized_email = InputSanitizer.sanitize_email(email)
            if not sanitized_email:
                return None
            
            # Trouver l'utilisateur
            user = await UserRepository.find_by_email(sanitized_email)
            if not user:
                return None
            
            # Vérifier le mot de passe
            hashed_password = user.get("hashed_password")
            if not hashed_password:
                return None
            
            if not PasswordHasher.verify_password(password, hashed_password):
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
            hashed_password = PasswordHasher.hash_password(password)
            
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
            
            user = await UserRepository.create(user_dict)
            
            # Retourner sans le mot de passe
            user.pop("hashed_password", None)
            user.pop("password_reset_token", None)
            user.pop("email_verification_token", None)
            
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur lors de l'inscription: {str(e)}"
            )
