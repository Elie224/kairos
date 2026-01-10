"""
Script pour définir kouroumaelisee@gmail.com comme admin principal
Peut être exécuté localement ou via Render Shell
"""
import asyncio
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH
script_dir = Path(__file__).parent
backend_dir = script_dir.parent
sys.path.insert(0, str(backend_dir))

from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.repositories.user_repository import UserRepository
from app.utils.security import InputSanitizer
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

ADMIN_EMAIL = "kouroumaelisee@gmail.com"


async def set_main_admin():
    """Définir l'utilisateur principal comme admin"""
    try:
        await connect_to_mongo()
        logger.info("=" * 80)
        logger.info("  PROMOTION DE L'ADMIN PRINCIPAL")
        logger.info("=" * 80)
        logger.info(f"Email: {ADMIN_EMAIL}")
        logger.info("")
        
        # Trouver l'utilisateur
        user = await UserRepository.find_by_email(ADMIN_EMAIL)
        
        if not user:
            logger.error(f"❌ Utilisateur avec l'email '{ADMIN_EMAIL}' non trouvé")
            logger.error("")
            logger.error("Action requise :")
            logger.error(f"1. Créez d'abord un compte avec l'email '{ADMIN_EMAIL}'")
            logger.error("2. Puis réexécutez ce script pour le promouvoir en admin")
            return False
        
        # Vérifier si déjà admin
        if user.get("is_admin", False):
            logger.info(f"✅ L'utilisateur '{ADMIN_EMAIL}' est déjà administrateur")
            logger.info(f"   - Email: {user.get('email')}")
            logger.info(f"   - Username: {user.get('username')}")
            logger.info(f"   - Nom: {user.get('first_name', '')} {user.get('last_name', '')}")
            logger.info(f"   - Admin: {user.get('is_admin', False)}")
            return True
        
        # Promouvoir en admin
        db = get_database()
        sanitized_id = InputSanitizer.sanitize_object_id(user["id"])
        
        if not sanitized_id:
            logger.error(f"❌ ID utilisateur invalide: {user.get('id')}")
            return False
        
        result = await db.users.update_one(
            {"_id": ObjectId(sanitized_id)},
            {"$set": {"is_admin": True}}
        )
        
        if result.modified_count > 0:
            # Récupérer l'utilisateur mis à jour
            updated_user = await UserRepository.find_by_id(sanitized_id)
            logger.info("")
            logger.info("✅ Promotion réussie !")
            logger.info(f"   - Email: {updated_user.get('email')}")
            logger.info(f"   - Username: {updated_user.get('username')}")
            logger.info(f"   - Nom: {updated_user.get('first_name', '')} {updated_user.get('last_name', '')}")
            logger.info(f"   - Admin: {updated_user.get('is_admin', False)}")
            logger.info("")
            logger.info("L'utilisateur peut maintenant accéder à la page admin après reconnexion.")
            return True
        else:
            logger.error(f"❌ Échec de la promotion (aucune modification effectuée)")
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
    success = await set_main_admin()
    
    logger.info("")
    logger.info("=" * 80)
    if success:
        logger.info("✅ Script terminé avec succès")
        sys.exit(0)
    else:
        logger.error("❌ Script terminé avec erreur")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
