"""
Configuration MongoDB avec Motor (async)
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def connect_to_mongo():
    """Connexion à MongoDB"""
    try:
        logger.info(f"Tentative de connexion à MongoDB: {settings.mongodb_url}")
        # Optimisations de performance pour MongoDB
        timeout_ms = getattr(settings, 'mongodb_timeout_ms', 5000)
        # Optimisations pour supporter des milliers d'utilisateurs simultanés
        # maxPoolSize augmenté pour gérer plus de connexions concurrentes
        # minPoolSize augmenté pour maintenir plus de connexions actives
        max_pool_size = getattr(settings, 'mongodb_max_pool_size', 200)
        min_pool_size = getattr(settings, 'mongodb_min_pool_size', 20)
        
        db.client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=timeout_ms,
            maxPoolSize=max_pool_size,  # Pool de connexions configurable
            minPoolSize=min_pool_size,  # Maintenir plus de connexions actives
            maxIdleTimeMS=60000,  # Fermer les connexions inactives après 60s (augmenté)
            connectTimeoutMS=10000,  # Timeout de connexion
            socketTimeoutMS=30000,  # Timeout socket
            retryWrites=True,  # Réessayer les écritures en cas d'erreur
            retryReads=True,  # Réessayer les lectures en cas d'erreur
            # Optimisations supplémentaires pour performance
            waitQueueTimeoutMS=5000,  # Timeout pour attendre une connexion du pool
            heartbeatFrequencyMS=10000,  # Fréquence de heartbeat (10s)
            # Compression pour réduire la bande passante
            compressors=['snappy', 'zlib'],  # Compression des données
            zlibCompressionLevel=6  # Niveau de compression zlib (équilibré)
        )
        db.database = db.client[settings.mongodb_db_name]
        logger.info("Connexion à MongoDB établie")
        # Test de connexion
        await db.client.admin.command('ping')
        logger.info("MongoDB ping réussi")
        
        # Créer les collections et index si nécessaire (sans bloquer si ça échoue)
        try:
            await ensure_collections_and_indexes()
        except Exception as init_error:
            logger.warning(f"Erreur lors de l'initialisation des collections/index: {init_error}")
            logger.warning("Les collections seront créées automatiquement lors du premier insert")
    except Exception as e:
        error_msg = f"Erreur de connexion à MongoDB: {e}"
        logger.error(error_msg)
        logger.error("Assurez-vous que MongoDB est démarré et accessible")
        raise ConnectionError(f"Impossible de se connecter à MongoDB. Vérifiez que MongoDB est démarré. Erreur: {str(e)}")

async def ensure_collections_and_indexes():
    """S'assure que les collections et index existent"""
    if db.database is None:
        return
    
    collections = await db.database.list_collection_names()
    
    # Créer les collections si elles n'existent pas
    if "users" not in collections:
        await db.database.create_collection("users")
        logger.info("Collection 'users' créée")
    
    if "modules" not in collections:
        await db.database.create_collection("modules")
        logger.info("Collection 'modules' créée")
    
    if "progress" not in collections:
        await db.database.create_collection("progress")
        logger.info("Collection 'progress' créée")
    
    if "password_resets" not in collections:
        await db.database.create_collection("password_resets")
        logger.info("Collection 'password_resets' créée")
    
    if "support_messages" not in collections:
        await db.database.create_collection("support_messages")
        logger.info("Collection 'support_messages' créée")
    
    # Créer les index (ignorer les erreurs si les index existent déjà)
    try:
        await db.database.users.create_index("email", unique=True)
        logger.info("Index unique créé sur 'users.email'")
    except Exception:
        pass  # Index existe déjà
    
    try:
        await db.database.users.create_index("username", unique=True)
        logger.info("Index unique créé sur 'users.username'")
    except Exception:
        pass  # Index existe déjà
    
    try:
        await db.database.modules.create_index("subject")
        logger.info("Index créé sur 'modules.subject'")
    except Exception:
        pass
    
    try:
        await db.database.modules.create_index("difficulty")
        logger.info("Index créé sur 'modules.difficulty'")
    except Exception:
        pass
    
    # Index composé pour les requêtes fréquentes (subject + difficulty + created_at)
    try:
        await db.database.modules.create_index([("subject", 1), ("difficulty", 1), ("created_at", -1)])
        logger.info("Index composé créé sur 'modules(subject, difficulty, created_at)'")
    except Exception:
        pass
    
    # Index de texte pour la recherche (titre et description)
    try:
        await db.database.modules.create_index([("title", "text"), ("description", "text")])
        logger.info("Index de texte créé sur 'modules(title, description)'")
    except Exception:
        pass
    
    # Index sur created_at pour le tri rapide
    try:
        await db.database.modules.create_index("created_at")
        logger.info("Index créé sur 'modules.created_at'")
    except Exception:
        pass
    
    try:
        await db.database.progress.create_index([("user_id", 1), ("module_id", 1)], unique=True)
        logger.info("Index composé unique créé sur 'progress(user_id, module_id)'")
    except Exception:
        pass
    
    # Index sur user_id pour les requêtes de progression
    try:
        await db.database.progress.create_index("user_id")
        logger.info("Index créé sur 'progress.user_id'")
    except Exception:
        pass
    
    # Index sur started_at pour le tri
    try:
        await db.database.progress.create_index("started_at")
        logger.info("Index créé sur 'progress.started_at'")
    except Exception:
        pass
    
    # Index pour les examens
    try:
        await db.database.exams.create_index("module_id")
        logger.info("Index créé sur 'exams.module_id'")
    except Exception:
        pass
    
    try:
        await db.database.exam_attempts.create_index([("user_id", 1), ("module_id", 1)])
        logger.info("Index composé créé sur 'exam_attempts(user_id, module_id)'")
    except Exception:
        pass
    
    # Index pour les quiz
    try:
        await db.database.quizzes.create_index("module_id", unique=True)
        logger.info("Index unique créé sur 'quizzes.module_id'")
    except Exception:
        pass
    
    try:
        await db.database.quizzes.create_index("created_at")
        logger.info("Index créé sur 'quizzes.created_at'")
    except Exception:
        pass
    
    # Index pour les tentatives de quiz
    try:
        await db.database.quiz_attempts.create_index([("user_id", 1), ("module_id", 1)])
        logger.info("Index composé créé sur 'quiz_attempts(user_id, module_id)'")
    except Exception:
        pass
    
    try:
        await db.database.quiz_attempts.create_index("completed_at")
        logger.info("Index créé sur 'quiz_attempts.completed_at'")
    except Exception:
        pass
    
    try:
        await db.database.quiz_attempts.create_index([("user_id", 1), ("completed_at", -1)])
        logger.info("Index composé créé sur 'quiz_attempts(user_id, completed_at)'")
    except Exception:
        pass
    
    # Index pour les validations
    try:
        await db.database.module_validations.create_index([("user_id", 1), ("module_id", 1)])
        logger.info("Index composé créé sur 'module_validations(user_id, module_id)'")
    except Exception:
        pass
    
    # Index pour TD et TP
    try:
        await db.database.tds.create_index("module_id")
        logger.info("Index créé sur 'tds.module_id'")
    except Exception:
        pass
    
    try:
        await db.database.tps.create_index("module_id")
        logger.info("Index créé sur 'tps.module_id'")
    except Exception:
        pass
    
    # Index pour learning_profiles (profils d'apprentissage adaptatif)
    try:
        await db.database.learning_profiles.create_index("user_id", unique=True)
        logger.info("Index unique créé sur 'learning_profiles.user_id'")
    except Exception:
        pass
    
    try:
        await db.database.learning_profiles.create_index("current_level")
        logger.info("Index créé sur 'learning_profiles.current_level'")
    except Exception:
        pass
    
    # Index pour pathways (parcours d'apprentissage)
    try:
        await db.database.pathways.create_index("subject")
        logger.info("Index créé sur 'pathways.subject'")
    except Exception:
        pass
    
    try:
        await db.database.pathways.create_index("status")
        logger.info("Index créé sur 'pathways.status'")
    except Exception:
        pass
    
    try:
        await db.database.pathways.create_index("created_by")
        logger.info("Index créé sur 'pathways.created_by'")
    except Exception:
        pass
    
    # Index pour subscriptions (abonnements)
    try:
        await db.database.subscriptions.create_index("user_id")
        logger.info("Index créé sur 'subscriptions.user_id'")
    except Exception:
        pass
    
    try:
        await db.database.subscriptions.create_index("stripe_subscription_id", unique=True)
        logger.info("Index unique créé sur 'subscriptions.stripe_subscription_id'")
    except Exception:
        pass
    
    try:
        await db.database.subscriptions.create_index("status")
        logger.info("Index créé sur 'subscriptions.status'")
    except Exception:
        pass
    
    # Index pour ai_requests (comptage requêtes IA)
    try:
        await db.database.ai_requests.create_index([("user_id", 1), ("created_at", -1)])
        logger.info("Index créé sur 'ai_requests(user_id, created_at)'")
    except Exception:
        pass
    
    # Index pour ai_usage (Cost Guard - suivi des coûts)
    try:
        await db.database.ai_usage.create_index([("user_id", 1), ("created_at", 1)])
        await db.database.ai_usage.create_index("created_at")
        logger.info("Indexes créés sur 'ai_usage.user_id' et 'ai_usage.created_at'")
    except Exception:
        pass
    
    # Index pour user_history (historique utilisateur)
    try:
        await db.database.user_history.create_index([("user_id", 1), ("created_at", -1)])
        await db.database.user_history.create_index([("user_id", 1), ("subject", 1)])
        await db.database.user_history.create_index([("user_id", 1), ("module_id", 1)])
        # Index textuel pour recherche de similarité
        await db.database.user_history.create_index([("question", "text")])
        logger.info("Indexes créés sur 'user_history'")
    except Exception:
        pass
    
    # Index pour gdpr_logs
    try:
        await db.database.gdpr_logs.create_index("user_id")
        logger.info("Index créé sur 'gdpr_logs.user_id'")
    except Exception:
        pass
    
    # Index pour password_resets avec TTL (expiration automatique après 1 heure)
    try:
        await db.database.password_resets.create_index("expires_at", expireAfterSeconds=0)
        logger.info("Index TTL créé sur 'password_resets.expires_at'")
    except Exception:
        pass
    
    try:
        await db.database.password_resets.create_index("token", unique=True)
        logger.info("Index unique créé sur 'password_resets.token'")
    except Exception:
        pass

async def close_mongo_connection():
    """Fermeture de la connexion MongoDB"""
    if db.client:
        db.client.close()
        logger.info("Connexion MongoDB fermée")

def get_database():
    """Retourne la base de données"""
    if db.database is None:
        logger.error("Base de données non initialisée. Vérifiez que MongoDB est démarré et que la connexion a réussi.")
        # Lever une exception pour que les repositories puissent la gérer
        raise ConnectionError("Base de données non initialisée. Vérifiez que MongoDB est démarré et que la connexion a réussi.")
    return db.database

