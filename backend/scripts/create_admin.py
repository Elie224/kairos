"""
Script pour créer directement un utilisateur administrateur
Usage: python scripts/create_admin.py <email> <username> <password> <first_name> <last_name> <date_of_birth> <country> <phone>
"""
import asyncio
import sys
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.utils.security import InputSanitizer
from datetime import datetime
from bson import ObjectId
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_admin_user(email: str, username: str, password: str, first_name: str, last_name: str, date_of_birth: str, country: str, phone: str):
    """Crée directement un utilisateur administrateur"""
    try:
        await connect_to_mongo()
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = await UserRepository.find_by_email_or_username(email)
        if existing_user:
            logger.warning(f"L'utilisateur avec l'email '{email}' existe déjà")
            # Promouvoir en admin s'il n'est pas déjà admin
            if not existing_user.get("is_admin", False):
                db = get_database()
                await db.users.update_one(
                    {"_id": ObjectId(existing_user["id"])},
                    {"$set": {"is_admin": True}}
                )
                logger.info(f"✅ Utilisateur '{email}' promu administrateur avec succès")
            else:
                logger.info(f"L'utilisateur '{email}' est déjà administrateur")
            return True
        
        # Valider les données
        sanitized_email = InputSanitizer.sanitize_email(email)
        if not sanitized_email:
            logger.error(f"Email invalide: {email}")
            return False
        
        sanitized_username = InputSanitizer.sanitize_string(username, max_length=50)
        if not sanitized_username or len(sanitized_username) < 3:
            logger.error(f"Nom d'utilisateur invalide: {username}")
            return False
        
        # Valider le mot de passe
        from app.utils.security import PasswordValidator
        password_valid, password_error = PasswordValidator.validate(password)
        if not password_valid:
            logger.error(f"Mot de passe invalide: {password_error}")
            return False
        
        # Valider le téléphone
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        international_format = re.match(r'^\+[1-9]\d{9,14}$', cleaned_phone)
        french_format = re.match(r'^0[1-9]\d{8}$', cleaned_phone)
        if not international_format and not french_format:
            logger.error(f"Format de téléphone invalide: {phone}")
            return False
        
        # Valider la date de naissance
        try:
            birth_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
            age = (datetime.utcnow() - birth_date).days / 365.25
            if age < 13:
                logger.error("L'utilisateur doit avoir au moins 13 ans")
                return False
        except ValueError:
            logger.error(f"Format de date invalide: {date_of_birth}. Utilisez YYYY-MM-DD")
            return False
        
        # Hasher le mot de passe
        hashed_password = AuthService.hash_password(password)
        
        # Créer l'utilisateur admin
        db = get_database()
        user_dict = {
            "email": sanitized_email,
            "username": sanitized_username,
            "first_name": InputSanitizer.sanitize_string(first_name, max_length=50),
            "last_name": InputSanitizer.sanitize_string(last_name, max_length=50),
            "date_of_birth": date_of_birth,
            "country": InputSanitizer.sanitize_string(country, max_length=100),
            "phone": cleaned_phone,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "is_active": True,
            "is_admin": True,  # Créer directement comme admin
            "auth_provider": "email"
        }
        
        result = await db.users.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        
        logger.info(f"✅ Administrateur créé avec succès:")
        logger.info(f"  - Email: {sanitized_email}")
        logger.info(f"  - Username: {sanitized_username}")
        logger.info(f"  - Nom: {first_name} {last_name}")
        logger.info(f"  - Admin: True")
        
        return True
            
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'administrateur: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        await close_mongo_connection()


async def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 9:
        print("Usage:")
        print("  python scripts/create_admin.py <email> <username> <password> <first_name> <last_name> <date_of_birth> <country> <phone>")
        print("")
        print("Exemple:")
        print("  python scripts/create_admin.py admin@example.com admin MyP@ssw0rd John Doe 1990-01-01 France +33612345678")
        sys.exit(1)
    
    email = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    first_name = sys.argv[4]
    last_name = sys.argv[5]
    date_of_birth = sys.argv[6]
    country = sys.argv[7]
    phone = sys.argv[8]
    
    await create_admin_user(email, username, password, first_name, last_name, date_of_birth, country, phone)


if __name__ == "__main__":
    asyncio.run(main())

