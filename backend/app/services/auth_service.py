"""
Service d'authentification - Business logic
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
from app.config import settings
from app.repositories.user_repository import UserRepository
from app.models import UserCreate, UserUpdate
from app.utils.security import PasswordValidator, PasswordHasher, InputSanitizer
# logging_utils et login_lockout supprimés - utiliser logging standard
import logging
from fastapi import Request
import re

logger = logging.getLogger(__name__)


class AuthService:
    """Service pour la gestion de l'authentification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash un mot de passe"""
        return PasswordHasher.hash_password(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie un mot de passe"""
        return PasswordHasher.verify_password(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crée un token JWT avec sécurité renforcée"""
        to_encode = data.copy()
        
        # Durée de vie par défaut plus courte pour la sécurité
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Token d'accès: 1 heure (au lieu de 24h)
            expire = datetime.utcnow() + timedelta(hours=1)
        
        # Ajouter des claims de sécurité
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),  # Issued at
            "type": "access"  # Type de token
        })
        
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crée un refresh token (durée de vie plus longue)"""
        to_encode = data.copy()
        # Par défaut, 7 jours pour refresh token; permettre la personnalisation si nécessaire
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)  # 7 jours pour refresh token
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Décode un token JWT"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def register_user(user_data: UserCreate) -> Dict[str, Any]:
        """Inscrit un nouvel utilisateur"""
        # Sanitizer les entrées
        sanitized_email = InputSanitizer.sanitize_email(user_data.email)
        if not sanitized_email:
            logger.error(f"Email rejeté par la validation: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email invalide: '{user_data.email}'. Vérifiez le format de votre email."
            )
        
        sanitized_username = InputSanitizer.sanitize_string(user_data.username, max_length=50)
        if not sanitized_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le nom d'utilisateur est requis"
            )
        
        # Validation du nom d'utilisateur
        if len(sanitized_username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le nom d'utilisateur doit contenir au moins 3 caractères"
            )
        
        if len(sanitized_username) > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le nom d'utilisateur ne doit pas dépasser 30 caractères"
            )
        
        # Vérifier que le nom d'utilisateur ne contient que des caractères autorisés
        if not re.match(r'^[a-zA-Z0-9_-]+$', sanitized_username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores"
            )
        
        # Validation du mot de passe (obligatoire)
        if not user_data.password or not user_data.password.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le mot de passe est requis"
            )
        
        # Valider la force du mot de passe
        password_valid, password_error = PasswordValidator.validate(user_data.password)
        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=password_error
            )
        
        # Validation du téléphone (obligatoire)
        if not user_data.phone or not user_data.phone.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le numéro de téléphone est requis"
            )
        
        # Nettoyer le numéro de téléphone (supprimer espaces, tirets, etc.)
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', user_data.phone)
        # Valider le format : accepter deux formats
        # 1. Format international : +33 6 12 34 56 78 → +33612345678
        # 2. Format français : 0612345678
        international_format = re.match(r'^\+[1-9]\d{9,14}$', cleaned_phone)  # + suivi de 1-9 puis 9-14 chiffres
        french_format = re.match(r'^0[1-9]\d{8}$', cleaned_phone)  # 0 suivi de 1-9 puis 8 chiffres
        if not international_format and not french_format:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de numéro de téléphone invalide. Utilisez +33 6 12 34 56 78 ou 0612345678"
            )
        phone = cleaned_phone
        
        # Validation des champs requis
        if not user_data.first_name or not user_data.first_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le prénom est requis"
            )
        
        if not user_data.last_name or not user_data.last_name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le nom est requis"
            )
        
        if not user_data.date_of_birth:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de naissance est requise"
            )
        
        # Validation de la date de naissance
        try:
            birth_date = datetime.strptime(user_data.date_of_birth, "%Y-%m-%d")
            # Vérifier que l'utilisateur a au moins 13 ans
            age = (datetime.utcnow() - birth_date).days / 365.25
            if age < 13:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vous devez avoir au moins 13 ans pour vous inscrire"
                )
            if age > 120:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Date de naissance invalide"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de date invalide. Utilisez YYYY-MM-DD"
            )
        
        if not user_data.country or not user_data.country.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le pays est requis"
            )
        
        email = sanitized_email
        username = sanitized_username
        first_name = InputSanitizer.sanitize_string(user_data.first_name, max_length=50)
        last_name = InputSanitizer.sanitize_string(user_data.last_name, max_length=50)
        country = InputSanitizer.sanitize_string(user_data.country, max_length=100)
        
        # Vérifier si l'utilisateur existe déjà
        if await UserRepository.exists(email=email, username=username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email ou nom d'utilisateur déjà utilisé"
            )
        
        # Hasher le mot de passe
        try:
            hashed_password = AuthService.hash_password(user_data.password)
        except Exception as hash_error:
            logger.error(f"Erreur lors du hachage du mot de passe: {hash_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur serveur: {str(hash_error)}"
            )
        
        # Créer l'utilisateur avec mot de passe
        user_dict = {
            "email": email,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": user_data.date_of_birth,
            "country": country,
            "phone": phone,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "is_active": True,
            "is_admin": False,  # Par défaut, les nouveaux utilisateurs ne sont pas admin
            "auth_provider": "email"  # Inscription par email
        }
        
        try:
            user = await UserRepository.create(user_dict)
            logger.info(f"Utilisateur créé: id={user.get('id')}, email={email}, username={username}")
            return user
        except Exception as e:
            error_str = str(e)
            if "duplicate key error" in error_str.lower() or "E11000" in error_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email ou nom d'utilisateur déjà utilisé"
                )
            logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la création de l'utilisateur"
            )
    
    @staticmethod
    async def authenticate_user(
        email_or_username: str,
        password: str,
        client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Authentifie un utilisateur avec protection contre les attaques brute force"""
        # Sanitizer les entrées
        sanitized_input = InputSanitizer.sanitize_string(email_or_username, max_length=100)
        
        # Note: login_lockout supprimé - protection basique via rate limiting middleware
        
        user = await UserRepository.find_by_email_or_username(sanitized_input)
        
        if not user:
            # Ne pas révéler si l'utilisateur existe ou non (security best practice)
            logger.warning(f"Tentative de connexion échouée: {sanitized_input} depuis {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email/username ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Récupérer le hash du mot de passe depuis la base
        from app.database import get_database
        from bson import ObjectId
        db = get_database()
        user_doc = await db.users.find_one({"_id": ObjectId(user["id"])})
        hashed_password = user_doc.get("hashed_password")
        
        # Vérifier si l'utilisateur a un mot de passe défini
        if not hashed_password:
            # Ne pas révéler que le compte existe mais n'a pas de mot de passe (sécurité)
            logger.warning(f"Tentative de connexion sans mot de passe: {sanitized_input} depuis {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email/username ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not AuthService.verify_password(password, hashed_password):
            # Enregistrer la tentative échouée
            logger.warning(f"Tentative de connexion échouée (mauvais mot de passe): {sanitized_input} depuis {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email/username ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Connexion réussie
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Compte utilisateur désactivé"
            )
        
        return user

    @staticmethod
    async def request_password_reset(email: str) -> Dict[str, Any]:
        """Génère un token de réinitialisation et envoie un email"""
        # Sanitizer l'email
        sanitized_email = InputSanitizer.sanitize_email(email)
        if not sanitized_email:
            # Ne pas révéler si l'email existe ou non (sécurité)
            return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé"}
        
        # Vérifier si l'utilisateur existe
        user = await UserRepository.find_by_email(sanitized_email)
        if not user:
            # Ne pas révéler si l'email existe ou non (sécurité)
            return {"message": "Si cet email existe, un lien de réinitialisation a été envoyé"}
        
        
        # Générer un token de réinitialisation sécurisé
        reset_token = PasswordHasher.generate_secure_token(32)
        
        # Stocker le token dans la base de données avec expiration (1 heure)
        from app.database import get_database
        from bson import ObjectId
        db = get_database()
        
        reset_data = {
            "user_id": ObjectId(user["id"]),
            "token": reset_token,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=1),
            "used": False
        }
        
        # Supprimer les anciens tokens non utilisés pour cet utilisateur
        await db.password_resets.delete_many({
            "user_id": ObjectId(user["id"]),
            "used": False
        })
        
        # Insérer le nouveau token
        await db.password_resets.insert_one(reset_data)
        
        # TODO: Envoyer l'email avec le lien de réinitialisation
        # Pour l'instant, on log le token (à remplacer par un vrai service d'email)
        reset_link = f"{settings.frontend_url or 'http://localhost:5173'}/reset-password?token={reset_token}"
        logger.info(f"Token de réinitialisation pour {sanitized_email}: {reset_link}")
        
        # En production, utiliser un service d'email comme SendGrid, AWS SES, etc.
        # await email_service.send_password_reset_email(sanitized_email, reset_link)
        
        # En développement, retourner aussi le lien pour faciliter les tests
        response = {"message": "Si cet email existe, un lien de réinitialisation a été envoyé"}
        if settings.is_development:
            response["reset_link"] = reset_link
            response["token"] = reset_token
        
        return response
    
    @staticmethod
    async def reset_password(token: str, new_password: str) -> Dict[str, Any]:
        """Réinitialise le mot de passe avec un token valide"""
        try:
            # Valider le nouveau mot de passe
            password_valid, password_error = PasswordValidator.validate(new_password)
            if not password_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=password_error
                )
            
            # Trouver le token de réinitialisation
            from app.database import get_database
            from bson import ObjectId
            db = get_database()
            
            reset_record = await db.password_resets.find_one({
                "token": token,
                "used": False,
                "expires_at": {"$gt": datetime.utcnow()}
            })
            
            if not reset_record:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Token de réinitialisation invalide ou expiré"
                )
            
            # Mettre à jour le mot de passe de l'utilisateur
            user_id = str(reset_record["user_id"])
            logger.info(f"Tentative de réinitialisation du mot de passe pour l'utilisateur {user_id}")
            logger.info(f"Longueur du mot de passe en bytes: {len(new_password.encode('utf-8'))}")
            
            try:
                hashed_password = AuthService.hash_password(new_password)
                logger.info("Mot de passe hashé avec succès")
            except Exception as hash_error:
                logger.error(f"Erreur lors du hachage du mot de passe: {hash_error}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erreur lors du hachage du mot de passe: {str(hash_error)}"
                )
            
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"hashed_password": hashed_password}}
            )
            
            # Marquer le token comme utilisé
            await db.password_resets.update_one(
                {"_id": reset_record["_id"]},
                {"$set": {"used": True}}
            )
            
            # Supprimer tous les autres tokens non utilisés pour cet utilisateur
            await db.password_resets.delete_many({
                "user_id": reset_record["user_id"],
                "used": False
            })
            
            logger.info(f"Mot de passe réinitialisé pour l'utilisateur {user_id}")
            
            return {"message": "Mot de passe réinitialisé avec succès"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation du mot de passe: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erreur serveur: {str(e)}"
            )

    @staticmethod
    async def login_user(
        email_or_username: str,
        password: str,
        client_ip: Optional[str] = None
    ) -> Dict[str, Any]:
        """Connecte un utilisateur et retourne les tokens"""
        # Sanitizer les entrées
        sanitized_input = InputSanitizer.sanitize_string(email_or_username, max_length=100)
        
        user = await AuthService.authenticate_user(sanitized_input, password, client_ip)
        
        # Créer les tokens avec durée de vie sécurisée
        access_token = AuthService.create_access_token(
            data={"sub": user["id"], "username": user.get("username")},
            expires_delta=timedelta(hours=1)  # Token d'accès: 1 heure
        )
        
        refresh_token = AuthService.create_refresh_token(
            data={"sub": user["id"]}
        )
        
        # Masquer l'email pour la sécurité (PII)
        # On successful login remove attempt counts (Redis)
        try:
            from app.utils.cache import get_redis
            redis = get_redis()
            if redis:
                attempt_key = f"login:attempts:{user['id']}"
                lock_key = f"login:lock:{user['id']}"
                await redis.delete(attempt_key)
                await redis.delete(lock_key)
        except Exception:
            pass
        user_id = user.get('id', 'unknown')
        logger.info(f"Utilisateur connecté: id={user_id}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,  # 1 heure en secondes
            "user": user
        }
    
    @staticmethod
    async def get_current_user_from_token(token: str) -> Dict[str, Any]:
        """Récupère l'utilisateur depuis un token"""
        payload = AuthService.decode_token(token)
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Impossible de valider les identifiants",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await UserRepository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utilisateur non trouvé",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    @staticmethod
    async def update_user(user_id: str, user_update: UserUpdate) -> Dict[str, Any]:
        """Met à jour les informations d'un utilisateur"""
        from app.repositories.user_repository import UserRepository
        
        # Vérifier que l'utilisateur existe
        user = await UserRepository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Préparer les données de mise à jour
        update_data: Dict[str, Any] = {}
        
        # Mettre à jour l'email si fourni
        if user_update.email is not None:
            sanitized_email = InputSanitizer.sanitize_email(user_update.email)
            if not sanitized_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email invalide"
                )
            # Vérifier que l'email n'est pas déjà utilisé
            existing_user = await UserRepository.find_by_email(sanitized_email)
            if existing_user and existing_user.get("id") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cet email est déjà utilisé"
                )
            update_data["email"] = sanitized_email
        
        # Mettre à jour le username si fourni
        if user_update.username is not None:
            sanitized_username = InputSanitizer.sanitize_string(user_update.username, max_length=50)
            if not sanitized_username or len(sanitized_username) < 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le nom d'utilisateur doit contenir au moins 3 caractères"
                )
            if not re.match(r'^[a-zA-Z0-9_-]+$', sanitized_username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le nom d'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores"
                )
            # Vérifier que le username n'est pas déjà utilisé
            existing_user = await UserRepository.find_by_username(sanitized_username)
            if existing_user and existing_user.get("id") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ce nom d'utilisateur est déjà utilisé"
                )
            update_data["username"] = sanitized_username
        
        # Mettre à jour les autres champs
        if user_update.first_name is not None:
            update_data["first_name"] = InputSanitizer.sanitize_string(user_update.first_name, max_length=100)
        
        if user_update.last_name is not None:
            update_data["last_name"] = InputSanitizer.sanitize_string(user_update.last_name, max_length=100)
        
        if user_update.date_of_birth is not None:
            # Valider la date de naissance
            try:
                birth_date = datetime.strptime(user_update.date_of_birth, "%Y-%m-%d")
                today = datetime.now()
                age = (today - birth_date).days / 365.25
                if age < 13 or age > 120:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Date de naissance invalide"
                    )
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Format de date invalide (attendu: YYYY-MM-DD)"
                )
            update_data["date_of_birth"] = user_update.date_of_birth
        
        if user_update.country is not None:
            update_data["country"] = InputSanitizer.sanitize_string(user_update.country, max_length=100)
        
        if user_update.phone is not None:
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', user_update.phone)
            # Valider le format : accepter deux formats
            # 1. Format international : +33 6 12 34 56 78 → +33612345678
            # 2. Format français : 0612345678
            international_format = re.match(r'^\+[1-9]\d{9,14}$', cleaned_phone)  # + suivi de 1-9 puis 9-14 chiffres
            french_format = re.match(r'^0[1-9]\d{8}$', cleaned_phone)  # 0 suivi de 1-9 puis 8 chiffres
            if not international_format and not french_format:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Format de numéro de téléphone invalide. Utilisez +33 6 12 34 56 78 ou 0612345678"
                )
            update_data["phone"] = cleaned_phone
        
        # Mettre à jour le mot de passe si fourni
        if user_update.password is not None:
            password_valid, password_error = PasswordValidator.validate(user_update.password)
            if not password_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=password_error
                )
            update_data["hashed_password"] = AuthService.hash_password(user_update.password)
        
        # Ajouter la date de mise à jour
        update_data["updated_at"] = datetime.utcnow()
        
        # Mettre à jour l'utilisateur
        updated_user = await UserRepository.update(user_id, update_data)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la mise à jour"
            )
        
        logger.info(f"Utilisateur {user_id} mis à jour")
        return updated_user

