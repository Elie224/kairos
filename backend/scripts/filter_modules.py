"""
Script pour lister tous les modules et identifier ceux à supprimer
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, get_database, close_mongo_connection
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def list_all_modules():
    """Liste tous les modules avec leurs détails"""
    try:
        await connect_to_mongo()
        db = get_database()
        
        modules = await db.modules.find({}).to_list(length=None)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"TOTAL: {len(modules)} modules trouvés")
        logger.info(f"{'='*80}\n")
        
        # Grouper par sujet
        by_subject = {}
        for module in modules:
            subject = module.get("subject", "unknown")
            title = module.get("title", "Sans titre")
            module_id = str(module.get("_id", "unknown"))
            
            if subject not in by_subject:
                by_subject[subject] = []
            
            by_subject[subject].append({
                "id": module_id,
                "title": title,
                "difficulty": module.get("difficulty", "unknown")
            })
        
        # Afficher par sujet
        for subject, mods in sorted(by_subject.items()):
            logger.info(f"\n{subject.upper()}: {len(mods)} module(s)")
            logger.info("-" * 80)
            for mod in mods:
                logger.info(f"  [{mod['id'][:8]}...] {mod['title']} ({mod['difficulty']})")
        
        return modules
        
    except Exception as e:
        logger.error(f"Erreur: {e}", exc_info=True)
        return []
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(list_all_modules())
