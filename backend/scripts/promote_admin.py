"""
Script pour promouvoir un utilisateur existant en administrateur
Usage: python scripts/promote_admin.py <email>
"""
import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour permettre les imports
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.repositories.user_repository import UserRepository
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def promote_to_admin(email: str):
    """Promouvoir un utilisateur en administrateur"""
    try:
        await connect_to_mongo()
        
        # Trouver l'utilisateur
        user = await UserRepository.find_by_email(email)
        
        if not user:
            logger.error(f"❌ Utilisateur avec l'email '{email}' non trouvé")
            return False
        
        # Vérifier si déjà admin
        if user.get("is_admin", False):
            logger.info(f"ℹ️  L'utilisateur '{email}' est déjà administrateur")
            logger.info(f"   - Email: {user.get('email')}")
            logger.info(f"   - Username: {user.get('username')}")
            logger.info(f"   - Nom: {user.get('first_name')} {user.get('last_name')}")
            return True
        
        # Promouvoir en admin
        db = get_database()
        result = await db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$set": {"is_admin": True}}
        )
        
        if result.modified_count > 0:
            logger.info(f"✅ Utilisateur promu administrateur avec succès:")
            logger.info(f"   - Email: {user.get('email')}")
            logger.info(f"   - Username: {user.get('username')}")
            logger.info(f"   - Nom: {user.get('first_name')} {user.get('last_name')}")
            logger.info(f"   - Admin: True")
            return True
        else:
            logger.error(f"❌ Échec de la promotion (aucune modification)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la promotion: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        await close_mongo_connection()


async def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/promote_admin.py <email>")
        print("")
        print("Exemple:")
        print("  python scripts/promote_admin.py kouroumaelisee@gmail.com")
        sys.exit(1)
    
    email = sys.argv[1]
    
    success = await promote_to_admin(email)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

