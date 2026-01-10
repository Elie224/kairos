"""
Service pour générer automatiquement des parcours d'apprentissage intelligents
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.models.pathway import (
    Pathway,
    PathwayCreate,
    PathwayModule,
    PathwayRecommendation,
    PathwayType,
    PathwayStatus,
    PrerequisiteLevel
)
from app.models import Subject, Difficulty
from app.repositories.pathway_repository import PathwayRepository
from app.repositories.module_repository import ModuleRepository
from app.repositories.progress_repository import ProgressRepository as ProgressRepo
from app.repositories.learning_profile_repository import LearningProfileRepository
from app.services.prerequisite_detector import PrerequisiteDetector
from app.services.ai_service import client, AI_MODEL
import logging
import json

logger = logging.getLogger(__name__)


class PathwayGeneratorService:
    """Service pour générer des parcours intelligents"""
    
    @staticmethod
    async def generate_pathway(
        subject: Subject,
        target_level: Difficulty,
        user_id: Optional[str] = None,
        learning_objectives: Optional[List[str]] = None
    ) -> Pathway:
        """
        Génère automatiquement un parcours d'apprentissage
        """
        try:
            # Récupérer tous les modules du sujet
            all_modules = await ModuleRepository.find_by_subject(subject)
            
            if not all_modules:
                raise ValueError(f"Aucun module trouvé pour le sujet {subject.value}")
            
            # Filtrer par niveau cible si nécessaire
            relevant_modules = [
                m for m in all_modules
                if m.get("difficulty") == target_level.value or target_level == Difficulty.BEGINNER
            ]
            
            # Si utilisateur fourni, analyser ses prérequis et progression
            if user_id:
                # Récupérer le profil d'apprentissage
                profile = await LearningProfileRepository.find_by_user_id(user_id)
                
                # Récupérer la progression
                user_progress = await ProgressRepo.find_by_user(user_id, limit=100)
                completed_module_ids = {
                    p.get("module_id") for p in user_progress
                    if p.get("completed", False)
                }
                
                # Filtrer les modules déjà complétés
                relevant_modules = [
                    m for m in relevant_modules
                    if m.get("id") not in completed_module_ids
                ]
            
            # Générer l'ordre optimal avec l'IA
            ordered_modules = await PathwayGeneratorService._order_modules_with_ai(
                relevant_modules,
                learning_objectives
            )
            
            # Créer les PathwayModules
            pathway_modules = []
            for idx, module in enumerate(ordered_modules):
                # Analyser les prérequis
                prereq_analysis = await PrerequisiteDetector.analyze_prerequisites(
                    module.get("id"),
                    user_id
                )
                
                pathway_modules.append(PathwayModule(
                    module_id=module.get("id"),
                    order=idx + 1,
                    prerequisite_level=PrerequisiteLevel.REQUIRED if prereq_analysis.prerequisite_score < 0.5 else PrerequisiteLevel.RECOMMENDED,
                    estimated_time=module.get("estimated_time", 30),
                    required_score=70.0 if target_level == Difficulty.ADVANCED else None
                ))
            
            # Générer titre et description avec IA
            title, description = await PathwayGeneratorService._generate_title_description(
                subject,
                target_level,
                len(pathway_modules)
            )
            
            # Calculer la durée totale
            estimated_duration = sum(m.estimated_time for m in pathway_modules) // 60  # en heures
            
            # Créer le parcours
            pathway_data = PathwayCreate(
                title=title,
                description=description,
                subject=subject,
                target_level=target_level,
                pathway_type=PathwayType.ADAPTIVE,
                learning_objectives=learning_objectives or PathwayGeneratorService._generate_default_objectives(subject, target_level),
                modules=pathway_modules,
                estimated_duration=estimated_duration
            )
            
            # Sauvegarder
            pathway_dict = {
                **pathway_data.dict(),
                "status": PathwayStatus.DRAFT.value,
                "created_by": user_id,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            saved_pathway = await PathwayRepository.create(pathway_dict)
            return Pathway(**saved_pathway)
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du parcours: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def recommend_pathways(
        user_id: str,
        limit: int = 5
    ) -> List[PathwayRecommendation]:
        """
        Recommande des parcours pour un utilisateur
        """
        try:
            # Récupérer le profil
            profile = await LearningProfileRepository.find_by_user_id(user_id)
            if not profile:
                return []
            
            # Récupérer la progression
            user_progress = await ProgressRepo.find_by_user(user_id, limit=100)
            completed_module_ids = {
                p.get("module_id") for p in user_progress
                if p.get("completed", False)
            }
            
            # Récupérer tous les parcours actifs
            all_pathways = await PathwayRepository.find_all(status="active", limit=50)
            
            recommendations = []
            
            for pathway_data in all_pathways:
                pathway = Pathway(**pathway_data)
                
                # Calculer le score de correspondance
                match_score = await PathwayGeneratorService._calculate_match_score(
                    pathway,
                    profile,
                    completed_module_ids
                )
                
                # Vérifier les prérequis
                prerequisites_met = await PathwayGeneratorService._check_prerequisites(
                    pathway,
                    completed_module_ids
                )
                
                # Vérifier la correspondance de difficulté
                difficulty_match = (
                    Difficulty(pathway.target_level).value == profile.get("current_difficulty") or
                    Difficulty(pathway.target_level).value == Difficulty.BEGINNER.value
                )
                
                # Générer le raisonnement
                reasoning = PathwayGeneratorService._generate_reasoning(
                    pathway,
                    match_score,
                    prerequisites_met,
                    difficulty_match
                )
                
                recommendations.append(PathwayRecommendation(
                    pathway_id=pathway.id,
                    pathway_title=pathway.title,
                    match_score=match_score,
                    reasoning=reasoning,
                    estimated_time=pathway.estimated_duration,
                    difficulty_match=difficulty_match,
                    prerequisites_met=prerequisites_met
                ))
            
            # Trier par score de correspondance
            recommendations.sort(key=lambda x: x.match_score, reverse=True)
            return recommendations[:limit]
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de recommandations: {e}", exc_info=True)
            return []
    
    @staticmethod
    async def _order_modules_with_ai(
        modules: List[Dict[str, Any]],
        learning_objectives: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Utilise l'IA pour ordonner les modules de manière optimale
        """
        if not client or len(modules) <= 1:
            # Si pas d'IA ou un seul module, retourner tel quel
            return modules
        
        try:
            modules_summary = [
                {
                    "id": m.get("id"),
                    "title": m.get("title"),
                    "description": m.get("description", "")[:200],
                    "difficulty": m.get("difficulty"),
                    "learning_objectives": m.get("learning_objectives", [])[:3]
                }
                for m in modules
            ]
            
            prompt = f"""Ordonne ces modules d'apprentissage dans l'ordre optimal pour un apprentissage progressif.

Modules disponibles :
{json.dumps(modules_summary, indent=2, ensure_ascii=False)}

Objectifs d'apprentissage : {learning_objectives or "Apprentissage général"}

Considère :
1. La progression logique des concepts
2. La difficulté (commencer par les plus faciles)
3. Les dépendances entre modules
4. Les objectifs d'apprentissage

Réponds UNIQUEMENT avec un JSON contenant les IDs dans l'ordre optimal :
{{
    "ordered_module_ids": ["id1", "id2", "id3", ...]
}}"""

            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en pédagogie. Ordonne les modules pour un apprentissage optimal."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            create_params.update(_get_max_tokens_param(AI_MODEL, 1000))
            response = await client.chat.completions.create(**create_params)
            
            response_text = response.choices[0].message.content
            
            # Extraire le JSON
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(response_text[json_start:json_end])
                    ordered_ids = result.get("ordered_module_ids", [])
                    
                    # Créer un mapping ID -> module
                    module_map = {m.get("id"): m for m in modules}
                    
                    # Réordonner selon l'ordre IA
                    ordered_modules = []
                    for module_id in ordered_ids:
                        if module_id in module_map:
                            ordered_modules.append(module_map[module_id])
                    
                    # Ajouter les modules non ordonnés par l'IA
                    for module in modules:
                        if module.get("id") not in ordered_ids:
                            ordered_modules.append(module)
                    
                    return ordered_modules
            except json.JSONDecodeError:
                pass
            
            # Fallback : ordre par difficulté
            return sorted(modules, key=lambda m: {
                "beginner": 1,
                "intermediate": 2,
                "advanced": 3
            }.get(m.get("difficulty", "beginner"), 1))
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ordonnancement IA: {e}", exc_info=True)
            # Fallback : ordre par difficulté
            return sorted(modules, key=lambda m: {
                "beginner": 1,
                "intermediate": 2,
                "advanced": 3
            }.get(m.get("difficulty", "beginner"), 1))
    
    @staticmethod
    async def _generate_title_description(
        subject: Subject,
        target_level: Difficulty,
        num_modules: int
    ) -> tuple[str, str]:
        """Génère un titre et une description pour le parcours"""
        if not client:
            return (
                f"Parcours {subject.value.capitalize()} - Niveau {target_level.value}",
                f"Un parcours complet de {num_modules} modules pour maîtriser {subject.value} au niveau {target_level.value}."
            )
        
        try:
            prompt = f"""Génère un titre accrocheur et une description pour un parcours d'apprentissage :
- Sujet : {subject.value}
- Niveau cible : {target_level.value}
- Nombre de modules : {num_modules}

Réponds en JSON :
{{
    "title": "<titre accrocheur et motivant>",
    "description": "<description détaillée du parcours>"
}}"""

            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "Tu es un expert en création de contenu pédagogique."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            create_params.update(_get_max_tokens_param(AI_MODEL, 300))
            response = await client.chat.completions.create(**create_params)
            
            response_text = response.choices[0].message.content
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(response_text[json_start:json_end])
                    return result.get("title", ""), result.get("description", "")
            except json.JSONDecodeError:
                pass
            
            # Fallback
            return (
                f"Parcours {subject.value.capitalize()} - Niveau {target_level.value}",
                f"Un parcours complet de {num_modules} modules pour maîtriser {subject.value} au niveau {target_level.value}."
            )
        except Exception as e:
            logger.error(f"Erreur lors de la génération titre/description: {e}", exc_info=True)
            return (
                f"Parcours {subject.value.capitalize()} - Niveau {target_level.value}",
                f"Un parcours complet de {num_modules} modules."
            )
    
    @staticmethod
    def _generate_default_objectives(subject: Subject, level: Difficulty) -> List[str]:
        """Génère des objectifs par défaut"""
        objectives_map = {
            (Subject.PHYSICS, Difficulty.BEGINNER): [
                "Comprendre les concepts fondamentaux de la physique",
                "Maîtriser les unités et mesures",
                "Appliquer les lois de base"
            ],
            (Subject.CHEMISTRY, Difficulty.BEGINNER): [
                "Comprendre la structure atomique",
                "Maîtriser les réactions chimiques de base",
                "Appliquer les concepts de stoechiométrie"
            ],
            # Ajouter d'autres combinaisons...
        }
        
        key = (subject, level)
        if key in objectives_map:
            return objectives_map[key]
        
        return [
            f"Maîtriser les concepts fondamentaux de {subject.value}",
            f"Appliquer les connaissances au niveau {level.value}",
            "Développer des compétences pratiques"
        ]
    
    @staticmethod
    async def _calculate_match_score(
        pathway: Pathway,
        profile: Dict[str, Any],
        completed_modules: set
    ) -> float:
        """Calcule le score de correspondance entre parcours et utilisateur"""
        score = 0.0
        
        # Correspondance sujet (si profil a des préférences)
        # Pour l'instant, on assume que tous les sujets sont intéressants
        score += 0.3
        
        # Correspondance difficulté
        user_level = profile.get("current_level", "beginner")
        if pathway.target_level.value == user_level or pathway.target_level == Difficulty.BEGINNER:
            score += 0.3
        
        # Progression dans le parcours
        pathway_module_ids = {m.module_id for m in pathway.modules}
        completed_in_pathway = len(completed_modules & pathway_module_ids)
        if len(pathway.modules) > 0:
            progress_ratio = completed_in_pathway / len(pathway.modules)
            score += 0.2 * progress_ratio
        
        # Nouveaux modules disponibles
        new_modules = len(pathway_module_ids - completed_modules)
        if len(pathway.modules) > 0:
            novelty_ratio = new_modules / len(pathway.modules)
            score += 0.2 * novelty_ratio
        
        return min(score, 1.0)
    
    @staticmethod
    async def _check_prerequisites(
        pathway: Pathway,
        completed_modules: set
    ) -> bool:
        """Vérifie si les prérequis du parcours sont satisfaits"""
        # Pour chaque module, vérifier ses prérequis
        for module in pathway.modules:
            if module.prerequisite_level == PrerequisiteLevel.REQUIRED:
                prereq_analysis = await PrerequisiteDetector.analyze_prerequisites(module.module_id)
                if prereq_analysis.prerequisite_score < 0.5:
                    # Vérifier si les prérequis manquants sont complétés
                    missing = set(prereq_analysis.missing_prerequisites)
                    if not missing.issubset(completed_modules):
                        return False
        return True
    
    @staticmethod
    def _generate_reasoning(
        pathway: Pathway,
        match_score: float,
        prerequisites_met: bool,
        difficulty_match: bool
    ) -> str:
        """Génère une explication pour la recommandation"""
        reasons = []
        
        if match_score > 0.8:
            reasons.append("Ce parcours correspond parfaitement à votre profil.")
        elif match_score > 0.6:
            reasons.append("Ce parcours correspond bien à votre niveau.")
        
        if difficulty_match:
            reasons.append("La difficulté correspond à votre niveau actuel.")
        
        if prerequisites_met:
            reasons.append("Vous avez les prérequis nécessaires.")
        else:
            reasons.append("Certains prérequis peuvent manquer, mais le parcours reste accessible.")
        
        if not reasons:
            reasons.append("Ce parcours pourrait vous intéresser.")
        
        return " ".join(reasons)


