"""
Script pour supprimer un utilisateur de la base de données
Usage: python scripts/delete_user.py <email_or_username>
"""
import asyncio
import sys
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.repositories.user_repository import UserRepository
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def delete_user(email_or_username: str):
    """Supprime un utilisateur de la base de données"""
    try:
        await connect_to_mongo()
        
        # Trouver l'utilisateur
        user = await UserRepository.find_by_email_or_username(email_or_username)
        
        if not user:
            logger.error(f"Utilisateur '{email_or_username}' non trouvé")
            return False
        
        # Confirmer la suppression
        logger.info(f"Utilisateur trouvé:")
        logger.info(f"  - Email: {user.get('email')}")
        logger.info(f"  - Username: {user.get('username')}")
        logger.info(f"  - Nom: {user.get('first_name')} {user.get('last_name')}")
        logger.info(f"  - Admin: {user.get('is_admin', False)}")
        
        # Supprimer l'utilisateur
        db = get_database()
        result = await db.users.delete_one({"_id": ObjectId(user["id"])})
        
        if result.deleted_count > 0:
            logger.info(f"✅ Utilisateur '{email_or_username}' supprimé avec succès")
            
            # Supprimer aussi les données associées (optionnel mais recommandé)
            # Supprimer les progressions
            progress_deleted = await db.progress.delete_many({"user_id": user["id"]})
            logger.info(f"  - {progress_deleted.deleted_count} progression(s) supprimée(s)")
            
            # Supprimer les favoris
            favorites_deleted = await db.favorites.delete_many({"user_id": user["id"]})
            logger.info(f"  - {favorites_deleted.deleted_count} favori(s) supprimé(s)")
            
            return True
        else:
            logger.error(f"Échec de la suppression de l'utilisateur '{email_or_username}'")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    finally:
        await close_mongo_connection()


async def list_users():
    """Liste tous les utilisateurs"""
    try:
        await connect_to_mongo()
        db = get_database()
        
        cursor = db.users.find({})
        users = await cursor.to_list(length=100)
        
        if not users:
            logger.info("Aucun utilisateur trouvé")
            return
        
        logger.info(f"\n📋 Utilisateurs ({len(users)}):")
        for user in users:
            logger.info(f"  - {user.get('email')} ({user.get('username')}) - Admin: {user.get('is_admin', False)}")
            
    except Exception as e:
        logger.error(f"Erreur lors de la liste des utilisateurs: {e}")
    finally:
        await close_mongo_connection()


async def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/delete_user.py <email_or_username>  # Supprimer un utilisateur")
        print("  python scripts/delete_user.py --list               # Lister tous les utilisateurs")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "--list":
        await list_users()
    else:
        await delete_user(command)


if __name__ == "__main__":
    asyncio.run(main())

















