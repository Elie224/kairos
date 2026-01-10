"""
Kaïros Backend - API principale
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.database import connect_to_mongo, close_mongo_connection
try:
    from app.database.postgres import init_postgres
except ImportError:
    # PostgreSQL est optionnel
    init_postgres = None
try:
    from app.utils.cache import init_redis, close_redis
except ImportError:
    # Redis est optionnel
    init_redis = None
    close_redis = None
from app.routers import auth, modules, ai_tutor, progress, badges, favorites, recommendations, support, quiz, exam, validation, td, tp, adaptive_learning, pathways, exercise_generator, error_learning, analytics, anti_cheat, virtual_labs, avatar, gamification, collaboration, gdpr, subscriptions, prompt_router, user_history, resources, openai_content
from app.middleware.error_handler import (
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from app.middleware.security import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    SecurityLoggingMiddleware,
    AIRateLimitMiddleware
)
from app.middleware.request_size import RequestSizeLimitMiddleware
from app.middleware.registration_rate_limit import RegistrationRateLimitMiddleware
from app.middleware.performance import PerformanceMiddleware
from app.config import settings
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    mongo_connected = False
    try:
        logger.info("Connexion à MongoDB...")
        await connect_to_mongo()
        logger.info("Connexion MongoDB réussie")
        mongo_connected = True
    except Exception as e:
        logger.error(f"Erreur de connexion MongoDB: {e}")
        logger.error("L'application va démarrer mais MongoDB n'est pas disponible.")
        logger.error("Certaines fonctionnalités ne fonctionneront pas.")
        logger.error("Assurez-vous que MongoDB est démarré avant d'utiliser l'application.")
        # Ne pas arrêter l'application, mais logger l'erreur
        mongo_connected = False
    
    # Initialiser PostgreSQL pour données relationnelles (optionnel)
    postgres_connected = False
    if init_postgres:
        try:
            logger.info("Initialisation PostgreSQL...")
            init_postgres()
            postgres_connected = True
            logger.info("✅ PostgreSQL initialisé avec succès")
        except Exception as e:
            logger.warning(f"⚠️  PostgreSQL non disponible: {e}")
            logger.warning("   L'application continuera avec MongoDB uniquement")
            logger.warning("   Pour activer PostgreSQL:")
            logger.warning("   1. Démarrez PostgreSQL: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine")
            logger.warning("   2. Créez la base: CREATE DATABASE eduverse;")
            logger.warning("   3. Vérifiez les variables POSTGRES_* dans .env")
            postgres_connected = False
    else:
        logger.info("PostgreSQL désactivé - Utilisation MongoDB uniquement")
    
    # Initialiser Redis si disponible (optionnel mais recommandé pour la performance)
    redis_connected = False
    if init_redis:
        try:
            await init_redis(app)
            from app.utils.cache import get_redis
            redis = get_redis()
            if redis:
                await redis.ping()
                redis_connected = True
                logger.info("✅ Redis connecté - Cache activé (performance optimale)")
            else:
                logger.warning("⚠️  Redis non configuré ou connexion refusée")
                logger.warning("   Cache désactivé (performance réduite)")
                logger.warning("   Solutions:")
                logger.warning("   1. Démarrez Redis: docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine")
                logger.warning("   2. Vérifiez REDIS_URL dans .env: REDIS_URL=redis://localhost:6379/0")
                logger.warning("   3. Vérifiez que le port 6379 n'est pas bloqué par un firewall")
        except Exception as e:
            logger.warning(f"⚠️  Redis non disponible: {e}")
            logger.warning("   L'application fonctionnera sans cache (performance réduite)")
            logger.warning("   Consultez backend/DEMARRER_REDIS.md pour plus d'informations")
    else:
        logger.warning("⚠️  Redis non disponible - Cache désactivé")
        logger.warning("   Installez redis: pip install redis[hiredis]")
        logger.warning("   Configurez REDIS_URL dans .env")
    
    yield
    
    if mongo_connected:
        await close_mongo_connection()
    
    # Fermer Redis si disponible
    if close_redis:
        try:
            await close_redis()
        except Exception:
            pass
    
    logger.info("Application arrêtée")

app = FastAPI(
    title="Kaïros API",
    description="API pour la plateforme d'apprentissage immersif avec IA",
    version="1.0.0",
    lifespan=lifespan
)

# Middlewares de sécurité (ordre important - du plus général au plus spécifique)
# 0. Performance monitoring (en premier pour mesurer tout)
app.add_middleware(PerformanceMiddleware)

# 1. Compression GZip (en premier pour compresser toutes les réponses)
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compresser les réponses > 1KB

# 2. Logging de sécurité (en premier pour logger toutes les requêtes)
app.add_middleware(SecurityLoggingMiddleware)

# 2. Rate limiting général (protège contre les attaques brute force)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=settings.rate_limit_requests_per_minute,
    burst_size=settings.rate_limit_burst_size
)

# 3. Rate limiting spécifique pour les inscriptions (très restrictif)
app.add_middleware(
    RegistrationRateLimitMiddleware,
    registrations_per_hour=3,  # Maximum 3 inscriptions par heure par IP
    registrations_per_day=5    # Maximum 5 inscriptions par jour par IP
)

# 4. Rate limiting spécifique pour les endpoints IA (plus restrictif)
app.add_middleware(
    AIRateLimitMiddleware,
    requests_per_minute=settings.ai_rate_limit_per_minute,
    requests_per_hour=settings.ai_rate_limit_per_hour
)

# 5. Limite de taille des requêtes
app.add_middleware(RequestSizeLimitMiddleware)

# 6. En-têtes de sécurité HTTP
app.add_middleware(SecurityHeadersMiddleware)

# 7. Configuration CORS (dynamique selon l'environnement)
# En développement, autoriser localhost par défaut
# En production, utiliser ALLOWED_HOSTS depuis les variables d'environnement
if settings.is_production:
    # Gérer le cas spécial "*" (wildcard)
    if settings.allowed_hosts == ["*"]:
        # Pour "*", autoriser tous les domaines Render (solution pragmatique)
        # Note: On ne peut pas utiliser ["*"] avec allow_credentials=True dans FastAPI
        # Donc on autorise explicitement les domaines Render courants
        allowed_origins = [
            "https://kairos-frontend.onrender.com",
            "https://kairos-backend.onrender.com",
        ]
        # Ajouter le FRONTEND_URL s'il est défini
        if settings.frontend_url and settings.frontend_url != "http://localhost:5173":
            frontend_origin = settings.frontend_url.rstrip("/")
            if frontend_origin not in allowed_origins:
                allowed_origins.append(frontend_origin)
    else:
        allowed_origins = [
            f"https://{host.strip()}" if not host.startswith("http") else host.strip()
            for host in settings.allowed_hosts
            if host.strip() and host != "*"
        ]
        # Ajouter le FRONTEND_URL s'il est défini
        if settings.frontend_url and settings.frontend_url != "http://localhost:5173":
            frontend_origin = settings.frontend_url.rstrip("/")
            if frontend_origin not in allowed_origins:
                allowed_origins.append(frontend_origin)
else:
    # En développement, autoriser les ports locaux courants
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    # Ajouter les hosts personnalisés (sauf localhost qui est déjà là)
    if settings.allowed_hosts != ["*"]:
        allowed_origins.extend([
            f"http://{host.strip()}" if not host.startswith("http") else host.strip()
            for host in settings.allowed_hosts
            if host.strip() and host not in ["localhost", "127.0.0.1", "*"]
        ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Middleware pour capturer toutes les erreurs
from starlette.middleware.base import BaseHTTPMiddleware

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            # Ne pas intercepter les HTTPException, elles sont déjà gérées
            raise exc
        except Exception as exc:
            import traceback
            error_trace = traceback.format_exc()
            error_message = str(exc)
            
            logger.error(f"Exception capturée par middleware: {error_message}")
            logger.error(f"Traceback: {error_trace}")
            logger.error(f"URL: {request.url}")
            logger.error(f"Method: {request.method}")
            
            # Message d'erreur plus spécifique selon le type d'erreur
            if "MongoDB" in error_message or "Connection" in error_message or "database" in error_message.lower():
                detail_message = "Erreur de connexion à la base de données. Vérifiez que MongoDB est démarré et accessible."
            else:
                detail_message = f"Erreur serveur: {error_message}"
            
            try:
                # Créer une réponse JSON sans compression pour éviter les problèmes GZip
                return JSONResponse(
                    status_code=500,
                    content={"detail": detail_message},
                    headers={"Content-Encoding": "identity"}  # Désactiver la compression pour les erreurs
                )
            except Exception as json_error:
                logger.error(f"Erreur lors de la création de la réponse JSON: {json_error}")
                # Fallback: retourner une réponse texte simple
                from fastapi.responses import Response
                return Response(
                    content=f'{{"detail": "{detail_message}"}}',
                    status_code=500,
                    media_type="application/json",
                    headers={"Content-Encoding": "identity"}  # Désactiver la compression
                )

# Ajouter le middleware d'erreur
app.add_middleware(ErrorHandlerMiddleware)

# Gestionnaires d'erreurs centralisés
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Inclusion des routeurs
app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(modules.router, prefix="/api/modules", tags=["Modules"])
app.include_router(ai_tutor.router, prefix="/api/ai", tags=["Kaïros"])
app.include_router(prompt_router.router, prefix="/api/prompt-router", tags=["Prompt Router"])
app.include_router(user_history.router, prefix="/api/user-history", tags=["Historique Utilisateur"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progression"])
app.include_router(badges.router, prefix="/api/badges", tags=["Badges"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favoris"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommandations"])
app.include_router(support.router, prefix="/api/support", tags=["Support"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])
app.include_router(exam.router, prefix="/api/exams", tags=["Examens"])
app.include_router(validation.router, prefix="/api/validations", tags=["Validations"])
app.include_router(td.router, prefix="/api/tds", tags=["Travaux Dirigés"])
app.include_router(tp.router, prefix="/api/tps", tags=["Travaux Pratiques"])
app.include_router(resources.router, prefix="/api/resources", tags=["Ressources"])
app.include_router(adaptive_learning.router, prefix="/api/adaptive-learning", tags=["Apprentissage Adaptatif"])
app.include_router(pathways.router, prefix="/api/pathways", tags=["Parcours Intelligents"])
app.include_router(exercise_generator.router, prefix="/api/exercise-generator", tags=["Génération Exercices"])
app.include_router(error_learning.router, prefix="/api/error-learning", tags=["Apprendre par l'Erreur"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Learning Analytics"])
app.include_router(anti_cheat.router, prefix="/api/anti-cheat", tags=["Anti-Triche"])
app.include_router(virtual_labs.router, prefix="/api/virtual-labs", tags=["Laboratoires Virtuels"])
app.include_router(avatar.router, prefix="/api/avatar", tags=["Avatar IA"])
app.include_router(gamification.router, prefix="/api/gamification", tags=["Gamification"])
app.include_router(collaboration.router, prefix="/api/collaboration", tags=["Collaboration"])
app.include_router(gdpr.router, prefix="/api/gdpr", tags=["RGPD"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Abonnements"])
app.include_router(openai_content.router, prefix="/api", tags=["OpenAI Content Generation"])

@app.get("/")
async def root():
    return {
        "message": "Bienvenue sur l'API Kaïros",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Vérifie l'état de santé de l'API et toutes les bases de données"""
    from app.database import db
    from app.utils.cache import get_redis
    import time
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "environment": settings.environment,
        "databases": {}
    }
    
    # Vérifier la connexion MongoDB
    try:
        if db.database is not None:
            await db.client.admin.command('ping')
            health_status["databases"]["mongodb"] = {
                "status": "connected",
                "url": settings.mongodb_url,
                "database": settings.mongodb_db_name
            }
        else:
            health_status["databases"]["mongodb"] = {"status": "disconnected"}
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["databases"]["mongodb"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Vérifier PostgreSQL
    try:
        from app.database.postgres import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["databases"]["postgresql"] = {
            "status": "connected",
            "host": f"{settings.postgres_host}:{settings.postgres_port}",
            "database": settings.postgres_db
        }
    except Exception as e:
        health_status["databases"]["postgresql"] = {
            "status": "error",
            "error": str(e)
        }
        # PostgreSQL est optionnel, ne pas dégrader le statut global
    
    # Vérifier Redis
    try:
        redis = get_redis()
        if redis:
            await redis.ping()
            health_status["databases"]["redis"] = {
                "status": "connected",
                "url": settings.redis_url or "not configured"
            }
        else:
            health_status["databases"]["redis"] = {
                "status": "not_configured",
                "message": "REDIS_URL non configuré dans .env"
            }
    except Exception as e:
        health_status["databases"]["redis"] = {
            "status": "error",
            "error": str(e)
        }
        # Redis est optionnel, ne pas dégrader le statut global
    
    # Vérifier OpenAI (optionnel)
    try:
        from app.services.ai_service import client
        if client:
            health_status["openai"] = "configured"
        else:
            health_status["openai"] = "not_configured"
    except Exception:
        health_status["openai"] = "unknown"
    
    return health_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

