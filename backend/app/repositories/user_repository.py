"""
Repository pour la gestion des utilisateurs
"""
from typing import Optional, Dict, Any
from bson import ObjectId
from app.database import get_database
from app.schemas import serialize_doc
from app.utils.security import InputSanitizer
import logging

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository pour les opérations CRUD sur les utilisateurs"""
    
    @staticmethod
    async def find_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Trouve un utilisateur par email"""
        try:
            # Sanitizer et valider l'email
            sanitized_email = InputSanitizer.sanitize_email(email)
            if not sanitized_email:
                return None
            
            db = get_database()
            # Utiliser une requête sécurisée (pas d'opérateurs MongoDB dans l'input)
            user = await db.users.find_one({"email": sanitized_email})
            return serialize_doc(user) if user else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par email: {e}")
            raise
    
    @staticmethod
    async def find_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Trouve un utilisateur par nom d'utilisateur"""
        try:
            db = get_database()
            # Projection pour exclure les champs sensibles
            user = await db.users.find_one(
                {"username": username.strip()},
                {"hashed_password": 0, "password_reset_token": 0, "email_verification_token": 0}
            )
            return serialize_doc(user) if user else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par username: {e}")
            raise
    
    @staticmethod
    async def find_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Trouve un utilisateur par ID"""
        try:
            # Valider et sanitizer l'ObjectId
            sanitized_id = InputSanitizer.sanitize_object_id(user_id)
            if not sanitized_id:
                return None
            
            db = get_database()
            # Projection pour exclure les champs sensibles
            user = await db.users.find_one(
                {"_id": ObjectId(sanitized_id)},
                {"hashed_password": 0, "password_reset_token": 0, "email_verification_token": 0}
            )
            return serialize_doc(user) if user else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par ID: {e}")
            raise
    
    @staticmethod
    async def find_by_email_or_username(email_or_username: str) -> Optional[Dict[str, Any]]:
        """Trouve un utilisateur par email ou nom d'utilisateur"""
        try:
            # Sanitizer l'input
            sanitized_input = InputSanitizer.sanitize_string(email_or_username, max_length=100)
            if not sanitized_input:
                return None
            
            db = get_database()
            # Construire la requête de manière sécurisée
            sanitized_email = InputSanitizer.sanitize_email(sanitized_input)
            sanitized_username = InputSanitizer.sanitize_string(sanitized_input, max_length=50)
            
            query = {"$or": []}
            if sanitized_email:
                query["$or"].append({"email": sanitized_email})
            if sanitized_username:
                query["$or"].append({"username": sanitized_username})
            
            if not query["$or"]:
                return None
            
            # Projection pour exclure les champs sensibles
            user = await db.users.find_one(
                query,
                {"hashed_password": 0, "password_reset_token": 0, "email_verification_token": 0}
            )
            return serialize_doc(user) if user else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par email/username: {e}")
            raise
    
    @staticmethod
    async def exists(email: str = None, username: str = None) -> bool:
        """Vérifie si un utilisateur existe avec cet email ou username"""
        try:
            db = get_database()
            query = {}
            if email:
                query["email"] = email.lower().strip()
            if username:
                query["username"] = username.strip()
            
            if not query:
                return False
            
            if email and username:
                query = {"$or": [{"email": email.lower().strip()}, {"username": username.strip()}]}
            
            count = await db.users.count_documents(query)
            return count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la vérification d'existence: {e}")
            raise
    
    @staticmethod
    async def create(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouvel utilisateur"""
        try:
            db = get_database()
            result = await db.users.insert_one(user_data)
            user_data["_id"] = result.inserted_id
            return serialize_doc(user_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
            raise
    
    @staticmethod
    async def update(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un utilisateur"""
        try:
            # Valider l'ObjectId avant utilisation
            sanitized_id = InputSanitizer.sanitize_object_id(user_id)
            if not sanitized_id:
                return None
            
            db = get_database()
            await db.users.update_one(
                {"_id": ObjectId(sanitized_id)},
                {"$set": update_data}
            )
            return await UserRepository.find_by_id(sanitized_id)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de l'utilisateur: {e}")
            raise
    
    @staticmethod
    async def find_all(skip: int = 0, limit: int = 100) -> list[Dict[str, Any]]:
        """Récupère tous les utilisateurs avec pagination (optimisé avec projection)"""
        try:
            db = get_database()
            # Projection pour exclure les champs sensibles et volumineux
            projection = {
                "hashed_password": 0,  # Ne jamais retourner les mots de passe
                "password_reset_token": 0,  # Ne pas retourner les tokens
                "email_verification_token": 0,  # Ne pas retourner les tokens
            }
            cursor = db.users.find({}, projection).skip(skip).limit(limit).sort("created_at", -1)
            users = await cursor.to_list(length=limit)
            return [serialize_doc(user) for user in users]
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            raise
    
    @staticmethod
    async def count() -> int:
        """Compte le nombre total d'utilisateurs"""
        try:
            db = get_database()
            return await db.users.count_documents({})
        except Exception as e:
            logger.error(f"Erreur lors du comptage des utilisateurs: {e}")
            raise


