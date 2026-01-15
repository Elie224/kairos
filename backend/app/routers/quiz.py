"""
Routeur pour les quiz
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app.models import (
    QuizResponse, 
    QuizGenerateRequest, 
    QuizAttemptCreate, 
    QuizAttempt, 
    QuizStatistics
)
from app.services.quiz_service import QuizService
from app.services.cached_quiz_service import CachedQuizService
# Authentification supprimée - toutes les routes sont publiques

router = APIRouter()


@router.get("/module/{module_id}", response_model=QuizResponse)
async def get_module_quiz(
    module_id: str,
    num_questions: int = Query(50, ge=1, le=50, description="Nombre de questions à retourner")
):
    """
    Récupère le quiz d'un module.
    Chaque module a un quiz unique qui ne change pas.
    """
    # Utiliser le service avec cache pour réduire les appels API OpenAI
    quiz = await CachedQuizService.get_or_generate_quiz(
        module_id=module_id,
        num_questions=num_questions
    )
    return QuizResponse(
        questions=quiz["questions"],
        module_id=quiz["module_id"],
        quiz_id=quiz.get("quiz_id")
    )


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizGenerateRequest
):
    """
    Génère ou récupère le quiz d'un module.
    Si le quiz existe déjà, il est retourné tel quel (pas de régénération).
    """
    difficulty = request.difficulty.value if request.difficulty else None
    # Utiliser le service avec cache
    quiz = await CachedQuizService.get_or_generate_quiz(
        module_id=request.module_id,
        num_questions=request.num_questions,
        difficulty=difficulty
    )
    return QuizResponse(
        questions=quiz["questions"],
        module_id=quiz["module_id"],
        quiz_id=quiz.get("quiz_id")
    )


@router.post("/regenerate", response_model=QuizResponse)
async def regenerate_quiz(
    request: QuizGenerateRequest
):
    """
    Force la régénération d'un quiz pour un module (route publique).
    Utile pour mettre à jour un quiz existant.
    """
    difficulty = request.difficulty.value if request.difficulty else None
    quiz = await CachedQuizService.regenerate_quiz(
        module_id=request.module_id,
        num_questions=request.num_questions,
        difficulty=difficulty
    )
    return QuizResponse(
        questions=quiz["questions"],
        module_id=quiz["module_id"],
        quiz_id=quiz.get("quiz_id")
    )


@router.delete("/module/{module_id}")
async def delete_module_quiz(
    module_id: str,
    admin_user: dict = Depends(require_admin)
):
    """Supprime le quiz d'un module (admin seulement)"""
    success = await CachedQuizService.delete_quiz(module_id)
    if not success:
        raise HTTPException(status_code=404, detail="Quiz non trouvé")
    return {"message": "Quiz supprimé avec succès"}


@router.post("/attempt", response_model=QuizAttempt)
async def save_quiz_attempt(
    request: QuizAttemptCreate,
    current_user: dict = Depends(get_current_user)
):
    """Sauvegarde une tentative de quiz"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    attempt = await QuizService.save_attempt(
        user_id=user_id,
        module_id=request.module_id,
        quiz_id=request.quiz_id,
        answers=request.answers,
        score=request.score,
        time_spent=request.time_spent,
        num_questions=request.num_questions,
        num_correct=request.num_correct
    )
    return QuizAttempt(
        id=str(attempt.get("_id", "")),
        user_id=user_id,
        module_id=request.module_id,
        quiz_id=request.quiz_id,
        score=request.score,
        time_spent=request.time_spent,
        num_questions=request.num_questions,
        num_correct=request.num_correct,
        answers=request.answers,
        started_at=attempt.get("started_at"),
        completed_at=attempt.get("completed_at")
    )


@router.get("/module/{module_id}/attempts", response_model=List[QuizAttempt])
async def get_quiz_attempts(
    module_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupère toutes les tentatives de quiz d'un utilisateur pour un module"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    attempts = await QuizService.get_user_attempts(user_id, module_id)
    return [
        QuizAttempt(
            id=str(attempt.get("_id", "")),
            user_id=user_id,
            module_id=attempt.get("module_id"),
            quiz_id=attempt.get("quiz_id"),
            score=attempt.get("score", 0),
            time_spent=attempt.get("time_spent", 0),
            num_questions=attempt.get("num_questions", 0),
            num_correct=attempt.get("num_correct", 0),
            answers=attempt.get("answers", {}),
            started_at=attempt.get("started_at"),
            completed_at=attempt.get("completed_at")
        )
        for attempt in attempts
    ]


@router.get("/module/{module_id}/statistics", response_model=QuizStatistics)
async def get_quiz_statistics(
    module_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Récupère les statistiques de quiz pour un utilisateur et un module"""
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    
    stats = await QuizService.get_statistics(user_id, module_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Aucune statistique trouvée pour ce module")
    
    return QuizStatistics(
        module_id=stats["module_id"],
        total_attempts=stats["total_attempts"],
        best_score=stats["best_score"],
        average_score=stats["average_score"],
        last_attempt_at=stats.get("last_attempt_at"),
        total_time_spent=stats["total_time_spent"]
    )




