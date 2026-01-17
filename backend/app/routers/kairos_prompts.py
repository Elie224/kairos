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
