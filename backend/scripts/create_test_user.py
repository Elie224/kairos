"""
Script pour créer un utilisateur de test
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_database, close_database
from app.repositories.user_repository import UserRepository
from app.utils.security import PasswordHasher
from datetime import datetime, timezone


async def create_test_user():
    """Crée un utilisateur de test"""
    try:
        # Initialiser la base de données
        await init_database()
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = await UserRepository.find_by_email("test@example.com")
        if existing_user:
            print("❌ L'utilisateur test@example.com existe déjà")
            print(f"   ID: {existing_user.get('id')}")
            print(f"   Username: {existing_user.get('username')}")
            return
        
        # Créer l'utilisateur de test
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": PasswordHasher.hash_password("test123"),
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        user = await UserRepository.create(user_data)
        print("✅ Utilisateur de test créé avec succès!")
        print(f"   Email: {user.get('email')}")
        print(f"   Username: {user.get('username')}")
        print(f"   Password: test123")
        print(f"   ID: {user.get('id')}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(create_test_user())
