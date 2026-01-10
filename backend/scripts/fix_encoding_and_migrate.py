"""
Script pour configurer l'encodage UTF-8 et exécuter les migrations PostgreSQL
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from sqlalchemy import create_engine, text
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

# Forcer l'encodage UTF-8 pour l'environnement
os.environ['PGCLIENTENCODING'] = 'UTF8'

def fix_encoding():
    """Configure l'encodage UTF-8 sur la base de données"""
    try:
        logger.info("Configuration de l'encodage UTF-8...")
        
        # Créer une URL de connexion simple
        if POSTGRES_PASSWORD:
            encoded_password = quote_plus(POSTGRES_PASSWORD)
            url = f"postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        else:
            url = f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        
        # Créer un engine temporaire pour configurer l'encodage
        temp_engine = create_engine(
            url,
            pool_pre_ping=True,
            echo=False,
            connect_args={
                "client_encoding": "UTF8"
            }
        )
        
        # Configurer l'encodage
        with temp_engine.connect() as conn:
            # Définir l'encodage pour cette session
            conn.execute(text("SET client_encoding TO 'UTF8';"))
            # Configurer l'encodage par défaut pour la base de données
            conn.execute(text(f"ALTER DATABASE {POSTGRES_DB} SET client_encoding = 'UTF8';"))
            conn.commit()
        
        logger.info("✅ Encodage UTF-8 configuré avec succès")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Impossible de configurer l'encodage automatiquement: {e}")
        logger.info("   Vous devrez le configurer manuellement dans PostgreSQL")
        return False

def run_migrations():
    """Exécute les migrations PostgreSQL"""
    try:
        logger.info("🚀 Exécution des migrations PostgreSQL...")
        
        # Importer les modules de migration
        from app.database.migrations import create_tables
        
        # Exécuter les migrations
        create_tables()
        
        logger.info("✅ Migrations terminées avec succès!")
        return True
    except Exception as e:
        logger.error(f"❌ Erreur lors des migrations: {e}")
        return False

if __name__ == "__main__":
    logger.info("========================================")
    logger.info("  Configuration et Migration PostgreSQL")
    logger.info("========================================")
    logger.info("")
    
    # Étape 1 : Configurer l'encodage
    fix_encoding()
    
    logger.info("")
    
    # Étape 2 : Exécuter les migrations
    if run_migrations():
        logger.info("")
        logger.info("✅ Toutes les tables PostgreSQL ont été créées avec succès!")
        logger.info("")
        logger.info("Tables créées:")
        logger.info("  - users")
        logger.info("  - courses")
        logger.info("  - modules")
        logger.info("  - enrollments")
        logger.info("  - user_progress")
        sys.exit(0)
    else:
        logger.error("")
        logger.error("❌ Les migrations ont échoué")
        logger.error("   Vérifiez les logs ci-dessus pour plus de détails")
        sys.exit(1)
