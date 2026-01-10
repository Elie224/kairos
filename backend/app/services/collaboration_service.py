"""
Service pour la collaboration intelligente
Travail en groupe assisté par IA
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.repositories.collaboration_repository import CollaborationRepository
from app.repositories.learning_profile_repository import LearningProfileRepository
from app.services.ai_service import client, AI_MODEL
import logging
import json

logger = logging.getLogger(__name__)


class CollaborationService:
    """Service de collaboration"""
    
    @staticmethod
    async def create_smart_group(
        user_ids: List[str],
        module_id: str,
        group_size: int = 4
    ) -> Dict[str, Any]:
        """
        Crée un groupe intelligent avec répartition automatique des rôles
        """
        try:
            # Analyser les profils des utilisateurs
            profiles = []
            for user_id in user_ids[:group_size]:
                profile = await LearningProfileRepository.find_by_user_id(user_id)
                if profile:
                    profiles.append({
                        "user_id": user_id,
                        "profile": profile
                    })
            
            # Attribuer les rôles avec IA
            roles = await CollaborationService._assign_roles_with_ai(profiles, module_id)
            
            # Créer le groupe
            group_data = {
                "module_id": module_id,
                "members": [
                    {
                        "user_id": p["user_id"],
                        "role": roles.get(p["user_id"], "member")
                    }
                    for p in profiles
                ],
                "created_at": datetime.now(timezone.utc),
                "status": "active"
            }
            
            saved_group = await CollaborationRepository.create_group(group_data)
            return saved_group
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du groupe: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def _assign_roles_with_ai(
        profiles: List[Dict[str, Any]],
        module_id: str
    ) -> Dict[str, str]:
        """Attribue les rôles avec IA"""
        if not client or not profiles:
            # Attribution basique
            roles = ["leader", "researcher", "presenter", "reviewer"]
            return {
                profiles[i]["user_id"]: roles[i % len(roles)]
                for i in range(len(profiles))
            }
        
        try:
            profiles_summary = [
                {
                    "user_id": p["user_id"],
                    "level": p["profile"].get("current_level", "beginner"),
                    "cognitive_profile": p["profile"].get("cognitive_profile", "mixed"),
                    "accuracy": p["profile"].get("accuracy_rate", 0.5)
                }
                for p in profiles
            ]
            
            prompt = f"""Attribue des rôles optimaux pour un travail de groupe sur le module {module_id}.

Profils des membres :
{json.dumps(profiles_summary, indent=2, ensure_ascii=False)}

Rôles disponibles :
- leader : Guide le groupe, organise le travail
- researcher : Recherche les informations, approfondit les concepts
- presenter : Présente les résultats, communique
- reviewer : Vérifie le travail, corrige les erreurs

Réponds en JSON :
{{
    "roles": {{
        "user_id_1": "leader",
        "user_id_2": "researcher",
        ...
    }}
}}"""

            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en travail collaboratif. Attribue les rôles pour optimiser l'apprentissage."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5
            }
            create_params.update(_get_max_tokens_param(AI_MODEL, 500))
            response = await client.chat.completions.create(**create_params)
            
            response_text = response.choices[0].message.content
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(response_text[json_start:json_end])
                    return result.get("roles", {})
            except json.JSONDecodeError:
                pass
            
            # Fallback
            roles_list = ["leader", "researcher", "presenter", "reviewer"]
            return {
                profiles[i]["user_id"]: roles_list[i % len(roles_list)]
                for i in range(len(profiles))
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'attribution de rôles: {e}", exc_info=True)
            roles_list = ["leader", "researcher", "presenter", "reviewer"]
            return {
                profiles[i]["user_id"]: roles_list[i % len(roles_list)]
                for i in range(len(profiles))
            }
    
    @staticmethod
    async def generate_group_feedback(
        group_id: str,
        work_submitted: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère un feedback collectif pour le groupe
        """
        try:
            if not client:
                return {
                    "feedback": "Bon travail de groupe !",
                    "strengths": ["Collaboration efficace"],
                    "improvements": ["Continuez ainsi"]
                }
            
            group = await CollaborationRepository.get_group(group_id)
            if not group:
                raise ValueError("Groupe non trouvé")
            
            prompt = f"""Analyse ce travail de groupe et génère un feedback constructif :

Travail soumis :
{json.dumps(work_submitted, indent=2, ensure_ascii=False)}

Groupe : {group_id}

Génère un feedback qui :
1. Identifie les points forts
2. Suggère des améliorations
3. Encourage la collaboration

Réponds en JSON :
{{
    "feedback": "<feedback général>",
    "strengths": ["force1", "force2"],
    "improvements": ["amélioration1", "amélioration2"],
    "individual_feedback": {{
        "user_id": "<feedback personnalisé>"
    }}
}}"""

            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en pédagogie collaborative. Génère des feedbacks constructifs."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.5
            }
            create_params.update(_get_max_tokens_param(AI_MODEL, 800))
            response = await client.chat.completions.create(**create_params)
            
            response_text = response.choices[0].message.content
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    feedback = json.loads(response_text[json_start:json_end])
                    return feedback
            except json.JSONDecodeError:
                pass
            
            return {
                "feedback": "Travail de groupe analysé.",
                "strengths": [],
                "improvements": []
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de feedback: {e}", exc_info=True)
            return {
                "feedback": "Erreur lors de l'analyse.",
                "strengths": [],
                "improvements": []
            }


