"""
Script de diagnostic complet des bases de données
Vérifie MongoDB, PostgreSQL et Redis
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, get_database, db
from app.database.postgres import engine, SessionLocal
from app.utils.cache import get_redis, init_redis
from app.config import settings
from sqlalchemy import text


async def check_mongodb():
    """Vérifie la connexion MongoDB"""
    print("\n" + "=" * 60)
    print("🔍 VÉRIFICATION MONGODB")
    print("=" * 60)
    try:
        print(f"URL: {settings.mongodb_url}")
        print(f"Base de données: {settings.mongodb_db_name}")
        
        await connect_to_mongo()
        database = get_database()
        
        # Test de ping
        await db.client.admin.command('ping')
        print("✅ MongoDB connecté avec succès")
        
        # Vérifier les collections
        collections = await database.list_collection_names()
        print(f"   Collections trouvées: {len(collections)}")
        if collections:
            print(f"   Exemples: {', '.join(collections[:5])}")
        
        # Vérifier les index sur modules
        try:
            indexes = await database.modules.index_information()
            print(f"   Index sur 'modules': {len(indexes)}")
        except Exception:
            print("   ⚠️  Collection 'modules' n'existe pas encore")
        
        return True
    except Exception as e:
        print(f"❌ Erreur MongoDB: {e}")
        print("\n💡 Solutions:")
        print("   1. Vérifiez que MongoDB est démarré:")
        print("      - Windows: Vérifiez le service MongoDB")
        print("      - Docker: docker run -d -p 27017:27017 mongo:7.0")
        print("   2. Vérifiez MONGODB_URL dans .env")
        return False


def check_postgresql():
    """Vérifie la connexion PostgreSQL"""
    print("\n" + "=" * 60)
    print("🔍 VÉRIFICATION POSTGRESQL")
    print("=" * 60)
    try:
        print(f"Host: {settings.postgres_host}:{settings.postgres_port}")
        print(f"Base de données: {settings.postgres_db}")
        print(f"Utilisateur: {settings.postgres_user}")
        
        # Test de connexion
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print("✅ PostgreSQL connecté avec succès")
            print(f"   Version: {version.split(',')[0]}")
        
        # Vérifier les tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"   Tables trouvées: {len(tables)}")
        if tables:
            print(f"   Exemples: {', '.join(tables[:5])}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur PostgreSQL: {e}")
        print("\n💡 Solutions:")
        print("   1. Vérifiez que PostgreSQL est démarré:")
        print("      - Windows: Vérifiez le service PostgreSQL")
        print("      - Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine")
        print("   2. Vérifiez les variables POSTGRES_* dans .env")
        print("   3. Créez la base de données si elle n'existe pas:")
        print("      CREATE DATABASE eduverse;")
        return False


async def check_redis():
    """Vérifie la connexion Redis"""
    print("\n" + "=" * 60)
    print("🔍 VÉRIFICATION REDIS")
    print("=" * 60)
    try:
        if not settings.redis_url:
            print("⚠️  REDIS_URL non configuré dans .env")
            print("\n💡 Solutions:")
            print("   1. Ajoutez REDIS_URL=redis://localhost:6379/0 dans .env")
            print("   2. Démarrez Redis:")
            print("      - Docker: docker run -d -p 6379:6379 redis:7-alpine")
            print("      - Windows: Téléchargez Redis pour Windows")
            return False
        
        print(f"URL: {settings.redis_url}")
        
        await init_redis()
        redis = get_redis()
        
        if redis:
            await redis.ping()
            print("✅ Redis connecté avec succès")
            
            # Informations système
            info = await redis.info("server")
            print(f"   Version: {info.get('redis_version', 'N/A')}")
            
            info_memory = await redis.info("memory")
            print(f"   Mémoire utilisée: {info_memory.get('used_memory_human', 'N/A')}")
            
            # Compter les clés
            keys = []
            async for key in redis.scan_iter(match="*"):
                keys.append(key)
            print(f"   Clés totales: {len(keys)}")
            
            return True
        else:
            print("❌ Redis non initialisé")
            return False
    except Exception as e:
        print(f"❌ Erreur Redis: {e}")
        print("\n💡 Solutions:")
        print("   1. Vérifiez que Redis est démarré:")
        print("      - Docker: docker run -d -p 6379:6379 redis:7-alpine")
        print("      - Windows: Téléchargez Redis pour Windows")
        print("   2. Vérifiez REDIS_URL dans .env")
        print("   3. Installez redis: pip install redis[hiredis]")
        return False


def check_environment():
    """Vérifie la configuration de l'environnement"""
    print("\n" + "=" * 60)
    print("🔍 CONFIGURATION ENVIRONNEMENT")
    print("=" * 60)
    
    issues = []
    
    # Vérifier MongoDB
    if settings.mongodb_url == "mongodb://localhost:27017":
        print("⚠️  MongoDB URL par défaut utilisée")
    
    # Vérifier PostgreSQL
    if not settings.postgres_password:
        print("⚠️  POSTGRES_PASSWORD non configuré (peut être vide si pas de mot de passe)")
    
    # Vérifier Redis
    if not settings.redis_url:
        print("⚠️  REDIS_URL non configuré - Cache désactivé")
        issues.append("Redis")
    
    # Vérifier SECRET_KEY
    if not settings.secret_key:
        print("⚠️  SECRET_KEY non configuré - Obligatoire en production")
        issues.append("SECRET_KEY")
    
    # Vérifier OpenAI
    if not settings.openai_api_key:
        print("⚠️  OPENAI_API_KEY non configuré - Fonctionnalités IA désactivées")
        issues.append("OpenAI")
    
    if not issues:
        print("✅ Configuration de base OK")
    
    return len(issues) == 0


async def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLET DES BASES DE DONNÉES - Kaïros")
    print("=" * 60)
    
    results = {
        "MongoDB": await check_mongodb(),
        "PostgreSQL": check_postgresql(),
        "Redis": await check_redis(),
        "Configuration": check_environment()
    }
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    for name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {name}: {'OK' if status else 'PROBLÈME'}")
    
    all_ok = all(results.values())
    
    if all_ok:
        print("\n✅ Toutes les bases de données sont correctement configurées!")
    else:
        print("\n⚠️  Certaines bases de données nécessitent une attention")
        print("\n📝 Actions recommandées:")
        
        if not results["MongoDB"]:
            print("\n  🔧 MongoDB:")
            print("     - Démarrer MongoDB")
            print("     - Vérifier MONGODB_URL dans .env")
        
        if not results["PostgreSQL"]:
            print("\n  🔧 PostgreSQL:")
            print("     - Démarrer PostgreSQL")
            print("     - Créer la base de données: CREATE DATABASE eduverse;")
            print("     - Vérifier POSTGRES_* dans .env")
        
        if not results["Redis"]:
            print("\n  🔧 Redis:")
            print("     - Ajouter REDIS_URL=redis://localhost:6379/0 dans .env")
            print("     - Démarrer Redis (Docker recommandé)")
        
        if not results["Configuration"]:
            print("\n  🔧 Configuration:")
            print("     - Créer un fichier .env à partir de .env.example")
            print("     - Configurer toutes les variables nécessaires")
    
    # Fermer les connexions
    try:
        if db.client:
            db.client.close()
    except Exception:
        pass
    
    try:
        redis = get_redis()
        if redis:
            await redis.aclose()
    except Exception:
        pass
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

