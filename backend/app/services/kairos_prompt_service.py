"""
Service pour gérer les prompts officiels Kairos
"""
from typing import Dict, Any, Optional, List
import json
import logging
from app.prompts.kairos_prompts import (
    SYSTEM_PROMPT,
    get_prompt,
    get_system_prompt,
    get_gamification_prompt,
    get_recommendation_prompt,
    MATHEMATICS_PROMPTS,
    PHYSICS_PROMPTS,
    CHEMISTRY_PROMPTS,
    AI_ML_PROMPTS,
    OTHER_SUBJECTS_PROMPTS,
    GAMIFICATION_PROMPTS,
    RECOMMENDATION_PROMPT
)

logger = logging.getLogger(__name__)


class KairosPromptService:
    """Service pour gérer les prompts officiels Kairos"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """Retourne le prompt système global Kairos"""
        return get_system_prompt()
    
    @staticmethod
    def get_subject_prompt(
        subject: str,
        topic: str,
        concept: str = None,
        level: str = "intermediate"
    ) -> str:
        """
        Récupère un prompt pour une matière spécifique
        
        Args:
            subject: La matière (mathematics, physics, chemistry, etc.)
            topic: Le sujet spécifique (functions_trigonometry, mechanics_dynamics, etc.)
            concept: Le concept à expliquer (optionnel)
            level: Le niveau (beginner, intermediate, advanced)
        
        Returns:
            Le prompt formaté
        """
        try:
            prompt = get_prompt(subject, topic, level)
            if concept:
                prompt = prompt.replace("{concept}", concept)
            return prompt
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du prompt: {e}")
            return SYSTEM_PROMPT
    
    @staticmethod
    def get_visualization_prompt(
        subject: str,
        concept: str,
        level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour créer une visualisation interactive
        
        Args:
            subject: La matière
            concept: Le concept à visualiser
            level: Le niveau
        
        Returns:
            Dict avec le prompt et les métadonnées
        """
        topic_map = {
            "mathematics": "functions_trigonometry",
            "physics": "mechanics_dynamics",
            "chemistry": "general_chemistry",
            "computer_science": "machine_learning",
            "biology": "biology",
            "geography": "geography",
            "economics": "economics",
            "history": "history"
        }
        
        topic = topic_map.get(subject, "functions_trigonometry")
        prompt = KairosPromptService.get_subject_prompt(subject, topic, concept, level)
        
        return {
            "prompt": prompt,
            "subject": subject,
            "concept": concept,
            "level": level,
            "response_format": "json"
        }
    
    @staticmethod
    def get_quest_prompt(
        user_profile: Dict[str, Any],
        subject: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour créer une quête personnalisée
        
        Args:
            user_profile: Profil de l'utilisateur
            subject: Matière optionnelle pour la quête
        
        Returns:
            Dict avec le prompt formaté
        """
        profile_str = json.dumps(user_profile, ensure_ascii=False, indent=2)
        prompt = get_gamification_prompt("quest_generation", user_profile=profile_str)
        
        return {
            "prompt": prompt,
            "user_profile": user_profile,
            "subject": subject,
            "response_format": "json"
        }
    
    @staticmethod
    def get_badge_prompt(user_progress: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un prompt pour attribuer un badge
        
        Args:
            user_progress: Progression de l'utilisateur
        
        Returns:
            Dict avec le prompt formaté
        """
        progress_str = json.dumps(user_progress, ensure_ascii=False, indent=2)
        prompt = get_gamification_prompt("badge_attribution", user_progress=progress_str)
        
        return {
            "prompt": prompt,
            "user_progress": user_progress,
            "response_format": "json"
        }
    
    @staticmethod
    def get_feedback_prompt(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Génère un prompt pour un feedback intelligent
        
        Args:
            errors: Liste des erreurs de l'utilisateur
        
        Returns:
            Dict avec le prompt formaté
        """
        errors_str = json.dumps(errors, ensure_ascii=False, indent=2)
        prompt = get_gamification_prompt("intelligent_feedback", errors=errors_str)
        
        return {
            "prompt": prompt,
            "errors": errors,
            "response_format": "json"
        }
    
    @staticmethod
    def get_recommendation_prompt(user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un prompt pour une recommandation IA
        
        Args:
            user_profile: Profil de l'utilisateur
        
        Returns:
            Dict avec le prompt formaté
        """
        profile_str = json.dumps(user_profile, ensure_ascii=False, indent=2)
        prompt = get_recommendation_prompt(user_profile=profile_str)
        
        return {
            "prompt": prompt,
            "user_profile": user_profile,
            "response_format": "json"
        }
    
    @staticmethod
    def get_available_topics(subject: str) -> List[str]:
        """
        Retourne la liste des topics disponibles pour une matière
        
        Args:
            subject: La matière
        
        Returns:
            Liste des topics disponibles
        """
        topics_map = {
            "mathematics": list(MATHEMATICS_PROMPTS.keys()),
            "physics": list(PHYSICS_PROMPTS.keys()),
            "chemistry": list(CHEMISTRY_PROMPTS.keys()),
            "computer_science": list(AI_ML_PROMPTS.keys()),
            "biology": ["biology"],
            "geography": ["geography"],
            "economics": ["economics"],
            "history": ["history"]
        }
        
        return topics_map.get(subject, [])
