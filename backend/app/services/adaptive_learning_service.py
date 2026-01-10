"""
Service pour l'IA pédagogique adaptative
Diagnostic automatique du niveau et adaptation dynamique
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.models.adaptive_learning import (
    AdaptiveDiagnostic,
    LearningProfile,
    AdaptiveRecommendation,
    DifficultyAdjustment,
    AdaptiveContentRequest,
    AdaptiveContentResponse,
    CognitiveProfile,
    LearningStyle,
    PerformanceLevel
)
from app.models import Difficulty, Subject
from app.repositories.learning_profile_repository import LearningProfileRepository
from app.repositories.progress_repository import ProgressRepository
from app.repositories.module_repository import ModuleRepository
from app.services.ai_service import AIService
import logging
import statistics

logger = logging.getLogger(__name__)


class AdaptiveLearningService:
    """Service pour l'apprentissage adaptatif"""
    
    @staticmethod
    async def run_initial_diagnostic(
        user_id: str,
        diagnostic_answers: Dict[str, Any]
    ) -> AdaptiveDiagnostic:
        """
        Exécute un diagnostic initial pour déterminer le niveau et le profil
        de l'apprenant
        """
        try:
            # Utiliser l'IA pour analyser les réponses du diagnostic
            # Utiliser l'IA pour analyser les réponses du diagnostic
            diagnostic_prompt = f"""Analyse les réponses suivantes d'un diagnostic pédagogique et retourne un JSON avec:
- overall_score: score global (0-100)
- learning_preferences: {{visual, auditory, kinesthetic, reading, sequential, global, active, reflective}} (valeurs 0-1)
- strengths: liste des points forts
- weaknesses: liste des points faibles

Réponses: {diagnostic_answers}

Retourne uniquement le JSON valide."""
            
            ai_response = await AIService.chat_with_ai(
                user_id=user_id,
                message=diagnostic_prompt,
                language="fr"
            )
            
            # Parser la réponse JSON
            import json
            try:
                ai_analysis = json.loads(ai_response.get("response", "{}"))
            except:
                # Fallback si JSON invalide
                ai_analysis = {
                    "overall_score": 50,
                    "learning_preferences": {},
                    "strengths": [],
                    "weaknesses": []
                }
            
            # Déterminer le niveau initial basé sur les réponses
            initial_level = AdaptiveLearningService._determine_level(
                ai_analysis.get("overall_score", 50)
            )
            
            # Déterminer le profil cognitif
            cognitive_profile = AdaptiveLearningService._determine_cognitive_profile(
                ai_analysis.get("learning_preferences", {})
            )
            
            # Déterminer le style d'apprentissage
            learning_style = AdaptiveLearningService._determine_learning_style(
                ai_analysis.get("learning_preferences", {})
            )
            
            # Recommander une difficulté initiale
            recommended_difficulty = AdaptiveLearningService._recommend_difficulty(
                initial_level
            )
            
            # Créer le profil d'apprentissage
            learning_profile = {
                "user_id": user_id,
                "current_level": initial_level.value,
                "cognitive_profile": cognitive_profile.value,
                "learning_style": learning_style.value,
                "average_response_time": 0.0,
                "accuracy_rate": ai_analysis.get("overall_score", 50) / 100,
                "completion_rate": 0.0,
                "engagement_score": 0.5,
                "current_difficulty": recommended_difficulty.value,
                "difficulty_history": [],
                "adaptation_frequency": 0,
                "preferred_explanation_type": AdaptiveLearningService._get_preferred_explanation(
                    cognitive_profile
                ),
                "preferred_exercise_format": AdaptiveLearningService._get_preferred_format(
                    cognitive_profile
                ),
                "subject_performance": {},
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            await LearningProfileRepository.create_or_update(learning_profile)
            
            # Créer le diagnostic
            diagnostic = AdaptiveDiagnostic(
                user_id=user_id,
                initial_level=initial_level,
                cognitive_profile=cognitive_profile,
                learning_style=learning_style,
                strengths=ai_analysis.get("strengths", []),
                weaknesses=ai_analysis.get("weaknesses", []),
                recommended_difficulty=recommended_difficulty,
                estimated_time_per_module=AdaptiveLearningService._estimate_time(initial_level),
                diagnostic_score=ai_analysis.get("overall_score", 50),
                completed_at=datetime.now(timezone.utc)
            )
            
            logger.info(f"Diagnostic initial créé pour utilisateur {user_id}")
            return diagnostic
            
        except Exception as e:
            logger.error(f"Erreur lors du diagnostic initial: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_learning_profile(user_id: str) -> Optional[LearningProfile]:
        """Récupère le profil d'apprentissage de l'utilisateur"""
        profile_data = await LearningProfileRepository.find_by_user_id(user_id)
        if not profile_data:
            return None
        return LearningProfile(**profile_data)
    
    @staticmethod
    async def adapt_difficulty(
        user_id: str,
        module_id: str,
        performance_data: Dict[str, Any]
    ) -> DifficultyAdjustment:
        """
        Adapte la difficulté d'un module basé sur les performances
        """
        try:
            profile = await AdaptiveLearningService.get_learning_profile(user_id)
            if not profile:
                raise ValueError("Profil d'apprentissage non trouvé")
            
            # Analyser les performances
            score = performance_data.get("score", 0)
            time_spent = performance_data.get("time_spent", 0)
            attempts = performance_data.get("attempts", 1)
            accuracy = performance_data.get("accuracy", 0)
            
            # Récupérer la difficulté actuelle du module
            module = await ModuleRepository.find_by_id(module_id)
            current_difficulty = Difficulty(module.get("difficulty", "beginner"))
            
            # Déterminer la nouvelle difficulté
            new_difficulty = AdaptiveLearningService._calculate_new_difficulty(
                current_difficulty,
                score,
                accuracy,
                attempts,
                profile.current_level
            )
            
            # Créer l'ajustement
            adjustment = DifficultyAdjustment(
                user_id=user_id,
                module_id=module_id,
                previous_difficulty=current_difficulty,
                new_difficulty=new_difficulty,
                reason=AdaptiveLearningService._generate_adjustment_reason(
                    current_difficulty,
                    new_difficulty,
                    score,
                    accuracy
                ),
                performance_data=performance_data,
                adjusted_at=datetime.now(timezone.utc)
            )
            
            # Mettre à jour le profil
            await AdaptiveLearningService._update_profile_from_performance(
                user_id,
                performance_data
            )
            
            logger.info(f"Difficulté adaptée pour {user_id} sur module {module_id}: {current_difficulty} -> {new_difficulty}")
            return adjustment
            
        except Exception as e:
            logger.error(f"Erreur lors de l'adaptation de difficulté: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def generate_adaptive_content(
        request: AdaptiveContentRequest
    ) -> AdaptiveContentResponse:
        """
        Génère du contenu adapté selon le profil de l'utilisateur
        """
        try:
            profile = await AdaptiveLearningService.get_learning_profile(request.user_id)
            if not profile:
                # Créer un profil par défaut si inexistant
                profile = await AdaptiveLearningService._create_default_profile(request.user_id)
            
            # Récupérer le module
            module = await ModuleRepository.find_by_id(request.module_id)
            if not module:
                raise ValueError("Module non trouvé")
            
            # Adapter le contenu selon le profil
            adapted_content = await AdaptiveLearningService._adapt_module_content(
                module,
                profile,
                request.preferred_format
            )
            
            # Générer des explications adaptées
            explanation_style = request.preferred_format or profile.preferred_explanation_type
            explanation_prompt = f"""Adapte le contenu suivant selon le profil cognitif '{profile.cognitive_profile.value}' et le style '{explanation_style}'.
Contenu: {module.get('content', {})}

Génère des explications adaptées en format JSON avec des sections adaptées au profil."""
            
            ai_response = await AIService.chat_with_ai(
                user_id=request.user_id,
                message=explanation_prompt,
                module_id=request.module_id,
                language="fr"
            )
            
            # Parser la réponse
            import json
            try:
                adapted_explanations = json.loads(ai_response.get("response", "{}"))
            except:
                adapted_explanations = module.get("content", {})
            
            # Déterminer la difficulté à utiliser
            difficulty = request.difficulty_override or Difficulty(profile.current_difficulty)
            
            # Estimer le temps
            estimated_time = AdaptiveLearningService._estimate_time_for_content(
                module,
                profile,
                difficulty
            )
            
            response = AdaptiveContentResponse(
                module_id=request.module_id,
                adapted_content={
                    **adapted_content,
                    "explanations": adapted_explanations
                },
                explanation_style=explanation_style,
                difficulty_level=difficulty,
                estimated_time=estimated_time,
                learning_objectives=module.get("learning_objectives", []),
                adaptation_notes=AdaptiveLearningService._generate_adaptation_notes(
                    profile,
                    difficulty
                )
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de contenu adaptatif: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def get_recommendations(
        user_id: str,
        limit: int = 5
    ) -> List[AdaptiveRecommendation]:
        """
        Génère des recommandations adaptatives pour l'utilisateur
        """
        try:
            profile = await AdaptiveLearningService.get_learning_profile(user_id)
            if not profile:
                return []
            
            # Récupérer les progressions récentes
            progressions = await ProgressRepository.find_by_user(user_id, limit=20)
            
            # Analyser les performances
            recommendations = []
            
            # Recommandation 1: Ajustement de difficulté si nécessaire
            if profile.accuracy_rate < 0.6:
                recommendations.append(AdaptiveRecommendation(
                    user_id=user_id,
                    recommendation_type="difficulty_adjustment",
                    current_state={"difficulty": profile.current_difficulty},
                    recommended_state={"difficulty": Difficulty.BEGINNER.value},
                    reasoning="Votre taux de précision est faible. Nous recommandons de commencer par des modules plus faciles.",
                    confidence_score=0.8,
                    created_at=datetime.now(timezone.utc)
                ))
            
            # Recommandation 2: Ajustement du rythme
            if profile.average_response_time > 300:  # Plus de 5 minutes par question
                recommendations.append(AdaptiveRecommendation(
                    user_id=user_id,
                    recommendation_type="pace_adjustment",
                    current_state={"pace": "normal"},
                    recommended_state={"pace": "slower", "suggested_time_per_module": AdaptiveLearningService._estimate_time(PerformanceLevel(profile.current_level)) * 1.5},
                    reasoning="Vous prenez plus de temps que la moyenne. Prenez votre temps, l'apprentissage n'est pas une course.",
                    confidence_score=0.7,
                    created_at=datetime.now(timezone.utc)
                ))
            
            # Recommandation 3: Suggestions de contenu
            # Analyser les matières où l'utilisateur performe le mieux
            best_subjects = AdaptiveLearningService._identify_best_subjects(profile)
            if best_subjects:
                recommendations.append(AdaptiveRecommendation(
                    user_id=user_id,
                    recommendation_type="content_suggestion",
                    current_state={"current_subjects": []},
                    recommended_state={"suggested_subjects": best_subjects},
                    reasoning=f"Vous excellez dans ces domaines. Explorez des modules plus avancés dans ces matières.",
                    confidence_score=0.9,
                    created_at=datetime.now(timezone.utc)
                ))
            
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de recommandations: {e}", exc_info=True)
            return []
    
    # Méthodes utilitaires privées
    
    @staticmethod
    def _determine_level(score: float) -> PerformanceLevel:
        """Détermine le niveau basé sur le score"""
        if score >= 90:
            return PerformanceLevel.EXPERT
        elif score >= 70:
            return PerformanceLevel.ADVANCED
        elif score >= 50:
            return PerformanceLevel.INTERMEDIATE
        else:
            return PerformanceLevel.BEGINNER
    
    @staticmethod
    def _determine_cognitive_profile(preferences: Dict[str, Any]) -> CognitiveProfile:
        """Détermine le profil cognitif"""
        visual_score = preferences.get("visual", 0)
        auditory_score = preferences.get("auditory", 0)
        kinesthetic_score = preferences.get("kinesthetic", 0)
        reading_score = preferences.get("reading", 0)
        
        scores = {
            CognitiveProfile.VISUAL: visual_score,
            CognitiveProfile.AUDITORY: auditory_score,
            CognitiveProfile.KINESTHETIC: kinesthetic_score,
            CognitiveProfile.READING: reading_score
        }
        
        max_profile = max(scores.items(), key=lambda x: x[1])
        if max_profile[1] > 0.7:
            return max_profile[0]
        return CognitiveProfile.MIXED
    
    @staticmethod
    def _determine_learning_style(preferences: Dict[str, Any]) -> LearningStyle:
        """Détermine le style d'apprentissage"""
        sequential_score = preferences.get("sequential", 0)
        global_score = preferences.get("global", 0)
        active_score = preferences.get("active", 0)
        reflective_score = preferences.get("reflective", 0)
        
        if sequential_score > global_score and active_score > reflective_score:
            return LearningStyle.SEQUENTIAL
        elif global_score > sequential_score:
            return LearningStyle.GLOBAL
        elif active_score > reflective_score:
            return LearningStyle.ACTIVE
        else:
            return LearningStyle.REFLECTIVE
    
    @staticmethod
    def _recommend_difficulty(level: PerformanceLevel) -> Difficulty:
        """Recommandation de difficulté basée sur le niveau"""
        mapping = {
            PerformanceLevel.BEGINNER: Difficulty.BEGINNER,
            PerformanceLevel.INTERMEDIATE: Difficulty.INTERMEDIATE,
            PerformanceLevel.ADVANCED: Difficulty.ADVANCED,
            PerformanceLevel.EXPERT: Difficulty.ADVANCED
        }
        return mapping.get(level, Difficulty.BEGINNER)
    
    @staticmethod
    def _estimate_time(level: PerformanceLevel) -> int:
        """Estime le temps par module selon le niveau"""
        mapping = {
            PerformanceLevel.BEGINNER: 45,
            PerformanceLevel.INTERMEDIATE: 30,
            PerformanceLevel.ADVANCED: 20,
            PerformanceLevel.EXPERT: 15
        }
        return mapping.get(level, 30)
    
    @staticmethod
    def _get_preferred_explanation(profile: CognitiveProfile) -> str:
        """Retourne le type d'explication préféré"""
        mapping = {
            CognitiveProfile.VISUAL: "visual",
            CognitiveProfile.AUDITORY: "textual",
            CognitiveProfile.KINESTHETIC: "step_by_step",
            CognitiveProfile.READING: "textual",
            CognitiveProfile.MIXED: "step_by_step"
        }
        return mapping.get(profile, "step_by_step")
    
    @staticmethod
    def _get_preferred_format(profile: CognitiveProfile) -> str:
        """Retourne le format d'exercice préféré"""
        mapping = {
            CognitiveProfile.VISUAL: "simulations",
            CognitiveProfile.AUDITORY: "quiz",
            CognitiveProfile.KINESTHETIC: "exercises",
            CognitiveProfile.READING: "quiz",
            CognitiveProfile.MIXED: "quiz"
        }
        return mapping.get(profile, "quiz")
    
    @staticmethod
    def _calculate_new_difficulty(
        current: Difficulty,
        score: float,
        accuracy: float,
        attempts: int,
        user_level: PerformanceLevel
    ) -> Difficulty:
        """Calcule la nouvelle difficulté basée sur les performances"""
        # Si score très élevé (>90%) et peu de tentatives, augmenter difficulté
        if score >= 90 and attempts <= 2 and current != Difficulty.ADVANCED:
            if current == Difficulty.BEGINNER:
                return Difficulty.INTERMEDIATE
            elif current == Difficulty.INTERMEDIATE:
                return Difficulty.ADVANCED
        
        # Si score très faible (<50%) ou beaucoup de tentatives, diminuer difficulté
        if (score < 50 or accuracy < 0.5) and current != Difficulty.BEGINNER:
            if current == Difficulty.ADVANCED:
                return Difficulty.INTERMEDIATE
            elif current == Difficulty.INTERMEDIATE:
                return Difficulty.BEGINNER
        
        # Sinon, garder la difficulté actuelle
        return current
    
    @staticmethod
    def _generate_adjustment_reason(
        previous: Difficulty,
        new: Difficulty,
        score: float,
        accuracy: float
    ) -> str:
        """Génère une explication pour l'ajustement"""
        if new.value > previous.value:
            return f"Excellent travail ! Votre score de {score:.1f}% et votre précision de {accuracy:.1%} montrent que vous maîtrisez ce niveau. Passons à quelque chose de plus stimulant."
        elif new.value < previous.value:
            return f"Ce module semble trop difficile (score: {score:.1f}%, précision: {accuracy:.1%}). Revenons à des bases plus solides pour mieux progresser."
        else:
            return "La difficulté reste adaptée à votre niveau actuel."
    
    @staticmethod
    async def _update_profile_from_performance(
        user_id: str,
        performance_data: Dict[str, Any]
    ):
        """Met à jour le profil basé sur les performances"""
        profile = await LearningProfileRepository.find_by_user_id(user_id)
        if not profile:
            return
        
        # Mettre à jour les métriques
        new_accuracy = performance_data.get("accuracy", 0)
        new_time = performance_data.get("time_spent", 0)
        
        # Moyenne mobile pour l'accuracy
        current_accuracy = profile.get("accuracy_rate", 0.5)
        updated_accuracy = (current_accuracy * 0.7) + (new_accuracy * 0.3)
        
        # Moyenne mobile pour le temps de réponse
        current_time = profile.get("average_response_time", 0)
        updated_time = (current_time * 0.7) + (new_time * 0.3)
        
        update_data = {
            "accuracy_rate": updated_accuracy,
            "average_response_time": updated_time,
            "updated_at": datetime.now(timezone.utc)
        }
        
        await LearningProfileRepository.update(user_id, update_data)
    
    @staticmethod
    async def _adapt_module_content(
        module: Dict[str, Any],
        profile: LearningProfile,
        preferred_format: Optional[str]
    ) -> Dict[str, Any]:
        """Adapte le contenu d'un module selon le profil"""
        content = module.get("content", {}).copy()
        
        # Adapter selon le profil cognitif
        if profile.cognitive_profile == CognitiveProfile.VISUAL:
            # Enrichir avec plus de visualisations
            content["enhanced_visualizations"] = True
            content["visual_density"] = "high"
        elif profile.cognitive_profile == CognitiveProfile.AUDITORY:
            # Ajouter des explications audio
            content["audio_explanations"] = True
            content["text_density"] = "high"
        elif profile.cognitive_profile == CognitiveProfile.KINESTHETIC:
            # Ajouter plus d'exercices pratiques
            content["interactive_exercises"] = True
            content["hands_on_activities"] = True
        
        return content
    
    @staticmethod
    def _estimate_time_for_content(
        module: Dict[str, Any],
        profile: LearningProfile,
        difficulty: Difficulty
    ) -> int:
        """Estime le temps pour le contenu adapté"""
        base_time = module.get("estimated_time", 30)
        
        # Ajuster selon le niveau
        level_multipliers = {
            PerformanceLevel.BEGINNER: 1.5,
            PerformanceLevel.INTERMEDIATE: 1.0,
            PerformanceLevel.ADVANCED: 0.8,
            PerformanceLevel.EXPERT: 0.6
        }
        
        multiplier = level_multipliers.get(
            PerformanceLevel(profile.current_level),
            1.0
        )
        
        return int(base_time * multiplier)
    
    @staticmethod
    def _generate_adaptation_notes(
        profile: LearningProfile,
        difficulty: Difficulty
    ) -> str:
        """Génère des notes sur les adaptations"""
        notes = []
        notes.append(f"Contenu adapté pour profil {profile.cognitive_profile.value}")
        notes.append(f"Style d'apprentissage: {profile.learning_style.value}")
        notes.append(f"Difficulté: {difficulty.value}")
        return ". ".join(notes)
    
    @staticmethod
    def _identify_best_subjects(profile: LearningProfile) -> List[str]:
        """Identifie les meilleures matières de l'utilisateur"""
        if not profile.subject_performance:
            return []
        
        # Trier par performance
        sorted_subjects = sorted(
            profile.subject_performance.items(),
            key=lambda x: x[1].get("average_score", 0),
            reverse=True
        )
        
        # Retourner les 3 meilleures
        return [subject for subject, _ in sorted_subjects[:3]]
    
    @staticmethod
    async def _create_default_profile(user_id: str) -> LearningProfile:
        """Crée un profil par défaut"""
        default_profile = {
            "user_id": user_id,
            "current_level": PerformanceLevel.BEGINNER.value,
            "cognitive_profile": CognitiveProfile.MIXED.value,
            "learning_style": LearningStyle.SEQUENTIAL.value,
            "average_response_time": 0.0,
            "accuracy_rate": 0.5,
            "completion_rate": 0.0,
            "engagement_score": 0.5,
            "current_difficulty": Difficulty.BEGINNER.value,
            "difficulty_history": [],
            "adaptation_frequency": 0,
            "preferred_explanation_type": "step_by_step",
            "preferred_exercise_format": "quiz",
            "subject_performance": {},
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await LearningProfileRepository.create_or_update(default_profile)
        return LearningProfile(**default_profile)

