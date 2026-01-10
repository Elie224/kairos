"""
Script de vérification complète des bases de données MongoDB et PostgreSQL
Vérifie que tout est bien configuré et que toutes les migrations sont faites
"""
import sys
import os
import asyncio

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Importer les settings
from app.config import settings

# Forcer l'encodage UTF-8
os.environ['PGCLIENTENCODING'] = 'UTF8'

# Tables PostgreSQL attendues
EXPECTED_POSTGRES_TABLES = ['users', 'courses', 'modules', 'enrollments', 'user_progress']

# Collections MongoDB attendues (principales)
EXPECTED_MONGO_COLLECTIONS = ['users', 'modules', 'progress', 'quizzes', 'exams']

def verify_postgresql():
    """Vérifie la connexion et les tables PostgreSQL"""
    logger.info("=" * 60)
    logger.info("VERIFICATION POSTGRESQL")
    logger.info("=" * 60)
    
    try:
        # Configuration PostgreSQL
        POSTGRES_USER = settings.postgres_user
        POSTGRES_PASSWORD = settings.postgres_password
        POSTGRES_HOST = settings.postgres_host
        POSTGRES_PORT = settings.postgres_port
        POSTGRES_DB = settings.postgres_db
        
        logger.info(f"Configuration:")
        logger.info(f"  Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
        logger.info(f"  Database: {POSTGRES_DB}")
        logger.info(f"  User: {POSTGRES_USER}")
        logger.info("")
        
        # Créer une URL de connexion
        if POSTGRES_PASSWORD:
            encoded_password = quote_plus(POSTGRES_PASSWORD)
            url = f"postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        else:
            url = f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        
        # Créer un engine
        engine = create_engine(
            url,
            pool_pre_ping=True,
            echo=False,
            connect_args={
                "client_encoding": "UTF8"
            }
        )
        
        # Tester la connexion
        logger.info("Test de connexion...")
        with engine.connect() as conn:
            # Vérifier la version PostgreSQL
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"  OK: Connexion reussie")
            logger.info(f"  Version: {version.split(',')[0]}")
            logger.info("")
            
            # Vérifier l'encodage
            result = conn.execute(text("SHOW client_encoding;"))
            encoding = result.fetchone()[0]
            logger.info(f"  Encodage: {encoding}")
            logger.info("")
            
            # Lister les tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            logger.info("Tables PostgreSQL:")
            logger.info("-" * 60)
            
            if tables:
                for table in sorted(tables):
                    columns = inspector.get_columns(table)
                    logger.info(f"  [OK] {table:20} ({len(columns)} colonnes)")
                
                logger.info("")
                logger.info(f"Total: {len(tables)} table(s)")
                
                # Vérifier les tables attendues
                missing_tables = [t for t in EXPECTED_POSTGRES_TABLES if t not in tables]
                extra_tables = [t for t in tables if t not in EXPECTED_POSTGRES_TABLES]
                
                if missing_tables:
                    logger.error("")
                    logger.error("ERREUR: Tables manquantes:")
                    for table in missing_tables:
                        logger.error(f"  - {table}")
                    return False
                
                if extra_tables:
                    logger.warning("")
                    logger.warning("Tables supplementaires (non critiques):")
                    for table in extra_tables:
                        logger.warning(f"  - {table}")
                
                logger.info("")
                logger.info("OK: Toutes les tables attendues sont presentes!")
                return True
            else:
                logger.error("ERREUR: Aucune table trouvee!")
                logger.error("Executez les migrations: python scripts/migrate_postgres.py create")
                return False
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"ERREUR: {error_msg}")
        
        if "password authentication failed" in error_msg.lower():
            logger.error("  Probleme d'authentification PostgreSQL")
            logger.error("  Verifiez POSTGRES_PASSWORD dans .env")
        elif "could not connect" in error_msg.lower():
            logger.error("  Impossible de se connecter a PostgreSQL")
            logger.error("  Verifiez que PostgreSQL 18 est demarre")
        elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
            logger.error(f"  La base de donnees '{POSTGRES_DB}' n'existe pas")
            logger.error("  Creez-la avec: CREATE DATABASE eduverse;")
        
        return False

async def verify_redis():
    """Vérifie la connexion Redis"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("VERIFICATION REDIS")
    logger.info("=" * 60)
    
    try:
        from app.utils.cache import init_redis, get_redis
        
        # Configuration Redis
        REDIS_URL = settings.redis_url or "redis://localhost:6379/0"
        
        logger.info(f"Configuration:")
        logger.info(f"  URL: {REDIS_URL}")
        logger.info("")
        
        # Tester la connexion
        logger.info("Test de connexion...")
        await init_redis()
        
        redis = get_redis()
        
        if redis:
            # Tester PING
            result = await redis.ping()
            if result:
                logger.info("  OK: Connexion reussie")
                logger.info("  Redis repond (PONG)")
                logger.info("")
                
                # Tester écriture/lecture
                await redis.set("test_verify", "ok", ex=5)
                value = await redis.get("test_verify")
                await redis.delete("test_verify")
                
                if value:
                    logger.info("  OK: Ecriture/lecture fonctionne")
                    logger.info("")
                    logger.info("OK: Redis fonctionne correctement!")
                    logger.info("  Cache active - Performance optimale")
                    return True
                else:
                    logger.warning("  ATTENTION: Probleme d'ecriture/lecture")
                    return False
            else:
                logger.error("  ERREUR: Redis ne repond pas")
                return False
        else:
            logger.error("  ERREUR: Impossible d'obtenir le client Redis")
            logger.error("")
            logger.error("  Verifiez:")
            logger.error("    1. Que Redis est demarre: docker ps | findstr redis")
            logger.error("    2. Que REDIS_URL est configure dans .env")
            logger.error("    3. Que le port 6379 n'est pas bloque")
            return False
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"ERREUR: {error_msg}")
        
        if "could not connect" in error_msg.lower() or "connection refused" in error_msg.lower():
            logger.error("  Impossible de se connecter a Redis")
            logger.error("  Demarrez Redis: docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine")
        elif "name 'redis'" in error_msg.lower() or "module" in error_msg.lower():
            logger.error("  Package Redis non installe")
            logger.error("  Installez: pip install redis[hiredis]")
        
        return False

async def verify_mongodb():
    """Vérifie la connexion et les collections MongoDB"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("VERIFICATION MONGODB")
    logger.info("=" * 60)
    
    try:
        from app.database import connect_to_mongo, get_database, close_mongo_connection
        
        # Configuration MongoDB
        MONGODB_URL = settings.mongodb_url
        MONGODB_DB_NAME = settings.mongodb_db_name
        
        logger.info(f"Configuration:")
        logger.info(f"  URL: {MONGODB_URL}")
        logger.info(f"  Database: {MONGODB_DB_NAME}")
        logger.info("")
        
        # Tester la connexion
        logger.info("Test de connexion...")
        await connect_to_mongo()
        logger.info("  OK: Connexion reussie")
        logger.info("")
        
        # Obtenir la base de données
        db = get_database()
        
        # Lister les collections
        collections = await db.list_collection_names()
        
        logger.info("Collections MongoDB:")
        logger.info("-" * 60)
        
        if collections:
            for collection in sorted(collections):
                count = await db[collection].count_documents({})
                logger.info(f"  [OK] {collection:20} ({count} documents)")
            
            logger.info("")
            logger.info(f"Total: {len(collections)} collection(s)")
            
            # Vérifier les collections principales
            found_important = [c for c in EXPECTED_MONGO_COLLECTIONS if c in collections]
            missing_important = [c for c in EXPECTED_MONGO_COLLECTIONS if c not in collections]
            
            if found_important:
                logger.info("")
                logger.info("Collections importantes presentes:")
                for collection in found_important:
                    logger.info(f"  [OK] {collection}")
            
            if missing_important:
                logger.warning("")
                logger.warning("Collections importantes manquantes (seront creees automatiquement):")
                for collection in missing_important:
                    logger.warning(f"  - {collection}")
            
            logger.info("")
            logger.info("OK: MongoDB fonctionne correctement!")
            
            # Fermer la connexion
            await close_mongo_connection()
            return True
        else:
            logger.warning("Aucune collection trouvee (normal si la base est vide)")
            logger.info("  Les collections seront creees automatiquement lors de l'utilisation")
            await close_mongo_connection()
            return True
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"ERREUR: {error_msg}")
        
        if "could not connect" in error_msg.lower() or "connection refused" in error_msg.lower():
            logger.error("  Impossible de se connecter a MongoDB")
            logger.error("  Verifiez que MongoDB est demarre")
            logger.error("  Windows: net start MongoDB")
        elif "authentication failed" in error_msg.lower():
            logger.error("  Probleme d'authentification MongoDB")
            logger.error("  Verifiez MONGODB_URL dans .env")
        
        return False

def verify_configuration():
    """Vérifie la configuration"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("VERIFICATION CONFIGURATION")
    logger.info("=" * 60)
    
    issues = []
    
    # Vérifier PostgreSQL
    if not settings.postgres_user:
        issues.append("POSTGRES_USER non configure")
    if not settings.postgres_db:
        issues.append("POSTGRES_DB non configure")
    
    # Vérifier MongoDB
    if not settings.mongodb_url:
        issues.append("MONGODB_URL non configure")
    if not settings.mongodb_db_name:
        issues.append("MONGODB_DB_NAME non configure")
    
    if issues:
        logger.error("Problemes de configuration:")
        for issue in issues:
            logger.error(f"  - {issue}")
        return False
    else:
        logger.info("OK: Configuration complete")
        return True

def main():
    """Fonction principale"""
    logger.info("")
    logger.info("=" * 60)
    logger.info("VERIFICATION COMPLETE DES BASES DE DONNEES")
    logger.info("=" * 60)
    logger.info("")
    
    results = {
        'config': False,
        'postgres': False,
        'mongodb': False,
        'redis': False
    }
    
    # Vérifier la configuration
    results['config'] = verify_configuration()
    
    # Vérifier PostgreSQL
    results['postgres'] = verify_postgresql()
    
    # Vérifier MongoDB
    results['mongodb'] = asyncio.run(verify_mongodb())
    
    # Vérifier Redis
    results['redis'] = asyncio.run(verify_redis())
    
    # Résumé final
    logger.info("")
    logger.info("=" * 60)
    logger.info("RESUME")
    logger.info("=" * 60)
    logger.info("")
    
    logger.info(f"Configuration:     {'[OK]' if results['config'] else '[ERREUR]'}")
    logger.info(f"PostgreSQL:        {'[OK]' if results['postgres'] else '[ERREUR]'}")
    logger.info(f"MongoDB:           {'[OK]' if results['mongodb'] else '[ERREUR]'}")
    logger.info(f"Redis:             {'[OK]' if results['redis'] else '[ERREUR]'}")
    logger.info("")
    
    # Redis est optionnel mais recommandé
    critical_results = {k: v for k, v in results.items() if k != 'redis'}
    
    if all(critical_results.values()):
        logger.info("=" * 60)
        if results['redis']:
            logger.info("SUCCES: Toutes les bases de donnees sont configurees!")
        else:
            logger.info("SUCCES: Bases de donnees principales configurees!")
            logger.info("  (Redis optionnel - Cache desactive mais application fonctionnelle)")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Tables PostgreSQL:")
        for table in EXPECTED_POSTGRES_TABLES:
            logger.info(f"  - {table}")
        logger.info("")
        if results['redis']:
            logger.info("Redis: Cache active - Performance optimale")
        else:
            logger.info("Redis: Non configure - Cache desactive")
        logger.info("")
        logger.info("Vous pouvez maintenant demarrer l'application:")
        logger.info("  .\\demarrer-backend.bat")
        return 0
    else:
        logger.error("=" * 60)
        logger.error("ERREUR: Certaines verifications ont echoue")
        logger.error("=" * 60)
        logger.error("")
        logger.error("Corrigez les problemes ci-dessus avant de continuer")
        return 1

if __name__ == "__main__":
    sys.exit(main())
