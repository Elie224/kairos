"""
Script pour supprimer les modules non souhaités
Garde uniquement :
- Informatique : Machine Learning et modules liés
- Mathématiques : Algèbre et Probabilités
"""
import sys
import os
import asyncio
import argparse
from bson import ObjectId

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, get_database, close_mongo_connection
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Modules à GARDER (par titre, insensible à la casse)
COMPUTER_SCIENCE_KEEP = [
    "machine learning"  # Uniquement Machine Learning pour l'informatique
]

MATHEMATICS_KEEP = [
    "algèbre",
    "probabilités",
    "statistiques"
]

async def should_keep_module(module: dict) -> bool:
    """Détermine si un module doit être conservé"""
    subject = module.get("subject", "").lower()
    title = module.get("title", "").lower()
    
    # Informatique : garder uniquement Machine Learning et modules liés
    if subject == "computer_science":
        for keep_term in COMPUTER_SCIENCE_KEEP:
            if keep_term in title:
                return True
        return False
    
    # Mathématiques : garder uniquement Algèbre et Probabilités
    if subject == "mathematics":
        for keep_term in MATHEMATICS_KEEP:
            if keep_term in title:
                return True
        return False
    
    # Tous les autres sujets (chemistry, physics, english) : supprimer
    return False

async def delete_modules_filtered(confirm: bool = False):
    """Supprime les modules non souhaités"""
    try:
        await connect_to_mongo()
        db = get_database()
        
        # Récupérer tous les modules
        all_modules = await db.modules.find({}).to_list(length=None)
        logger.info(f"\n{'='*80}")
        logger.info(f"TOTAL: {len(all_modules)} modules trouvés")
        logger.info(f"{'='*80}\n")
        
        # Séparer les modules à garder et à supprimer
        to_keep = []
        to_delete = []
        
        for module in all_modules:
            if await should_keep_module(module):
                to_keep.append(module)
            else:
                to_delete.append(module)
        
        logger.info(f"📦 Modules à CONSERVER: {len(to_keep)}")
        logger.info(f"🗑️  Modules à SUPPRIMER: {len(to_delete)}\n")
        
        # Afficher les modules à garder
        if to_keep:
            logger.info("=" * 80)
            logger.info("MODULES À CONSERVER:")
            logger.info("=" * 80)
            for module in to_keep:
                subject = module.get("subject", "unknown")
                title = module.get("title", "Sans titre")
                module_id = str(module.get("_id", "unknown"))
                logger.info(f"  [{subject.upper():15}] {title} (ID: {module_id[:8]}...)")
        
        # Afficher les modules à supprimer (premiers 20)
        if to_delete:
            logger.info("\n" + "=" * 80)
            logger.info("MODULES À SUPPRIMER (premiers 20):")
            logger.info("=" * 80)
            for module in to_delete[:20]:
                subject = module.get("subject", "unknown")
                title = module.get("title", "Sans titre")
                module_id = str(module.get("_id", "unknown"))
                logger.info(f"  [{subject.upper():15}] {title} (ID: {module_id[:8]}...)")
            if len(to_delete) > 20:
                logger.info(f"  ... et {len(to_delete) - 20} autres modules")
        
        if not confirm:
            logger.info("\n" + "=" * 80)
            logger.warning("⚠️  MODE PRÉVISUALISATION - Aucune suppression effectuée")
            logger.info("=" * 80)
            logger.info("Pour confirmer la suppression, utilisez: --confirm")
            return
        
        # Confirmation
        logger.info("\n" + "=" * 80)
        logger.warning(f"⚠️  SUPPRESSION DE {len(to_delete)} MODULE(S)")
        logger.info("=" * 80)
        
        # Supprimer les modules
        deleted_count = 0
        for module in to_delete:
            try:
                module_id = module.get("_id")
                result = await db.modules.delete_one({"_id": module_id})
                if result.deleted_count > 0:
                    deleted_count += 1
                    logger.info(f"  ✅ Supprimé: {module.get('title', 'Sans titre')}")
            except Exception as e:
                logger.error(f"  ❌ Erreur lors de la suppression de {module.get('title', 'Sans titre')}: {e}")
        
        logger.info("\n" + "=" * 80)
        logger.info(f"✅ SUPPRESSION TERMINÉE")
        logger.info(f"   Modules supprimés: {deleted_count}/{len(to_delete)}")
        logger.info(f"   Modules conservés: {len(to_keep)}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        raise
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supprimer les modules non souhaités")
    parser.add_argument("--confirm", action="store_true", help="Confirmer la suppression")
    args = parser.parse_args()
    
    asyncio.run(delete_modules_filtered(confirm=args.confirm))
