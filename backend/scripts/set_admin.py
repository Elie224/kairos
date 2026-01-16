"""
Script pour définir un utilisateur comme administrateur
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au PYTHONPATH pour les imports relatifs
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import connect_to_mongo, close_mongo_connection
from app.repositories.user_repository import UserRepository
from app.utils.security import InputSanitizer
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def set_admin(email: str, is_admin: bool = True):
    """
    Définit un utilisateur comme administrateur ou le retire du rôle admin
    
    Args:
        email: Email de l'utilisateur
        is_admin: True pour promouvoir admin, False pour rétrograder
    """
    await connect_to_mongo()
    
    try:
        sanitized_email = InputSanitizer.sanitize_email(email)
        if not sanitized_email:
            logger.error(f"Email invalide fourni: {email}")
            return False

        user = await UserRepository.find_by_email(sanitized_email)
        if not user:
            logger.error(f"Utilisateur non trouvé pour l'email: {sanitized_email}")
            return False

        user_id = str(user["id"])
        current_admin_status = user.get("is_admin", False)
        
        if current_admin_status == is_admin:
            logger.info(f"L'utilisateur {sanitized_email} a déjà le statut admin={is_admin}")
            return True
        
        logger.info(f"Mise à jour du statut admin pour {sanitized_email}: {current_admin_status} -> {is_admin}")
        
        update_data = {
            "is_admin": is_admin,
            "updated_at": datetime.now(timezone.utc)
        }
        
        updated_user = await UserRepository.update(user_id, update_data)
        
        if updated_user:
            logger.info(f"✅ Statut admin mis à jour avec succès pour {sanitized_email}: is_admin={is_admin}")
            logger.info(f"   ID utilisateur: {user_id}")
            logger.info(f"   Email: {updated_user.get('email')}")
            logger.info(f"   Username: {updated_user.get('username')}")
            logger.info(f"   is_admin: {updated_user.get('is_admin')}")
            return True
        else:
            logger.error(f"❌ Échec de la mise à jour du statut admin pour {sanitized_email}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du statut admin: {e}", exc_info=True)
        return False
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    # Email de l'admin principal
    admin_email = "kouroumaelisee@gmail.com"
    
    print(f"\n{'='*60}")
    print(f"Promotion de l'utilisateur en administrateur")
    print(f"{'='*60}")
    print(f"Email: {admin_email}")
    print(f"{'='*60}\n")
    
    result = asyncio.run(set_admin(admin_email, is_admin=True))
    
    if result:
        print(f"\n✅ Succès! L'utilisateur {admin_email} est maintenant administrateur.")
    else:
        print(f"\n❌ Échec! Impossible de promouvoir {admin_email} en administrateur.")
        sys.exit(1)
