"""
Script pour supprimer un utilisateur par email
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, get_database, close_mongo_connection
from bson import ObjectId
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def delete_user_by_email(email: str):
    """Supprime un utilisateur par email"""
    try:
        await connect_to_mongo()
        db = get_database()
        
        # Chercher l'utilisateur par email
        user = await db.users.find_one({"email": email})
        
        if not user:
            print(f"Aucun utilisateur trouve avec l'email: {email}")
            return
        
        user_id = user.get("_id")
        print(f"Utilisateur trouve:")
        print(f"  - Email: {user.get('email')}")
        print(f"  - Username: {user.get('username')}")
        print(f"  - Nom: {user.get('first_name')} {user.get('last_name')}")
        
        # Supprimer l'utilisateur
        result = await db.users.delete_one({"_id": user_id})
        
        if result.deleted_count > 0:
            print(f"[OK] Utilisateur supprime avec succes")
            
            # Supprimer aussi les tokens de réinitialisation
            reset_result = await db.password_resets.delete_many({"user_id": user_id})
            if reset_result.deleted_count > 0:
                print(f"[OK] {reset_result.deleted_count} token(s) de reinitialisation supprime(s)")
            
            # Supprimer les progressions (optionnel)
            progress_result = await db.progress.delete_many({"user_id": str(user_id)})
            if progress_result.deleted_count > 0:
                print(f"[OK] {progress_result.deleted_count} progression(s) supprimee(s)")
        else:
            print("[ERREUR] Echec de la suppression")
        
    except Exception as e:
        logger.error(f"Erreur: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    email = "kouroumaelisee@gmail.com"
    print("=" * 50)
    print(f"  Suppression de l'utilisateur: {email}")
    print("=" * 50)
    print()
    
    asyncio.run(delete_user_by_email(email))
    print("\n[OK] Termine !")
