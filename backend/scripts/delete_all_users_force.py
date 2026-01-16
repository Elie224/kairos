"""
Script pour supprimer tous les utilisateurs SANS confirmation (pour automation)
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_database, close_database
from app.database.mongo import db


async def delete_all_users_force():
    """Supprime tous les utilisateurs de la base de données SANS confirmation"""
    try:
        # Initialiser la base de données
        await init_database()
        
        # Compter les utilisateurs avant suppression
        count_before = await db.database.users.count_documents({})
        print(f"📊 Nombre d'utilisateurs: {count_before}")
        
        if count_before == 0:
            print("✅ Aucun utilisateur à supprimer")
            return
        
        # Supprimer tous les utilisateurs
        result = await db.database.users.delete_many({})
        deleted_count = result.deleted_count
        
        print(f"✅ {deleted_count} utilisateur(s) supprimé(s) avec succès!")
        
        # Vérifier qu'il ne reste plus d'utilisateurs
        count_after = await db.database.users.count_documents({})
        print(f"📊 Nombre d'utilisateurs après suppression: {count_after}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(delete_all_users_force())
