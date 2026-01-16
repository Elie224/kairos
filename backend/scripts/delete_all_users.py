"""
Script pour supprimer tous les utilisateurs de la base de données
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_database, close_database, get_database


async def delete_all_users():
    """Supprime tous les utilisateurs de la base de données"""
    try:
        # Initialiser la base de données
        await init_database()
        
        # Compter les utilisateurs avant suppression
        count_before = await db.database.users.count_documents({})
        print(f"📊 Nombre d'utilisateurs avant suppression: {count_before}")
        
        if count_before == 0:
            print("✅ Aucun utilisateur à supprimer")
            return
        
        # Demander confirmation
        print(f"\n⚠️  ATTENTION: Vous êtes sur le point de supprimer {count_before} utilisateur(s)")
        confirmation = input("Tapez 'OUI' pour confirmer: ")
        
        if confirmation != 'OUI':
            print("❌ Suppression annulée")
            return
        
        # Supprimer tous les utilisateurs
        result = await db.database.users.delete_many({})
        deleted_count = result.deleted_count
        
        print(f"\n✅ {deleted_count} utilisateur(s) supprimé(s) avec succès!")
        
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
    asyncio.run(delete_all_users())
