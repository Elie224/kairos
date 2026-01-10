"""
Package database pour PostgreSQL et MongoDB
"""
import sys
import os
import importlib.util

# Charger directement le fichier database.py depuis le répertoire parent
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
database_file = os.path.join(parent_dir, 'database.py')

if os.path.exists(database_file):
    spec = importlib.util.spec_from_file_location("app.database_mongo", database_file)
    mongo_db = importlib.util.module_from_spec(spec)
    sys.modules["app.database_mongo"] = mongo_db
    spec.loader.exec_module(mongo_db)
    
    # Réexporter les fonctions MongoDB
    connect_to_mongo = mongo_db.connect_to_mongo
    close_mongo_connection = mongo_db.close_mongo_connection
    get_database = mongo_db.get_database
    db = mongo_db.db
else:
    raise ImportError(f"Fichier database.py introuvable: {database_file}")

# Exporter aussi les modules PostgreSQL
try:
    from app.database.postgres import init_postgres, engine, get_postgres_session, SessionLocal, Base
except ImportError as e:
    # PostgreSQL est optionnel
    logger = logging.getLogger(__name__)
    logger.warning(f"PostgreSQL non disponible: {e}")
    init_postgres = None
    engine = None
    get_postgres_session = None
    SessionLocal = None
    Base = None

