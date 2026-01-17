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
    get_curriculum_prompt,
    get_learner_profile_prompt,
    get_evaluation_prompt,
    get_explainability_prompt,
    get_lab_simulation_prompt,
    get_gamification_advanced_prompt,
    get_multi_agent_prompt,
    get_analytics_prompt,
    get_academic_content_prompt,
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
    
    @staticmethod
    def get_curriculum_prompt_data(
        subject: str,
        level: str,
        objective: str
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour créer un curriculum complet
        
        Args:
            subject: La matière
            level: Le niveau (collège, lycée, université)
            objective: L'objectif (exam, compréhension, rattrapage)
        
        Returns:
            Dict avec le prompt formaté
        """
        prompt = get_curriculum_prompt(subject, level, objective)
        
        return {
            "prompt": prompt,
            "subject": subject,
            "level": level,
            "objective": objective,
            "response_format": "json"
        }
    
    @staticmethod
    def get_learner_profile_prompt_data(
        learning_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour créer un profil cognitif
        
        Args:
            learning_data: Données d'apprentissage de l'utilisateur
        
        Returns:
            Dict avec le prompt formaté
        """
        learning_data_str = json.dumps(learning_data, ensure_ascii=False, indent=2)
        prompt = get_learner_profile_prompt(learning_data_str)
        
        return {
            "prompt": prompt,
            "learning_data": learning_data,
            "response_format": "json"
        }
    
    @staticmethod
    def get_evaluation_prompt_data(
        subject: str,
        level: str,
        evaluation_type: str
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour créer une évaluation
        
        Args:
            subject: La matière
            level: Le niveau
            evaluation_type: Type d'évaluation (formative, summative, adaptive, oral)
        
        Returns:
            Dict avec le prompt formaté
        """
        prompt = get_evaluation_prompt(subject, level, evaluation_type)
        
        return {
            "prompt": prompt,
            "subject": subject,
            "level": level,
            "evaluation_type": evaluation_type,
            "response_format": "json"
        }
    
    @staticmethod
    def get_explainability_prompt_data(
        error_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour expliquer une erreur (Explainable AI)
        
        Args:
            error_analysis: Analyse de l'erreur
        
        Returns:
            Dict avec le prompt formaté
        """
        error_str = json.dumps(error_analysis, ensure_ascii=False, indent=2)
        prompt = get_explainability_prompt(error_str)
        
        return {
            "prompt": prompt,
            "error_analysis": error_analysis,
            "response_format": "json"
        }
    
    @staticmethod
    def get_lab_simulation_prompt_data(
        simulation_request: str
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour créer une simulation de laboratoire
        
        Args:
            simulation_request: Demande de simulation de l'apprenant
        
        Returns:
            Dict avec le prompt formaté
        """
        prompt = get_lab_simulation_prompt(simulation_request)
        
        return {
            "prompt": prompt,
            "simulation_request": simulation_request,
            "response_format": "json"
        }
    
    @staticmethod
    def get_season_prompt_data(
        subject: str,
        theme: str
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour créer une saison pédagogique
        PRIORITÉ 6 - Gamification avancée
        """
        prompt = get_gamification_advanced_prompt("season_generation", subject=subject, theme=theme)
        
        return {
            "prompt": prompt,
            "subject": subject,
            "theme": theme,
            "response_format": "json"
        }
    
    @staticmethod
    def get_evolving_badge_prompt_data(
        badge_type: str,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour évaluer l'évolution d'un badge
        PRIORITÉ 6 - Gamification avancée
        """
        progress_str = json.dumps(progress_data, ensure_ascii=False, indent=2)
        prompt = get_gamification_advanced_prompt("evolving_badge", badge_type=badge_type, progress=progress_str)
        
        return {
            "prompt": prompt,
            "badge_type": badge_type,
            "progress_data": progress_data,
            "response_format": "json"
        }
    
    @staticmethod
    def get_multi_agent_prompt_data(
        agent_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour un agent IA spécifique
        PRIORITÉ 7 - Multi-agents IA
        """
        context_str = json.dumps(context, ensure_ascii=False, indent=2)
        prompt = get_multi_agent_prompt(agent_type, context=context_str)
        
        return {
            "prompt": prompt,
            "agent_type": agent_type,
            "context": context,
            "response_format": "json"
        }
    
    @staticmethod
    def get_analytics_prompt_data(
        prompt_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère un prompt d'analytics
        PRIORITÉ 8 - Analytics & Dashboard IA
        """
        data_str = json.dumps(data, ensure_ascii=False, indent=2)
        prompt = get_analytics_prompt(prompt_type, **{f"{prompt_type}_data": data_str})
        
        return {
            "prompt": prompt,
            "analytics_type": prompt_type,
            "data": data,
            "response_format": "json"
        }
    
    @staticmethod
    def get_academic_content_prompt_data(
        prompt_type: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Génère un prompt pour du contenu académique
        PRIORITÉ 9 - Génération de contenu académique
        """
        prompt = get_academic_content_prompt(prompt_type, **kwargs)
        
        return {
            "prompt": prompt,
            "content_type": prompt_type,
            "parameters": kwargs,
            "response_format": "json"
        }