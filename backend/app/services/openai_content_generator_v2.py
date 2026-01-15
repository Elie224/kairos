"""
Service OpenAI pour générer du contenu pédagogique avec les modèles GPT-5.2, GPT-5-mini, GPT-5-nano
Selon les spécifications fournies
"""
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, APITimeoutError
from app.config import settings
from app.repositories.module_repository import ModuleRepository
from app.utils.retry import retry_with_backoff
from app.models import Subject, Difficulty, QuizQuestion, TDExercise, TPStep

logger = logging.getLogger(__name__)

# Initialiser le client OpenAI
openai_client = None
GPT_5_2_MODEL = "gpt-5.2"  # Expert - Raisonnement complexe
GPT_5_MINI_MODEL = "gpt-5-mini"  # Principal - Pédagogique
GPT_5_NANO_MODEL = "gpt-5-nano"  # Rapide - Économique

def _initialize_openai_client():
    """Initialise le client OpenAI"""
    global openai_client
    if settings.openai_api_key:
        try:
            import httpx
            http_client_kwargs = {
                "timeout": 120.0,
                "limits": httpx.Limits(max_keepalive_connections=10, max_connections=50)
            }
            proxy = getattr(settings, "openai_proxy", None)
            if proxy:
                http_client_kwargs["proxy"] = proxy
            http_client = httpx.Client(**http_client_kwargs)
            openai_client = OpenAI(
                api_key=settings.openai_api_key,
                http_client=http_client
            )
            logger.info("✅ Client OpenAI initialisé avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation OpenAI: {e}")
            openai_client = None
    else:
        logger.warning("⚠️ OpenAI API key non configurée")

_initialize_openai_client()


class OpenAIContentGeneratorV2:
    """Service pour la génération de contenu éducatif avec les modèles GPT-5.2, GPT-5-mini, GPT-5-nano"""
    
    @staticmethod
    async def _call_openai_chat(
        messages: List[Dict[str, str]],
        model: str = GPT_5_MINI_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        """Appelle l'API OpenAI avec retry"""
        if not openai_client:
            raise ValueError("OpenAI client non initialisé. Vérifiez OPENAI_API_KEY.")
        
        async def _do_call():
            from app.services.ai_service import _get_max_tokens_param
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            # Utiliser _get_max_tokens_param pour gérer max_tokens vs max_completion_tokens
            params.update(_get_max_tokens_param(model, max_tokens))
            if response_format:
                params["response_format"] = response_format
            
            response = await asyncio.to_thread(
                openai_client.chat.completions.create,
                **params
            )
            return response.choices[0].message.content
        
        return await retry_with_backoff(
            _do_call,
            max_retries=3,
            initial_delay=1.0,
            max_delay=10.0,
            exceptions=(APIConnectionError, APITimeoutError, RateLimitError)
        )
    
    @staticmethod
    async def generate_td_advanced(
        module_id: str,
        num_exercises: int = 5,
        difficulty: Optional[Difficulty] = None,
        language: str = "fr"
    ) -> List[TDExercise]:
        """
        Génère des TD avancés avec GPT-5.2 (Expert)
        Usage: Examens, TD avancés, TP Machine Learning, corrections détaillées
        """
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            raise ValueError("Module non trouvé")
        
        system_prompt = f"""Tu es un professeur universitaire expert en mathématiques et machine learning.
Ton objectif est de générer des contenus pédagogiques avancés pour les étudiants de niveau Licence 3 / Master 1.
Crée un contenu structuré comprenant :
1. Objectifs pédagogiques précis
2. Une série d'exercices progressifs (algèbre, probabilités, machine learning)
3. Des TP avec instructions pratiques et jeux de données simulés
4. Corrigés détaillés et explicatifs
5. Barème et astuces méthodologiques

Format de sortie : JSON structuré
{{
  "titre": "",
  "niveau": "L3/M1",
  "exercices": [
    {{
      "type": "TD/TP/Examen",
      "enonce": "",
      "solution": "",
      "points": ""
    }}
  ]
}}

LANGUE : Génère TOUJOURS en {language}."""
        
        user_prompt = f"Génère {num_exercises} exercices de TD avancés pour le module '{module['title']}' ({module.get('description', '')})."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_json_str = await OpenAIContentGeneratorV2._call_openai_chat(
                messages,
                model=GPT_5_2_MODEL,
                max_tokens=4000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            response_data = json.loads(response_json_str)
            if "exercices" in response_data:
                return [TDExercise(**ex) for ex in response_data["exercices"]]
            return []
        except Exception as e:
            logger.error(f"Erreur génération TD avancé: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def generate_td_standard(
        module_id: str,
        num_exercises: int = 5,
        difficulty: Optional[Difficulty] = None,
        language: str = "fr"
    ) -> List[TDExercise]:
        """
        Génère des TD standards avec GPT-5-mini (Principal)
        Usage: TD standards, quiz, explications de cours, exercices progressifs
        """
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            raise ValueError("Module non trouvé")
        
        system_prompt = f"""Tu es un professeur pédagogue en mathématiques et machine learning.
Génère un TD ou quiz pour les étudiants de Licence 3.
Le contenu doit inclure :
1. Titre du TD ou quiz
2. Liste de 5 à 10 exercices variés (probabilités, algèbre, ML)
3. Corrigés simples et clairs pour chaque exercice
4. Suggestions de difficulté pour chaque exercice (facile, moyen, difficile)
5. Formatage clair pour intégration dans une application

Sortie : JSON structuré
{{
  "titre": "",
  "niveau": "L3",
  "exercices": [
    {{
      "type": "TD/Quiz",
      "enonce": "",
      "solution": "",
      "difficulte": ""
    }}
  ]
}}

LANGUE : Génère TOUJOURS en {language}."""
        
        user_prompt = f"Génère {num_exercises} exercices de TD pour le module '{module['title']}' ({module.get('description', '')})."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_json_str = await OpenAIContentGeneratorV2._call_openai_chat(
                messages,
                model=GPT_5_MINI_MODEL,
                max_tokens=2000,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            response_data = json.loads(response_json_str)
            if "exercices" in response_data:
                return [TDExercise(**ex) for ex in response_data["exercices"]]
            return []
        except Exception as e:
            logger.error(f"Erreur génération TD standard: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def generate_qcm_rapide(
        module_id: str,
        num_questions: int = 10,
        language: str = "fr"
    ) -> List[Dict[str, Any]]:
        """
        Génère des QCM rapides avec GPT-5-nano (Rapide)
        Usage: QCM, flash-cards, vérification de réponses, révisions rapides
        """
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            raise ValueError("Module non trouvé")
        
        system_prompt = f"""Tu es un assistant pédagogique rapide.
Génère un QCM ou flash-card pour étudiants en probabilités, algèbre ou machine learning.
Chaque QCM doit inclure :
1. Question concise
2. 3 à 4 options
3. Indication de la bonne réponse
4. Explication courte si nécessaire

Sortie : JSON simple
{{
  "question": "",
  "options": [],
  "bonne_reponse": "",
  "explication_courte": ""
}}

LANGUE : Génère TOUJOURS en {language}."""
        
        user_prompt = f"Génère {num_questions} questions QCM pour le module '{module['title']}' ({module.get('description', '')})."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response_json_str = await OpenAIContentGeneratorV2._call_openai_chat(
                messages,
                model=GPT_5_NANO_MODEL,
                max_tokens=1000,
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            response_data = json.loads(response_json_str)
            if "questions" in response_data:
                return response_data["questions"]
            elif isinstance(response_data, list):
                return response_data
            return []
        except Exception as e:
            logger.error(f"Erreur génération QCM: {e}", exc_info=True)
            raise
