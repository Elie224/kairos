"""
Script de diagnostic des performances
Vérifie que toutes les optimisations sont en place
"""
import asyncio
import time
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, get_database, db
from app.utils.cache import get_redis, init_redis
from app.config import settings


async def check_mongodb():
    """Vérifie la connexion MongoDB et les index"""
    print("🔍 Vérification MongoDB...")
    try:
        await connect_to_mongo()
        database = get_database()
        
        # Vérifier les index sur modules
        indexes = await database.modules.index_information()
        print(f"✅ MongoDB connecté")
        print(f"   Index modules: {len(indexes)} index trouvés")
        
        # Vérifier les index critiques
        critical_indexes = [
            ("subject", "difficulty", "created_at"),
            ("user_id", "module_id"),
            "created_at",
            "user_id"
        ]
        
        index_names = [idx.get("name", "") if isinstance(idx, dict) else idx for idx in indexes.values()]
        for critical in critical_indexes:
            if isinstance(critical, tuple):
                found = any(all(part in name for part in critical) for name in index_names)
            else:
                found = critical in index_names
            status = "✅" if found else "❌"
            print(f"   {status} Index: {critical}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur MongoDB: {e}")
        return False


async def check_redis():
    """Vérifie la connexion Redis"""
    print("\n🔍 Vérification Redis...")
    try:
        await init_redis()
        redis = get_redis()
        
        if redis:
            await redis.ping()
            info = await redis.info("memory")
            print(f"✅ Redis connecté")
            print(f"   Mémoire utilisée: {info.get('used_memory_human', 'N/A')}")
            
            # Compter les clés de cache
            keys = []
            async for key in redis.scan_iter(match="cache:*"):
                keys.append(key)
            print(f"   Clés de cache: {len(keys)}")
            
            return True
        else:
            print("⚠️  Redis non configuré (REDIS_URL manquant)")
            print("   Le cache ne sera pas utilisé - performance réduite")
            return False
    except Exception as e:
        print(f"❌ Erreur Redis: {e}")
        print("   Le cache ne sera pas utilisé - performance réduite")
        return False


async def test_query_performance():
    """Teste la performance d'une requête"""
    print("\n🔍 Test de performance...")
    try:
        database = get_database()
        
        # Test 1: Liste des modules (sans contenu)
        start = time.time()
        cursor = database.modules.find({}, {"content": 0}).limit(10)
        modules = await cursor.to_list(length=10)
        time1 = time.time() - start
        print(f"   Liste modules (10): {time1*1000:.2f}ms")
        
        # Test 2: Progression utilisateur
        start = time.time()
        cursor = database.progress.find({"user_id": "test"}).limit(10)
        progress = await cursor.to_list(length=10)
        time2 = time.time() - start
        print(f"   Progression (10): {time2*1000:.2f}ms")
        
        if time1 > 0.5 or time2 > 0.5:
            print("   ⚠️  Requêtes lentes détectées!")
            print("   Vérifiez les index MongoDB")
        else:
            print("   ✅ Performances OK")
        
        return True
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        return False


async def main():
    """Fonction principale"""
    print("=" * 50)
    print("DIAGNOSTIC DE PERFORMANCE - Kaïrox")
    print("=" * 50)
    
    results = []
    
    # Vérifications
    results.append(await check_mongodb())
    results.append(await check_redis())
    results.append(await test_query_performance())
    
    # Résumé
    print("\n" + "=" * 50)
    print("RÉSUMÉ")
    print("=" * 50)
    
    if all(results):
        print("✅ Toutes les optimisations sont en place")
    else:
        print("⚠️  Certaines optimisations manquent")
        print("\nActions recommandées:")
        if not results[0]:
            print("  - Vérifier que MongoDB est démarré")
        if not results[1]:
            print("  - Configurer REDIS_URL dans .env")
            print("  - Démarrer Redis: docker run -d -p 6379:6379 redis:7-alpine")
        if not results[2]:
            print("  - Vérifier les index MongoDB")
    
    # Fermer les connexions
    if db.client:
        db.client.close()


if __name__ == "__main__":
    asyncio.run(main())














