"""
Service OpenAI pour générer du contenu pédagogique (TD, TP, Quiz)
Application d'apprentissage immersive
"""
from typing import Dict, Any, List, Optional
from openai import OpenAI, APIError, RateLimitError
from app.config import settings
from app.repositories.module_repository import ModuleRepository
import logging
import json

logger = logging.getLogger(__name__)

# Initialiser le client OpenAI
client = None

def _initialize_openai_client():
    """Initialise le client OpenAI"""
    global client
    if settings.openai_api_key:
        try:
            import httpx
            http_client_kwargs = {
                "timeout": 120.0,
                "limits": httpx.Limits(max_keepalive_connections=5, max_connections=10)
            }
            
            proxy = getattr(settings, "openai_proxy", None)
            if proxy:
                http_client_kwargs["proxy"] = proxy
            
            http_client = httpx.Client(**http_client_kwargs)
            client = OpenAI(
                api_key=settings.openai_api_key,
                http_client=http_client
            )
            logger.info("✅ Client OpenAI initialisé pour génération de contenu")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation OpenAI: {e}")
            client = None
    else:
        logger.warning("⚠️ OpenAI API key non configurée")

_initialize_openai_client()


class OpenAIContentGenerator:
    """Service pour générer du contenu pédagogique avec OpenAI"""
    
    @staticmethod
    async def generate_td(
        module_title: str,
        lesson_content: str,
        subject: str,
        difficulty: str,
        language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Génère un TD (Travaux Dirigés) avec OpenAI
        
        Args:
            module_title: Titre du module
            lesson_content: Contenu de la leçon
            subject: Matière (mathematics, computer_science)
            difficulty: Niveau de difficulté
            language: Langue (fr, en)
        
        Returns:
            Dict avec le TD généré
        """
        if not client:
            logger.warning("OpenAI non configuré, retour d'un TD exemple")
            return {
                "title": f"TD - {module_title}",
                "exercises": [
                    {
                        "question": "Exercice exemple",
                        "solution": "Solution exemple"
                    }
                ]
            }
        
        try:
            subject_names = {
                "mathematics": "Mathématiques (Algèbre)",
                "computer_science": "Informatique (Machine Learning)"
            }
            subject_name = subject_names.get(subject, subject)
            
            # Prompt selon les spécifications GPT-5-mini (pédagogique)
            prompt = f"""Tu es un professeur pédagogue en mathématiques et machine learning.
Génère un TD ou quiz pour les étudiants de Licence 3.
Le contenu doit inclure :
1. Titre du TD ou quiz
2. Liste de 5 à 10 exercices variés (probabilités, algèbre, ML)
3. Corrigés simples et clairs pour chaque exercice
4. Suggestions de difficulté pour chaque exercice (facile, moyen, difficile)
5. Formatage clair pour intégration dans une application

CONTEXTE DU MODULE:
Titre: {module_title}
Matière: {subject_name}
Niveau: {difficulty}
Contenu: {lesson_content[:1500]}

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

LANGUE : Génère TOUJOURS en {language}
FORMAT: JSON valide uniquement, pas de markdown"""

            # Utiliser GPT-5-mini pour les TD standards (pédagogique)
            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": settings.gpt_5_mini_model,  # GPT-5-mini pour TD standards
                "messages": [
                    {"role": "system", "content": "Tu es un expert en pédagogie. Génère toujours du JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
            }
            create_params.update(_get_max_tokens_param(settings.gpt_5_mini_model, 3000))
            response = client.chat.completions.create(**create_params)
            
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON si nécessaire
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            td_data = json.loads(content)
            logger.info(f"✅ TD généré pour {module_title}")
            return td_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON TD: {e}")
            logger.error(f"Contenu reçu: {content[:500]}")
            raise
        except Exception as e:
            logger.error(f"Erreur génération TD: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def generate_tp(
        module_title: str,
        lesson_content: str,
        subject: str,
        difficulty: str,
        language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Génère un TP (Travaux Pratiques) avec OpenAI
        
        Args:
            module_title: Titre du module
            lesson_content: Contenu de la leçon
            subject: Matière
            difficulty: Niveau de difficulté
            language: Langue
        
        Returns:
            Dict avec le TP généré
        """
        if not client:
            logger.warning("OpenAI non configuré, retour d'un TP exemple")
            return {
                "title": f"TP - {module_title}",
                "objectives": ["Objectif 1", "Objectif 2"],
                "steps": [
                    {
                        "step": 1,
                        "title": "Étape 1",
                        "description": "Description"
                    }
                ]
            }
        
        try:
            subject_names = {
                "mathematics": "Mathématiques (Algèbre)",
                "computer_science": "Informatique (Machine Learning)"
            }
            subject_name = subject_names.get(subject, subject)
            
            # Pour les TP Machine Learning, utiliser le prompt GPT-5.2 (Expert)
            if subject == "computer_science":
                prompt = f"""Tu es un professeur universitaire expert en mathématiques et machine learning.
Ton objectif est de générer des contenus pédagogiques avancés pour les étudiants de niveau Licence 3 / Master 1.
Crée un contenu structuré comprenant :
1. Objectifs pédagogiques précis
2. Une série d'exercices progressifs (algèbre, probabilités, machine learning)
3. Des TP avec instructions pratiques et jeux de données simulés
4. Corrigés détaillés et explicatifs
5. Barème et astuces méthodologiques

CONTEXTE DU MODULE:
Titre: {module_title}
Matière: {subject_name}
Niveau: {difficulty}
Contenu: {lesson_content[:1500]}

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

LANGUE : Génère TOUJOURS en {language}
FORMAT: JSON valide uniquement, pas de markdown"""
            else:
                # Pour les autres matières, utiliser GPT-5-mini
                prompt = f"""Tu es un professeur pédagogue en mathématiques.
Génère un TP pour les étudiants de Licence 3.
Le contenu doit inclure :
1. Titre du TP
2. Objectifs pédagogiques
3. Étapes pratiques claires
4. Instructions détaillées
5. Critères d'évaluation

CONTEXTE DU MODULE:
Titre: {module_title}
Matière: {subject_name}
Niveau: {difficulty}
Contenu: {lesson_content[:1500]}

Format JSON:
{{
  "title": "Titre du TP",
  "objectives": ["Objectif 1", "Objectif 2"],
  "steps": [
    {{
      "step": 1,
      "title": "Titre de l'étape",
      "description": "Description détaillée",
      "expected_result": "Résultat attendu"
    }}
  ]
}}

LANGUE : Génère TOUJOURS en {language}
FORMAT: JSON valide uniquement, pas de markdown"""

            # Utiliser GPT-5.2 pour les TP Machine Learning (expert)
            from app.services.ai_service import _get_max_tokens_param
            model_to_use = settings.gpt_5_2_model if subject == "computer_science" else settings.gpt_5_mini_model
            max_tokens_value = 4000 if model_to_use == settings.gpt_5_2_model else 3000
            create_params = {
                "model": model_to_use,
                "messages": [
                    {"role": "system", "content": "Tu es un expert en pédagogie. Génère toujours du JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3 if model_to_use == settings.gpt_5_2_model else 0.7,
            }
            create_params.update(_get_max_tokens_param(model_to_use, max_tokens_value))
            response = client.chat.completions.create(**create_params)
            
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            tp_data = json.loads(content)
            logger.info(f"✅ TP généré pour {module_title}")
            return tp_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON TP: {e}")
            logger.error(f"Contenu reçu: {content[:500]}")
            raise
        except Exception as e:
            logger.error(f"Erreur génération TP: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def generate_quiz_questions(
        module_title: str,
        lesson_content: str,
        subject: str,
        num_questions: int = 10,
        difficulty: Optional[str] = None,
        language: str = "fr"
    ) -> List[Dict[str, Any]]:
        """
        Génère des questions de quiz avec OpenAI
        
        Args:
            module_title: Titre du module
            lesson_content: Contenu de la leçon
            subject: Matière
            num_questions: Nombre de questions
            difficulty: Niveau de difficulté (optionnel)
            language: Langue
        
        Returns:
            Liste de questions de quiz
        """
        if not client:
            logger.warning("OpenAI non configuré, retour de questions exemple")
            return [
                {
                    "question": "Question exemple",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": 0,
                    "explanation": "Explication"
                }
            ]
        
        try:
            subject_names = {
                "mathematics": "Mathématiques (Algèbre)",
                "computer_science": "Informatique (Machine Learning)"
            }
            subject_name = subject_names.get(subject, subject)
            
            # Utiliser GPT-5-nano pour les QCM (rapide/économique)
            prompt = f"""Tu es un assistant pédagogique rapide.
Génère un QCM ou flash-card pour étudiants en probabilités, algèbre ou machine learning.
Chaque QCM doit inclure :
1. Question concise
2. 3 à 4 options
3. Indication de la bonne réponse
4. Explication courte si nécessaire

CONTEXTE DU MODULE:
Titre: {module_title}
Matière: {subject_name}
Niveau: {difficulty or 'standard'}
Contenu: {lesson_content[:1500]}

Sortie : JSON simple
{{
  "question": "",
  "options": [],
  "bonne_reponse": "",
  "explication_courte": ""
}}

Génère {num_questions} questions.

LANGUE : Génère TOUJOURS en {language}
FORMAT: JSON valide uniquement, tableau de questions"""

            # Utiliser GPT-5-nano pour les QCM (rapide/économique)
            nano_model = getattr(settings, 'gpt_5_nano_model', 'gpt-5-mini')  # Fallback sur mini si nano n'existe pas
            response = client.chat.completions.create(
                model=nano_model,
                messages=[
                    {"role": "system", "content": "Tu es un assistant pédagogique rapide. Génère toujours du JSON valide."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Nettoyer le JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            questions = json.loads(content)
            
            # S'assurer que c'est une liste
            if isinstance(questions, dict):
                questions = [questions]
            
            logger.info(f"✅ {len(questions)} questions de quiz générées pour {module_title}")
            return questions[:num_questions]  # Limiter au nombre demandé
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON Quiz: {e}")
            logger.error(f"Contenu reçu: {content[:500]}")
            raise
        except Exception as e:
            logger.error(f"Erreur génération Quiz: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def chat_with_student(
        user_message: str,
        module_context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        subject: Optional[str] = None,
        language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Échange conversationnel avec l'étudiant via OpenAI
        
        Args:
            user_message: Message de l'utilisateur
            module_context: Contexte du module actuel
            conversation_history: Historique de la conversation
            subject: Matière
            language: Langue
        
        Returns:
            Dict avec la réponse et suggestions
        """
        if not client:
            return {
                "response": "Mode démo: OpenAI non configuré. Configurez OPENAI_API_KEY pour activer l'assistant IA.",
                "suggestions": []
            }
        
        try:
            subject_names = {
                "mathematics": "Mathématiques (Algèbre)",
                "computer_science": "Informatique (Machine Learning)"
            }
            subject_name = subject_names.get(subject, "apprentissage") if subject else "apprentissage"
            
            system_prompt = f"""Tu es Kaïros, un assistant pédagogique intelligent et bienveillant spécialisé en {subject_name}.

Ta mission est d'aider les étudiants à apprendre de manière naturelle et conversationnelle.

RÈGLES DE CONVERSATION :
- Sois naturel et conversationnel, comme un vrai tuteur humain
- Adapte la longueur de ta réponse au contexte :
  * Salutations simples (bonjour, salut, etc.) → Réponse brève et amicale (1-2 phrases max)
  * Questions simples → Réponse concise et directe (2-4 phrases)
  * Questions complexes → Réponse détaillée et structurée
- Ne donne JAMAIS de longues listes ou structures rigides pour des messages simples
- Sois encourageant et positif
- Explique de manière claire et progressive
- Utilise des exemples concrets quand utile
- Pose des questions de suivi seulement si pertinent
- Adapte-toi au niveau de l'étudiant
- Sois concis mais complet

EXEMPLES :
- Si l'utilisateur dit "bonjour" → Réponds simplement "Bonjour ! Comment puis-je t'aider aujourd'hui ?"
- Si l'utilisateur pose une question → Réponds directement à la question de manière concise

LANGUE: Réponds TOUJOURS en {language}"""
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Ajouter le contexte du module si disponible
            if module_context:
                messages.append({
                    "role": "system",
                    "content": f"CONTEXTE DU MODULE ACTUEL:\n{module_context[:1000]}"
                })
            
            # Ajouter l'historique de conversation
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Garder les 10 derniers messages
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": user_message})
            
            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": settings.gpt_5_mini_model,  # GPT-5-mini pour le chat
                "messages": messages,
                "temperature": 0.7,
            }
            create_params.update(_get_max_tokens_param(settings.gpt_5_mini_model, 1000))
            response = client.chat.completions.create(**create_params)
            
            ai_response = response.choices[0].message.content.strip()
            
            # Générer des suggestions de questions
            suggestions = [
                "Peux-tu expliquer plus en détail ?",
                "Donne-moi un exemple pratique",
                "Quelle est la prochaine étape ?"
            ]
            
            return {
                "response": ai_response,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Erreur chat avec étudiant: {e}", exc_info=True)
            return {
                "response": "Désolé, une erreur s'est produite. Veuillez réessayer.",
                "suggestions": []
            }
