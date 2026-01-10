"""
Script simple pour supprimer TOUS les utilisateurs de la base de données
ATTENTION: Cette opération est irréversible !
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, get_database, close_mongo_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def delete_all_users():
    """Supprime tous les utilisateurs de la base de données"""
    try:
        await connect_to_mongo()
        db = get_database()
        
        # Compter les utilisateurs avant suppression
        user_count = await db.users.count_documents({})
        logger.info(f"Nombre d'utilisateurs trouvés: {user_count}")
        
        if user_count == 0:
            logger.info("Aucun utilisateur à supprimer")
            return
        
        # Supprimer tous les utilisateurs
        result = await db.users.delete_many({})
        logger.info(f"[OK] {result.deleted_count} utilisateur(s) supprime(s)")
        
        # Supprimer aussi les tokens de réinitialisation
        reset_count = await db.password_resets.count_documents({})
        if reset_count > 0:
            reset_result = await db.password_resets.delete_many({})
            logger.info(f"[OK] {reset_result.deleted_count} token(s) de reinitialisation supprime(s)")
        
        print(f"\n[OK] Suppression terminee: {result.deleted_count} utilisateur(s) supprime(s)")
        
    except Exception as e:
        logger.error(f"[ERREUR] Erreur lors de la suppression: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    print("=" * 50)
    print("  Suppression de tous les utilisateurs")
    print("=" * 50)
    print()
    
    asyncio.run(delete_all_users())
    print("\n[OK] Termine !")
