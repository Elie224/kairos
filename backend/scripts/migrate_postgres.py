"""
Script de migration PostgreSQL pour Kaïros
Crée les tables nécessaires dans PostgreSQL
"""
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.migrations import create_tables, drop_tables
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Fonction principale"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            logger.info("🚀 Création des tables PostgreSQL...")
            try:
                create_tables()
                logger.info("✅ Migration terminée avec succès!")
            except Exception as e:
                logger.error(f"❌ Erreur lors de la migration: {e}")
                sys.exit(1)
        
        elif command == "drop":
            logger.warning("⚠️  ATTENTION: Vous allez supprimer toutes les tables PostgreSQL!")
            confirm = input("Tapez 'yes' pour confirmer: ")
            if confirm.lower() == "yes":
                try:
                    drop_tables()
                    logger.info("✅ Tables supprimées")
                except Exception as e:
                    logger.error(f"❌ Erreur lors de la suppression: {e}")
                    sys.exit(1)
            else:
                logger.info("Opération annulée")
        
        elif command == "reset":
            logger.warning("⚠️  ATTENTION: Vous allez supprimer et recréer toutes les tables!")
            confirm = input("Tapez 'yes' pour confirmer: ")
            if confirm.lower() == "yes":
                try:
                    drop_tables()
                    create_tables()
                    logger.info("✅ Reset terminé avec succès!")
                except Exception as e:
                    logger.error(f"❌ Erreur lors du reset: {e}")
                    sys.exit(1)
            else:
                logger.info("Opération annulée")
        
        else:
            print("Usage: python migrate_postgres.py [create|drop|reset]")
            sys.exit(1)
    else:
        # Par défaut, créer les tables
        logger.info("🚀 Création des tables PostgreSQL...")
        try:
            create_tables()
            logger.info("✅ Migration terminée avec succès!")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la migration: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()











