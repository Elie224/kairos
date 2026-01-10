"""
Script pour configurer l'encodage UTF-8 dans PostgreSQL via Python
Évite les problèmes d'authentification avec psql
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

def configure_encoding():
    """Configure l'encodage UTF-8 sur la base de données via Python"""
    try:
        logger.info("Configuration de l'encodage UTF-8 via Python...")
        logger.info(f"Connexion à PostgreSQL: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
        
        # Créer une URL de connexion
        if POSTGRES_PASSWORD:
            encoded_password = quote_plus(POSTGRES_PASSWORD)
            url = f"postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        else:
            url = f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        
        # Créer un engine temporaire pour configurer l'encodage
        # Utiliser connect_args pour gérer l'encodage dès la connexion
        temp_engine = create_engine(
            url,
            pool_pre_ping=True,
            echo=False,
            connect_args={
                "client_encoding": "UTF8"
            },
            # Utiliser un pool minimal pour cette opération
            pool_size=1,
            max_overflow=0
        )
        
        logger.info("Tentative de connexion...")
        
        # Configurer l'encodage
        with temp_engine.connect() as conn:
            # Définir l'encodage pour cette session
            logger.info("Configuration de l'encodage pour la session...")
            conn.execute(text("SET client_encoding TO 'UTF8';"))
            conn.commit()
            
            # Configurer l'encodage par défaut pour la base de données
            logger.info(f"Configuration de l'encodage par défaut pour la base '{POSTGRES_DB}'...")
            conn.execute(text(f"ALTER DATABASE {POSTGRES_DB} SET client_encoding = 'UTF8';"))
            conn.commit()
            
            # Vérifier l'encodage
            result = conn.execute(text("SHOW client_encoding;"))
            encoding = result.fetchone()[0]
            logger.info(f"Encodage actuel: {encoding}")
        
        logger.info("✅ Encodage UTF-8 configuré avec succès")
        return True
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Erreur lors de la configuration de l'encodage: {error_msg}")
        
        if "password authentication failed" in error_msg.lower():
            logger.error("")
            logger.error("🔐 Problème d'authentification PostgreSQL")
            logger.error("   Le mot de passe dans .env ne correspond pas au mot de passe PostgreSQL")
            logger.error("")
            logger.error("Solutions:")
            logger.error("   1. Vérifiez le mot de passe dans .env")
            logger.error("   2. Utilisez pgAdmin pour configurer l'encodage:")
            logger.error("      - Ouvrez pgAdmin")
            logger.error("      - Clic droit sur 'eduverse' → Properties")
            logger.error("      - Variables → Ajoutez: client_encoding = UTF8")
            logger.error("   3. Ou réinitialisez le mot de passe PostgreSQL")
        elif "could not connect" in error_msg.lower():
            logger.error("")
            logger.error("🔌 Problème de connexion PostgreSQL")
            logger.error("   Vérifiez que PostgreSQL 18 est démarré")
        else:
            logger.error("")
            logger.error("   Essayez de configurer l'encodage manuellement via pgAdmin")
        
        return False

if __name__ == "__main__":
    logger.info("========================================")
    logger.info("  Configuration Encodage PostgreSQL")
    logger.info("========================================")
    logger.info("")
    
    if configure_encoding():
        logger.info("")
        logger.info("✅ Configuration terminée avec succès!")
        logger.info("   Vous pouvez maintenant exécuter les migrations:")
        logger.info("   python scripts/migrate_postgres.py create")
        sys.exit(0)
    else:
        logger.error("")
        logger.error("❌ Configuration échouée")
        logger.error("   Consultez les messages ci-dessus pour plus de détails")
        sys.exit(1)
