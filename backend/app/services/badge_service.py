"""
Service pour la gestion des badges et récompenses
"""
from typing import List, Dict, Any
from app.repositories.badge_repository import BadgeRepository
from app.repositories.progress_repository import ProgressRepository
from app.models import BadgeType
import logging

logger = logging.getLogger(__name__)


class BadgeService:
    """Service pour la gestion des badges"""
    
    @staticmethod
    async def check_and_award_badges(user_id: str) -> List[Dict[str, Any]]:
        """Vérifie et attribue les badges automatiquement"""
        new_badges = []
        
        # Récupérer la progression de l'utilisateur
        progress_list = await ProgressRepository.find_by_user(user_id, limit=1000)
        completed_modules = [p for p in progress_list if p.get("completed", False)]
        
        # Badge: Premier module complété
        if len(completed_modules) == 1:
            existing = await BadgeRepository.find_by_user_and_type(user_id, BadgeType.FIRST_MODULE)
            if not existing:
                badge = await BadgeRepository.create(user_id, BadgeType.FIRST_MODULE)
                new_badges.append(badge)
        
        # Badge: Score parfait (100%)
        perfect_scores = [p for p in completed_modules if p.get("score") == 100.0]
        if perfect_scores:
            existing = await BadgeRepository.find_by_user_and_type(user_id, BadgeType.PERFECT_SCORE)
            if not existing:
                badge = await BadgeRepository.create(
                    user_id, 
                    BadgeType.PERFECT_SCORE,
                    {"count": len(perfect_scores)}
                )
                new_badges.append(badge)
        
        # Badge: Maître d'une matière (tous les modules d'une matière complétés)
        from app.repositories.module_repository import ModuleRepository
        modules = await ModuleRepository.find_all()
        
        subjects = {}
        for module in modules:
            subject = module.get("subject")
            if subject not in subjects:
                subjects[subject] = []
            subjects[subject].append(module.get("id"))
        
        for subject, module_ids in subjects.items():
            completed_in_subject = [
                p for p in completed_modules 
                if p.get("module_id") in module_ids
            ]
            if len(completed_in_subject) == len(module_ids) and len(module_ids) > 0:
                existing = await BadgeRepository.find_by_user_and_type(user_id, BadgeType.SUBJECT_MASTER)
                if not existing:
                    badge = await BadgeRepository.create(
                        user_id,
                        BadgeType.SUBJECT_MASTER,
                        {"subject": subject}
                    )
                    new_badges.append(badge)
                    break  # Un seul badge par matière pour l'instant
        
        # Badge: Apprenant dévoué (10+ modules complétés)
        if len(completed_modules) >= 10:
            existing = await BadgeRepository.find_by_user_and_type(user_id, BadgeType.DEDICATED_LEARNER)
            if not existing:
                badge = await BadgeRepository.create(
                    user_id,
                    BadgeType.DEDICATED_LEARNER,
                    {"modules_completed": len(completed_modules)}
                )
                new_badges.append(badge)
        
        return new_badges
    
    @staticmethod
    async def get_user_badges(user_id: str) -> List[Dict[str, Any]]:
        """Récupère tous les badges d'un utilisateur"""
        return await BadgeRepository.find_by_user(user_id)
    
    @staticmethod
    async def get_badge_count(user_id: str) -> int:
        """Compte le nombre de badges d'un utilisateur"""
        return await BadgeRepository.count_by_user(user_id)

