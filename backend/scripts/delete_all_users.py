"""
Script pour supprimer tous les utilisateurs de la base de données
ATTENTION: Cette opération est irréversible !
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, get_database, close_mongo_connection
from app.config import settings
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
        
        # Demander confirmation
        print(f"\n⚠️  ATTENTION: Vous êtes sur le point de supprimer {user_count} utilisateur(s)")
        print("Cette opération est IRRÉVERSIBLE !")
        confirmation = input("Tapez 'SUPPRIMER' pour confirmer: ")
        
        if confirmation != "SUPPRIMER":
            print("❌ Opération annulée")
            return
        
        # Supprimer tous les utilisateurs
        result = await db.users.delete_many({})
        logger.info(f"✅ {result.deleted_count} utilisateur(s) supprimé(s)")
        
        # Supprimer aussi les données associées (optionnel)
        # Supprimer les tokens de réinitialisation
        reset_count = await db.password_resets.count_documents({})
        if reset_count > 0:
            await db.password_resets.delete_many({})
            logger.info(f"✅ {reset_count} token(s) de réinitialisation supprimé(s)")
        
        # Supprimer les progressions (optionnel - commenté pour préserver les données)
        # progress_count = await db.progress.count_documents({})
        # if progress_count > 0:
        #     await db.progress.delete_many({})
        #     logger.info(f"✅ {progress_count} progression(s) supprimée(s)")
        
        print(f"\n✅ Suppression terminée: {result.deleted_count} utilisateur(s) supprimé(s)")
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression: {e}")
        raise
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    print("=" * 50)
    print("  Suppression de tous les utilisateurs")
    print("=" * 50)
    print()
    
    asyncio.run(delete_all_users())
