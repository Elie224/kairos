"""
Service pour générer automatiquement des exercices TD/TP avec solutions
"""
from typing import List, Dict, Any, Optional
from app.models import Subject, Difficulty
from app.repositories.module_repository import ModuleRepository
from app.services.ai_service import client, AI_MODEL, AIService
import logging
import json

logger = logging.getLogger(__name__)


class ExerciseGeneratorService:
    """Service pour générer des exercices automatiquement"""
    
    @staticmethod
    async def generate_td_exercises(
        module_id: str,
        num_exercises: int = 5,
        difficulty: Optional[Difficulty] = None
    ) -> List[Dict[str, Any]]:
        """
        Génère des exercices de TD pour un module
        """
        try:
            module = await ModuleRepository.find_by_id(module_id)
            if not module:
                raise ValueError(f"Module {module_id} non trouvé")
            
            # Utiliser l'IA pour générer les exercices
            exercises = await ExerciseGeneratorService._generate_with_ai(
                module,
                num_exercises,
                difficulty or Difficulty(module.get("difficulty", "beginner")),
                exercise_type="td"
            )
            
            return exercises
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'exercices TD: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def generate_tp_steps(
        module_id: str,
        num_steps: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Génère des étapes de TP pour un module
        """
        try:
            module = await ModuleRepository.find_by_id(module_id)
            if not module:
                raise ValueError(f"Module {module_id} non trouvé")
            
            # Utiliser l'IA pour générer les étapes
            steps = await ExerciseGeneratorService._generate_with_ai(
                module,
                num_steps,
                Difficulty(module.get("difficulty", "beginner")),
                exercise_type="tp"
            )
            
            return steps
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'étapes TP: {e}", exc_info=True)
            raise
    
    @staticmethod
    async def generate_solution(
        exercise: Dict[str, Any],
        exercise_type: str = "td"
    ) -> Dict[str, Any]:
        """
        Génère une solution détaillée pour un exercice
        """
        try:
            if not client:
                return {
                    "solution": "Solution détaillée générée automatiquement.",
                    "steps": ["Étape 1", "Étape 2", "Étape 3"],
                    "explanation": "Explication de la méthode utilisée."
                }
            
            prompt = f"""Génère une solution détaillée pas à pas pour cet exercice de {exercise_type.upper()} :

Exercice :
{json.dumps(exercise, indent=2, ensure_ascii=False)}

Fournis :
1. Une solution complète étape par étape
2. Les explications pour chaque étape
3. Les formules/concepts utilisés
4. Le résultat final

Réponds en JSON :
{{
    "solution": "<solution complète>",
    "steps": ["étape 1", "étape 2", ...],
    "explanation": "<explication de la méthode>",
    "formulas_used": ["formule1", "formule2"],
    "final_answer": "<réponse finale>"
}}"""

            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert pédagogique. Génère des solutions détaillées et pédagogiques."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }
            create_params.update(_get_max_tokens_param(AI_MODEL, 1500))
            response = await client.chat.completions.create(**create_params)
            
            response_text = response.choices[0].message.content
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    solution = json.loads(response_text[json_start:json_end])
                    return solution
            except json.JSONDecodeError:
                pass
            
            # Fallback
            return {
                "solution": "Solution générée par l'IA.",
                "steps": ["Étape 1", "Étape 2"],
                "explanation": "Méthode standard pour ce type d'exercice."
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de solution: {e}", exc_info=True)
            return {
                "solution": "Solution non disponible.",
                "steps": [],
                "explanation": "Erreur lors de la génération."
            }
    
    @staticmethod
    async def _generate_with_ai(
        module: Dict[str, Any],
        num_items: int,
        difficulty: Difficulty,
        exercise_type: str
    ) -> List[Dict[str, Any]]:
        """Génère des exercices/étapes avec l'IA"""
        if not client:
            return ExerciseGeneratorService._generate_demo_exercises(
                num_items,
                difficulty,
                exercise_type
            )
        
        try:
            # Récupérer le contexte complet du module pour l'IA
            module_context_data = await AIService.get_module_context_for_ai(module.get("id", ""))
            
            # Construire les informations du module avec le contenu complet
            module_info = {
                "title": module_context_data.get("title", ""),
                "description": module_context_data.get("description", ""),
                "subject": module_context_data.get("subject", ""),
                "difficulty": module_context_data.get("difficulty", "intermediate"),
                "learning_objectives": module_context_data.get("learning_objectives", [])
            }
            
            # Ajouter le contenu des leçons
            content = module_context_data.get("content", {})
            if content.get("lessons"):
                module_info["lessons"] = []
                for lesson in content["lessons"][:5]:  # Limiter à 5 leçons pour le contexte
                    lesson_info = {
                        "title": lesson.get("title", ""),
                        "summary": lesson.get("summary", "")[:200],  # Limiter la longueur
                        "content": lesson.get("content", "")[:500] if lesson.get("content") else ""
                    }
                    module_info["lessons"].append(lesson_info)
            
            # Ajouter les ressources disponibles
            resources = module_context_data.get("resources", [])
            if resources:
                module_info["resources"] = [
                    {
                        "title": r.get("title", ""),
                        "type": r.get("type", ""),
                        "description": r.get("description", "")[:100] if r.get("description") else ""
                    }
                    for r in resources[:5]  # Limiter à 5 ressources
                ]
            
            if exercise_type == "td":
                subject = module_info.get("subject", "").lower()
                if subject == "mathematics":
                    num_exercises_instruction = f"- Génère {num_items * 2} à {num_items * 3} exercices de Travaux Dirigés (beaucoup d'exercices pour les mathématiques)"
                    complexity_instruction = "- Les exercices doivent être COMPLEXES et APPROFONDIS, pas basiques ou petits\n- Chaque exercice doit être un problème complet avec plusieurs étapes de résolution\n- Focus sur des CAS CONCRETS et RÉELS, des situations pratiques"
                else:
                    num_exercises_instruction = f"- Génère {num_items} exercices de Travaux Dirigés"
                    complexity_instruction = "- Les exercices doivent être des CAS CONCRETS et RÉELS, pas des exercices basiques\n- Chaque exercice doit être un problème complet avec plusieurs étapes"
                
                prompt = f"""Tu es un expert pédagogique qui crée des exercices de Travaux Dirigés avec des cas concrets et réels.

CONTEXTE DU MODULE :
{json.dumps(module_info, indent=2, ensure_ascii=False)}

Niveau de difficulté demandé : {difficulty.value}

INSTRUCTIONS IMPORTANTES :
{num_exercises_instruction}
- Utilise les leçons et les ressources disponibles comme référence
{complexity_instruction}
- Les exercices doivent être progressifs mais tous substantiels (du moyen au très avancé)
- Chaque exercice doit tester la compréhension approfondie des concepts enseignés dans le module
- Adapte la difficulté au niveau spécifié ({difficulty.value}) mais reste exigeant
- PAS DE NOTATION : Les exercices ne doivent PAS avoir de système de points ou de notation

FORMAT DE RÉPONSE JSON strict :
{{
    "exercises": [
        {{
            "question": "<énoncé complet de l'exercice avec cas concret et contexte réel>",
            "difficulty": "{difficulty.value}",
            "hint": "<indice optionnel pour aider l'étudiant>"
        }},
        ...
    ]
}}

IMPORTANT : 
- Génère des exercices CONCRETS avec des situations RÉELLES
- Pas d'exercices basiques ou trop simples
- Pour les mathématiques : génère beaucoup d'exercices complexes et variés
- PAS de champ "points" dans les exercices

Génère exactement le nombre demandé d'exercices au format JSON ci-dessus."""
            else:  # tp
                prompt = f"""Tu es un expert pédagogique qui crée des Travaux Pratiques.

CONTEXTE DU MODULE :
{json.dumps(module_info, indent=2, ensure_ascii=False)}

Niveau de difficulté demandé : {difficulty.value}

INSTRUCTIONS :
- Génère {num_items} étapes pour un Travail Pratique basé sur le contenu réel du module
- Utilise les leçons et les ressources disponibles comme référence
- Les étapes doivent être logiques et progressives
- Chaque étape doit permettre à l'étudiant d'appliquer les concepts enseignés
- Adapte la complexité au niveau spécifié ({difficulty.value})

FORMAT DE RÉPONSE JSON strict :
{{
    "steps": [
        {{
            "step_number": <numéro d'ordre>,
            "title": "<titre clair de l'étape>",
            "instructions": "<instructions détaillées et précises pour réaliser l'étape>",
            "expected_result": "<description du résultat attendu après cette étape>",
            "tips": ["conseil pratique 1", "conseil pratique 2"]
        }},
        ...
    ]
}}

Génère exactement {num_items} étapes au format JSON ci-dessus."""

            from app.services.ai_service import _get_max_tokens_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": f"Tu es un expert en création d'exercices pédagogiques de type {exercise_type.upper()}."
                    },
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7
            }
            create_params.update(_get_max_tokens_param(AI_MODEL, 2000))
            response = await client.chat.completions.create(**create_params)
            
            response_text = response.choices[0].message.content
            
            try:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    result = json.loads(response_text[json_start:json_end])
                    
                    if exercise_type == "td":
                        exercises = result.get("exercises", [])
                        # Générer les solutions pour chaque exercice
                        for exercise in exercises:
                            solution = await ExerciseGeneratorService.generate_solution(
                                exercise,
                                "td"
                            )
                            exercise["solution"] = solution
                        return exercises
                    else:
                        return result.get("steps", [])
            except json.JSONDecodeError:
                pass
            
            # Fallback
            return ExerciseGeneratorService._generate_demo_exercises(
                num_items,
                difficulty,
                exercise_type
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération IA: {e}", exc_info=True)
            return ExerciseGeneratorService._generate_demo_exercises(
                num_items,
                difficulty,
                exercise_type
            )
    
    @staticmethod
    def _generate_demo_exercises(
        num_items: int,
        difficulty: Difficulty,
        exercise_type: str
    ) -> List[Dict[str, Any]]:
        """Génère des exercices de démo"""
        if exercise_type == "td":
            return [
                {
                    "question": f"Exercice {i+1} - Niveau {difficulty.value}",
                    "difficulty": difficulty.value,
                    "hint": f"Indice pour l'exercice {i+1}",
                    "solution": {
                        "solution": f"Solution de l'exercice {i+1}",
                        "steps": [f"Étape {j+1}" for j in range(3)],
                        "explanation": "Explication de la méthode"
                    }
                }
                for i in range(num_items)
            ]
        else:  # tp
            return [
                {
                    "step_number": i+1,
                    "title": f"Étape {i+1}",
                    "instructions": f"Instructions détaillées pour l'étape {i+1}",
                    "expected_result": f"Résultat attendu pour l'étape {i+1}",
                    "tips": [f"Conseil {j+1}" for j in range(2)]
                }
                for i in range(num_items)
            ]


