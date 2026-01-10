"""
Script pour supprimer TOUTES les données utilisateur de la base de données
ATTENTION: Cette opération est irréversible !
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import connect_to_mongo, get_database, close_mongo_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def delete_all_user_data():
    """Supprime toutes les données utilisateur"""
    try:
        await connect_to_mongo()
        db = get_database()
        
        # Supprimer tous les utilisateurs
        user_result = await db.users.delete_many({})
        print(f"[OK] {user_result.deleted_count} utilisateur(s) supprime(s)")
        
        # Supprimer tous les tokens de réinitialisation
        reset_result = await db.password_resets.delete_many({})
        print(f"[OK] {reset_result.deleted_count} token(s) de reinitialisation supprime(s)")
        
        # Supprimer toutes les progressions
        progress_result = await db.progress.delete_many({})
        print(f"[OK] {progress_result.deleted_count} progression(s) supprimee(s)")
        
        # Supprimer tous les profils d'apprentissage
        profile_result = await db.learning_profiles.delete_many({})
        print(f"[OK] {profile_result.deleted_count} profil(s) d'apprentissage supprime(s)")
        
        # Supprimer tous les historiques utilisateur
        history_result = await db.user_history.delete_many({})
        print(f"[OK] {history_result.deleted_count} historique(s) utilisateur supprime(s)")
        
        # Supprimer tous les favoris
        favorites_result = await db.favorites.delete_many({})
        print(f"[OK] {favorites_result.deleted_count} favori(s) supprime(s)")
        
        # Supprimer toutes les tentatives de quiz
        quiz_attempts_result = await db.quiz_attempts.delete_many({})
        print(f"[OK] {quiz_attempts_result.deleted_count} tentative(s) de quiz supprimee(s)")
        
        # Supprimer toutes les tentatives d'examen
        exam_attempts_result = await db.exam_attempts.delete_many({})
        print(f"[OK] {exam_attempts_result.deleted_count} tentative(s) d'examen supprimee(s)")
        
        # Supprimer tous les abonnements
        subscriptions_result = await db.subscriptions.delete_many({})
        print(f"[OK] {subscriptions_result.deleted_count} abonnement(s) supprime(s)")
        
        # Supprimer tous les logs RGPD
        gdpr_result = await db.gdpr_logs.delete_many({})
        print(f"[OK] {gdpr_result.deleted_count} log(s) RGPD supprime(s)")
        
        print(f"\n[OK] Suppression complete terminee !")
        
    except Exception as e:
        logger.error(f"[ERREUR] Erreur lors de la suppression: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    print("=" * 50)
    print("  Suppression de TOUTES les donnees utilisateur")
    print("=" * 50)
    print()
    
    asyncio.run(delete_all_user_data())
    print("\n[OK] Termine !")
