"""
Package database pour PostgreSQL et MongoDB
"""
import logging

logger = logging.getLogger(__name__)

# Importer MongoDB depuis mongo.py
from app.database.mongo import (
    connect_to_mongo,
    close_mongo_connection,
    get_database,
    db,
    Database
)

# Exporter aussi les modules PostgreSQL
try:
    from app.database.postgres import init_postgres, engine, get_postgres_session, SessionLocal, Base
except (ImportError, Exception) as e:
    # PostgreSQL est optionnel
    logger.info(f"ℹ️  PostgreSQL non disponible: {e}")
    init_postgres = None
    engine = None
    get_postgres_session = None
    SessionLocal = None
    Base = None

