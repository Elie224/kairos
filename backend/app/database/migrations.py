"""
Script de migration PostgreSQL pour créer les tables
"""
from app.database.postgres import Base, engine
from app.models.postgres_models import User, Course, Module, Enrollment, UserProgress
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


def create_tables():
    """Crée toutes les tables PostgreSQL"""
    try:
        logger.info("Création des tables PostgreSQL...")
        
        # Tester la connexion d'abord avec gestion d'encodage
        with engine.connect() as conn:
            # Définir l'encodage explicitement
            conn.execute(text("SET client_encoding TO 'UTF8';"))
            # Tester la connexion
            result = conn.execute(text("SELECT 1;"))
            result.fetchone()
        
        # Créer les tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables PostgreSQL créées avec succès")
        return True
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Erreur lors de la création des tables PostgreSQL: {error_msg}")
        
        # Gérer spécifiquement les erreurs d'encodage
        if "codec" in error_msg.lower() or "encoding" in error_msg.lower():
            logger.error("   Problème d'encodage détecté. Vérifiez:")
            logger.error("   1. Que la base de données 'eduverse' est créée avec ENCODING = 'UTF8'")
            logger.error("   2. Que PostgreSQL utilise l'encodage UTF-8")
            logger.error("   3. Exécutez: ALTER DATABASE eduverse SET client_encoding = 'UTF8';")
        
        raise


def drop_tables():
    """Supprime toutes les tables PostgreSQL (ATTENTION: supprime toutes les données)"""
    try:
        # Importer ici pour éviter les erreurs circulaires
        from app.database.postgres import Base, engine
        from app.models.postgres_models import User, Course, Module, Enrollment, UserProgress
        
        logger.warning("⚠️  Suppression de toutes les tables PostgreSQL...")
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Tables PostgreSQL supprimées")
        return True
    except ImportError as e:
        logger.error(f"❌ Erreur d'import PostgreSQL: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Erreur lors de la suppression des tables: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        print("⚠️  ATTENTION: Vous allez supprimer toutes les tables PostgreSQL!")
        confirm = input("Tapez 'yes' pour confirmer: ")
        if confirm.lower() == "yes":
            drop_tables()
        else:
            print("Opération annulée")
    else:
        create_tables()

