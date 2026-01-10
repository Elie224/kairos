"""
Script pour supprimer tous les utilisateurs des deux bases de données
MongoDB et PostgreSQL
"""
import sys
import os
import asyncio

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Importer les settings
from app.config import settings

# Forcer l'encodage UTF-8
os.environ['PGCLIENTENCODING'] = 'UTF8'

async def delete_mongodb_users():
    """Supprime tous les utilisateurs de MongoDB"""
    try:
        logger.info("Suppression des utilisateurs MongoDB...")
        
        from app.database import connect_to_mongo, get_database, close_mongo_connection
        
        # Se connecter à MongoDB
        await connect_to_mongo()
        db = get_database()
        
        # Supprimer tous les utilisateurs
        result = await db.users.delete_many({})
        count = result.deleted_count
        
        logger.info(f"  OK: {count} utilisateur(s) supprime(s) de MongoDB")
        
        # Fermer la connexion
        await close_mongo_connection()
        
        return count
    except Exception as e:
        logger.error(f"ERREUR lors de la suppression MongoDB: {e}")
        return 0

def delete_postgresql_users():
    """Supprime tous les utilisateurs de PostgreSQL"""
    try:
        logger.info("Suppression des utilisateurs PostgreSQL...")
        
        # Configuration PostgreSQL
        POSTGRES_USER = settings.postgres_user
        POSTGRES_PASSWORD = settings.postgres_password
        POSTGRES_HOST = settings.postgres_host
        POSTGRES_PORT = settings.postgres_port
        POSTGRES_DB = settings.postgres_db
        
        # Créer une URL de connexion
        if POSTGRES_PASSWORD:
            encoded_password = quote_plus(POSTGRES_PASSWORD)
            url = f"postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        else:
            url = f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        
        # Créer un engine
        engine = create_engine(
            url,
            pool_pre_ping=True,
            echo=False,
            connect_args={
                "client_encoding": "UTF8"
            }
        )
        
        # Supprimer tous les utilisateurs
        with engine.connect() as conn:
            # Supprimer d'abord les données liées (enrollments, user_progress)
            logger.info("  Suppression des donnees liees (enrollments, user_progress)...")
            conn.execute(text("DELETE FROM enrollments;"))
            conn.execute(text("DELETE FROM user_progress;"))
            conn.commit()
            
            # Supprimer les utilisateurs
            result = conn.execute(text("DELETE FROM users;"))
            count = result.rowcount
            conn.commit()
        
        logger.info(f"  OK: {count} utilisateur(s) supprime(s) de PostgreSQL")
        
        return count
    except Exception as e:
        logger.error(f"ERREUR lors de la suppression PostgreSQL: {e}")
        return 0

async def main():
    """Fonction principale"""
    logger.info("=" * 60)
    logger.info("  SUPPRESSION DE TOUS LES UTILISATEURS")
    logger.info("=" * 60)
    logger.info("")
    logger.warning("ATTENTION: Cette operation va supprimer TOUS les utilisateurs!")
    logger.warning("  - MongoDB: Collection 'users'")
    logger.warning("  - PostgreSQL: Table 'users' + donnees liees")
    logger.info("")
    
    # Vérifier si confirmation en ligne de commande
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        logger.info("Confirmation via parametre --confirm")
    else:
        logger.warning("Pour executer, utilisez: python delete_all_users_complete.py --confirm")
        logger.info("Ou modifiez le script pour supprimer la confirmation")
        return
    
    logger.info("")
    logger.info("Suppression en cours...")
    logger.info("")
    
    # Supprimer de MongoDB
    mongo_count = await delete_mongodb_users()
    
    logger.info("")
    
    # Supprimer de PostgreSQL
    postgres_count = delete_postgresql_users()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("  RESUME")
    logger.info("=" * 60)
    logger.info("")
    logger.info(f"MongoDB:    {mongo_count} utilisateur(s) supprime(s)")
    logger.info(f"PostgreSQL: {postgres_count} utilisateur(s) supprime(s)")
    logger.info("")
    
    if mongo_count > 0 or postgres_count > 0:
        logger.info("OK: Suppression terminee avec succes!")
        logger.info("")
        logger.info("Vous pouvez maintenant creer un nouveau compte.")
    else:
        logger.info("Aucun utilisateur trouve a supprimer.")

if __name__ == "__main__":
    asyncio.run(main())
