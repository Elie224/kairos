"""
Service d'auto-évaluation IA - L'IA évalue ses propres réponses
"""
from typing import Dict, Any, Optional
from app.services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)


class AISelfEvaluationService:
    """Service pour l'auto-évaluation des réponses IA"""
    
    @staticmethod
    async def evaluate_response(
        question: str,
        response: str,
        model: str = "gpt-5-mini"
    ) -> Dict[str, Any]:
        """Évalue une réponse IA (clarté, cohérence, complétude)"""
        try:
            evaluation_prompt = f"""Tu es un évaluateur de réponses pédagogiques. Évalue cette réponse selon 3 critères (0-100):

Question: {question}
Réponse à évaluer: {response}

Critères d'évaluation:
1. CLARTÉ (0-100): La réponse est-elle claire et compréhensible?
2. COHÉRENCE (0-100): La réponse est-elle cohérente avec la question?
3. COMPLÉTUDE (0-100): La réponse couvre-t-elle suffisamment le sujet?

Réponds UNIQUEMENT avec un JSON valide dans ce format:
{{
  "clarity": 85,
  "coherence": 90,
  "completeness": 75,
  "overall_score": 83,
  "feedback": "Réponse claire et cohérente, mais pourrait être plus complète",
  "needs_improvement": false
}}
"""
            
            # Utiliser un user_id système pour l'auto-évaluation
            evaluation_response = await AIService.chat_with_ai(
                user_id="system_evaluation",
                message=evaluation_prompt,
                language="fr",
                expert_mode=(model == "gpt-5.2")  # Utiliser expert_mode pour les modèles plus puissants
            )
            
            # Parser la réponse JSON
            import json
            try:
                evaluation_text = evaluation_response.get("response", "")
                # Extraire le JSON de la réponse
                json_match = None
                if "{" in evaluation_text:
                    start = evaluation_text.find("{")
                    end = evaluation_text.rfind("}") + 1
                    json_match = evaluation_text[start:end]
                
                if json_match:
                    evaluation_data = json.loads(json_match)
                    return {
                        "clarity": evaluation_data.get("clarity", 0),
                        "coherence": evaluation_data.get("coherence", 0),
                        "completeness": evaluation_data.get("completeness", 0),
                        "overall_score": evaluation_data.get("overall_score", 0),
                        "feedback": evaluation_data.get("feedback", ""),
                        "needs_improvement": evaluation_data.get("needs_improvement", False),
                        "evaluated_at": evaluation_response.get("created_at")
                    }
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Erreur lors du parsing de l'évaluation: {e}")
            
            # Fallback si le parsing échoue
            return {
                "clarity": 70,
                "coherence": 70,
                "completeness": 70,
                "overall_score": 70,
                "feedback": "Évaluation automatique non disponible",
                "needs_improvement": False,
                "evaluated_at": None
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'auto-évaluation: {e}")
            return {
                "clarity": 70,
                "coherence": 70,
                "completeness": 70,
                "overall_score": 70,
                "feedback": "Erreur lors de l'évaluation",
                "needs_improvement": False,
                "evaluated_at": None
            }
    
    @staticmethod
    async def improve_response_if_needed(
        question: str,
        original_response: str,
        evaluation: Dict[str, Any],
        model: str = "gpt-5.2"
    ) -> Optional[str]:
        """Améliore une réponse si le score est trop bas"""
        try:
            overall_score = evaluation.get("overall_score", 100)
            needs_improvement = evaluation.get("needs_improvement", False)
            
            # Seuil d'amélioration (score < 70)
            if overall_score >= 70 and not needs_improvement:
                return None  # Pas besoin d'amélioration
            
            improvement_prompt = f"""Tu es un tuteur pédagogique. Améliore cette réponse pour qu'elle soit plus claire, cohérente et complète.

Question: {question}
Réponse originale: {original_response}
Problèmes identifiés: {evaluation.get('feedback', '')}

Fournis une version améliorée de la réponse qui:
- Est plus claire et compréhensible
- Est plus cohérente avec la question
- Couvre mieux le sujet
- Maintient la même longueur approximative
"""
            
            # Utiliser un user_id système pour l'amélioration
            improved_response = await AIService.chat_with_ai(
                user_id="system_improvement",
                message=improvement_prompt,
                language="fr",
                expert_mode=(model == "gpt-5.2")  # Utiliser expert_mode pour les modèles plus puissants
            )
            
            return improved_response.get("response", None)
        except Exception as e:
            logger.error(f"Erreur lors de l'amélioration de la réponse: {e}")
            return None
