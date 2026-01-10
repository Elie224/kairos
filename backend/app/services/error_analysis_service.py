"""
Service pour analyser les erreurs et générer des explications ciblées
Mode "Apprendre par l'erreur"
"""
from typing import Dict, Any, List, Optional
from app.services.ai_service import client, AI_MODEL
import logging
import json

logger = logging.getLogger(__name__)


class ErrorAnalysisService:
    """Service d'analyse d'erreurs"""
    
    @staticmethod
    async def analyze_error(
        user_answer: str,
        correct_answer: str,
        question: str,
        module_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyse une erreur et génère une explication ciblée
        """
        try:
            if not client:
                return ErrorAnalysisService._get_demo_analysis()
            
            prompt = f"""Analyse cette erreur d'apprentissage et génère une explication ciblée :

Question : {question}
Réponse de l'élève : {user_answer}
Réponse correcte : {correct_answer}
Contexte du module : {json.dumps(module_context or {}, indent=2, ensure_ascii=False)}

Identifie :
1. Le type d'erreur (conceptuelle, calcul, compréhension, application)
2. La cause probable de l'erreur
3. Une explication ciblée sur le blocage spécifique
4. Des suggestions pour éviter cette erreur

Réponds en JSON :
{{
    "error_type": "<type d'erreur>",
    "error_category": "<catégorie>",
    "probable_cause": "<cause probable>",
    "targeted_explanation": "<explication ciblée>",
    "comparison": "<comparaison avec la bonne réponse>",
    "suggestions": ["suggestion1", "suggestion2"],
    "similar_exercises_needed": true/false
}}"""

            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert pédagogique spécialisé dans l'analyse d'erreurs d'apprentissage."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            create_params.update(_get_max_tokens_param(AI_MODEL, 800))
            response = await client.chat.completions.create(**create_params)
            
            response_text = response.choices[0].message.content
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    analysis = json.loads(response_text[json_start:json_end])
                    return analysis
            except json.JSONDecodeError:
                pass
            
            return ErrorAnalysisService._get_demo_analysis()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse d'erreur: {e}", exc_info=True)
            return ErrorAnalysisService._get_demo_analysis()
    
    @staticmethod
    def _get_demo_analysis() -> Dict[str, Any]:
        """Analyse de démo"""
        return {
            "error_type": "conceptuelle",
            "error_category": "compréhension",
            "probable_cause": "Mauvaise compréhension du concept de base",
            "targeted_explanation": "L'erreur vient d'une incompréhension du concept fondamental.",
            "comparison": "La bonne réponse utilise une approche différente.",
            "suggestions": ["Revoir les bases", "Faire des exercices similaires"],
            "similar_exercises_needed": True
        }


