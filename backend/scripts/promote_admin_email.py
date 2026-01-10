"""
Script pour promouvoir un utilisateur en administrateur par email
Gère à la fois MongoDB et PostgreSQL
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
from app.database.postgres import engine, init_postgres
from bson import ObjectId
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


async def promote_to_admin_mongo(email: str):
    """Promouvoir un utilisateur en administrateur dans MongoDB"""
    try:
        await connect_to_mongo()
        
        # Trouver l'utilisateur
        user = await UserRepository.find_by_email(email)
        
        if not user:
            logger.error(f"❌ Utilisateur avec l'email '{email}' non trouvé dans MongoDB")
            return False
        
        # Vérifier si déjà admin
        if user.get("is_admin", False):
            logger.info(f"ℹ️  L'utilisateur '{email}' est déjà administrateur dans MongoDB")
            return True
        
        # Promouvoir en admin
        db = get_database()
        result = await db.users.update_one(
            {"_id": ObjectId(user["id"])},
            {"$set": {"is_admin": True}}
        )
        
        if result.modified_count > 0:
            logger.info(f"✅ Utilisateur promu administrateur dans MongoDB:")
            logger.info(f"   - Email: {user.get('email')}")
            logger.info(f"   - Username: {user.get('username')}")
            logger.info(f"   - Nom: {user.get('first_name')} {user.get('last_name')}")
            return True
        else:
            logger.error(f"❌ Échec de la promotion dans MongoDB (aucune modification)")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la promotion dans MongoDB: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        await close_mongo_connection()


async def promote_to_admin_postgres(email: str):
    """Promouvoir un utilisateur en administrateur dans PostgreSQL"""
    try:
        init_postgres()
        
        # Utiliser une connexion synchrone car engine n'est pas async
        with engine.connect() as conn:
            # Trouver l'utilisateur
            result = conn.execute(
                text("SELECT id, email, username, first_name, last_name, is_admin FROM users WHERE email = :email"),
                {"email": email}
            )
            user_row = result.fetchone()
            
            if not user_row:
                logger.warning(f"⚠️  Utilisateur avec l'email '{email}' non trouvé dans PostgreSQL")
                return False
            
            user_id, user_email, username, first_name, last_name, is_admin = user_row
            
            # Vérifier si déjà admin
            if is_admin:
                logger.info(f"ℹ️  L'utilisateur '{email}' est déjà administrateur dans PostgreSQL")
                return True
            
            # Promouvoir en admin
            conn.execute(
                text("UPDATE users SET is_admin = TRUE WHERE id = :user_id"),
                {"user_id": user_id}
            )
            conn.commit()
            
            logger.info(f"✅ Utilisateur promu administrateur dans PostgreSQL:")
            logger.info(f"   - Email: {user_email}")
            logger.info(f"   - Username: {username}")
            logger.info(f"   - Nom: {first_name} {last_name}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la promotion dans PostgreSQL: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Point d'entrée principal"""
    email = "kouroumaelisee@gmail.com"
    
    logger.info("=" * 80)
    logger.info(f"  PROMOTION EN ADMINISTRATEUR")
    logger.info("=" * 80)
    logger.info(f"Email: {email}")
    logger.info("")
    
    # Promouvoir dans MongoDB
    logger.info("📦 Promotion dans MongoDB...")
    mongo_success = await promote_to_admin_mongo(email)
    logger.info("")
    
    # Promouvoir dans PostgreSQL
    logger.info("🐘 Promotion dans PostgreSQL...")
    postgres_success = await promote_to_admin_postgres(email)
    logger.info("")
    
    # Résumé
    logger.info("=" * 80)
    logger.info("  RÉSUMÉ")
    logger.info("=" * 80)
    logger.info(f"MongoDB:    {'✅ Succès' if mongo_success else '❌ Échec'}")
    logger.info(f"PostgreSQL: {'✅ Succès' if postgres_success else '❌ Échec'}")
    logger.info("")
    
    if mongo_success or postgres_success:
        logger.info("✅ Promotion terminée avec succès")
        logger.info("")
        logger.info("L'utilisateur peut maintenant accéder à la page admin après reconnexion.")
    else:
        logger.error("❌ Échec de la promotion dans toutes les bases de données")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
