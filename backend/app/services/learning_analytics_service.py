"""
Service pour Learning Analytics avancé
Détection décrochage, prédiction réussite, heatmaps
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from app.repositories.progress_repository import ProgressRepository as ProgressRepo
from app.repositories.learning_profile_repository import LearningProfileRepository
import logging
import statistics

logger = logging.getLogger(__name__)


class LearningAnalyticsService:
    """Service d'analytics d'apprentissage"""
    
    @staticmethod
    async def detect_dropout_risk(user_id: str) -> Dict[str, Any]:
        """
        Détecte le risque de décrochage d'un utilisateur
        """
        try:
            # Récupérer la progression récente (30 derniers jours)
            progress = await ProgressRepo.find_by_user(user_id, limit=100)
            
            # Analyser les patterns
            recent_activity = []
            for p in progress:
                started_at = p.get("started_at")
                if isinstance(started_at, str):
                    try:
                        started_at = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                    except:
                        continue
                
                if started_at and started_at > datetime.now() - timedelta(days=30):
                    recent_activity.append(p)
            
            # Calculer les métriques
            days_since_last_activity = 0
            if recent_activity:
                last_activity = max(
                    datetime.fromisoformat(p.get("started_at", "").replace('Z', '+00:00'))
                    for p in recent_activity
                    if p.get("started_at")
                )
                days_since_last_activity = (datetime.now() - last_activity.replace(tzinfo=None)).days
            
            completion_rate = sum(1 for p in recent_activity if p.get("completed", False)) / len(recent_activity) if recent_activity else 0
            
            # Calculer le risque
            risk_score = 0.0
            risk_factors = []
            
            if days_since_last_activity > 7:
                risk_score += 0.3
                risk_factors.append("Inactivité prolongée")
            
            if completion_rate < 0.3:
                risk_score += 0.4
                risk_factors.append("Taux de complétion faible")
            
            if len(recent_activity) < 3:
                risk_score += 0.3
                risk_factors.append("Peu d'activité récente")
            
            risk_level = "low" if risk_score < 0.3 else "medium" if risk_score < 0.6 else "high"
            
            return {
                "user_id": user_id,
                "risk_level": risk_level,
                "risk_score": min(risk_score, 1.0),
                "risk_factors": risk_factors,
                "days_since_last_activity": days_since_last_activity,
                "completion_rate": completion_rate,
                "recommendations": LearningAnalyticsService._generate_dropout_recommendations(risk_level)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection de décrochage: {e}", exc_info=True)
            return {
                "user_id": user_id,
                "risk_level": "unknown",
                "risk_score": 0.0,
                "risk_factors": [],
                "recommendations": []
            }
    
    @staticmethod
    async def predict_success(user_id: str, module_id: str) -> Dict[str, Any]:
        """
        Prédit la probabilité de réussite pour un module
        """
        try:
            # Récupérer le profil
            profile = await LearningProfileRepository.find_by_user_id(user_id)
            if not profile:
                return {"success_probability": 0.5, "confidence": "low"}
            
            # Récupérer la progression
            progress = await ProgressRepo.find_by_user(user_id, limit=50)
            
            # Calculer métriques
            accuracy = profile.get("accuracy_rate", 0.5)
            completion_rate = profile.get("completion_rate", 0.5)
            
            # Score de prédiction simple (à améliorer avec ML)
            success_probability = (accuracy * 0.6) + (completion_rate * 0.4)
            
            confidence = "high" if len(progress) > 10 else "medium" if len(progress) > 5 else "low"
            
            return {
                "user_id": user_id,
                "module_id": module_id,
                "success_probability": success_probability,
                "confidence": confidence,
                "factors": {
                    "accuracy_rate": accuracy,
                    "completion_rate": completion_rate,
                    "data_points": len(progress)
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}", exc_info=True)
            return {"success_probability": 0.5, "confidence": "low"}
    
    @staticmethod
    async def generate_difficulty_heatmap(user_id: str) -> Dict[str, Any]:
        """
        Génère une heatmap des difficultés par notion
        """
        try:
            progress = await ProgressRepo.find_by_user(user_id, limit=100)
            
            # Grouper par module et calculer difficulté moyenne
            module_difficulties = {}
            
            for p in progress:
                module_id = p.get("module_id")
                score = p.get("score", 0)
                
                if module_id not in module_difficulties:
                    module_difficulties[module_id] = []
                
                module_difficulties[module_id].append(score)
            
            # Calculer moyenne par module
            heatmap_data = {}
            for module_id, scores in module_difficulties.items():
                avg_score = statistics.mean(scores) if scores else 0
                # Convertir score en difficulté (0-100 -> facile à difficile)
                difficulty_level = 100 - avg_score
                heatmap_data[module_id] = {
                    "difficulty": difficulty_level,
                    "average_score": avg_score,
                    "attempts": len(scores)
                }
            
            return {
                "user_id": user_id,
                "heatmap": heatmap_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de heatmap: {e}", exc_info=True)
            return {"user_id": user_id, "heatmap": {}}
    
    @staticmethod
    def _generate_dropout_recommendations(risk_level: str) -> List[str]:
        """Génère des recommandations selon le niveau de risque"""
        if risk_level == "high":
            return [
                "Contactez votre tuteur pour obtenir de l'aide",
                "Revenez aux modules de base pour reprendre confiance",
                "Fixez-vous des objectifs quotidiens réalisables"
            ]
        elif risk_level == "medium":
            return [
                "Essayez de vous connecter régulièrement",
                "Complétez au moins un module par semaine",
                "Participez aux activités de groupe"
            ]
        else:
            return [
                "Continuez votre excellent travail !",
                "Explorez de nouveaux défis"
            ]











