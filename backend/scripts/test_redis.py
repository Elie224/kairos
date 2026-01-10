"""
Script pour tester la connexion Redis
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app.utils.cache import init_redis, get_redis

async def test_redis():
    """Test de connexion et opérations Redis"""
    print("Initialisation Redis...")
    await init_redis()
    
    redis = get_redis()
    if not redis:
        print("❌ Redis non connecté")
        return False
    
    print("✅ Redis connecté")
    
    # Test des opérations de base
    try:
        # Test SET/GET
        await redis.set("test:key", "test_value")
        value = await redis.get("test:key")
        print(f"✅ SET/GET test: {value}")
        
        # Test INCR
        count = await redis.incr("test:counter")
        print(f"✅ INCR test: {count}")
        
        # Test EXPIRE
        await redis.expire("test:key", 10)
        print("✅ EXPIRE test: OK")
        
        # Nettoyage
        await redis.delete("test:key", "test:counter")
        print("✅ DELETE test: OK")
        
        print("\n🎉 Tous les tests Redis sont réussis!")
        return True
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False
    finally:
        await redis.aclose()

if __name__ == "__main__":
    success = asyncio.run(test_redis())
    sys.exit(0 if success else 1)














