"""
Service pour les recommandations de modules personnalisées
"""
from typing import List, Dict, Any
from app.repositories.progress_repository import ProgressRepository
from app.repositories.module_repository import ModuleRepository
from app.models import Subject, Difficulty
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service pour les recommandations personnalisées"""
    
    @staticmethod
    async def get_recommendations(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Génère des recommandations personnalisées pour un utilisateur"""
        # Récupérer la progression de l'utilisateur
        progress_list = await ProgressRepository.find_by_user(user_id)
        completed_module_ids = {p.get("module_id") for p in progress_list if p.get("completed", False)}
        started_module_ids = {p.get("module_id") for p in progress_list}
        
        # Récupérer tous les modules
        all_modules = await ModuleRepository.find_all()
        
        # Analyser les préférences de l'utilisateur
        subject_preferences = {}
        difficulty_preferences = {}
        
        for progress in progress_list:
            module_id = progress.get("module_id")
            module = next((m for m in all_modules if m.get("id") == module_id), None)
            if module:
                subject = module.get("subject")
                difficulty = module.get("difficulty")
                
                # Compter les préférences basées sur le temps passé
                time_spent = progress.get("time_spent", 0)
                if subject:
                    subject_preferences[subject] = subject_preferences.get(subject, 0) + time_spent
                if difficulty:
                    difficulty_preferences[difficulty] = difficulty_preferences.get(difficulty, 0) + time_spent
        
        # Trouver le sujet préféré
        favorite_subject = max(subject_preferences.items(), key=lambda x: x[1])[0] if subject_preferences else None
        
        # Trouver la difficulté préférée
        favorite_difficulty = max(difficulty_preferences.items(), key=lambda x: x[1])[0] if difficulty_preferences else None
        
        # Générer des recommandations
        recommendations = []
        
        # 1. Modules du sujet préféré non complétés
        if favorite_subject:
            subject_modules = [
                m for m in all_modules 
                if m.get("subject") == favorite_subject 
                and m.get("id") not in completed_module_ids
            ]
            recommendations.extend(subject_modules[:2])
        
        # 2. Modules de difficulté similaire
        if favorite_difficulty:
            difficulty_modules = [
                m for m in all_modules 
                if m.get("difficulty") == favorite_difficulty
                and m.get("id") not in completed_module_ids
                and m.get("id") not in [r.get("id") for r in recommendations]
            ]
            recommendations.extend(difficulty_modules[:2])
        
        # 3. Modules populaires (non complétés)
        remaining_modules = [
            m for m in all_modules 
            if m.get("id") not in completed_module_ids
            and m.get("id") not in [r.get("id") for r in recommendations]
        ]
        
        # Trier par popularité (basé sur le nombre de complétions)
        module_popularity = {}
        # Récupérer toutes les progressions (limité pour les performances)
        from app.database import get_database
        db = get_database()
        all_progress_cursor = db.progress.find({"completed": True})
        all_progress = await all_progress_cursor.to_list(length=1000)
        for p in all_progress:
            if p.get("completed"):
                module_id = p.get("module_id")
                module_popularity[module_id] = module_popularity.get(module_id, 0) + 1
        
        remaining_modules.sort(
            key=lambda m: module_popularity.get(m.get("id"), 0),
            reverse=True
        )
        
        recommendations.extend(remaining_modules[:limit - len(recommendations)])
        
        return recommendations[:limit]

