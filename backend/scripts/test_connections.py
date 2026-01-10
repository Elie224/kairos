"""
Script de test rapide des connexions aux bases de données
Teste MongoDB, PostgreSQL et Redis
"""
import asyncio
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
import socket


def test_port(host, port, name):
    """Teste si un port est accessible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            print(f"[OK] {name} - Port {port} accessible sur {host}")
            return True
        else:
            print(f"[ERREUR] {name} - Port {port} REFUSE sur {host}")
            return False
    except Exception as e:
        print(f"[ERREUR] {name} - Erreur de connexion: {e}")
        return False


async def test_mongodb():
    """Teste la connexion MongoDB"""
    print("\n" + "=" * 60)
    print("TEST CONNEXION MONGODB")
    print("=" * 60)
    
    # Test du port
    port_ok = test_port("localhost", 27017, "MongoDB")
    
    if not port_ok:
        print("\n💡 MongoDB n'est pas accessible")
        print("   Solutions:")
        print("   1. Vérifiez que MongoDB est démarré")
        print("   2. Windows: Vérifiez le service MongoDB dans les Services")
        print("   3. Docker: docker run -d -p 27017:27017 --name kaïros-mongo mongo:7.0")
        return False
    
    # Test de connexion réelle
    try:
        from app.database import connect_to_mongo, db
        await connect_to_mongo()
        await db.client.admin.command('ping')
        print("[OK] Connexion MongoDB reussie")
        return True
    except Exception as e:
        print(f"[ERREUR] Erreur de connexion MongoDB: {e}")
        return False


def test_postgresql():
    """Teste la connexion PostgreSQL"""
    print("\n" + "=" * 60)
    print("TEST CONNEXION POSTGRESQL")
    print("=" * 60)
    
    host = settings.postgres_host
    port = int(settings.postgres_port)
    
    # Test du port
    port_ok = test_port(host, port, "PostgreSQL")
    
    if not port_ok:
        print(f"\n💡 PostgreSQL n'est pas accessible sur {host}:{port}")
        print("   Solutions:")
        print("   1. Vérifiez que PostgreSQL est démarré")
        print("   2. Windows: Vérifiez le service PostgreSQL dans les Services")
        print("   3. Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine")
        return False
    
    # Test de connexion réelle
    try:
        from app.database.postgres import engine
        from sqlalchemy import text
        
        print(f"   Tentative de connexion à {host}:{port}/{settings.postgres_db}...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"[OK] Connexion PostgreSQL reussie")
            print(f"   Version: {version.split(',')[0]}")
            return True
    except Exception as e:
        error_msg = str(e)
        print(f"[ERREUR] Erreur de connexion PostgreSQL: {error_msg}")
        
        if "could not connect" in error_msg.lower() or "connection refused" in error_msg.lower():
            print(f"\n💡 PostgreSQL refuse la connexion sur {host}:{port}")
            print("   Solutions:")
            print("   1. Vérifiez que PostgreSQL est démarré")
            print("   2. Vérifiez que le port 5432 n'est pas bloqué par un firewall")
        elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
            print(f"\n💡 La base de données '{settings.postgres_db}' n'existe pas")
            print(f"   Créez-la avec: CREATE DATABASE {settings.postgres_db};")
        elif "password authentication failed" in error_msg.lower():
            print(f"\n💡 Authentification échouée")
            print("   Vérifiez POSTGRES_USER et POSTGRES_PASSWORD dans .env")
        else:
            print(f"\n💡 Erreur: {error_msg}")
        
        return False


async def test_redis():
    """Teste la connexion Redis"""
    print("\n" + "=" * 60)
    print("TEST CONNEXION REDIS")
    print("=" * 60)
    
    if not settings.redis_url:
        print("[ATTENTION] REDIS_URL non configure dans .env")
        print("   Ajoutez: REDIS_URL=redis://localhost:6379/0")
        return False
    
    # Extraire host et port de l'URL Redis
    try:
        from urllib.parse import urlparse
        parsed = urlparse(settings.redis_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
    except:
        host = "localhost"
        port = 6379
    
    # Test du port
    port_ok = test_port(host, port, "Redis")
    
    if not port_ok:
        print(f"\n💡 Redis n'est pas accessible sur {host}:{port}")
        print("   Solutions:")
        print("   1. Démarrez Redis:")
        print("      - Docker: docker run -d -p 6379:6379 --name kaïros-redis redis:7-alpine")
        print("      - Windows: Téléchargez Redis pour Windows")
        print("   2. Vérifiez REDIS_URL dans .env")
        return False
    
    # Test de connexion réelle
    try:
        import redis.asyncio as redis
        client = redis.from_url(settings.redis_url, encoding='utf-8', decode_responses=True)
        await client.ping()
        print("[OK] Connexion Redis reussie")
        await client.aclose()
        return True
    except ImportError:
        print("[ERREUR] Module redis non installe")
        print("   Installez avec: pip install redis[hiredis]")
        return False
    except Exception as e:
        print(f"[ERREUR] Erreur de connexion Redis: {e}")
        return False


async def main():
    """Fonction principale"""
    print("\n" + "=" * 60)
    print("TEST DES CONNEXIONS AUX BASES DE DONNÉES")
    print("=" * 60)
    
    results = {
        "MongoDB": await test_mongodb(),
        "PostgreSQL": test_postgresql(),
        "Redis": await test_redis()
    }
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    for name, status in results.items():
        status_icon = "[OK]" if status else "[ERREUR]"
        print(f"{status_icon} {name}: {'CONNECTE' if status else 'CONNEXION REFUSEE'}")
    
    all_ok = all(results.values())
    
    if all_ok:
        print("\n[OK] Toutes les bases de donnees sont accessibles!")
    else:
        print("\n[ATTENTION] Certaines connexions sont refusees")
        print("\nActions a effectuer:")
        
        if not results["MongoDB"]:
            print("\n  MongoDB:")
            print("     docker run -d -p 27017:27017 --name kairos-mongo mongo:7.0")
        
        if not results["PostgreSQL"]:
            print("\n  PostgreSQL:")
            print("     docker run -d -p 5432:5432 -e POSTGRES_DB=eduverse -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres --name kairos-postgres postgres:15-alpine")
            print("     Puis creez la base: CREATE DATABASE eduverse;")
        
        if not results["Redis"]:
            print("\n  Redis:")
            print("     docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine")
            print("     Ajoutez dans .env: REDIS_URL=redis://localhost:6379/0")
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

