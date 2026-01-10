"""
Service pour détecter automatiquement les prérequis d'un module
Utilise l'IA pour analyser le contenu et identifier les dépendances
"""
from typing import List, Dict, Any, Optional
from app.models.pathway import PrerequisiteAnalysis
from app.repositories.module_repository import ModuleRepository
from app.repositories.progress_repository import ProgressRepository as ProgressRepo
from app.services.ai_service import client, AI_MODEL
import logging
import json

logger = logging.getLogger(__name__)


class PrerequisiteDetector:
    """Détecteur de prérequis automatique"""
    
    @staticmethod
    async def analyze_prerequisites(
        module_id: str,
        user_id: Optional[str] = None
    ) -> PrerequisiteAnalysis:
        """
        Analyse les prérequis d'un module et vérifie si l'utilisateur les a complétés
        """
        try:
            # Récupérer le module
            module = await ModuleRepository.find_by_id(module_id)
            if not module:
                raise ValueError(f"Module {module_id} non trouvé")
            
            # Détecter les prérequis avec l'IA
            detected_prereqs = await PrerequisiteDetector._detect_with_ai(module)
            
            # Si un utilisateur est fourni, vérifier ses complétions
            satisfied = []
            missing = []
            
            if user_id:
                user_progress = await ProgressRepo.find_by_user(user_id, limit=100)
                completed_module_ids = {
                    p.get("module_id") for p in user_progress 
                    if p.get("completed", False)
                }
                
                for prereq_id in detected_prereqs:
                    if prereq_id in completed_module_ids:
                        satisfied.append(prereq_id)
                    else:
                        missing.append(prereq_id)
            else:
                missing = detected_prereqs
            
            # Calculer le score de prérequis
            total_prereqs = len(detected_prereqs)
            satisfied_count = len(satisfied)
            prerequisite_score = satisfied_count / total_prereqs if total_prereqs > 0 else 1.0
            
            # Générer une recommandation
            recommendation = PrerequisiteDetector._generate_recommendation(
                missing,
                satisfied,
                prerequisite_score,
                module
            )
            
            return PrerequisiteAnalysis(
                module_id=module_id,
                missing_prerequisites=missing,
                satisfied_prerequisites=satisfied,
                prerequisite_score=prerequisite_score,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des prérequis: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def _detect_with_ai(module: Dict[str, Any]) -> List[str]:
        """
        Utilise l'IA pour détecter les prérequis d'un module
        """
        if not client:
            # Mode démo - retourner des prérequis basiques basés sur le sujet
            return await PrerequisiteDetector._detect_basic_prerequisites(module)
        
        try:
            # Récupérer tous les modules du même sujet pour contexte
            subject = module.get("subject")
            all_modules = await ModuleRepository.find_by_subject(subject)
            
            # Préparer le prompt
            module_content = {
                "title": module.get("title"),
                "description": module.get("description"),
                "learning_objectives": module.get("learning_objectives", []),
                "difficulty": module.get("difficulty")
            }
            
            available_modules = [
                {
                    "id": m.get("id"),
                    "title": m.get("title"),
                    "description": m.get("description", "")[:200],
                    "difficulty": m.get("difficulty")
                }
                for m in all_modules[:20]  # Limiter à 20 pour le contexte
            ]
            
            prompt = f"""Analyse ce module et identifie les modules prérequis nécessaires pour le comprendre.

Module à analyser :
{json.dumps(module_content, indent=2, ensure_ascii=False)}

Modules disponibles :
{json.dumps(available_modules, indent=2, ensure_ascii=False)}

Identifie les modules qui doivent être complétés AVANT ce module pour une bonne compréhension.
Considère :
1. Les concepts fondamentaux nécessaires
2. La progression logique d'apprentissage
3. La difficulté (un module avancé nécessite souvent des modules débutants/intermédiaires)

Réponds UNIQUEMENT avec un JSON contenant une liste d'IDs de modules prérequis :
{{
    "prerequisites": ["module_id_1", "module_id_2", ...]
}}

Si aucun prérequis n'est nécessaire, retourne une liste vide."""

            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en pédagogie. Analyse les dépendances entre modules d'apprentissage."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            create_params.update(_get_max_tokens_param(AI_MODEL, 500))
            response = await client.chat.completions.create(**create_params)
            
            response_text = response.choices[0].message.content
            
            # Extraire le JSON
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(response_text[json_start:json_end])
                    prerequisites = result.get("prerequisites", [])
                    # Valider que les IDs existent
                    valid_prereqs = []
                    for prereq_id in prerequisites:
                        prereq_module = await ModuleRepository.find_by_id(prereq_id)
                        if prereq_module:
                            valid_prereqs.append(prereq_id)
                    return valid_prereqs
            except json.JSONDecodeError:
                pass
            
            # Fallback vers détection basique
            return await PrerequisiteDetector._detect_basic_prerequisites(module)
            
        except Exception as e:
            logger.error(f"Erreur lors de la détection IA des prérequis: {e}", exc_info=True)
            return await PrerequisiteDetector._detect_basic_prerequisites(module)
    
    @staticmethod
    async def _detect_basic_prerequisites(module: Dict[str, Any]) -> List[str]:
        """
        Détection basique des prérequis sans IA
        Basée sur la difficulté et le sujet
        """
        try:
            subject = module.get("subject")
            difficulty = module.get("difficulty")
            
            # Si le module est avancé, chercher des modules débutants/intermédiaires du même sujet
            if difficulty == "advanced":
                all_modules = await ModuleRepository.find_by_subject(subject)
                prereqs = [
                    m.get("id") for m in all_modules
                    if m.get("difficulty") in ["beginner", "intermediate"]
                    and m.get("id") != module.get("id")
                ]
                return prereqs[:3]  # Limiter à 3 prérequis
            
            return []
        except Exception as e:
            logger.error(f"Erreur lors de la détection basique: {e}", exc_info=True)
            return []
    
    @staticmethod
    def _generate_recommendation(
        missing: List[str],
        satisfied: List[str],
        score: float,
        module: Dict[str, Any]
    ) -> str:
        """Génère une recommandation basée sur l'analyse"""
        if score == 1.0:
            return f"Tous les prérequis sont satisfaits. Vous pouvez commencer le module '{module.get('title')}'."
        elif score >= 0.5:
            return f"La plupart des prérequis sont satisfaits ({len(satisfied)}/{len(missing) + len(satisfied)}). Vous pouvez commencer, mais certains concepts pourraient être difficiles."
        else:
            return f"Plusieurs prérequis manquent ({len(missing)} modules). Il est recommandé de compléter ces modules d'abord pour une meilleure compréhension."


