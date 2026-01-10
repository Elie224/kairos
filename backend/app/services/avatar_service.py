"""
Service pour l'Avatar IA Enseignant
Prof virtuel 3D avec explications orales
"""
from typing import Dict, Any, Optional, List
from app.services.ai_service import client, AI_MODEL
import logging
import json

logger = logging.getLogger(__name__)


class AvatarService:
    """Service pour l'avatar enseignant IA"""
    
    @staticmethod
    async def generate_explanation_script(
        content: str,
        explanation_type: str = "step_by_step"
    ) -> Dict[str, Any]:
        """
        Génère un script d'explication pour l'avatar
        """
        try:
            if not client:
                return {
                    "script": content,
                    "gestures": [],
                    "expressions": [],
                    "timing": []
                }
            
            prompt = f"""Crée un script d'explication pour un avatar enseignant 3D.

Contenu à expliquer :
{content}

Type d'explication : {explanation_type}

Génère un script avec :
1. Le texte à prononcer (divisé en phrases courtes)
2. Les gestes à faire à chaque moment
3. Les expressions faciales
4. Le timing (durée de chaque phrase)

Réponds en JSON :
{{
    "script": [
        {{
            "text": "<phrase à prononcer>",
            "gesture": "<geste>",
            "expression": "<expression>",
            "duration": <durée en secondes>
        }},
        ...
    ],
    "total_duration": <durée totale>
}}"""

            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en animation et pédagogie. Crée des scripts pour avatar enseignant."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5
            }
            create_params.update(_get_max_tokens_param(AI_MODEL, 1500))
            response = await client.chat.completions.create(**create_params)
            
            response_text = response.choices[0].message.content
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    script = json.loads(response_text[json_start:json_end])
                    return script
            except json.JSONDecodeError:
                pass
            
            # Fallback
            return {
                "script": [
                    {
                        "text": content[:100],
                        "gesture": "pointing",
                        "expression": "friendly",
                        "duration": 3
                    }
                ],
                "total_duration": 3
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de script: {e}", exc_info=True)
            return {
                "script": [{"text": content, "gesture": "neutral", "expression": "neutral", "duration": 5}],
                "total_duration": 5
            }
    
    @staticmethod
    async def generate_speech_audio(
        text: str,
        language: str = "fr"
    ) -> Dict[str, Any]:
        """
        Génère l'audio pour la synthèse vocale
        Note: Utilise Web Speech API côté frontend ou service cloud
        """
        # Pour l'instant, retourner les paramètres pour le frontend
        return {
            "text": text,
            "language": language,
            "voice": "fr-FR-Standard-A" if language == "fr" else "en-US-Standard-A",
            "pitch": 1.0,
            "rate": 1.0,
            "volume": 1.0,
            "use_web_speech": True  # Indique d'utiliser Web Speech API
        }
    
    @staticmethod
    def get_avatar_config(
        avatar_type: str = "default"
    ) -> Dict[str, Any]:
        """
        Retourne la configuration de l'avatar
        """
        configs = {
            "default": {
                "model": "teacher_male",
                "animations": {
                    "idle": "idle_animation",
                    "talking": "talking_animation",
                    "pointing": "pointing_animation",
                    "explaining": "explaining_animation"
                },
                "expressions": {
                    "friendly": "smile",
                    "serious": "neutral",
                    "encouraging": "warm_smile",
                    "thinking": "thoughtful"
                }
            },
            "female": {
                "model": "teacher_female",
                "animations": {
                    "idle": "idle_animation_f",
                    "talking": "talking_animation_f",
                    "pointing": "pointing_animation_f",
                    "explaining": "explaining_animation_f"
                },
                "expressions": {
                    "friendly": "smile_f",
                    "serious": "neutral_f",
                    "encouraging": "warm_smile_f",
                    "thinking": "thoughtful_f"
                }
            }
        }
        
        return configs.get(avatar_type, configs["default"])


