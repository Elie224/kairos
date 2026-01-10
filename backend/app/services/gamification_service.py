"""
Service pour la gamification avancée
Quêtes, classements intelligents, défis personnalisés
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from app.models.gamification import (
    Quest,
    QuestType,
    QuestStatus,
    QuestRequirement,
    UserQuest,
    LeaderboardEntry,
    Challenge
)
from app.models import Difficulty, Subject
from app.repositories.gamification_repository import GamificationRepository
from app.repositories.progress_repository import ProgressRepository as ProgressRepo
from app.repositories.learning_profile_repository import LearningProfileRepository
import logging

logger = logging.getLogger(__name__)


class GamificationService:
    """Service de gamification"""
    
    @staticmethod
    async def generate_personalized_quests(
        user_id: str,
        limit: int = 5
    ) -> List[Quest]:
        """
        Génère des quêtes personnalisées pour un utilisateur
        """
        try:
            # Récupérer le profil et la progression
            profile = await LearningProfileRepository.find_by_user_id(user_id)
            progress = await ProgressRepo.find_by_user(user_id, limit=50)
            
            if not profile:
                return []
            
            # Générer des quêtes selon le profil
            quests = []
            
            # Quête quotidienne : Compléter un module
            quests.append(Quest(
                id="daily_complete_module",
                title="Défi Quotidien",
                description="Complète un module aujourd'hui",
                quest_type=QuestType.DAILY,
                requirements=[
                    QuestRequirement(
                        type="complete_modules",
                        target=1,
                        current=0
                    )
                ],
                rewards={"points": 100, "streak": 1},
                difficulty=Difficulty.BEGINNER,
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                created_at=datetime.now(timezone.utc)
            ))
            
            # Quête hebdomadaire : Score moyen élevé
            quests.append(Quest(
                id="weekly_high_score",
                title="Excellence Hebdomadaire",
                description="Maintiens un score moyen de 80% cette semaine",
                quest_type=QuestType.WEEKLY,
                requirements=[
                    QuestRequirement(
                        type="average_score",
                        target=80.0,
                        current=profile.get("accuracy_rate", 0) * 100
                    )
                ],
                rewards={"points": 500, "badge": "excellence_weekly"},
                difficulty=Difficulty.INTERMEDIATE,
                expires_at=datetime.now(timezone.utc) + timedelta(days=7),
                created_at=datetime.now(timezone.utc)
            ))
            
            # Quête achievement : Compléter 10 modules
            completed_count = sum(1 for p in progress if p.get("completed", False))
            quests.append(Quest(
                id="achievement_10_modules",
                title="Explorateur",
                description="Complète 10 modules",
                quest_type=QuestType.ACHIEVEMENT,
                requirements=[
                    QuestRequirement(
                        type="complete_modules",
                        target=10,
                        current=completed_count
                    )
                ],
                rewards={"points": 1000, "badge": "explorer"},
                difficulty=Difficulty.BEGINNER,
                created_at=datetime.now(timezone.utc)
            ))
            
            return quests[:limit]
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de quêtes: {e}", exc_info=True)
            return []
    
    @staticmethod
    async def get_leaderboard(
        leaderboard_type: str = "points",
        subject: Optional[Subject] = None,
        limit: int = 100
    ) -> List[LeaderboardEntry]:
        """
        Récupère un classement intelligent (non toxique)
        """
        try:
            # Récupérer les utilisateurs avec leurs scores
            leaderboard_data = await GamificationRepository.get_leaderboard(
                leaderboard_type=leaderboard_type,
                subject=subject.value if subject else None,
                limit=limit
            )
            
            entries = []
            for idx, entry_data in enumerate(leaderboard_data, 1):
                entries.append(LeaderboardEntry(
                    user_id=entry_data.get("user_id"),
                    username=entry_data.get("username", "Utilisateur"),
                    score=entry_data.get("score", 0),
                    rank=idx,
                    badge=entry_data.get("badge")
                ))
            
            return entries
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du classement: {e}", exc_info=True)
            return []
    
    @staticmethod
    async def create_personalized_challenge(
        user_id: str,
        title: str,
        description: str,
        target: Dict[str, Any],
        difficulty: Difficulty,
        deadline_days: int = 7
    ) -> Challenge:
        """
        Crée un défi personnalisé pour un utilisateur
        """
        try:
            challenge_data = {
                "user_id": user_id,
                "title": title,
                "description": description,
                "target": target,
                "current": {},
                "difficulty": difficulty.value,
                "deadline": datetime.now(timezone.utc) + timedelta(days=deadline_days),
                "created_at": datetime.now(timezone.utc)
            }
            
            saved_challenge = await GamificationRepository.create_challenge(challenge_data)
            return Challenge(**saved_challenge)
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du défi: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def update_quest_progress(
        user_id: str,
        quest_id: str,
        progress_data: Dict[str, Any]
    ) -> UserQuest:
        """
        Met à jour la progression d'une quête
        """
        try:
            user_quest = await GamificationRepository.get_user_quest(user_id, quest_id)
            
            if not user_quest:
                # Créer nouvelle quête utilisateur
                user_quest_data = {
                    "user_id": user_id,
                    "quest_id": quest_id,
                    "status": QuestStatus.IN_PROGRESS.value,
                    "progress": progress_data,
                    "started_at": datetime.now(timezone.utc)
                }
                user_quest = await GamificationRepository.create_user_quest(user_quest_data)
            else:
                # Mettre à jour
                user_quest["progress"] = {**user_quest.get("progress", {}), **progress_data}
                user_quest = await GamificationRepository.update_user_quest(
                    user_id,
                    quest_id,
                    {"progress": user_quest["progress"]}
                )
            
            # Vérifier si la quête est complétée
            quest = await GamificationRepository.get_quest(quest_id)
            if quest:
                completed = GamificationService._check_quest_completion(
                    quest,
                    user_quest.get("progress", {})
                )
                
                if completed and user_quest.get("status") != QuestStatus.COMPLETED.value:
                    await GamificationRepository.update_user_quest(
                        user_id,
                        quest_id,
                        {
                            "status": QuestStatus.COMPLETED.value,
                            "completed_at": datetime.now(timezone.utc)
                        }
                    )
                    user_quest["status"] = QuestStatus.COMPLETED.value
            
            return UserQuest(**user_quest)
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de progression: {e}", exc_info=True)
            raise
    
    @staticmethod
    def _check_quest_completion(
        quest: Dict[str, Any],
        progress: Dict[str, Any]
    ) -> bool:
        """Vérifie si une quête est complétée"""
        requirements = quest.get("requirements", [])
        
        for req in requirements:
            req_type = req.get("type")
            target = req.get("target")
            current = progress.get(req_type, 0)
            
            if current < target:
                return False
        
        return True











