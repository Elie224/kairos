"""
Routes pour la génération de contenu avec OpenAI
TD, TP, Quiz et Chat avec l'étudiant
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from app.services.openai_content_generator import OpenAIContentGenerator
# Authentification supprimée - toutes les routes sont publiques
from app.repositories.module_repository import ModuleRepository
from app.utils.security import InputSanitizer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openai", tags=["OpenAI Content"])


class ChatRequest(BaseModel):
    message: str
    module_id: Optional[str] = None
    conversation_history: Optional[List[dict]] = None


class GenerateContentRequest(BaseModel):
    module_id: str
    lesson_index: Optional[int] = None
    content_type: str  # "td", "tp", "quiz"


@router.post("/chat")
async def chat_with_ai(
    request: ChatRequest
):
    """
    Chat conversationnel avec l'assistant IA
    """
    try:
        module_context = None
        subject = None
        
        # Récupérer le contexte du module si module_id fourni
        if request.module_id:
            sanitized_id = InputSanitizer.sanitize_object_id(request.module_id)
            if sanitized_id:
                module = await ModuleRepository.find_by_id(sanitized_id)
                if module:
                    module_context = f"Module: {module.get('title', '')}\n{module.get('description', '')}"
                    subject = module.get('subject')
        
        result = await OpenAIContentGenerator.chat_with_student(
            user_message=request.message,
            module_context=module_context,
            conversation_history=request.conversation_history,
            subject=subject,
            language="fr"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur chat OpenAI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du chat: {str(e)}")


@router.post("/generate/{content_type}")
async def generate_content(
    content_type: str,
    module_id: str = Query(...),
    lesson_index: Optional[int] = Query(None),
    num_questions: int = Query(10, ge=1, le=50),
):
    """
    Génère du contenu pédagogique (TD, TP, Quiz) avec OpenAI (route publique)
    
    content_type: "td", "tp", ou "quiz"
    """
    try:
        # Valider le type de contenu
        if content_type not in ["td", "tp", "quiz"]:
            raise HTTPException(status_code=400, detail="Type de contenu invalide. Utilisez: td, tp, ou quiz")
        
        # Valider et récupérer le module
        sanitized_id = InputSanitizer.sanitize_object_id(module_id)
        if not sanitized_id:
            raise HTTPException(status_code=400, detail="ID de module invalide")
        
        module = await ModuleRepository.find_by_id(sanitized_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        # Récupérer le contenu de la leçon
        content = module.get("content", {})
        lessons = content.get("lessons", [])
        
        if not lessons:
            raise HTTPException(status_code=400, detail="Aucune leçon trouvée dans ce module")
        
        # Sélectionner la leçon
        if lesson_index is not None:
            if lesson_index < 0 or lesson_index >= len(lessons):
                raise HTTPException(status_code=400, detail="Index de leçon invalide")
            lesson = lessons[lesson_index]
        else:
            # Utiliser la première leçon
            lesson = lessons[0]
        
        lesson_content = lesson.get("content", "") or lesson.get("title", "")
        module_title = module.get("title", "")
        subject = module.get("subject", "")
        difficulty = module.get("difficulty", "moyen")
        
        # Générer le contenu selon le type
        if content_type == "td":
            result = await OpenAIContentGenerator.generate_td(
                module_title=module_title,
                lesson_content=lesson_content,
                subject=subject,
                difficulty=difficulty,
                language="fr"
            )
            return {"type": "td", "data": result}
        
        elif content_type == "tp":
            result = await OpenAIContentGenerator.generate_tp(
                module_title=module_title,
                lesson_content=lesson_content,
                subject=subject,
                difficulty=difficulty,
                language="fr"
            )
            return {"type": "tp", "data": result}
        
        elif content_type == "quiz":
            result = await OpenAIContentGenerator.generate_quiz_questions(
                module_title=module_title,
                lesson_content=lesson_content,
                subject=subject,
                num_questions=num_questions,
                difficulty=difficulty,
                language="fr"
            )
            return {"type": "quiz", "data": result, "count": len(result)}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur génération contenu OpenAI: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération: {str(e)}")


@router.post("/generate-all/{module_id}")
async def generate_all_content(
    module_id: str,
):
    """
    Génère automatiquement TD, TP et Quiz pour un module (route publique)
    """
    try:
        sanitized_id = InputSanitizer.sanitize_object_id(module_id)
        if not sanitized_id:
            raise HTTPException(status_code=400, detail="ID de module invalide")
        
        module = await ModuleRepository.find_by_id(sanitized_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        content = module.get("content", {})
        lessons = content.get("lessons", [])
        
        if not lessons:
            raise HTTPException(status_code=400, detail="Aucune leçon trouvée")
        
        results = {
            "tds": [],
            "tps": [],
            "quizzes": [],
            "errors": []
        }
        
        module_title = module.get("title", "")
        subject = module.get("subject", "")
        difficulty = module.get("difficulty", "moyen")
        
        # Générer pour chaque leçon
        for i, lesson in enumerate(lessons):
            lesson_content = lesson.get("content", "") or lesson.get("title", "")
            
            try:
                # Générer TD
                td = await OpenAIContentGenerator.generate_td(
                    module_title=module_title,
                    lesson_content=lesson_content,
                    subject=subject,
                    difficulty=difficulty
                )
                results["tds"].append({"lesson_index": i, "td": td})
            except Exception as e:
                logger.error(f"Erreur génération TD leçon {i}: {e}")
                results["errors"].append({"type": "td", "lesson": i, "error": str(e)})
            
            try:
                # Générer TP
                tp = await OpenAIContentGenerator.generate_tp(
                    module_title=module_title,
                    lesson_content=lesson_content,
                    subject=subject,
                    difficulty=difficulty
                )
                results["tps"].append({"lesson_index": i, "tp": tp})
            except Exception as e:
                logger.error(f"Erreur génération TP leçon {i}: {e}")
                results["errors"].append({"type": "tp", "lesson": i, "error": str(e)})
            
            try:
                # Générer Quiz
                quiz = await OpenAIContentGenerator.generate_quiz_questions(
                    module_title=module_title,
                    lesson_content=lesson_content,
                    subject=subject,
                    num_questions=10,
                    difficulty=difficulty
                )
                results["quizzes"].append({"lesson_index": i, "questions": quiz})
            except Exception as e:
                logger.error(f"Erreur génération Quiz leçon {i}: {e}")
                results["errors"].append({"type": "quiz", "lesson": i, "error": str(e)})
        
        return {
            "message": f"Génération terminée pour {len(lessons)} leçon(s)",
            "tds_generated": len(results["tds"]),
            "tps_generated": len(results["tps"]),
            "quizzes_generated": len(results["quizzes"]),
            "errors": len(results["errors"]),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur génération complète: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
