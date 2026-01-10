"""
Script pour lister tous les utilisateurs de la base de données
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, get_database, close_mongo_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def list_all_users():
    """Liste tous les utilisateurs"""
    try:
        await connect_to_mongo()
        db = get_database()
        
        users = await db.users.find({}).to_list(length=1000)
        
        print(f"\nNombre d'utilisateurs: {len(users)}")
        
        if len(users) == 0:
            print("Aucun utilisateur dans la base de donnees")
        else:
            print("\nUtilisateurs:")
            for user in users:
                print(f"  - Email: {user.get('email')}, Username: {user.get('username')}, ID: {user.get('_id')}")
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(list_all_users())
