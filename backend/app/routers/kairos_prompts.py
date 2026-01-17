"""
Routeur pour les prompts officiels Kairos - Visualisations, Quêtes, Badges, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.services.kairos_prompt_service import KairosPromptService
from app.services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class VisualizationRequest(BaseModel):
    subject: str
    concept: str
    level: str = "intermediate"


class QuestRequest(BaseModel):
    user_profile: Dict[str, Any]
    subject: Optional[str] = None


class BadgeRequest(BaseModel):
    user_progress: Dict[str, Any]


class FeedbackRequest(BaseModel):
    errors: List[Dict[str, Any]]


class RecommendationRequest(BaseModel):
    user_profile: Dict[str, Any]


@router.post("/visualization/generate")
async def generate_visualization(request: VisualizationRequest) -> Dict[str, Any]:
    """
    Génère une visualisation interactive pour un concept donné
    Utilise les prompts officiels Kairos
    """
    try:
        prompt_data = KairosPromptService.get_visualization_prompt(
            subject=request.subject,
            concept=request.concept,
            level=request.level
        )
        
        # Appeler OpenAI avec le prompt
        response = await AIService.chat_with_ai(
            user_id="system",
            message=prompt_data["prompt"],
            language="fr"
        )
        
        # Parser la réponse JSON si possible
        try:
            import json
            visualization_data = json.loads(response.get("response", "{}"))
        except:
            visualization_data = {"raw_response": response.get("response", "")}
        
        return {
            "success": True,
            "visualization": visualization_data,
            "subject": request.subject,
            "concept": request.concept,
            "level": request.level
        }
    except Exception as e:
        logger.error(f"Erreur lors de la génération de visualisation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quest/generate")
async def generate_quest(request: QuestRequest) -> Dict[str, Any]:
    """
    Génère une quête pédagogique personnalisée
    Utilise les prompts officiels Kairos
    """
    try:
        prompt_data = KairosPromptService.get_quest_prompt(
            user_profile=request.user_profile,
            subject=request.subject
        )
        
        # Appeler OpenAI avec le prompt
        response = await AIService.chat_with_ai(
            user_id="system",
            message=prompt_data["prompt"],
            language="fr"
        )
        
        # Parser la réponse JSON si possible
        try:
            import json
            quest_data = json.loads(response.get("response", "{}"))
        except:
            quest_data = {"raw_response": response.get("response", "")}
        
        return {
            "success": True,
            "quest": quest_data,
            "subject": request.subject
        }
    except Exception as e:
        logger.error(f"Erreur lors de la génération de quête: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/badge/attribute")
async def attribute_badge(request: BadgeRequest) -> Dict[str, Any]:
    """
    Attribue un badge basé sur la progression de l'utilisateur
    Utilise les prompts officiels Kairos
    """
    try:
        prompt_data = KairosPromptService.get_badge_prompt(
            user_progress=request.user_progress
        )
        
        # Appeler OpenAI avec le prompt
        response = await AIService.chat_with_ai(
            user_id="system",
            message=prompt_data["prompt"],
            language="fr"
        )
        
        # Parser la réponse JSON si possible
        try:
            import json
            badge_data = json.loads(response.get("response", "{}"))
        except:
            badge_data = {"raw_response": response.get("response", "")}
        
        return {
            "success": True,
            "badge": badge_data
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'attribution de badge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/generate")
async def generate_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    """
    Génère un feedback intelligent basé sur les erreurs
    Utilise les prompts officiels Kairos
    """
    try:
        prompt_data = KairosPromptService.get_feedback_prompt(
            errors=request.errors
        )
        
        # Appeler OpenAI avec le prompt
        response = await AIService.chat_with_ai(
            user_id="system",
            message=prompt_data["prompt"],
            language="fr"
        )
        
        # Parser la réponse JSON si possible
        try:
            import json
            feedback_data = json.loads(response.get("response", "{}"))
        except:
            feedback_data = {"raw_response": response.get("response", "")}
        
        return {
            "success": True,
            "feedback": feedback_data
        }
    except Exception as e:
        logger.error(f"Erreur lors de la génération de feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendation/generate")
async def generate_recommendation(request: RecommendationRequest) -> Dict[str, Any]:
    """
    Génère une recommandation IA personnalisée
    Utilise les prompts officiels Kairos
    """
    try:
        prompt_data = KairosPromptService.get_recommendation_prompt(
            user_profile=request.user_profile
        )
        
        # Appeler OpenAI avec le prompt
        response = await AIService.chat_with_ai(
            user_id="system",
            message=prompt_data["prompt"],
            language="fr"
        )
        
        # Parser la réponse JSON si possible
        try:
            import json
            recommendation_data = json.loads(response.get("response", "{}"))
        except:
            recommendation_data = {"raw_response": response.get("response", "")}
        
        return {
            "success": True,
            "recommendation": recommendation_data
        }
    except Exception as e:
        logger.error(f"Erreur lors de la génération de recommandation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics/{subject}")
async def get_available_topics(subject: str) -> Dict[str, Any]:
    """
    Récupère la liste des topics disponibles pour une matière
    """
    try:
        topics = KairosPromptService.get_available_topics(subject)
        return {
            "success": True,
            "subject": subject,
            "topics": topics
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PRIORITÉ 1 - CURRICULUM INTELLIGENT
# ============================================================================

class CurriculumRequest(BaseModel):
    subject: str
    level: str  # collège, lycée, université
    objective: str  # exam, compréhension, rattrapage


@router.post("/curriculum/generate")
async def generate_curriculum(request: CurriculumRequest) -> Dict[str, Any]:
    """
    Génère un curriculum complet et structuré pour une matière
    PRIORITÉ 1 - Curriculum intelligent généré par l'IA
    """
    try:
        prompt_data = KairosPromptService.get_curriculum_prompt_data(
            subject=request.subject,
            level=request.level,
            objective=request.objective
        )
        
        # Appeler OpenAI avec le prompt
        response = await AIService.chat_with_ai(
            user_id="system",
            message=prompt_data["prompt"],
            language="fr"
        )
        
        # Parser la réponse JSON si possible
        try:
            import json
            curriculum_data = json.loads(response.get("response", "{}"))
        except:
            curriculum_data = {"raw_response": response.get("response", "")}
        
        return {
            "success": True,
            "curriculum": curriculum_data,
            "subject": request.subject,
            "level": request.level,
            "objective": request.objective
        }
    except Exception as e:
        logger.error(f"Erreur lors de la génération du curriculum: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PRIORITÉ 2 - PROFIL COGNITIF DE L'APPRENANT
# ============================================================================

class LearnerProfileRequest(BaseModel):
    learning_data: Dict[str, Any]


@router.post("/learner/profile/update")
async def update_learner_profile(request: LearnerProfileRequest) -> Dict[str, Any]:
    """
    Met à jour le profil cognitif de l'apprenant
    PRIORITÉ 2 - Profil cognitif de l'apprenant (Learner Model IA)
    """
    try:
        prompt_data = KairosPromptService.get_learner_profile_prompt_data(
            learning_data=request.learning_data
        )
        
        # Appeler OpenAI avec le prompt
        response = await AIService.chat_with_ai(
            user_id="system",
            message=prompt_data["prompt"],
            language="fr"
        )
        
        # Parser la réponse JSON si possible
        try:
            import json
            profile_data = json.loads(response.get("response", "{}"))
        except:
            profile_data = {"raw_response": response.get("response", "")}
        
        return {
            "success": True,
            "learner_profile": profile_data
        }
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du profil: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learner/profile")
async def get_learner_profile(user_id: str) -> Dict[str, Any]:
    """
    Récupère le profil cognitif de l'apprenant
    PRIORITÉ 2 - Profil cognitif de l'apprenant
    """
    try:
        # TODO: Récupérer les données d'apprentissage depuis la base de données
        # Pour l'instant, retourner un message indiquant que c'est à implémenter
        return {
            "success": True,
            "message": "Endpoint à implémenter avec récupération des données depuis la base",
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du profil: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PRIORITÉ 3 - ÉVALUATION INTELLIGENTE
# ============================================================================

class EvaluationRequest(BaseModel):
    subject: str
    level: str
    evaluation_type: str  # formative, summative, adaptive, oral


@router.post("/evaluation/generate")
async def generate_evaluation(request: EvaluationRequest) -> Dict[str, Any]:
    """
    Génère une évaluation pédagogique complète
    PRIORITÉ 3 - Évaluation intelligente (Examens générés par IA)
    """
    try:
        prompt_data = KairosPromptService.get_evaluation_prompt_data(
            subject=request.subject,
            level=request.level,
            evaluation_type=request.evaluation_type
        )
        
        # Appeler OpenAI avec le prompt
        response = await AIService.chat_with_ai(
            user_id="system",
            message=prompt_data["prompt"],
            language="fr"
        )
        
        # Parser la réponse JSON si possible
        try:
            import json
            evaluation_data = json.loads(response.get("response", "{}"))
        except:
            evaluation_data = {"raw_response": response.get("response", "")}
        
        return {
            "success": True,
            "evaluation": evaluation_data,
            "subject": request.subject,
            "level": request.level,
            "evaluation_type": request.evaluation_type
        }
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'évaluation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class CorrectionRequest(BaseModel):
    evaluation_id: str
    user_answers: Dict[str, Any]
    evaluation_data: Dict[str, Any]


@router.post("/evaluation/correct")
async def correct_evaluation(request: CorrectionRequest) -> Dict[str, Any]:
    """
    Corrige une évaluation et génère un feedback détaillé
    PRIORITÉ 3 - Évaluation intelligente
    """
    try:
        # Utiliser le prompt d'explainability pour chaque erreur
        corrections = []
        for question_id, user_answer in request.user_answers.items():
            question = request.evaluation_data.get("questions", {}).get(question_id, {})
            if question:
                error_analysis = {
                    "question_id": question_id,
                    "user_answer": user_answer,
                    "correct_answer": question.get("correct_answer"),
                    "question": question.get("question")
                }
                
                prompt_data = KairosPromptService.get_explainability_prompt_data(
                    error_analysis=error_analysis
                )
                
                response = await AIService.chat_with_ai(
                    user_id="system",
                    message=prompt_data["prompt"],
                    language="fr"
                )
                
                try:
                    import json
                    correction_data = json.loads(response.get("response", "{}"))
                except:
                    correction_data = {"raw_response": response.get("response", "")}
                
                corrections.append(correction_data)
        
        return {
            "success": True,
            "corrections": corrections,
            "evaluation_id": request.evaluation_id
        }
    except Exception as e:
        logger.error(f"Erreur lors de la correction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PRIORITÉ 4 - EXPLAINABILITY & MÉTACOGNITION
# ============================================================================

class ExplainabilityRequest(BaseModel):
    error_analysis: Dict[str, Any]


@router.post("/explainability/analyze")
async def analyze_error(request: ExplainabilityRequest) -> Dict[str, Any]:
    """
    Analyse une erreur et explique pourquoi l'apprenant s'est trompé
    PRIORITÉ 4 - Explainability & Métacognition
    """
    try:
        prompt_data = KairosPromptService.get_explainability_prompt_data(
            error_analysis=request.error_analysis
        )
        
        # Appeler OpenAI avec le prompt
        response = await AIService.chat_with_ai(
            user_id="system",
            message=prompt_data["prompt"],
            language="fr"
        )
        
        # Parser la réponse JSON si possible
        try:
            import json
            explanation_data = json.loads(response.get("response", "{}"))
        except:
            explanation_data = {"raw_response": response.get("response", "")}
        
        return {
            "success": True,
            "explanation": explanation_data
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse d'erreur: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PRIORITÉ 5 - MODE LABORATOIRE AVANCÉ
# ============================================================================

class LabSimulationRequest(BaseModel):
    simulation_request: str


@router.post("/lab/simulate")
async def simulate_lab(request: LabSimulationRequest) -> Dict[str, Any]:
    """
    Génère une simulation de laboratoire interactive
    PRIORITÉ 5 - Mode laboratoire avancé
    """
    try:
        prompt_data = KairosPromptService.get_lab_simulation_prompt_data(
            simulation_request=request.simulation_request
        )
        
        # Appeler OpenAI avec le prompt
        response = await AIService.chat_with_ai(
            user_id="system",
            message=prompt_data["prompt"],
            language="fr"
        )
        
        # Parser la réponse JSON si possible
        try:
            import json
            simulation_data = json.loads(response.get("response", "{}"))
        except:
            simulation_data = {"raw_response": response.get("response", "")}
        
        return {
            "success": True,
            "simulation": simulation_data
        }
    except Exception as e:
        logger.error(f"Erreur lors de la génération de simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
