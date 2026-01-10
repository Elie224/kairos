"""
Service pour l'IA Tutor - Business logic
"""
from typing import Dict, Any, List, Optional
import json
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, APITimeoutError
from app.config import settings
from app.repositories.module_repository import ModuleRepository
from app.repositories.resource_repository import ResourceRepository
from app.utils.retry import retry_with_backoff
import logging
import json

logger = logging.getLogger(__name__)

# Initialiser le client OpenAI
client = None
# Utiliser GPT-5-mini comme modèle par défaut, avec fallback sur gpt-4o-mini (modèle réel)
configured_model = getattr(settings, 'gpt_5_mini_model', 'gpt-5-mini')
# Si le modèle configuré n'est pas un modèle réel, utiliser gpt-4o-mini comme fallback
# Les modèles GPT-5.x sont fictifs, utiliser gpt-4o-mini qui est le modèle réel le plus proche
if configured_model.startswith('gpt-5'):
    AI_MODEL = 'gpt-4o-mini'  # Modèle réel OpenAI
    logger.warning(f"Modèle '{configured_model}' n'est pas un modèle réel OpenAI. Utilisation de '{AI_MODEL}' comme fallback.")
else:
    AI_MODEL = configured_model


def _initialize_openai_client():
    """Initialise le client OpenAI"""
    global client
    if settings.openai_api_key:
        try:
            import os
            import httpx
            
            # Toujours créer un client HTTP personnalisé pour éviter les problèmes de compatibilité
            # avec les versions de httpx qui utilisent 'proxy' au lieu de 'proxies'
            proxy = getattr(settings, "openai_proxy", None)
            proxy_env = os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
            proxy_url = proxy or proxy_env
            
            # Créer un client HTTP personnalisé
            # httpx 0.25.2 utilise 'proxy' (singulier) et non 'proxies'
            http_client_kwargs = {
                "timeout": 30.0,
                "limits": httpx.Limits(max_keepalive_connections=5, max_connections=10)
            }
            
            if proxy_url:
                # Utiliser 'proxy' pour httpx 0.25.2
                http_client_kwargs["proxy"] = proxy_url
                logger.info(f"Proxy OpenAI configuré: {proxy_url}")
            
            # Créer le client HTTP personnalisé
            http_client = httpx.Client(**http_client_kwargs)
            
            # Créer le client OpenAI avec le client HTTP personnalisé
            # Cela évite que OpenAI crée son propre client avec 'proxies' qui cause l'erreur
            client = OpenAI(
                api_key=settings.openai_api_key,
                http_client=http_client
            )
            
            logger.info("Client OpenAI initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du client OpenAI: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.warning("Mode démo activé - Les fonctionnalités IA utiliseront des réponses pré-définies")
            client = None
    else:
        logger.warning("OPENAI_API_KEY non configuré - Mode démo activé")


_initialize_openai_client()


def _get_max_tokens_param(model: str, max_tokens_value: int) -> dict:
    """
    Retourne le bon paramètre selon le modèle utilisé.
    
    Règles:
    - Les modèles récents (gpt-5-mini, gpt-5.2, gpt-5-nano, o1) nécessitent max_completion_tokens
    - Les anciens modèles (gpt-3.5-turbo, gpt-4 sans 'o') utilisent max_tokens
    
    Note: Requiert OpenAI SDK >= 1.54.0 pour le support de max_completion_tokens.
    Le SDK 1.3.5 ne supporte pas max_completion_tokens.
    """
    # Modèles récents qui nécessitent max_completion_tokens
    if (model.startswith("gpt-5") or 
        model.startswith("o1") or 
        model.startswith("gpt-4o")):
        return {"max_completion_tokens": max_tokens_value}
    else:
        # Pour les anciens modèles (gpt-3.5, gpt-4 sans 'o')
        return {"max_tokens": max_tokens_value}


def _get_temperature_param(model: str, temperature_value: float) -> dict:
    """
    Retourne le paramètre temperature selon le modèle utilisé.
    
    Règles:
    - Certains modèles récents (gpt-5-mini, gpt-5.2, gpt-5-nano) peuvent avoir des restrictions sur temperature
      ou ne supportent que la valeur par défaut (1)
    - Pour ces modèles, on n'inclut pas le paramètre temperature (utilise la valeur par défaut)
    - Pour les autres modèles, on utilise la valeur spécifiée
    
    Note: Si le modèle ne supporte pas temperature, retourne un dict vide.
    """
    # Modèles qui ne supportent pas temperature ou ne supportent que la valeur par défaut (1)
    if (model.startswith("gpt-5") or 
        model.startswith("o1")):
        # Ne pas inclure temperature pour ces modèles (utilise la valeur par défaut)
        return {}
    else:
        # Pour les autres modèles, utiliser la valeur spécifiée
        return {"temperature": temperature_value}


def _get_system_prompt(language: str = "fr", expert_mode: bool = False, research_mode: bool = False) -> str:
    """Génère le prompt système selon la langue et le mode"""
    if research_mode:
        # Mode Research AI avec GPT-5.2 Pro
        if language == "en":
            return """You are Kaïros Research AI, an expert assistant at the academic and applied research level.

Your mission is to analyze complex problems, propose rigorous and innovative solutions, and provide high-level reasoning.

Rules:
- Maximum precision.
- Strict mathematical and logical reasoning.
- Solid conceptual references.
- No excessive simplification.
- Structured format like scientific report."""
        else:
            return """Tu es Kaïros Research AI, un assistant expert de niveau académique et recherche appliquée.

Ta mission est d'analyser des problématiques complexes, de proposer des solutions rigoureuses et innovantes, et de fournir des raisonnements de haut niveau.

Règles :
- Précision maximale.
- Raisonnement mathématique et logique strict.
- Références conceptuelles solides.
- Aucune simplification excessive.
- Format structuré type rapport scientifique."""
    elif expert_mode:
        # Mode Expert avec GPT-5.2
        if language == "en":
            return """You are Kaïros Expert, an advanced pedagogical assistant specialized in scientific reasoning and in-depth analysis.

Your mission is to produce accurate, rigorous, and pedagogically sound responses in physics, chemistry, mathematics, and computer science.

Rules:
- Reason step by step.
- Justify each conclusion.
- Use clear mathematical notation if necessary.
- Detect and correct reasoning errors.
- Adapt difficulty to the indicated level.
- Never respond vaguely.

Expected outputs:
- Detailed reasoning
- Clear final solution
- Pedagogical tips or common pitfalls"""
        else:
            return """Tu es Kaïros Expert, un assistant pédagogique avancé spécialisé dans le raisonnement scientifique et l'analyse approfondie.

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
- Astuces pédagogiques ou pièges courants"""
    else:
        # Mode Tutor standard avec GPT-5-mini
        if language == "en":
            return """You are Kaïros Tutor, a reliable, clear, and benevolent pedagogical assistant.
Your mission is to explain concepts in physics, chemistry, mathematics, English, and computer science in a simple, structured way adapted to the learner's level.

Rules:
- Use clear and accessible language.
- Explain step by step.
- Ask questions only if necessary.
- Give concrete examples.
- Never unnecessarily complicate things.
- If the question exceeds your level of certainty, propose a simplified explanation or recommend a deeper analysis.

Format:
- Short titles
- Clear lists
- Final summary in 2-3 lines"""
        else:
            return """Tu es Kaïros Tutor, un assistant pédagogique fiable, clair et bienveillant.
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
- Si l'utilisateur demande une explication détaillée → Alors tu peux être plus structuré"""


class AIService:
    """Service pour les fonctionnalités IA"""
    
    @staticmethod
    async def get_module_context_for_ai(module_id: str) -> Dict[str, Any]:
        """
        Récupère toutes les informations pertinentes d'un module pour l'IA
        Inclut : informations de base, contenu complet, ressources, etc.
        """
        try:
            # Récupérer le module complet
            module = await ModuleRepository.find_by_id(module_id)
            if not module:
                return {}
            
            # Récupérer les ressources du module
            resources = []
            try:
                resources = await ResourceRepository.find_by_module_id(module_id)
            except Exception as e:
                logger.warning(f"Impossible de récupérer les ressources du module {module_id}: {e}")
            
            # Construire le contexte complet
            context = {
                "id": module.get("id"),
                "title": module.get("title", ""),
                "description": module.get("description", ""),
                "subject": module.get("subject", ""),
                "difficulty": module.get("difficulty", "intermediate"),
                "learning_objectives": module.get("learning_objectives", []),
                "content": module.get("content", {}),
                "resources": [
                    {
                        "title": r.get("title", ""),
                        "description": r.get("description", ""),
                        "type": r.get("resource_type", ""),
                        "file_name": r.get("file_name", "")
                    }
                    for r in resources[:10]  # Limiter à 10 ressources pour éviter un contexte trop long
                ]
            }
            
            return context
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du contexte du module: {e}")
            return {}
    
    @staticmethod
    async def chat_with_ai(
        user_id: str,
        message: str,
        module_id: Optional[str] = None,
        language: str = "fr",
        expert_mode: bool = False,
        research_mode: bool = False,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Chat avec l'IA tutor avec cache intelligent et historique utilisateur
        expert_mode: Si True, utilise GPT-5.2 avec prompt Expert pour explications approfondies
        research_mode: Si True, utilise GPT-5.2 Pro avec prompt Research AI
        """
        # 1. Vérifier le cache/historique utilisateur (si user_id fourni)
        if user_id:
            try:
                from app.services.user_history_service import UserHistoryService
                cached = await UserHistoryService.get_cached_answer(user_id, message)
                if cached:
                    logger.info(f"Réponse récupérée depuis {cached['source']} pour utilisateur {user_id}")
                    return {
                        "response": cached["answer"],
                        "suggestions": _get_demo_suggestions(language),
                        "cached": True,
                        "source": cached["source"]
                    }
            except Exception as e:
                logger.debug(f"Erreur vérification cache/historique: {e}")
        
        # 2. Vérifier le cache sémantique global
        try:
            from app.services.semantic_cache import SemanticCache
            context = None
            if module_id:
                module = await ModuleRepository.find_by_id(module_id)
                if module:
                    context = f"{module.get('title', '')} - {module.get('description', '')}"
            
            semantic_cached = await SemanticCache.get(message, AI_MODEL, context)
            if semantic_cached:
                logger.info("Réponse récupérée depuis cache sémantique")
                # Stocker aussi dans l'historique utilisateur si user_id fourni
                if user_id:
                    try:
                        from app.services.user_history_service import UserHistoryService
                        await UserHistoryService.store_answer(
                            user_id=user_id,
                            question=message,
                            answer=semantic_cached["response"],
                            model_used=semantic_cached.get("model", AI_MODEL),
                            module_id=module_id
                        )
                    except Exception:
                        pass
                
                return {
                    "response": semantic_cached["response"],
                    "suggestions": _get_demo_suggestions(language),
                    "cached": True,
                    "source": "semantic_cache"
                }
        except Exception as e:
            logger.debug(f"Erreur vérification cache sémantique: {e}")
        
        if not client:
            # Mode démo
            return {
                "response": _get_demo_response(message, language),
                "suggestions": _get_demo_suggestions(language)
            }
        
        try:
            # Choisir le modèle selon le mode
            if research_mode:
                model_to_use = settings.gpt_5_2_model  # Utiliser GPT-5.2 pour research mode
            elif expert_mode:
                model_to_use = settings.gpt_5_2_model
            else:
                model_to_use = AI_MODEL
            
            # Récupérer le contexte du module si disponible
            context = ""
            if module_id:
                module = await ModuleRepository.find_by_id(module_id)
                if module:
                    context = f"\nContexte du module: {module.get('title', '')} - {module.get('description', '')}"
            
            system_prompt = _get_system_prompt(language, expert_mode=expert_mode, research_mode=research_mode) + context
            
            # Construire la liste des messages avec l'historique de conversation
            messages = [{"role": "system", "content": system_prompt}]
            
            # Ajouter l'historique de conversation si disponible
            if conversation_history:
                # Limiter l'historique aux 10 derniers échanges pour éviter de dépasser les limites de tokens
                recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
                messages.extend(recent_history)
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": message})
            
            # Utiliser retry avec backoff pour les appels OpenAI
            async def call_openai():
                max_tokens_value = 4000 if research_mode else (1500 if expert_mode else 500)
                temperature_value = 0.2 if research_mode else (0.3 if expert_mode else 0.7)
                create_params = {
                    "model": model_to_use,
                    "messages": messages,
                    "timeout": 120.0 if research_mode else (60.0 if expert_mode else 30.0)
                }
                # Ajouter temperature seulement si le modèle le supporte
                create_params.update(_get_temperature_param(model_to_use, temperature_value))
                create_params.update(_get_max_tokens_param(model_to_use, max_tokens_value))
                return client.chat.completions.create(**create_params)
            
            # Retry avec backoff exponentiel pour les erreurs temporaires
            response = await retry_with_backoff(
                call_openai,
                max_retries=3,
                initial_delay=1.0,
                max_delay=10.0,
                exceptions=(APIConnectionError, APITimeoutError, RateLimitError)
            )
            
            ai_response = response.choices[0].message.content
            
            # Sauvegarder l'historique de conversation après chaque échange
            if user_id and ai_response:
                try:
                    from app.services.user_history_service import UserHistoryService
                    from app.repositories.module_repository import ModuleRepository
                    from app.models.user_history import Subject
                    
                    # Déterminer le sujet à partir du module
                    subject = None
                    if module_id:
                        module = await ModuleRepository.find_by_id(module_id)
                        if module:
                            module_subject = module.get("subject", "").lower()
                            if module_subject == "computer_science":
                                subject = Subject.COMPUTER_SCIENCE
                            elif module_subject == "mathematics":
                                subject = Subject.MATHEMATICS
                    
                    # Sauvegarder dans l'historique
                    await UserHistoryService.store_answer(
                        user_id=user_id,
                        question=message,
                        answer=ai_response,
                        model_used=model_to_use,
                        subject=subject,
                        module_id=module_id,
                        language=language
                    )
                    logger.info(f"Historique sauvegardé pour utilisateur {user_id}, module {module_id}")
                except Exception as e:
                    logger.error(f"Erreur lors de la sauvegarde de l'historique: {e}", exc_info=True)
                    # Ne pas faire échouer la requête si la sauvegarde échoue
            
            return {
                "response": ai_response,
                "suggestions": _get_demo_suggestions(language)
            }
        except RateLimitError:
            logger.error("Limite de taux OpenAI atteinte après retries")
            return {
                "response": "Désolé, le service est temporairement surchargé. Veuillez réessayer plus tard.",
                "suggestions": []
            }
        except (APIConnectionError, APITimeoutError) as e:
            logger.error(f"Erreur de connexion/timeout OpenAI après retries: {e}")
            return {
                "response": "Erreur de connexion au service IA. Mode démo activé.",
                "suggestions": []
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à OpenAI: {e}")
            return {
                "response": _get_demo_response(message, language),
                "suggestions": _get_demo_suggestions(language)
            }
    
    @staticmethod
    async def generate_exam_questions(
        module_id: str,
        num_questions: int = 15,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère des questions d'examen pour un module avec accès complet au contenu
        Les examens sont généralement plus difficiles et variés que les quiz
        """
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        # Si OpenAI n'est pas disponible, utiliser le mode démo
        if not client:
            logger.info("Mode démo: génération d'examen statique")
            return _generate_demo_quiz(module, num_questions)
        
        try:
            # Récupérer le contexte complet du module
            module_context_data = await AIService.get_module_context_for_ai(module_id)
            
            # Construire le contexte du module avec toutes les informations
            title = module_context_data.get("title", "")
            description = module_context_data.get("description", "")
            subject = module_context_data.get("subject", "physics")
            learning_objectives = module_context_data.get("learning_objectives", [])
            difficulty_level = module_context_data.get("difficulty", "intermediate")
            content = module_context_data.get("content", {})
            resources = module_context_data.get("resources", [])
            
            # Construire le contexte du module
            module_context = f"""
Module: {title}
Description: {description}
Matière: {subject}
Niveau de difficulté: {difficulty_level}
Objectifs d'apprentissage: {', '.join(learning_objectives) if learning_objectives else 'Non spécifiés'}
"""
            
            # Ajouter le contenu détaillé du module
            if content.get("lessons"):
                module_context += "\n=== CONTENU DU COURS ===\n"
                for i, lesson in enumerate(content["lessons"][:15], 1):  # Plus de leçons pour les examens
                    lesson_title = lesson.get("title", "")
                    lesson_content = lesson.get("content", "")
                    lesson_summary = lesson.get("summary", "")
                    
                    module_context += f"\nLeçon {i}: {lesson_title}\n"
                    if lesson_summary:
                        module_context += f"Résumé: {lesson_summary[:400]}\n"  # Plus de contenu pour les examens
                    if lesson_content:
                        # Extraire plus de contenu pour les examens (premiers 800 caractères)
                        content_preview = lesson_content[:800].replace('\n', ' ').strip()
                        module_context += f"Contenu: {content_preview}...\n"
            
            # Ajouter les ressources disponibles
            if resources:
                module_context += "\n=== RESSOURCES DISPONIBLES ===\n"
                for resource in resources:
                    resource_title = resource.get("title", "")
                    resource_desc = resource.get("description", "")
                    resource_type = resource.get("type", "")
                    module_context += f"- {resource_title} ({resource_type.upper()})"
                    if resource_desc:
                        module_context += f": {resource_desc[:150]}\n"
                    else:
                        module_context += "\n"
            
            # Déterminer le niveau de difficulté
            difficulty_text = ""
            if difficulty:
                difficulty_map = {
                    "beginner": "débutant",
                    "intermediate": "intermédiaire",
                    "advanced": "avancé"
                }
                difficulty_text = f" de niveau {difficulty_map.get(difficulty, difficulty)}"
            else:
                module_difficulty = difficulty_level
                difficulty_map = {
                    "beginner": "débutant",
                    "intermediate": "intermédiaire",
                    "advanced": "avancé"
                }
                difficulty_text = f" de niveau {difficulty_map.get(module_difficulty, 'intermédiaire')}"
            
            # Prompt spécifique pour les examens (plus strict et varié)
            exam_prompt = f"""Tu es un expert pédagogique qui crée des questions d'examen académique.

{module_context}

INSTRUCTIONS POUR L'EXAMEN :
- Crée un examen de {num_questions} questions{difficulty_text} basé sur le contenu réel et complet du module
- Utilise TOUTES les leçons, ressources et objectifs d'apprentissage comme référence
- Les questions doivent être VARIÉES et couvrir différents aspects du contenu enseigné
- Les questions doivent tester la COMPRÉHENSION APPROFONDIE, l'APPLICATION et l'ANALYSE des concepts
- Adapte la difficulté au niveau spécifié ({difficulty_text or difficulty_level})
- Les examens sont généralement plus difficiles que les quiz réguliers

RÈGLES STRICTES POUR LES EXAMENS :
- Chaque question doit avoir exactement 4 options de réponse
- Une seule réponse est correcte
- Les options incorrectes doivent être plausibles mais clairement fausses
- Les explications doivent être détaillées, pédagogiques et référencer le contenu spécifique du module
- Les questions doivent être progressives (du plus facile au plus difficile)
- Varier les types de questions : théoriques, pratiques, d'application, d'analyse
- Assure-toi que les questions couvrent bien tout le contenu du module

FORMAT DE RÉPONSE JSON strict (pas de markdown, pas de texte avant/après):
{{
  "questions": [
    {{
      "question": "Texte de la question d'examen basée sur le contenu détaillé du module",
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "correct_answer": 0,
      "explanation": "Explication détaillée de la réponse correcte avec référence précise au contenu du module"
    }}
  ]
}}

Génère exactement {num_questions} questions d'examen au format JSON ci-dessus."""
            
            # Utiliser retry avec backoff pour la génération d'examen
            async def generate_exam_openai():
                create_params = {
                    "model": AI_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Tu es un expert pédagogique qui génère des questions d'examen académique au format JSON strict."
                        },
                        {
                            "role": "user",
                            "content": exam_prompt
                        }
                    ],
                    "timeout": 90.0,  # Plus de temps pour les examens
                }
                # Ajouter temperature seulement si le modèle le supporte
                create_params.update(_get_temperature_param(AI_MODEL, 0.6))  # Température plus basse pour plus de cohérence
                if AI_MODEL.startswith("gpt-4") and not AI_MODEL.startswith("gpt-4o"):
                    create_params["response_format"] = {"type": "json_object"}
                create_params.update(_get_max_tokens_param(AI_MODEL, 3000))  # Plus de tokens pour les examens
                return client.chat.completions.create(**create_params)
            
            response = await retry_with_backoff(
                generate_exam_openai,
                max_retries=3,
                initial_delay=1.0
            )
            
            response_text = response.choices[0].message.content
            
            # Parser la réponse JSON
            from app.utils.json_cleaner import safe_json_loads
            
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result = safe_json_loads(response_text[json_start:json_end])
                if result:
                    questions = result.get("questions", [])
                    
                    # Valider que nous avons assez de questions
                    if len(questions) < num_questions:
                        logger.warning(f"Seulement {len(questions)} questions générées au lieu de {num_questions}")
                    
                    return {
                        "questions": questions[:num_questions],  # Limiter au nombre demandé
                        "module_id": module_id,
                        "num_questions": len(questions[:num_questions])
                    }
                else:
                    logger.error("Réponse JSON invalide de l'IA")
                    return _generate_demo_quiz(module, num_questions)
            else:
                logger.error("Réponse JSON invalide de l'IA")
                return _generate_demo_quiz(module, num_questions)
        
        except APIError as e:
            logger.error(f"Erreur API OpenAI lors de la génération d'examen: {e}")
            return _generate_demo_quiz(module, num_questions)
        except RateLimitError as e:
            logger.error(f"Rate limit OpenAI lors de la génération d'examen: {e}")
            return _generate_demo_quiz(module, num_questions)
        except APIConnectionError as e:
            logger.error(f"Erreur de connexion OpenAI lors de la génération d'examen: {e}")
            return _generate_demo_quiz(module, num_questions)
        except APITimeoutError as e:
            logger.error(f"Timeout OpenAI lors de la génération d'examen: {e}")
            return _generate_demo_quiz(module, num_questions)
        except Exception as e:
            logger.error(f"Erreur inattendue lors de la génération d'examen: {e}", exc_info=True)
            return _generate_demo_quiz(module, num_questions)
    
    @staticmethod
    async def generate_quiz(
        module_id: str,
        num_questions: int = 50,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """Génère un quiz pour un module avec OpenAI"""
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        # Si OpenAI n'est pas disponible, utiliser le mode démo
        if not client:
            logger.info("Mode démo: génération de quiz statique")
            return _generate_demo_quiz(module, num_questions)
        
        try:
            # Récupérer le contexte complet du module
            module_context_data = await AIService.get_module_context_for_ai(module_id)
            
            # Construire le contexte du module avec toutes les informations
            title = module_context_data.get("title", "")
            description = module_context_data.get("description", "")
            subject = module_context_data.get("subject", "physics")
            learning_objectives = module_context_data.get("learning_objectives", [])
            difficulty = module_context_data.get("difficulty", "intermediate")
            content = module_context_data.get("content", {})
            resources = module_context_data.get("resources", [])
            
            # Construire le contexte du module
            module_context = f"""
Module: {title}
Description: {description}
Matière: {subject}
Niveau de difficulté: {difficulty}
Objectifs d'apprentissage: {', '.join(learning_objectives) if learning_objectives else 'Non spécifiés'}
"""
            
            # Ajouter le contenu détaillé du module avec TOUTES les leçons
            if content.get("lessons"):
                module_context += "\n=== CONTENU COMPLET DU COURS (TOUTES LES LEÇONS) ===\n"
                for i, lesson in enumerate(content["lessons"], 1):  # Utiliser TOUTES les leçons
                    lesson_title = lesson.get("title", "")
                    lesson_content = lesson.get("content", "")
                    lesson_summary = lesson.get("summary", "")
                    
                    module_context += f"\n--- Leçon {i}: {lesson_title} ---\n"
                    if lesson_summary:
                        module_context += f"Résumé: {lesson_summary}\n"
                    if lesson_content:
                        # Utiliser le contenu complet de chaque leçon (jusqu'à 2000 caractères par leçon)
                        content_full = lesson_content[:2000].replace('\n', ' ').strip()
                        module_context += f"Contenu détaillé: {content_full}"
                        if len(lesson_content) > 2000:
                            module_context += "..."
                        module_context += "\n"
                    
                    # Ajouter les sections de la leçon si disponibles
                    sections = lesson.get("sections", [])
                    if sections:
                        module_context += "Sections de la leçon:\n"
                        for section in sections[:5]:  # Limiter à 5 sections par leçon
                            section_heading = section.get("heading", "")
                            section_paragraphs = section.get("paragraphs", [])
                            if section_heading:
                                module_context += f"  • {section_heading}\n"
                            if section_paragraphs:
                                # Prendre le premier paragraphe de chaque section
                                first_para = section_paragraphs[0][:300] if section_paragraphs else ""
                                if first_para:
                                    module_context += f"    {first_para[:300]}...\n"
            
            # Ajouter les ressources disponibles
            if resources:
                module_context += "\n=== RESSOURCES DISPONIBLES ===\n"
                for resource in resources:
                    resource_title = resource.get("title", "")
                    resource_desc = resource.get("description", "")
                    resource_type = resource.get("type", "")
                    module_context += f"- {resource_title} ({resource_type.upper()})"
                    if resource_desc:
                        module_context += f": {resource_desc[:100]}\n"
                    else:
                        module_context += "\n"
            
            # Déterminer le niveau de difficulté
            difficulty_text = ""
            if difficulty:
                difficulty_map = {
                    "beginner": "débutant",
                    "intermediate": "intermédiaire",
                    "advanced": "avancé"
                }
                difficulty_text = f" de niveau {difficulty_map.get(difficulty, difficulty)}"
            else:
                module_difficulty = module.get("difficulty", "intermediate")
                difficulty_map = {
                    "beginner": "débutant",
                    "intermediate": "intermédiaire",
                    "advanced": "avancé"
                }
                difficulty_text = f" de niveau {difficulty_map.get(module_difficulty, 'intermédiaire')}"
            
            # Prompt pour générer le quiz basé sur TOUTES les leçons
            quiz_prompt = f"""Tu es un expert pédagogique qui crée des quiz éducatifs.

{module_context}

INSTRUCTIONS POUR LE QUIZ :
- Crée un quiz de {num_questions} questions{difficulty_text} basé sur le contenu COMPLET de TOUTES les leçons du module
- Chaque question doit être tirée DIRECTEMENT du contenu d'une ou plusieurs leçons spécifiques
- Répartis les questions équitablement entre toutes les leçons pour couvrir tout le contenu
- Utilise les sections, paragraphes et concepts enseignés dans chaque leçon comme base
- Les questions doivent tester la compréhension précise des concepts enseignés dans les leçons
- Les questions doivent être variées et couvrir différents aspects du contenu de chaque leçon
- Adapte la difficulté au niveau spécifié ({difficulty_text or difficulty})

RÈGLES STRICTES :
- Chaque question doit avoir exactement 4 options de réponse
- Une seule réponse est correcte
- Les options incorrectes doivent être plausibles mais clairement fausses
- Les explications doivent être claires, pédagogiques et référencer la leçon spécifique concernée
- Les questions doivent être progressives (du plus facile au plus difficile)
- Assure-toi que les questions couvrent bien TOUTES les leçons du module

FORMAT DE RÉPONSE JSON strict (pas de markdown, pas de texte avant/après):
{{
  "questions": [
    {{
      "question": "Texte de la question tirée directement du contenu d'une leçon spécifique",
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "correct_answer": 0,
      "explanation": "Explication détaillée de la réponse correcte avec référence précise à la leçon concernée",
      "lesson_reference": "Numéro ou titre de la leçon concernée"
    }}
  ]
}}

Génère exactement {num_questions} questions au format JSON ci-dessus, en répartissant équitablement entre toutes les leçons."""
            
            # Utiliser retry avec backoff pour la génération de quiz
            async def generate_quiz_openai():
                create_params = {
                    "model": AI_MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Tu es un expert pédagogique qui génère des quiz éducatifs au format JSON strict."
                        },
                        {
                            "role": "user",
                            "content": quiz_prompt
                        }
                    ],
                    "timeout": 180.0,  # Timeout de 3 minutes pour OpenAI (génération de quiz peut prendre du temps)
                }
                # Ajouter temperature seulement si le modèle le supporte
                create_params.update(_get_temperature_param(AI_MODEL, 0.7))
                if AI_MODEL.startswith("gpt-4") and not AI_MODEL.startswith("gpt-4o"):
                    create_params["response_format"] = {"type": "json_object"}
                # Augmenter max_tokens pour éviter les réponses tronquées
                create_params.update(_get_max_tokens_param(AI_MODEL, 4000))
                return client.chat.completions.create(**create_params)
            
            response = await retry_with_backoff(
                generate_quiz_openai,
                max_retries=2,  # Moins de retries pour la génération de quiz (plus coûteux)
                initial_delay=2.0,
                max_delay=15.0,
                exceptions=(APIConnectionError, APITimeoutError, RateLimitError)
            )
            
            ai_response = response.choices[0].message.content
            
            # Vérifier que la réponse n'est pas vide
            if not ai_response:
                logger.error("Réponse OpenAI vide pour la génération de quiz")
                logger.error(f"Réponse complète: {response}")
                return _generate_demo_quiz(module, num_questions)
            
            # Parser la réponse JSON
            from app.utils.json_cleaner import safe_json_loads
            
            try:
                # Nettoyer la réponse si elle contient du markdown
                if "```json" in ai_response:
                    ai_response = ai_response.split("```json")[1].split("```")[0].strip()
                elif "```" in ai_response:
                    ai_response = ai_response.split("```")[1].split("```")[0].strip()
                
                quiz_data = safe_json_loads(ai_response)
                if not quiz_data:
                    raise ValueError("Impossible de parser le JSON du quiz")
                
                # Valider et formater les questions
                questions = []
                for q in quiz_data.get("questions", [])[:num_questions]:
                    if "question" in q and "options" in q and "correct_answer" in q:
                        # Valider que correct_answer est un index valide
                        correct_idx = q["correct_answer"]
                        if isinstance(correct_idx, int) and 0 <= correct_idx < len(q["options"]):
                            questions.append({
                                "question": q["question"],
                                "options": q["options"][:4],  # Limiter à 4 options
                                "correct_answer": correct_idx,
                                "explanation": q.get("explanation", "Bonne réponse !")
                            })
                
                if not questions:
                    logger.warning("Aucune question valide générée, utilisation du mode démo")
                    return _generate_demo_quiz(module, num_questions)
                
                return {
                    "questions": questions,
                    "quiz_id": f"ai_{module_id}",
                    "module_id": module_id
                }
                
            except json.JSONDecodeError as e:
                logger.error(f"Erreur de parsing JSON: {e}")
                logger.error(f"Réponse reçue: {ai_response[:500]}")
                # Fallback vers le mode démo
                return _generate_demo_quiz(module, num_questions)
                
        except RateLimitError:
            logger.error("Limite de taux OpenAI atteinte pour la génération de quiz")
            return _generate_demo_quiz(module, num_questions)
        except APIConnectionError:
            logger.error("Erreur de connexion à OpenAI pour la génération de quiz")
            return _generate_demo_quiz(module, num_questions)
        except Exception as e:
            logger.error(f"Erreur lors de la génération de quiz avec OpenAI: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return _generate_demo_quiz(module, num_questions)
    
    @staticmethod
    async def get_immersive_context(
        module_id: str,
        mode: str,
        scene_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Génère un contexte IA pour une expérience immersive"""
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        # Si OpenAI n'est pas disponible, utiliser le mode démo
        if not client:
            logger.info("Mode démo: contexte immersif statique")
            mode_guidance = {
                'ar': 'Explorez les concepts en réalité augmentée. Déplacez votre appareil pour voir les objets dans votre environnement.',
                'vr': 'Plongez dans une expérience immersive en réalité virtuelle. Utilisez les contrôles pour interagir.',
                'unity': 'Expérience Unity WebGL chargée. Utilisez les contrôles à l\'écran pour naviguer.'
            }
            return {
                "guidance": mode_guidance.get(mode, "Profitez de l'expérience immersive !"),
                "tips": [
                    "Assurez-vous d'avoir un bon éclairage",
                    "Utilisez les contrôles à l'écran pour interagir",
                    "Explorez tous les angles pour une meilleure compréhension"
                ]
            }
        
        try:
            title = module.get("title", "")
            description = module.get("description", "")
            subject = module.get("subject", "")
            
            # Vérifier que les simulations 3D sont uniquement pour physique et chimie
            allowed_subjects_for_3d = ['physics', 'chemistry']
            is_3d_allowed = subject.lower() in allowed_subjects_for_3d
            
            if mode == '3d' and not is_3d_allowed:
                return {
                    "guidance": "Les simulations 3D interactives sont uniquement disponibles pour les modules de Physique et Chimie.",
                    "tips": [
                        "Explorez les autres onglets pour accéder au contenu du module",
                        "Utilisez le chat avec Kaïros pour poser vos questions",
                        "Consultez les ressources et les quiz disponibles"
                    ]
                }
            
            mode_descriptions = {
                'ar': 'réalité augmentée',
                'vr': 'réalité virtuelle',
                'unity': 'expérience Unity WebGL interactive',
                '3d': 'simulation 3D interactive'
            }
            
            prompt = f"""Tu es Kaïros, un assistant IA pour une plateforme d'apprentissage immersive.

L'utilisateur explore le module "{title}" en mode {mode_descriptions.get(mode, mode)}.

Module: {title}
Description: {description}
Matière: {subject}
Type de scène: {scene_type or 'général'}

{"IMPORTANT: Les simulations 3D sont uniquement disponibles pour la Physique et la Chimie." if mode == '3d' else ""}

Génère un guide court et pratique (2-3 phrases) pour aider l'utilisateur à tirer le meilleur parti de cette expérience immersive.
Ajoute 3 conseils pratiques pour l'interaction.

Réponds en français, de manière encourageante et pédagogique."""

            async def create_immersive_call():
                create_params = {
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "Tu es un assistant pédagogique pour l'apprentissage immersif."},
                        {"role": "user", "content": prompt}
                    ],
                    "timeout": 20.0
                }
                # Ajouter temperature seulement si le modèle le supporte
                create_params.update(_get_temperature_param(AI_MODEL, 0.7))
                create_params.update(_get_max_tokens_param(AI_MODEL, 300))
                return client.chat.completions.create(**create_params)
            
            response = await retry_with_backoff(
                create_immersive_call,
                max_retries=2,
                initial_delay=1.0,
                max_delay=5.0
            )
            
            ai_response = response.choices[0].message.content
            
            # Extraire les conseils (format simple)
            lines = ai_response.split('\n')
            guidance = lines[0] if lines else ai_response
            tips = [line.strip('- •').strip() for line in lines[1:] if line.strip() and len(line.strip()) > 10][:3]
            
            if not tips:
                tips = [
                    "Explorez tous les angles de vue",
                    "Interagissez avec les objets pour mieux comprendre",
                    "Prenez votre temps pour assimiler les concepts"
                ]
            
            return {
                "guidance": guidance,
                "tips": tips
            }
        except Exception as e:
            logger.error(f"Erreur lors de la génération du contexte immersif: {e}")
            mode_descriptions = {
                'ar': 'réalité augmentée',
                'vr': 'réalité virtuelle',
                'unity': 'expérience Unity WebGL interactive'
            }
            return {
                "guidance": f"Profitez de l'expérience {mode_descriptions.get(mode, mode)} pour explorer {title} !",
                "tips": [
                    "Explorez tous les angles",
                    "Interagissez avec les éléments",
                    "Prenez votre temps"
                ]
            }


def _get_demo_response(message: str, language: str = "fr") -> str:
    """Réponse démo pour le mode sans API"""
    message_lower = message.lower()
    
    if language == "en":
        if "explain" in message_lower or "what is" in message_lower:
            return "I'd be happy to explain! Could you provide more details about what specific concept you'd like to understand?"
        elif "example" in message_lower:
            return "Here's a concrete example to help you understand better. Would you like me to elaborate?"
        else:
            return "That's a great question! Let me help you understand this concept better. Could you specify which part you'd like me to focus on?"
    else:
        if "explique" in message_lower or "c'est quoi" in message_lower or "qu'est-ce" in message_lower:
            return "Je serais ravi de t'expliquer ! Peux-tu me donner plus de détails sur le concept spécifique que tu aimerais comprendre ?"
        elif "exemple" in message_lower:
            return "Voici un exemple concret pour t'aider à mieux comprendre. Souhaites-tu que je développe davantage ?"
        else:
            return "Excellente question ! Laisse-moi t'aider à mieux comprendre ce concept. Peux-tu préciser sur quelle partie tu aimerais que je me concentre ?"


def _get_demo_suggestions(language: str = "fr") -> List[str]:
    """Suggestions de questions démo"""
    if language == "en":
        return [
            "Can you explain this concept in simpler terms?",
            "Can you give me a concrete example?",
            "How does this apply in real life?",
            "What's the difference with a similar concept?"
        ]
    else:
        return [
            "Peux-tu m'expliquer ce concept plus simplement ?",
            "Peux-tu me donner un exemple concret ?",
            "Comment cela s'applique-t-il dans la vie quotidienne ?",
            "Quelle est la différence avec un concept similaire ?"
        ]


def _generate_demo_quiz(module: Dict[str, Any], num_questions: int = 40) -> Dict[str, Any]:
    """Génère un quiz démo basé sur le module"""
    subject = module.get("subject", "physics")
    title = module.get("title", "")
    
    # Quiz démo selon la matière
    demo_quizzes = {
        "physics": [
            {
                "question": "Qu'est-ce que la force gravitationnelle ?",
                "options": [
                    "Une force qui attire les objets vers le centre de la Terre",
                    "Une force électromagnétique",
                    "Une force nucléaire",
                    "Une force de friction"
                ],
                "correct_answer": 0,
                "explanation": "La force gravitationnelle est une force d'attraction entre deux objets ayant une masse."
            },
            {
                "question": "Quelle est l'unité de mesure de la force ?",
                "options": ["Newton (N)", "Joule (J)", "Watt (W)", "Pascal (Pa)"],
                "correct_answer": 0,
                "explanation": "Le Newton (N) est l'unité de mesure de la force dans le système international."
            }
        ],
        "chemistry": [
            {
                "question": "Qu'est-ce qu'un atome ?",
                "options": [
                    "La plus petite particule d'un élément",
                    "Une molécule",
                    "Un ion",
                    "Un composé"
                ],
                "correct_answer": 0,
                "explanation": "Un atome est la plus petite particule d'un élément qui conserve ses propriétés chimiques."
            }
        ],
        "mathematics": [
            {
                "question": "Qu'est-ce qu'une dérivée ?",
                "options": [
                    "Le taux de variation d'une fonction",
                    "L'intégrale d'une fonction",
                    "La limite d'une fonction",
                    "La valeur moyenne d'une fonction"
                ],
                "correct_answer": 0,
                "explanation": "La dérivée représente le taux de variation instantané d'une fonction."
            }
        ],
        "computer_science": [
            {
                "question": "Qu'est-ce qu'un algorithme ?",
                "options": [
                    "Une séquence d'instructions pour résoudre un problème",
                    "Un langage de programmation",
                    "Une base de données",
                    "Un système d'exploitation"
                ],
                "correct_answer": 0,
                "explanation": "Un algorithme est une séquence d'instructions logiques pour résoudre un problème."
            }
        ]
    }
    
    questions = demo_quizzes.get(subject, demo_quizzes["physics"])[:num_questions]
    
    return {
        "questions": questions,
        "quiz_id": f"demo_{module.get('id', 'unknown')}",
        "module_id": str(module.get('id', 'unknown'))
    }
    
    @staticmethod
    async def get_immersive_context(
        module_id: str,
        mode: str,
        scene_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Génère un contexte IA pour une expérience immersive"""
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        # Si OpenAI n'est pas disponible, utiliser le mode démo
        if not client:
            logger.info("Mode démo: contexte immersif statique")
            mode_guidance = {
                'ar': 'Explorez les concepts en réalité augmentée. Déplacez votre appareil pour voir les objets dans votre environnement.',
                'vr': 'Plongez dans une expérience immersive en réalité virtuelle. Utilisez les contrôles pour interagir.',
                'unity': 'Expérience Unity WebGL chargée. Utilisez les contrôles à l\'écran pour naviguer.'
            }
            return {
                "guidance": mode_guidance.get(mode, "Profitez de l'expérience immersive !"),
                "tips": [
                    "Assurez-vous d'avoir un bon éclairage",
                    "Utilisez les contrôles à l'écran pour interagir",
                    "Explorez tous les angles pour une meilleure compréhension"
                ]
            }
        
        try:
            title = module.get("title", "")
            description = module.get("description", "")
            subject = module.get("subject", "")
            
            # Vérifier que les simulations 3D sont uniquement pour physique et chimie
            allowed_subjects_for_3d = ['physics', 'chemistry']
            is_3d_allowed = subject.lower() in allowed_subjects_for_3d
            
            if mode == '3d' and not is_3d_allowed:
                return {
                    "guidance": "Les simulations 3D interactives sont uniquement disponibles pour les modules de Physique et Chimie.",
                    "tips": [
                        "Explorez les autres onglets pour accéder au contenu du module",
                        "Utilisez le chat avec Kaïros pour poser vos questions",
                        "Consultez les ressources et les quiz disponibles"
                    ]
                }
            
            mode_descriptions = {
                'ar': 'réalité augmentée',
                'vr': 'réalité virtuelle',
                'unity': 'expérience Unity WebGL interactive',
                '3d': 'simulation 3D interactive'
            }
            
            prompt = f"""Tu es Kaïros, un assistant IA pour une plateforme d'apprentissage immersive.

L'utilisateur explore le module "{title}" en mode {mode_descriptions.get(mode, mode)}.

Module: {title}
Description: {description}
Matière: {subject}
Type de scène: {scene_type or 'général'}

{"IMPORTANT: Les simulations 3D sont uniquement disponibles pour la Physique et la Chimie." if mode == '3d' else ""}

Génère un guide court et pratique (2-3 phrases) pour aider l'utilisateur à tirer le meilleur parti de cette expérience immersive.
Ajoute 3 conseils pratiques pour l'interaction.

Réponds en français, de manière encourageante et pédagogique."""

            async def create_immersive_call():
                create_params = {
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": "Tu es un assistant pédagogique pour l'apprentissage immersif."},
                        {"role": "user", "content": prompt}
                    ],
                    "timeout": 20.0
                }
                # Ajouter temperature seulement si le modèle le supporte
                create_params.update(_get_temperature_param(AI_MODEL, 0.7))
                create_params.update(_get_max_tokens_param(AI_MODEL, 300))
                return client.chat.completions.create(**create_params)
            
            response = await retry_with_backoff(
                create_immersive_call,
                max_retries=2,
                initial_delay=1.0,
                max_delay=5.0
            )
            
            ai_response = response.choices[0].message.content
            
            # Extraire les conseils (format simple)
            lines = ai_response.split('\n')
            guidance = lines[0] if lines else ai_response
            tips = [line.strip('- •').strip() for line in lines[1:] if line.strip() and len(line.strip()) > 10][:3]
            
            if not tips:
                tips = [
                    "Explorez tous les angles de vue",
                    "Interagissez avec les objets pour mieux comprendre",
                    "Prenez votre temps pour assimiler les concepts"
                ]
            
            return {
                "guidance": guidance,
                "tips": tips
            }
        except Exception as e:
            logger.error(f"Erreur lors de la génération du contexte immersif: {e}")
            mode_descriptions = {
                'ar': 'réalité augmentée',
                'vr': 'réalité virtuelle',
                'unity': 'expérience Unity WebGL interactive'
            }
            return {
                "guidance": f"Profitez de l'expérience {mode_descriptions.get(mode, mode)} pour explorer {title} !",
                "tips": [
                    "Explorez tous les angles",
                    "Interagissez avec les éléments",
                    "Prenez votre temps"
                ]
            }


