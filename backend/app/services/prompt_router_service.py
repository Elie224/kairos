"""
Service de routing intelligent avec prompt de classification
Utilise GPT-5-mini pour classifier les requêtes et optimiser l'utilisation des modèles
"""
from typing import Dict, Any, Optional
from app.services.ai_service import client, AI_MODEL
from app.config import settings
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

# Import Redis si disponible
REDIS_AVAILABLE = False
try:
    from app.config import settings
    if settings.redis_url:
        REDIS_AVAILABLE = True
except AttributeError:
    pass


class PromptRouterService:
    """Service de routing intelligent avec classification par prompt"""
    
    # Prompt de classification
    CLASSIFICATION_PROMPT = """Analyse la demande de l'utilisateur et classe-la dans l'une des catégories suivantes :

1. Explication simple / aide rapide
2. Exercice standard / quiz
3. Raisonnement complexe / TD / TP
4. Analyse approfondie / diagnostic pédagogique

Retourne uniquement le numéro correspondant (1, 2, 3 ou 4)."""

    # Mapping catégories → modèles
    CATEGORY_TO_MODEL = {
        1: "gpt-5-mini",  # Explication simple → GPT-5-mini
        2: "gpt-5-mini",  # Exercice standard → GPT-5-mini
        3: "gpt-5.2",    # Raisonnement complexe → GPT-5.2 Expert
        4: "gpt-5.2"  # Analyse approfondie → GPT-5.2 Expert
    }
    
    # Cache TTL (1 heure)
    CACHE_TTL = 3600
    
    @staticmethod
    def _get_cache_key(message: str) -> str:
        """Génère une clé de cache pour la requête"""
        # Normaliser le message (minuscules, supprimer espaces multiples)
        normalized = " ".join(message.lower().split())
        # Hash MD5 pour une clé de taille fixe
        hash_obj = hashlib.md5(normalized.encode())
        return f"prompt_router:classification:{hash_obj.hexdigest()}"
    
    @staticmethod
    async def _get_from_cache(cache_key: str) -> Optional[int]:
        """Récupère la classification depuis le cache Redis"""
        if not REDIS_AVAILABLE:
            return None
        
        try:
            redis_client = await get_redis_client()
            if redis_client:
                cached = await redis_client.get(cache_key)
                if cached:
                    category = int(cached)
                    logger.debug(f"Classification récupérée du cache: {category}")
                    return category
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération du cache: {e}")
        
        return None
    
    @staticmethod
    async def _save_to_cache(cache_key: str, category: int) -> None:
        """Sauvegarde la classification dans le cache Redis"""
        if not REDIS_AVAILABLE:
            return
        
        try:
            redis_client = await get_redis_client()
            if redis_client:
                await redis_client.setex(
                    cache_key,
                    PromptRouterService.CACHE_TTL,
                    str(category)
                )
                logger.debug(f"Classification sauvegardée dans le cache: {category}")
        except Exception as e:
            logger.warning(f"Erreur lors de la sauvegarde du cache: {e}")
    
    @staticmethod
    async def classify_request(message: str, context: Optional[str] = None) -> int:
        """
        Classifie une requête utilisateur en utilisant GPT-5-mini
        
        Retourne:
        1: Explication simple / aide rapide
        2: Exercice standard / quiz
        3: Raisonnement complexe / TD / TP
        4: Analyse approfondie / diagnostic pédagogique
        """
        # Vérifier le cache d'abord
        cache_key = PromptRouterService._get_cache_key(message)
        cached_category = await PromptRouterService._get_from_cache(cache_key)
        if cached_category:
            return cached_category
        
        # Si pas de client OpenAI, retourner catégorie par défaut (simple)
        if not client:
            logger.warning("Client OpenAI non disponible - Classification par défaut: 1")
            return 1
        
        try:
            # Construire le prompt de classification
            classification_message = f"{PromptRouterService.CLASSIFICATION_PROMPT}\n\nDemande utilisateur: {message}"
            if context:
                classification_message += f"\n\nContexte: {context}"
            
            # Appel à GPT-5-mini pour la classification (rapide et économique)
            # S'assurer que client.chat.completions.create() est appelé correctement
            # et ne retourne pas une coroutine
            try:
                from app.services.ai_service import _get_max_tokens_param
                create_params = {
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "Tu es un classificateur de requêtes pédagogiques. Réponds uniquement par un nombre entre 1 et 4."},
                        {"role": "user", "content": classification_message}
                    ],
                    "temperature": 0.1,
                    "timeout": 10.0
                }
                create_params.update(_get_max_tokens_param(AI_MODEL, 5))
                response = client.chat.completions.create(**create_params)
                # Vérifier que la réponse n'est pas une coroutine
                import inspect
                if inspect.iscoroutine(response):
                    logger.error("client.chat.completions.create() a retourné une coroutine au lieu d'une réponse")
                    return 1  # Retourner catégorie par défaut
            except Exception as create_error:
                logger.error(f"Erreur lors de l'appel OpenAI dans classify_request: {create_error}", exc_info=True)
                return 1  # Retourner catégorie par défaut en cas d'erreur
            
            # Extraire le numéro de la réponse
            response_text = response.choices[0].message.content.strip()
            
            # Parser le numéro (peut être "1", "1.", "Catégorie 1", etc.)
            category = None
            for char in response_text:
                if char.isdigit():
                    category = int(char)
                    break
            
            # Validation : doit être entre 1 et 4
            if category is None or category < 1 or category > 4:
                logger.warning(f"Classification invalide '{response_text}', utilisation par défaut: 1")
                category = 1
            
            # Sauvegarder dans le cache
            await PromptRouterService._save_to_cache(cache_key, category)
            
            logger.info(f"Requête classifiée: catégorie {category} (modèle: {PromptRouterService.CATEGORY_TO_MODEL[category]})")
            return category
            
        except Exception as e:
            logger.error(f"Erreur lors de la classification: {e}", exc_info=True)
            # En cas d'erreur, retourner catégorie par défaut (simple)
            return 1
    
    @staticmethod
    async def route_to_model(
        message: str,
        context: Optional[str] = None,
        force_model: Optional[str] = None
    ) -> str:
        """
        Route une requête vers le modèle approprié en utilisant la classification
        
        Args:
            message: Message de l'utilisateur
            context: Contexte optionnel
            force_model: Modèle forcé (ignore la classification)
        
        Returns:
            Nom du modèle à utiliser
        """
        # Si un modèle est forcé, l'utiliser directement
        if force_model:
            logger.info(f"Modèle forcé: {force_model}")
            return force_model
        
        # Classifier la requête
        category = await PromptRouterService.classify_request(message, context)
        
        # Mapper la catégorie au modèle
        model = PromptRouterService.CATEGORY_TO_MODEL.get(category, "gpt-5-mini")
        
        return model
    
    @staticmethod
    def get_category_stats() -> Dict[str, Any]:
        """Retourne les statistiques de routing"""
        return {
            "categories": {
                1: {"name": "Explication simple / aide rapide", "model": "gpt-5-mini"},
                2: {"name": "Exercice standard / quiz", "model": "gpt-5-mini"},
                3: {"name": "Raisonnement complexe / TD / TP", "model": "gpt-5.2"},
                4: {"name": "Analyse approfondie / diagnostic pédagogique", "model": "gpt-5.2"}
            },
            "cache_enabled": REDIS_AVAILABLE,
            "cache_ttl": PromptRouterService.CACHE_TTL
        }

