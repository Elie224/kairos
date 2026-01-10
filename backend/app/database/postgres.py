"""
Configuration PostgreSQL pour données relationnelles
Cours, utilisateurs, relations, etc.
"""
from sqlalchemy import create_engine, MetaData, text, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Forcer l'encodage UTF-8 pour l'environnement Python
os.environ['PGCLIENTENCODING'] = 'UTF8'

# Configuration PostgreSQL (depuis settings qui charge automatiquement .env)
POSTGRES_USER = settings.postgres_user
POSTGRES_PASSWORD = settings.postgres_password
POSTGRES_HOST = settings.postgres_host
POSTGRES_PORT = settings.postgres_port
POSTGRES_DB = settings.postgres_db

# Vérifier si PostgreSQL est réellement configuré
# Sur Render, si POSTGRES_HOST n'est pas défini ou pointe vers localhost, PostgreSQL n'est pas disponible
# Détecter si on est sur Render (production déployée)
is_on_render = os.getenv("RENDER") == "true" or os.getenv("RENDER_EXTERNAL_HOSTNAME") is not None
is_production = settings.is_production or is_on_render

IS_POSTGRES_CONFIGURED = (
    POSTGRES_HOST and 
    POSTGRES_HOST.strip() and 
    POSTGRES_HOST.lower() not in ["localhost", "127.0.0.1"] and
    POSTGRES_USER and
    POSTGRES_DB
) or (
    # En développement local uniquement, permettre localhost si PostgreSQL est démarré
    not is_production and
    POSTGRES_HOST in ["localhost", "127.0.0.1"] and
    POSTGRES_USER and
    POSTGRES_DB
)

# URL de connexion PostgreSQL avec encodage UTF-8
# Gérer le cas où le mot de passe est vide et encoder correctement les caractères spéciaux
from urllib.parse import quote_plus

if IS_POSTGRES_CONFIGURED:
    if POSTGRES_PASSWORD:
        # Encoder le mot de passe pour gérer les caractères spéciaux
        encoded_password = quote_plus(POSTGRES_PASSWORD)
        POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    else:
        POSTGRES_URL = f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    # Engine avec pool de connexions pour scalabilité
    # Utiliser psycopg2 avec encodage UTF-8 explicite
    # On crée l'engine d'abord, puis on ajoute l'event listener
    try:
        engine = create_engine(
            POSTGRES_URL,
            poolclass=QueuePool,
            pool_size=20,  # Nombre de connexions dans le pool
            max_overflow=40,  # Connexions supplémentaires en cas de pic
            pool_pre_ping=True,  # Vérifier la santé des connexions
            pool_recycle=3600,  # Recycler les connexions après 1h
            echo=False,  # Désactiver les logs SQL en production
            connect_args={
                "client_encoding": "UTF8",
                "connect_timeout": 5  # Timeout de 5 secondes pour éviter de bloquer au démarrage
            }  # Forcer l'encodage UTF-8 dans les paramètres de connexion
        )
    except Exception as e:
        logger.warning(f"Impossible de créer l'engine PostgreSQL: {e}")
        logger.warning("PostgreSQL sera désactivé")
        IS_POSTGRES_CONFIGURED = False
        engine = None
else:
    logger.info("PostgreSQL non configuré - Host: localhost non autorisé en production")
    POSTGRES_URL = None
    engine = None

# Event listener pour configurer l'encodage après chaque connexion
if engine is not None:
    @event.listens_for(engine, "connect")
    def set_encoding(dbapi_conn, connection_record):
        """Configure l'encodage UTF-8 après chaque connexion"""
        try:
            # Utiliser execute directement sur la connexion
            with dbapi_conn.cursor() as cursor:
                cursor.execute("SET client_encoding TO 'UTF8';")
                dbapi_conn.commit()
        except Exception as e:
            # Ignorer les erreurs - l'encodage peut déjà être configuré
            logger.debug(f"Encodage peut déjà être configuré: {e}")
    
    # Session factory
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # Si PostgreSQL n'est pas configuré, créer des objets None/placeholder
    SessionLocal = None

# Base pour les modèles (toujours créer, même si engine est None)
Base = declarative_base()

# Metadata
metadata = MetaData()


def get_postgres_session():
    """Dependency pour obtenir une session PostgreSQL"""
    if not IS_POSTGRES_CONFIGURED or SessionLocal is None:
        raise RuntimeError("PostgreSQL n'est pas configuré ou disponible")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_postgres():
    """Initialise les tables PostgreSQL"""
    # Vérifier d'abord si PostgreSQL est configuré
    if not IS_POSTGRES_CONFIGURED:
        logger.info("PostgreSQL non configuré - Skipping initialization")
        logger.info(f"  POSTGRES_HOST={POSTGRES_HOST} (doit être différent de localhost en production)")
        logger.info(f"  POSTGRES_USER={POSTGRES_USER}")
        logger.info(f"  POSTGRES_DB={POSTGRES_DB}")
        logger.info("  Pour activer PostgreSQL sur Render, configurez POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB")
        return
    
    if engine is None:
        logger.warning("PostgreSQL engine non disponible - Skipping initialization")
        return
    
    try:
        # TESTER LA CONNEXION RÉELLE AVANT DE CONTINUER
        logger.info(f"Test de connexion PostgreSQL à {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}...")
        with engine.connect() as conn:
            # Test de connexion réel
            result = conn.execute(text("SELECT version();"))
            version_row = result.fetchone()
            if version_row:
                version = version_row[0]
                # Gérer l'encodage UTF-8 correctement
                try:
                    if isinstance(version, bytes):
                        version = version.decode('utf-8', errors='replace')
                    version_info = version.split(',')[0] if ',' in version else version
                    logger.info(f"Connexion PostgreSQL réussie - Version: {version_info}")
                except Exception as decode_error:
                    logger.warning(f"Erreur lors du décodage de la version PostgreSQL: {decode_error}")
                    logger.info("Connexion PostgreSQL réussie (version non lisible)")
            else:
                logger.info("Connexion PostgreSQL réussie")
        
        # Importer les modèles pour qu'ils soient enregistrés dans Base.metadata
        from app.models.postgres_models import User, Course, Module, Enrollment, UserProgress
        
        # Créer les tables seulement si la connexion fonctionne
        Base.metadata.create_all(bind=engine)
        logger.info("Tables PostgreSQL initialisées avec succès")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Erreur lors de l'initialisation PostgreSQL: {error_msg}")
        
        # Messages d'erreur plus détaillés selon le type d'erreur
        if "could not connect" in error_msg.lower() or "connection refused" in error_msg.lower():
            logger.error(f"❌ PostgreSQL n'est pas accessible à {POSTGRES_HOST}:{POSTGRES_PORT}")
            logger.error("   Vérifiez que PostgreSQL est démarré et accessible")
            logger.error("   Sur Render, utilisez un service PostgreSQL externe (par exemple: ElephantSQL, Supabase)")
        elif "database" in error_msg.lower() and "does not exist" in error_msg.lower():
            logger.error(f"❌ La base de données '{POSTGRES_DB}' n'existe pas")
            logger.error(f"   Créez-la avec: CREATE DATABASE {POSTGRES_DB};")
        elif "password authentication failed" in error_msg.lower():
            logger.error(f"❌ Authentification PostgreSQL échouée pour l'utilisateur '{POSTGRES_USER}'")
            logger.error("   Vérifiez POSTGRES_PASSWORD dans les variables d'environnement Render")
        else:
            logger.error(f"❌ Erreur PostgreSQL: {error_msg}")
        
        # Ne pas lever l'exception - PostgreSQL est optionnel, l'application continue avec MongoDB uniquement
        logger.warning("   L'application continuera avec MongoDB uniquement")
        logger.warning("   PostgreSQL est optionnel et n'est pas requis pour le fonctionnement de base")

