"""
Service de routing intelligent pour GPT-5.1 et GPT-5-mini
Optimisé pour 100k utilisateurs avec gestion de charge
"""
from typing import Dict, Any, Optional, AsyncGenerator, List
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk
from app.config import settings
from app.utils.model_mapper import map_to_real_model
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# Modèles disponibles
GPT_5_2_MODEL = "gpt-5.2"  # Expert - Raisonnement complexe (Examens, TD avancés, TP ML)
GPT_5_MINI_MODEL = "gpt-5-mini"  # Principal - Pédagogique (TD standards, quiz, explications)
GPT_5_NANO_MODEL = "gpt-5-nano"  # Rapide - Économique (QCM, flash-cards, vérifications)

# Client OpenAI
client = None

def _initialize_openai_client():
    """Initialise le client OpenAI"""
    global client
    if settings.openai_api_key:
        try:
            import httpx
            
            http_client_kwargs = {
                "timeout": 60.0,  # Timeout plus long pour GPT-5.1
                "limits": httpx.Limits(max_keepalive_connections=10, max_connections=50)
            }
            
            proxy = getattr(settings, "openai_proxy", None)
            if proxy:
                http_client_kwargs["proxy"] = proxy
            
            http_client = httpx.Client(**http_client_kwargs)
            client = OpenAI(
                api_key=settings.openai_api_key,
                http_client=http_client
            )
            logger.info("Client OpenAI initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation OpenAI: {e}")
            client = None
    else:
        logger.warning("OpenAI API key non configurée")

_initialize_openai_client()


class AIRoutingService:
    """Service de routing intelligent pour choisir le bon modèle"""
    
    # Seuils pour décider quel modèle utiliser
    COMPLEXITY_THRESHOLD = 50  # Nombre de tokens estimés
    CONTEXT_LENGTH_THRESHOLD = 1000  # Longueur du contexte
    
    @staticmethod
    def _estimate_complexity(message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Estime la complexité de la requête"""
        message_length = len(message)
        context_length = len(context) if context else 0
        total_length = message_length + context_length
        
        # Mots-clés indiquant une requête complexe
        complex_keywords = [
            "explique", "simulation", "calcul", "démontre", "analyse",
            "pourquoi", "comment fonctionne", "principe", "théorème"
        ]
        
        # Mots-clés indiquant une requête simple
        simple_keywords = [
            "quoi", "c'est quoi", "définition", "exemple", "rapide"
        ]
        
        # Mots-clés indiquant une requête de recherche académique
        research_keywords = [
            "recherche", "académique", "publication", "thèse", "mémoire", "méthodologie",
            "littérature", "hypothèse", "expérimental", "modélisation avancée", "critique"
        ]
        
        complexity_score = 0
        is_research_request = any(keyword in message.lower() for keyword in research_keywords)
        
        if any(keyword in message.lower() for keyword in complex_keywords):
            complexity_score += 30
        if any(keyword in message.lower() for keyword in simple_keywords):
            complexity_score -= 20
        if is_research_request:
            complexity_score += 50  # Score élevé pour requêtes recherche
        
        if total_length > AIRoutingService.CONTEXT_LENGTH_THRESHOLD:
            complexity_score += 20
        
        return {
            "score": complexity_score,
            "message_length": message_length,
            "context_length": context_length,
            "is_complex": complexity_score > AIRoutingService.COMPLEXITY_THRESHOLD,
            "is_research": is_research_request
        }
    
    @staticmethod
    async def select_model(message: str, context: Optional[str] = None, 
                    force_model: Optional[str] = None, use_prompt_router: bool = True) -> str:
        """
        Sélectionne le modèle approprié
        
        Args:
            message: Message de l'utilisateur
            context: Contexte optionnel
            force_model: Modèle forcé
            use_prompt_router: Si True, utilise le prompt router (recommandé)
        """
        if force_model:
            return force_model
        
        # Utiliser le prompt router si activé (recommandé pour optimiser les coûts)
        if use_prompt_router:
            try:
                from app.services.prompt_router_service import PromptRouterService
                model = await PromptRouterService.route_to_model(message, context, force_model)
                logger.info(f"Modèle sélectionné via Prompt Router: {model}")
                return model
            except Exception as e:
                logger.warning(f"Erreur avec Prompt Router, fallback sur méthode classique: {e}")
        
        # Fallback sur la méthode classique (estimation de complexité)
        complexity = AIRoutingService._estimate_complexity(message, context)
        
        # Détecter si la requête nécessite un raisonnement scientifique approfondi
        expert_keywords = [
            "démontre", "prouve", "justifie", "analyse en détail", "raisonnement",
            "théorème", "formule", "calcul complexe", "dérivation", "démonstration",
            "erreur de raisonnement", "corrige", "rigoureux", "approfondi", "détaillé"
        ]
        
        is_expert_request = any(keyword in message.lower() for keyword in expert_keywords)
        
        # Utiliser GPT-5.2 pour raisonnement scientifique approfondi
        if is_expert_request or (complexity["is_complex"] and complexity["score"] > 70):
            logger.info(f"Utilisation GPT-5.2 (Expert) pour raisonnement approfondi (score: {complexity['score']})")
            return GPT_5_2_MODEL
        
        # Utiliser GPT-5.2 pour les requêtes complexes (simulations, etc.)
        if complexity["is_complex"]:
            logger.info(f"Utilisation GPT-5.2 pour requête complexe (score: {complexity['score']})")
            return GPT_5_2_MODEL
        else:
            logger.info(f"Utilisation GPT-5-mini pour requête simple (score: {complexity['score']})")
            return GPT_5_MINI_MODEL
    
    @staticmethod
    async def chat_stream_with_vision(
        message_content: List[Dict[str, Any]],
        module_id: Optional[str] = None,
        context: Optional[str] = None,
        language: str = "fr",
        force_model: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Chat avec streaming et support de la vision (images).
        message_content est une liste d'objets avec type "text" ou "image_url".
        """
        if not client:
            yield "Mode démo activé. OpenAI non configuré."
            return
        
        # Utiliser GPT-5.2 avec vision si des images sont présentes
        model = force_model or GPT_5_2_MODEL  # GPT-5.2 supporte la vision
        # Mapper le modèle fictif vers le vrai modèle OpenAI
        actual_model = map_to_real_model(model)
        if model != actual_model:
            logger.debug(f"Modèle '{model}' mappé vers '{actual_model}' (modèle réel OpenAI)")
        
        try:
            # Construire le contexte système
            system_prompt = f"""Tu es Kaïrox Tutor, un assistant pédagogique fiable, clair et bienveillant.
Ta mission est d'aider les étudiants à apprendre de manière naturelle et conversationnelle.

RÈGLES DE CONVERSATION :
- Sois naturel et conversationnel, comme un vrai tuteur humain
- Adapte la longueur de ta réponse au contexte :
  * Salutations simples (bonjour, salut, etc.) → Réponse brève et amicale (1-2 phrases max)
  * Questions simples → Réponse concise et directe (2-4 phrases)
  * Questions complexes → Réponse détaillée et structurée
- Ne donne JAMAIS de longues listes ou structures rigides pour des messages simples

ANALYSE DE DOCUMENTS (PDF, Word, PPT, Images) :
- Si l'utilisateur envoie un document (PDF, image, Word, PPT), analyse-le EN DÉTAIL
- Pour les exercices dans les documents, fournis une solution COMPLÈTE et ÉTAPE PAR ÉTAPE
- Pour les exercices mathématiques, montre TOUS les calculs étape par étape
- Réponds directement aux questions posées sur le document
- Si le document contient plusieurs exercices, réponds à celui demandé par l'utilisateur
- Utilise les informations du document pour donner des réponses précises et contextuelles

RÈGLES GÉNÉRALES :
- Utilise un langage clair et accessible
- Explique étape par étape seulement si nécessaire
- Donne des exemples concrets quand utile
- Ne complexifie jamais inutilement

EXEMPLES :
- Si l'utilisateur dit "bonjour" → Réponds simplement "Bonjour ! Comment puis-je t'aider aujourd'hui ?"
- Si l'utilisateur envoie un PDF avec "répondre à l'exercice 1" → Analyse le PDF, trouve l'exercice 1, et fournis une solution complète
- Si l'utilisateur pose une question → Réponds directement à la question de manière concise

LANGUE : Réponds TOUJOURS en {language}"""

            if context:
                system_prompt += f"\n\nContexte: {context}"
            
            # Construire la liste des messages avec l'historique de conversation
            messages = [{"role": "system", "content": system_prompt}]
            
            # Ajouter l'historique de conversation si disponible
            if conversation_history:
                recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                messages.extend(recent_history)
            
            # Ajouter le message actuel avec images
            messages.append({
                "role": "user",
                "content": message_content
            })
            
            # Créer le stream avec le modèle de vision
            from app.services.ai_service import _get_max_tokens_param, _get_temperature_param
            max_tokens_value = 4000
            temperature_value = 0.7
            create_params = {
                "model": actual_model,  # Utiliser le modèle réel mappé
                "messages": messages,
                "stream": True,
                "timeout": 120.0
            }
            create_params.update(_get_max_tokens_param(actual_model, max_tokens_value))
            create_params.update(_get_temperature_param(actual_model, temperature_value))
            
            stream: Stream[ChatCompletionChunk] = client.chat.completions.create(**create_params)
            
            # Streamer les réponses
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        content = delta.content
                        if isinstance(content, str):
                            yield content
                        else:
                            try:
                                yield str(content)
                            except Exception as e:
                                logger.error(f"Erreur conversion chunk content: {e}")
                                yield ""
                    
        except Exception as e:
            logger.error(f"Erreur lors du streaming chat avec vision: {e}", exc_info=True)
            import inspect
            if inspect.iscoroutine(e):
                error_message = "Une coroutine a été détectée dans l'erreur (bug)"
            elif inspect.iscoroutinefunction(e):
                error_message = "Une fonction coroutine a été détectée dans l'erreur (bug)"
            else:
                try:
                    error_message = str(e) if e else "Une erreur inconnue s'est produite"
                except Exception:
                    error_message = "Erreur lors de la conversion de l'exception en string"
            yield f"Erreur: {error_message}"
    
    @staticmethod
    async def chat_stream(
        message: str,
        module_id: Optional[str] = None,
        context: Optional[str] = None,
        language: str = "fr",
        force_model: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """Chat avec streaming pour meilleure UX avec support de l'historique de conversation"""
        if not client:
            # Mode démo
            yield "Mode démo activé. OpenAI non configuré."
            return
        
        model = await AIRoutingService.select_model(message, context, force_model)
        
        try:
            # Construire le contexte système selon le modèle
            if model == GPT_5_2_MODEL:
                # Prompt Expert pour GPT-5.2
                system_prompt = f"""Tu es Kaïrox Expert, un assistant pédagogique avancé spécialisé dans le raisonnement scientifique et l'analyse approfondie.

Ta mission est de produire des réponses exactes, rigoureuses et pédagogiquement solides en physique, chimie, mathématiques et informatique.

Règles :
- Raisonne étape par étape.
- Justifie chaque conclusion.
- Utilise des notations mathématiques claires si nécessaire.
- Détecte et corrige les erreurs de raisonnement.
- Adapte la difficulté au niveau indiqué.
- Ne réponds jamais de façon vague.

Sorties attendues :
- Raisonnement détaillé
- Solution finale claire
- Astuces pédagogiques ou pièges courants

LANGUE : Réponds TOUJOURS en {language}"""
            else:
                # Prompt Tutor standard pour GPT-5-mini
                system_prompt = f"""Tu es Kaïrox Tutor, un assistant pédagogique fiable, clair et bienveillant.
Ta mission est d'aider les étudiants à apprendre de manière naturelle et conversationnelle.

RÈGLES DE CONVERSATION :
- Sois naturel et conversationnel, comme un vrai tuteur humain
- Adapte la longueur de ta réponse au contexte :
  * Salutations simples (bonjour, salut, etc.) → Réponse brève et amicale (1-2 phrases max)
  * Questions simples → Réponse concise et directe (2-4 phrases)
  * Questions complexes → Réponse détaillée et structurée
- Ne donne JAMAIS de longues listes ou structures rigides pour des messages simples
- Utilise un langage clair et accessible
- Explique étape par étape seulement si nécessaire
- Pose des questions de suivi seulement si pertinent
- Donne des exemples concrets quand utile
- Ne complexifie jamais inutilement

EXEMPLES :
- Si l'utilisateur dit "bonjour" → Réponds simplement "Bonjour ! Comment puis-je t'aider aujourd'hui ?"
- Si l'utilisateur pose une question → Réponds directement à la question de manière concise
- Si l'utilisateur demande une explication détaillée → Alors tu peux être plus structuré

LANGUE : Réponds TOUJOURS en {language}"""

            if context:
                system_prompt += f"\n\nContexte: {context}"
            
            # Construire la liste des messages avec l'historique de conversation
            messages = [{"role": "system", "content": system_prompt}]
            
            # Ajouter l'historique de conversation si disponible
            if conversation_history:
                # Limiter l'historique aux 10 derniers échanges pour éviter de dépasser les limites de tokens
                recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                messages.extend(recent_history)
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": message})
            
            # Mapper le modèle fictif vers le vrai modèle OpenAI
            actual_model = map_to_real_model(model)
            if model != actual_model:
                logger.debug(f"Modèle '{model}' mappé vers '{actual_model}' (modèle réel OpenAI)")
            
            # Créer le stream
            from app.services.ai_service import _get_max_tokens_param, _get_temperature_param
            max_tokens_value = 4000 if model == GPT_5_2_MODEL else (2000 if model == GPT_5_MINI_MODEL else 1000)
            temperature_value = 0.3 if model == GPT_5_2_MODEL else (0.7 if model == GPT_5_MINI_MODEL else 0.8)
            create_params = {
                "model": actual_model,  # Utiliser le modèle réel mappé
                "messages": messages,
                "stream": True,
                "timeout": 120.0 if model == GPT_5_2_MODEL else (60.0 if model == GPT_5_MINI_MODEL else 30.0)
            }
            # Ajouter temperature seulement si le modèle le supporte
            create_params.update(_get_temperature_param(actual_model, temperature_value))
            create_params.update(_get_max_tokens_param(actual_model, max_tokens_value))
            
            stream: Stream[ChatCompletionChunk] = client.chat.completions.create(**create_params)
            
            # Streamer les réponses
            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        content = delta.content
                        # S'assurer que content est une string et non une coroutine
                        if isinstance(content, str):
                            yield content
                        else:
                            # Convertir en string de manière sécurisée
                            try:
                                yield str(content)
                            except Exception as e:
                                logger.error(f"Erreur conversion chunk content: {e}")
                                yield ""
                    
        except Exception as e:
            logger.error(f"Erreur lors du streaming chat: {e}", exc_info=True)
            # S'assurer que l'erreur est bien convertie en string (éviter les coroutines)
            import inspect
            if inspect.iscoroutine(e):
                error_message = "Une coroutine a été détectée dans l'erreur (bug)"
            elif inspect.iscoroutinefunction(e):
                error_message = "Une fonction coroutine a été détectée dans l'erreur (bug)"
            else:
                try:
                    error_message = str(e) if e else "Une erreur inconnue s'est produite"
                except Exception:
                    error_message = "Erreur lors de la conversion de l'exception en string"
            yield f"Erreur: {error_message}"
    
    @staticmethod
    async def chat(
        message: str,
        module_id: Optional[str] = None,
        context: Optional[str] = None,
        language: str = "fr",
        force_model: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Chat standard (non-streaming) avec support de l'historique de conversation"""
        if not client:
            return {
                "response": "Mode démo activé. OpenAI non configuré.",
                "model_used": "demo",
                "suggestions": []
            }
        
        model = await AIRoutingService.select_model(message, context, force_model)
        
        try:
            # Construire le contexte système selon le modèle
            if model == GPT_5_2_MODEL:
                # Prompt Expert pour GPT-5.2
                system_prompt = f"""Tu es Kaïrox Expert, un assistant pédagogique avancé spécialisé dans le raisonnement scientifique et l'analyse approfondie.

Ta mission est de produire des réponses exactes, rigoureuses et pédagogiquement solides en physique, chimie, mathématiques et informatique.

Règles :
- Raisonne étape par étape.
- Justifie chaque conclusion.
- Utilise des notations mathématiques claires si nécessaire.
- Détecte et corrige les erreurs de raisonnement.
- Adapte la difficulté au niveau indiqué.
- Ne réponds jamais de façon vague.

Sorties attendues :
- Raisonnement détaillé
- Solution finale claire
- Astuces pédagogiques ou pièges courants

LANGUE : Réponds TOUJOURS en {language}"""
            else:
                # Prompt Tutor standard pour GPT-5-mini
                system_prompt = f"""Tu es Kaïrox Tutor, un assistant pédagogique fiable, clair et bienveillant.
Ta mission est d'aider les étudiants à apprendre de manière naturelle et conversationnelle.

RÈGLES DE CONVERSATION :
- Sois naturel et conversationnel, comme un vrai tuteur humain
- Adapte la longueur de ta réponse au contexte :
  * Salutations simples (bonjour, salut, etc.) → Réponse brève et amicale (1-2 phrases max)
  * Questions simples → Réponse concise et directe (2-4 phrases)
  * Questions complexes → Réponse détaillée et structurée
- Ne donne JAMAIS de longues listes ou structures rigides pour des messages simples
- Utilise un langage clair et accessible
- Explique étape par étape seulement si nécessaire
- Pose des questions de suivi seulement si pertinent
- Donne des exemples concrets quand utile
- Ne complexifie jamais inutilement

EXEMPLES :
- Si l'utilisateur dit "bonjour" → Réponds simplement "Bonjour ! Comment puis-je t'aider aujourd'hui ?"
- Si l'utilisateur pose une question → Réponds directement à la question de manière concise
- Si l'utilisateur demande une explication détaillée → Alors tu peux être plus structuré

LANGUE : Réponds TOUJOURS en {language}"""
            
            if context:
                system_prompt += f"\n\nContexte: {context}"
            
            # Construire la liste des messages avec l'historique de conversation
            messages = [{"role": "system", "content": system_prompt}]
            
            # Ajouter l'historique de conversation si disponible
            if conversation_history:
                # Limiter l'historique aux 10 derniers échanges pour éviter de dépasser les limites de tokens
                recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                messages.extend(recent_history)
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": message})
            
            # Mapper le modèle fictif vers le vrai modèle OpenAI
            actual_model = map_to_real_model(model)
            if model != actual_model:
                logger.debug(f"Modèle '{model}' mappé vers '{actual_model}' (modèle réel OpenAI)")
            
            from app.services.ai_service import _get_max_tokens_param, _get_temperature_param
            max_tokens_value = 4000 if model == GPT_5_2_MODEL else (2000 if model == GPT_5_MINI_MODEL else 1000)
            temperature_value = 0.3 if model == GPT_5_2_MODEL else (0.7 if model == GPT_5_MINI_MODEL else 0.8)
            create_params = {
                "model": actual_model,  # Utiliser le modèle réel mappé
                "messages": messages,
                "timeout": 120.0 if model == GPT_5_2_MODEL else (60.0 if model == GPT_5_MINI_MODEL else 30.0)
            }
            # Ajouter temperature seulement si le modèle le supporte
            create_params.update(_get_temperature_param(actual_model, temperature_value))
            create_params.update(_get_max_tokens_param(actual_model, max_tokens_value))
            
            response = client.chat.completions.create(**create_params)
            
            return {
                "response": response.choices[0].message.content,
                "model_used": model,
                "suggestions": []
            }
        except Exception as e:
            logger.error(f"Erreur lors du chat: {e}")
            return {
                "response": f"Erreur: {str(e)}",
                "model_used": "error",
                "suggestions": []
            }





