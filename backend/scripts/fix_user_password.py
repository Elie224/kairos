"""
Script pour corriger le mot de passe d'un utilisateur existant
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour les imports relatifs
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.utils.security import PasswordHasher
from app.repositories.user_repository import UserRepository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_user_password(email: str, new_password: str):
    """Corrige le mot de passe d'un utilisateur"""
    await connect_to_mongo()
    
    try:
        # Trouver l'utilisateur
        user = await UserRepository.find_by_email(email)
        if not user:
            logger.error(f"Utilisateur non trouvé: {email}")
            return
        
        logger.info(f"Utilisateur trouvé: {user.get('id')}, email: {user.get('email')}, username: {user.get('username')}")
        
        # Hasher le nouveau mot de passe
        hashed_password = PasswordHasher.hash_password(new_password)
        logger.info(f"Mot de passe hashé avec succès")
        
        # Mettre à jour l'utilisateur
        db = get_database()
        from bson import ObjectId
        user_id = user.get('id') or user.get('_id')
        result = await db.users.update_one(
            {"_id": ObjectId(str(user_id))},
            {"$set": {"hashed_password": hashed_password}}
        )
        
        if result.modified_count > 0:
            logger.info(f"✅ Mot de passe mis à jour avec succès pour {email}")
        else:
            logger.warning(f"⚠️  Aucune modification effectuée pour {email}")
            
    except Exception as e:
        logger.error(f"Erreur lors de la correction du mot de passe: {e}", exc_info=True)
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fix_user_password.py <email> <new_password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    asyncio.run(fix_user_password(email, password))
