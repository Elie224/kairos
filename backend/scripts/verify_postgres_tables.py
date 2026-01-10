"""
Script pour vérifier les tables PostgreSQL créées
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from sqlalchemy import create_engine, text, inspect
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importer les settings
from app.config import settings

# Configuration PostgreSQL
POSTGRES_USER = settings.postgres_user
POSTGRES_PASSWORD = settings.postgres_password
POSTGRES_HOST = settings.postgres_host
POSTGRES_PORT = settings.postgres_port
POSTGRES_DB = settings.postgres_db

# Forcer l'encodage UTF-8
os.environ['PGCLIENTENCODING'] = 'UTF8'

def verify_tables():
    """Vérifie les tables PostgreSQL"""
    try:
        logger.info("Connexion a PostgreSQL...")
        logger.info(f"Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
        logger.info(f"Database: {POSTGRES_DB}")
        logger.info(f"User: {POSTGRES_USER}")
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
        with engine.connect() as conn:
            # Vérifier la version PostgreSQL
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            logger.info(f"Version PostgreSQL: {version.split(',')[0]}")
            logger.info("")
            
            # Lister les tables
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            logger.info("=" * 50)
            logger.info("TABLES DANS LA BASE DE DONNEES:")
            logger.info("=" * 50)
            
            if tables:
                for i, table in enumerate(tables, 1):
                    logger.info(f"{i}. {table}")
                    
                    # Afficher les colonnes de chaque table
                    columns = inspector.get_columns(table)
                    logger.info(f"   Colonnes ({len(columns)}):")
                    for col in columns:
                        logger.info(f"      - {col['name']} ({col['type']})")
                    logger.info("")
                
                logger.info(f"Total: {len(tables)} table(s)")
                
                # Vérifier les tables attendues
                expected_tables = ['users', 'courses', 'modules', 'enrollments', 'user_progress']
                missing_tables = [t for t in expected_tables if t not in tables]
                
                if missing_tables:
                    logger.warning("")
                    logger.warning("ATTENTION: Tables manquantes:")
                    for table in missing_tables:
                        logger.warning(f"  - {table}")
                    logger.warning("")
                    logger.warning("Executez les migrations:")
                    logger.warning("  python scripts/migrate_postgres.py create")
                else:
                    logger.info("")
                    logger.info("OK: Toutes les tables attendues sont presentes!")
            else:
                logger.warning("AUCUNE TABLE TROUVEE!")
                logger.warning("")
                logger.warning("Les migrations n'ont pas ete executees.")
                logger.warning("Executez:")
                logger.warning("  python scripts/migrate_postgres.py create")
        
        return True
    except Exception as e:
        error_msg = str(e)
        logger.error(f"ERREUR: {error_msg}")
        
        if "password authentication failed" in error_msg.lower():
            logger.error("")
            logger.error("Probleme d'authentification PostgreSQL")
            logger.error("Verifiez le mot de passe dans .env")
        elif "could not connect" in error_msg.lower():
            logger.error("")
            logger.error("Impossible de se connecter a PostgreSQL")
            logger.error("Verifiez que PostgreSQL 18 est demarre")
        elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
            logger.error("")
            logger.error(f"La base de donnees '{POSTGRES_DB}' n'existe pas")
            logger.error("Creez-la avec: CREATE DATABASE eduverse;")
        
        return False

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("  VERIFICATION DES TABLES POSTGRESQL")
    logger.info("=" * 50)
    logger.info("")
    
    if verify_tables():
        logger.info("")
        logger.info("Verification terminee")
    else:
        logger.error("")
        logger.error("Verification echouee")
        sys.exit(1)
