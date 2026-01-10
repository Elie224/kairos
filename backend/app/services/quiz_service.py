"""
Service pour la gestion des quiz - Business logic
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.repositories.quiz_repository import QuizRepository
from app.repositories.module_repository import ModuleRepository
from app.services.ai_service import AIService
from app.models import QuizCreate, QuizQuestion
import logging

logger = logging.getLogger(__name__)


class QuizService:
    """Service pour la gestion des quiz"""
    
    @staticmethod
    async def get_or_generate_quiz(
        module_id: str,
        num_questions: int = 50,
        difficulty: Optional[str] = None,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Récupère le quiz d'un module ou le génère s'il n'existe pas.
        Chaque module a un seul quiz unique qui ne change pas.
        """
        try:
            # Vérifier que le module existe et est d'informatique
            module = await ModuleRepository.find_by_id(module_id)
            if not module:
                from fastapi import HTTPException
                raise HTTPException(status_code=404, detail="Module non trouvé")
            
            module_subject = module.get("subject", "").lower()
            if module_subject != "computer_science":
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=403, 
                    detail="Les quiz sont disponibles uniquement pour les modules d'informatique"
                )
            
            # Vérifier si un quiz existe déjà pour ce module
            if not force_regenerate:
                existing_quiz = await QuizRepository.find_by_module_id(module_id)
                if existing_quiz:
                    logger.info(f"Quiz existant trouvé pour le module {module_id}")
                    # Retourner le quiz existant, en limitant le nombre de questions si nécessaire
                    questions = existing_quiz.get("questions", [])
                    if num_questions < len(questions):
                        questions = questions[:num_questions]
                    
                    return {
                        "questions": questions,
                        "module_id": module_id,
                        "quiz_id": str(existing_quiz.get("_id", "")),
                        "num_questions": len(questions)
                    }
            
            # Générer un nouveau quiz via l'IA
            logger.info(f"Génération d'un nouveau quiz pour le module {module_id}")
            ai_quiz = await AIService.generate_quiz(
                module_id=module_id,
                num_questions=num_questions,
                difficulty=difficulty
            )
            
            # Sauvegarder le quiz en base de données
            quiz_data = {
                "module_id": module_id,
                "questions": ai_quiz.get("questions", []),
                "num_questions": len(ai_quiz.get("questions", [])),
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Si un quiz existe déjà, le mettre à jour, sinon en créer un nouveau
            if await QuizRepository.exists(module_id):
                await QuizRepository.update(module_id, {
                    "questions": quiz_data["questions"],
                    "num_questions": quiz_data["num_questions"],
                    "updated_at": quiz_data["updated_at"]
                })
                saved_quiz = await QuizRepository.find_by_module_id(module_id)
            else:
                saved_quiz = await QuizRepository.create(quiz_data)
            
            return {
                "questions": saved_quiz.get("questions", []),
                "module_id": module_id,
                "quiz_id": str(saved_quiz.get("_id", "")),
                "num_questions": saved_quiz.get("num_questions", len(saved_quiz.get("questions", [])))
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération/génération du quiz: {e}")
            raise
    
    @staticmethod
    async def get_quiz(module_id: str) -> Dict[str, Any]:
        """Récupère le quiz d'un module"""
        # Vérifier que le module est d'informatique
        module = await ModuleRepository.find_by_id(module_id)
        if not module:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Module non trouvé")
        
        module_subject = module.get("subject", "").lower()
        if module_subject != "computer_science":
            from fastapi import HTTPException
            raise HTTPException(
                status_code=403, 
                detail="Les quiz sont disponibles uniquement pour les modules d'informatique"
            )
        
        quiz = await QuizRepository.find_by_module_id(module_id)
        if not quiz:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Quiz non trouvé pour ce module")
        return quiz
    
    @staticmethod
    async def delete_quiz(module_id: str) -> bool:
        """Supprime le quiz d'un module"""
        return await QuizRepository.delete(module_id)
    
    @staticmethod
    async def regenerate_quiz(
        module_id: str,
        num_questions: int = 50,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """Force la régénération d'un quiz pour un module"""
        return await QuizService.get_or_generate_quiz(
            module_id=module_id,
            num_questions=num_questions,
            difficulty=difficulty,
            force_regenerate=True
        )
    
    @staticmethod
    async def save_attempt(
        user_id: str,
        module_id: str,
        quiz_id: str,
        answers: Dict[int, int],
        score: float,
        time_spent: int,
        num_questions: int,
        num_correct: int
    ) -> Dict[str, Any]:
        """Sauvegarde une tentative de quiz"""
        try:
            # Validation des données
            if not user_id or not module_id or not quiz_id:
                raise ValueError("user_id, module_id et quiz_id sont requis")
            if score < 0 or score > 100:
                raise ValueError("Le score doit être entre 0 et 100")
            if time_spent < 0:
                raise ValueError("Le temps passé doit être positif")
            if num_questions <= 0:
                raise ValueError("Le nombre de questions doit être positif")
            if num_correct < 0 or num_correct > num_questions:
                raise ValueError("Le nombre de réponses correctes doit être entre 0 et le nombre de questions")
            
            from datetime import datetime, timezone
            attempt_data = {
                "user_id": user_id,
                "module_id": module_id,
                "quiz_id": quiz_id,
                "answers": answers,
                "score": score,
                "time_spent": time_spent,
                "num_questions": num_questions,
                "num_correct": num_correct,
                "started_at": datetime.now(timezone.utc),  # On utilise le même timestamp pour started et completed
                "completed_at": datetime.now(timezone.utc)
            }
            return await QuizRepository.create_attempt(attempt_data)
        except ValueError as e:
            logger.error(f"Erreur de validation lors de la sauvegarde de la tentative: {e}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la tentative: {e}")
            raise
    
    @staticmethod
    async def get_user_attempts(user_id: str, module_id: str) -> List[Dict[str, Any]]:
        """Récupère toutes les tentatives de quiz d'un utilisateur pour un module"""
        return await QuizRepository.find_attempts_by_user_and_module(user_id, module_id)
    
    @staticmethod
    async def get_statistics(user_id: str, module_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les statistiques de quiz pour un utilisateur et un module"""
        return await QuizRepository.get_statistics(user_id, module_id)




