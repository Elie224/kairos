"""
Service pour générer automatiquement des TD et TP en format PDF
"""
from typing import Dict, Any, List, Optional
from app.services.ai_service import AIService, client, AI_MODEL
from app.services.exercise_generator_service import ExerciseGeneratorService
from app.repositories.td_repository import TDRepository
from app.repositories.tp_repository import TPRepository
from app.repositories.resource_repository import ResourceRepository
from app.models import TDCreate, TPCreate, ResourceCreate, ResourceType
from app.repositories.module_repository import ModuleRepository
from app.database import get_database
from bson import ObjectId
import logging
import json
from datetime import datetime, timezone
from pathlib import Path
import uuid
import asyncio
from app.utils.json_cleaner import safe_json_loads

logger = logging.getLogger(__name__)

# Dossier pour stocker les PDF générés
# Utiliser un chemin absolu pour éviter les problèmes de chemin relatif
import os
PDF_DIR = Path(os.path.join(os.getcwd(), "uploads", "resources"))
PDF_DIR.mkdir(parents=True, exist_ok=True)


class PDFGeneratorService:
    """Service pour générer automatiquement des TD et TP en PDF"""
    
    @staticmethod
    async def generate_td_pdf_for_lesson(
        module_id: str,
        lesson_title: str,
        lesson_content: str,
        lesson_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère un TD en PDF pour une leçon spécifique
        """
        try:
            # Récupérer le module pour obtenir le contexte
            module = await ModuleRepository.find_by_id(module_id)
            if not module:
                logger.error(f"Module {module_id} non trouvé pour génération TD")
                return None
            
            # Générer le contenu du TD via l'IA
            td_content = await PDFGeneratorService._generate_td_content_with_ai(
                module=module,
                lesson_title=lesson_title,
                lesson_content=lesson_content,
                lesson_summary=lesson_summary
            )
            
            if not td_content:
                logger.error(f"Impossible de générer le contenu du TD pour la leçon '{lesson_title}'")
                logger.error("Vérifiez que OPENAI_API_KEY est configuré et que le client OpenAI est initialisé")
                return None
            
            # Créer le TD dans la base de données
            logger.info(f"📝 Création du TD dans la base de données pour '{lesson_title}'")
            logger.debug(f"Nombre d'exercices: {len(td_content.get('exercises', []))}")
            
            try:
                logger.info(f"📝 Préparation des données TD pour '{lesson_title}'...")
                td_data = TDCreate(
                    module_id=module_id,
                    title=f"TD - {lesson_title}",
                    description=f"Travaux Dirigés générés automatiquement pour la leçon : {lesson_title}",
                    exercises=td_content.get("exercises", []),
                    estimated_time=td_content.get("estimated_time", 60)
                )
                
                logger.info(f"📝 Conversion des données TD en dictionnaire pour '{lesson_title}'...")
                td_dict = td_data.dict()
                logger.debug(f"Données TD préparées: {list(td_dict.keys())}")
                
                logger.info(f"📝 Appel TDRepository.create pour '{lesson_title}'...")
                td = await TDRepository.create(td_dict)
                td_id = td.get('id') or td.get('_id', 'N/A')
                logger.info(f"✅ TD créé dans la base de données avec l'ID: {td_id}")
            except Exception as db_error:
                logger.error(f"❌ Erreur lors de la création du TD dans la base de données: {db_error}", exc_info=True)
                raise
            
            # Générer le PDF
            logger.info(f"📄 Génération du PDF pour le TD '{lesson_title}'...")
            pdf_path = await PDFGeneratorService._create_pdf_from_td(
                td=td,
                lesson_title=lesson_title
            )
            logger.info(f"📄 PDF généré: {pdf_path if pdf_path else 'None'}")
            
            if pdf_path:
                # Sauvegarder le PDF comme ressource
                resource_data = ResourceCreate(
                    module_id=module_id,
                    title=f"TD - {lesson_title}",
                    description=f"Travaux Dirigés en PDF pour la leçon : {lesson_title}",
                    resource_type=ResourceType.PDF,
                    file_url=f"/api/resources/files/{pdf_path.name}",
                    file_size=pdf_path.stat().st_size,
                    file_name=pdf_path.name
                )
                
                resource_dict = resource_data.dict()
                resource_dict["created_at"] = datetime.now(timezone.utc)
                resource_dict["updated_at"] = datetime.now(timezone.utc)
                resource = await ResourceRepository.create(resource_dict)
                
                # Mettre à jour le TD avec l'URL du PDF
                pdf_url = f"/api/resources/files/{pdf_path.name}"
                db = get_database()
                td_id = td.get('id') or td.get('_id')
                if td_id:
                    await db.tds.update_one(
                        {"_id": ObjectId(str(td_id))},
                        {"$set": {"pdf_url": pdf_url, "updated_at": datetime.now(timezone.utc)}}
                    )
                    td["pdf_url"] = pdf_url
                    logger.info(f"✅ TD mis à jour avec pdf_url: {pdf_url}")
                
                logger.info(f"✅ TD PDF généré et sauvegardé pour la leçon {lesson_title}")
                result = {
                    "td": td,
                    "resource": resource,
                    "pdf_path": str(pdf_path),
                    "pdf_url": pdf_url
                }
                logger.info(f"✅ Retour de generate_td_pdf_for_lesson pour '{lesson_title}': TD créé, PDF créé")
                return result
            
            logger.info(f"⚠️ TD créé mais PDF non généré pour '{lesson_title}'")
            result = {"td": td}
            logger.info(f"✅ Retour de generate_td_pdf_for_lesson pour '{lesson_title}': TD créé uniquement")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération du TD PDF: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def generate_tp_pdf_for_lesson(
        module_id: str,
        lesson_title: str,
        lesson_content: str = "",
        lesson_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère un TP en PDF pour une leçon spécifique
        """
        try:
            # Récupérer le module pour obtenir le contexte
            module = await ModuleRepository.find_by_id(module_id)
            if not module:
                logger.error(f"Module {module_id} non trouvé pour génération TP")
                return None
            
            # S'assurer que lesson_content est une string
            if not isinstance(lesson_content, str):
                lesson_content = str(lesson_content) if lesson_content else ""
            
            # Générer le contenu du TP via l'IA
            tp_content = await PDFGeneratorService._generate_tp_content_with_ai(
                module=module,
                lesson_title=lesson_title,
                lesson_content=lesson_content,
                lesson_summary=lesson_summary
            )
            
            if not tp_content:
                logger.error(f"Impossible de générer le contenu du TP pour la leçon '{lesson_title}'")
                logger.error("Vérifiez que OPENAI_API_KEY est configuré et que le client OpenAI est initialisé")
                return None
            
            # Créer le TP dans la base de données
            tp_data = TPCreate(
                module_id=module_id,
                title=f"TP - {lesson_title}",
                description=f"Travaux Pratiques générés automatiquement pour la leçon : {lesson_title}",
                objectives=tp_content.get("objectives", []),
                steps=tp_content.get("steps", []),
                estimated_time=tp_content.get("estimated_time", 90),
                materials_needed=tp_content.get("materials_needed", [])
            )
            
            tp_dict = tp_data.dict()
            tp = await TPRepository.create(tp_dict)
            
            # Générer le PDF
            pdf_path = await PDFGeneratorService._create_pdf_from_tp(
                tp=tp,
                lesson_title=lesson_title
            )
            
            if pdf_path:
                # Sauvegarder le PDF comme ressource
                resource_data = ResourceCreate(
                    module_id=module_id,
                    title=f"TP - {lesson_title}",
                    description=f"Travaux Pratiques en PDF pour la leçon : {lesson_title}",
                    resource_type=ResourceType.PDF,
                    file_url=f"/api/resources/files/{pdf_path.name}",
                    file_size=pdf_path.stat().st_size,
                    file_name=pdf_path.name
                )
                
                resource_dict = resource_data.dict()
                resource_dict["created_at"] = datetime.now(timezone.utc)
                resource_dict["updated_at"] = datetime.now(timezone.utc)
                resource = await ResourceRepository.create(resource_dict)
                
                # Mettre à jour le TP avec l'URL du PDF
                pdf_url = f"/api/resources/files/{pdf_path.name}"
                db = get_database()
                tp_id = tp.get('id') or tp.get('_id')
                if tp_id:
                    await db.tps.update_one(
                        {"_id": ObjectId(str(tp_id))},
                        {"$set": {"pdf_url": pdf_url, "updated_at": datetime.now(timezone.utc)}}
                    )
                    tp["pdf_url"] = pdf_url
                    logger.info(f"✅ TP mis à jour avec pdf_url: {pdf_url}")
                
                logger.info(f"✅ TP PDF généré et sauvegardé pour la leçon {lesson_title}")
                return {
                    "tp": tp,
                    "resource": resource,
                    "pdf_path": str(pdf_path),
                    "pdf_url": pdf_url
                }
            
            return {"tp": tp}
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du TP PDF: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def _generate_td_content_with_ai(
        module: Dict[str, Any],
        lesson_title: str,
        lesson_content: str,
        lesson_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """Génère le contenu d'un TD via l'IA basé sur une leçon"""
        if not client:
            error_msg = "OpenAI client non disponible - Vérifiez que OPENAI_API_KEY est configuré dans .env et redémarrez le backend"
            logger.error(error_msg)
            logger.error("La génération TD/TP nécessite une clé API OpenAI valide")
            raise ValueError(error_msg)
        
        try:
            subject = module.get("subject", "")
            difficulty = module.get("difficulty", "intermediate")
            
            # Récupérer les ressources du module pour enrichir le contexte
            resources_info = ""
            try:
                from app.repositories.resource_repository import ResourceRepository
                resources = await ResourceRepository.find_by_module_id(module.get("id", ""))
                if resources:
                    resources_info = "\n\nRESSOURCES DISPONIBLES POUR CETTE LEÇON :\n"
                    for r in resources[:5]:  # Limiter à 5 ressources
                        resources_info += f"- {r.get('title', '')} ({r.get('resource_type', '')})\n"
                    resources_info += "\nLe contenu détaillé de la leçon provient de ces ressources (PDF, Word, PPT, Vidéo, Audio)."
            except Exception as e:
                logger.warning(f"Impossible de récupérer les ressources: {e}")
            
            # Tous les modules doivent avoir 6 à 10 exercices par chapitre/leçon
            num_exercises = "6 à 10"
            exercise_instruction = f"""- Crée EXACTEMENT {num_exercises} exercices de TD basés sur le titre et le résumé de cette leçon
- Les exercices doivent être des CAS CONCRETS et RÉELS, pas des exercices basiques
- Chaque exercice doit être un problème complet et complexe, avec plusieurs étapes de résolution
- Les exercices doivent couvrir TOUS les aspects importants du chapitre de manière approfondie
- Adapte la complexité au niveau du module ({difficulty}) mais reste exigeant
- Les exercices doivent être progressifs mais tous substantiels (du moyen au très avancé)
- Inclus des problèmes appliqués, des situations réelles, des cas d'étude concrets
- IMPORTANT : Assure-toi de couvrir TOUS les concepts clés de ce chapitre dans les exercices"""
            
            prompt = f"""Tu es un expert pédagogique qui crée des Travaux Dirigés (TD) avec des cas concrets et réels.

CONTEXTE DU MODULE :
- Titre: {module.get('title', '')}
- Matière: {subject}
- Niveau: {difficulty}

CHAPITRE/LEÇON POUR LAQUELLE CRÉER LE TD :
- Titre du chapitre: {lesson_title}
- Résumé: {lesson_summary or 'Non disponible'}
- Contenu complet du chapitre: {lesson_content[:3000] if lesson_content else 'Le contenu de ce chapitre provient des ressources (PDF, Word, PPT, Vidéo, Audio) disponibles dans le module.'}
{resources_info}

OBJECTIF CRITIQUE :
Tu dois créer un TD pour ce chapitre spécifique qui couvre TOUS les concepts et notions importantes de ce chapitre.
Le TD doit permettre aux étudiants de maîtriser l'ensemble du contenu du chapitre à travers des exercices pratiques.

INSTRUCTIONS IMPORTANTES :
{exercise_instruction}
- Chaque exercice doit tester la compréhension approfondie des concepts couverts par cette leçon
- Référence les ressources disponibles si pertinent
- PAS DE NOTATION : Les exercices ne doivent PAS avoir de système de points ou de notation
- Focus sur l'apprentissage pratique et la résolution de problèmes réels

FORMAT JSON strict :
{{
  "exercises": [
    {{
      "question": "Énoncé complet de l'exercice avec cas concret et contexte réel",
      "difficulty": "beginner|intermediate|advanced",
      "hint": "Indice optionnel pour aider l'étudiant"
    }},
    ... (6 à 10 exercices au total)
  ],
  "estimated_time": 90
}}

CRITÈRE DE VALIDATION :
- Tu DOIS générer EXACTEMENT entre 6 et 10 exercices (ni moins, ni beaucoup plus)
- Minimum : 6 exercices obligatoires
- Maximum recommandé : 10 exercices
- Si tu génères moins de 6 exercices, le TD sera incomplet

IMPORTANT : 
- Génère EXACTEMENT 6 à 10 exercices CONCRETS avec des situations RÉELLES pour ce chapitre
- Pas d'exercices basiques ou trop simples
- Chaque exercice doit être substantiel et tester un aspect différent du chapitre
- Assure-toi de couvrir TOUS les concepts importants du chapitre dans les exercices
- Les exercices doivent être variés pour couvrir l'ensemble du contenu du chapitre
- PAS de champ "points" dans les exercices

Génère le TD avec EXACTEMENT 6 à 10 exercices au format JSON ci-dessus."""
            
            from app.services.ai_service import _get_max_tokens_param, _get_temperature_param
            create_params = {
                "model": AI_MODEL,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert pédagogique qui génère des Travaux Dirigés au format JSON strict."
                    },
                    {"role": "user", "content": prompt}
                ]
            }
            # Augmenter les tokens max pour permettre la génération de 6-10 exercices détaillés
            create_params.update(_get_max_tokens_param(AI_MODEL, 4000))
            create_params.update(_get_temperature_param(AI_MODEL, 0.7))
            
            # gpt-4o supporte response_format, on peut l'ajouter pour forcer le format JSON
            # Note: gpt-4o-mini est déjà le modèle mappé depuis gpt-5-mini
            if not AI_MODEL.startswith("gpt-3.5"):
                create_params["response_format"] = {"type": "json_object"}
            
            # client.chat.completions.create() est synchrone, utiliser asyncio.to_thread
            logger.info(f"Appel OpenAI pour génération TD - Modèle: {AI_MODEL}, Leçon: {lesson_title}")
            logger.info(f"Paramètres de l'appel: model={AI_MODEL}, messages_count={len(create_params['messages'])}")
            try:
                response = await asyncio.to_thread(client.chat.completions.create, **create_params)
                logger.info(f"✅ Réponse OpenAI reçue pour '{lesson_title}'")
            except Exception as api_error:
                logger.error(f"❌ ERREUR API OpenAI lors de l'appel: {type(api_error).__name__}: {api_error}")
                logger.error(f"Détails de l'erreur: {str(api_error)}")
                # Si c'est une erreur de modèle, suggérer un modèle alternatif
                if "model" in str(api_error).lower() or "not found" in str(api_error).lower():
                    logger.error(f"⚠️ Le modèle '{AI_MODEL}' n'existe peut-être pas. Essayez 'gpt-4o-mini' ou 'gpt-4-turbo'")
                raise
            
            if not response or not response.choices or len(response.choices) == 0:
                logger.error(f"❌ Réponse OpenAI invalide (pas de choices)")
                return None
            
            response_text = response.choices[0].message.content
            logger.info(f"Contenu extrait: {len(response_text) if response_text else 0} caractères")
            
            # Vérifier que la réponse n'est pas vide
            if not response_text:
                logger.error(f"❌ Réponse OpenAI vide pour '{lesson_title}'")
                logger.error(f"Finish reason: {response.choices[0].finish_reason}")
                if hasattr(response, 'usage') and response.usage:
                    logger.error(f"Usage: {response.usage}")
                return None
            
            logger.debug(f"Premiers 200 caractères: {response_text[:200]}")
            
            # Parser le JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            logger.info(f"Recherche JSON: start={json_start}, end={json_end}")
            
            if json_start >= 0 and json_end > json_start:
                json_content = response_text[json_start:json_end]
                logger.info(f"Parsing JSON ({len(json_content)} caractères)")
                try:
                    result = safe_json_loads(json_content)
                    if result:
                        exercises = result.get('exercises', [])
                        num_exercises = len(exercises)
                        
                        # Valider que le nombre d'exercices est entre 6 et 10
                        if num_exercises < 6:
                            logger.warning(f"⚠️ Seulement {num_exercises} exercices générés pour le chapitre '{lesson_title}', attendu 6 à 10")
                        elif num_exercises > 10:
                            logger.warning(f"⚠️ {num_exercises} exercices générés pour le chapitre '{lesson_title}', attendu 6 à 10 (sera utilisé tel quel)")
                        else:
                            logger.info(f"✅ TD généré avec succès - {num_exercises} exercices (conforme : 6-10)")
                        
                        return result
                    else:
                        logger.error(f"❌ Impossible de parser le JSON du TD")
                        logger.error(f"Contenu problématique: {json_content[:1000]}")
                        return None
                except Exception as parse_error:
                    logger.error(f"❌ Erreur inattendue lors du parsing: {parse_error}", exc_info=True)
                    return None
            
            logger.warning(f"⚠️ JSON non trouvé dans la réponse. Réponse: {response_text[:500]}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du contenu TD: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def _generate_tp_content_with_ai(
        module: Dict[str, Any],
        lesson_title: str,
        lesson_content: str,
        lesson_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """Génère le contenu d'un TP via l'IA basé sur une leçon"""
        if not client:
            error_msg = "OpenAI client non disponible - Vérifiez que OPENAI_API_KEY est configuré dans .env et redémarrez le backend"
            logger.error(error_msg)
            logger.error("La génération TD/TP nécessite une clé API OpenAI valide")
            raise ValueError(error_msg)
        
        try:
            subject = module.get("subject", "")
            difficulty = module.get("difficulty", "intermediate")
            
            # Récupérer les ressources du module pour enrichir le contexte
            resources_info = ""
            try:
                from app.repositories.resource_repository import ResourceRepository
                resources = await ResourceRepository.find_by_module_id(module.get("id", ""))
                if resources:
                    resources_info = "\n\nRESSOURCES DISPONIBLES POUR CETTE LEÇON :\n"
                    for r in resources[:5]:  # Limiter à 5 ressources
                        resources_info += f"- {r.get('title', '')} ({r.get('resource_type', '')})\n"
                    resources_info += "\nLe contenu détaillé de la leçon provient de ces ressources (PDF, Word, PPT, Vidéo, Audio)."
            except Exception as e:
                logger.warning(f"Impossible de récupérer les ressources: {e}")
            
            # Pour les mathématiques, générer plus d'exercices pratiques
            if subject.lower() == "mathematics":
                num_steps = "6 à 10"
                step_instruction = f"""- Crée un TP avec {num_steps} exercices pratiques de PROGRAMMATION et d'ALGORITHMIQUE
- Chaque exercice doit être un CAS CONCRET avec un problème réel à résoudre
- Les exercices doivent être complexes et approfondis, pas basiques
- Focus sur l'implémentation d'algorithmes mathématiques avancés, la résolution numérique, la visualisation de données mathématiques"""
            else:
                num_steps = "4 à 6"
                step_instruction = f"""- Crée un TP avec {num_steps} exercices pratiques de PROGRAMMATION et d'ALGORITHMIQUE
- Chaque exercice doit être un CAS CONCRET avec un problème réel à résoudre
- Focus sur l'implémentation d'algorithmes, la manipulation de données, l'entraînement de modèles"""
            
            prompt = f"""Tu es un expert en programmation et algorithmique qui crée des Travaux Pratiques (TP) avec des cas concrets et réels.

CONTEXTE DU MODULE :
- Titre: {module.get('title', '')}
- Matière: {subject}
- Niveau: {difficulty}

LEÇON POUR LAQUELLE CRÉER LE TP :
- Titre: {lesson_title}
- Résumé: {lesson_summary or 'Non disponible'}
- Contenu: {lesson_content[:2000] if lesson_content else 'Le contenu de cette leçon provient des ressources (PDF, Word, PPT, Vidéo, Audio) disponibles dans le module.'}
{resources_info}

INSTRUCTIONS IMPORTANTES :
{step_instruction}
- Chaque exercice doit inclure :
  * Un énoncé clair avec un problème CONCRET et RÉEL à résoudre (pas théorique)
  * Un algorithme à implémenter ou un programme complet à écrire
  * Des spécifications techniques précises (langage, structures de données, contraintes)
  * Des exemples de code ou de pseudo-code si pertinent
  * Des tests à effectuer pour valider la solution
- Les exercices doivent être progressifs mais tous substantiels : du moyen au très complexe
- Adapte la complexité au niveau du module ({difficulty}) mais reste exigeant
- PAS DE NOTATION : Les exercices ne doivent PAS avoir de système de points ou de notation
- Focus sur l'apprentissage pratique et la résolution de problèmes réels

FORMAT JSON strict :
{{
  "objectives": ["Objectif pratique 1", "Objectif pratique 2", "Objectif pratique 3"],
  "steps": [
    {{
      "step_number": 1,
      "title": "Exercice 1 : [Titre de l'exercice pratique]",
      "instructions": "ÉNONCÉ : [Description du problème à résoudre]\n\nTÂCHE : [Ce qu'il faut faire - implémenter un algorithme, écrire un programme, etc.]\n\nSPÉCIFICATIONS : [Langage, structures de données, contraintes techniques]\n\nEXEMPLE : [Exemple de code ou de résultat attendu si pertinent]",
      "expected_result": "Résultat attendu : [Description du résultat, sortie du programme, ou validation]",
      "code_example": "// Exemple de code ou pseudo-code (optionnel)",
      "tests": ["Test 1 : [Description]", "Test 2 : [Description]"],
      "tips": ["Conseil technique 1", "Conseil technique 2"]
    }},
    {{
      "step_number": 2,
      "title": "Exercice 2 : [Titre de l'exercice pratique]",
      "instructions": "[Même structure que l'exercice 1]",
      "expected_result": "[Résultat attendu]",
      "code_example": "[Code ou pseudo-code si pertinent]",
      "tests": ["Test 1", "Test 2"],
      "tips": ["Conseil 1", "Conseil 2"]
    }}
  ],
  "estimated_time": 90,
  "materials_needed": ["IDE/Éditeur de code", "Langage de programmation approprié", "Bibliothèques nécessaires"],
  "programming_language": "Python ou autre selon le contexte"
}}

IMPORTANT : Génère des exercices PRATIQUES avec du CODE, des ALGORITHMES, des PROGRAMMES à écrire. Pas juste des étapes théoriques.

Génère le TP au format JSON ci-dessus."""
            
            from app.services.ai_service import _get_max_tokens_param, _get_temperature_param
            from app.config import settings
            from app.utils.model_mapper import map_to_real_model
            
            # Utiliser GPT-5.2 (Expert) pour les TP Machine Learning, GPT-5-mini pour les autres
            if subject.lower() == "computer_science" and "machine learning" in lesson_title.lower():
                tp_model = settings.gpt_5_2_model  # Expert pour TP ML
                logger.info(f"Utilisation du modèle Expert (GPT-5.2) pour TP Machine Learning")
            else:
                tp_model = settings.gpt_5_mini_model  # Principal pour autres TP
                logger.info(f"Utilisation du modèle Principal (GPT-5-mini) pour TP {subject}")
            
            # Mapper le modèle fictif vers le vrai modèle OpenAI
            actual_model = map_to_real_model(tp_model)
            if tp_model != actual_model:
                logger.info(f"Modèle '{tp_model}' mappé vers '{actual_model}' (modèle réel OpenAI)")
            
            create_params = {
                "model": actual_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en programmation et algorithmique qui génère des Travaux Pratiques avec exercices pratiques, programmes et algorithmes au format JSON strict."
                    },
                    {"role": "user", "content": prompt}
                ]
            }
            create_params.update(_get_max_tokens_param(actual_model, 3000))  # Plus de tokens pour les TP avec code
            create_params.update(_get_temperature_param(actual_model, 0.7))
            
            # gpt-4o supporte response_format, on peut l'ajouter pour forcer le format JSON
            if not actual_model.startswith("gpt-3.5"):
                create_params["response_format"] = {"type": "json_object"}
            
            # client.chat.completions.create() est synchrone, utiliser asyncio.to_thread
            logger.info(f"Appel OpenAI pour génération TP - Modèle: {actual_model}, Leçon: {lesson_title}")
            logger.info(f"Paramètres de l'appel TP: model={actual_model}, messages_count={len(create_params['messages'])}")
            try:
                response = await asyncio.to_thread(client.chat.completions.create, **create_params)
                logger.info(f"✅ Réponse OpenAI reçue pour TP '{lesson_title}'")
            except Exception as api_error:
                logger.error(f"❌ ERREUR API OpenAI lors de l'appel TP: {type(api_error).__name__}: {api_error}")
                logger.error(f"Détails de l'erreur TP: {str(api_error)}")
                # Si c'est une erreur de modèle, suggérer un modèle alternatif
                if "model" in str(api_error).lower() or "not found" in str(api_error).lower():
                    logger.error(f"⚠️ Le modèle '{actual_model}' n'existe peut-être pas. Essayez 'gpt-4o-mini' ou 'gpt-4-turbo'")
                raise
            
            if not response or not response.choices or len(response.choices) == 0:
                logger.error(f"Réponse OpenAI invalide pour la génération TP de la leçon '{lesson_title}'")
                return None
            
            response_text = response.choices[0].message.content
            
            # Vérifier que la réponse n'est pas vide
            if not response_text:
                logger.error(f"Réponse OpenAI vide pour la génération TP de la leçon '{lesson_title}'")
                logger.error(f"Finish reason: {response.choices[0].finish_reason}")
                if hasattr(response, 'usage') and response.usage:
                    logger.error(f"Usage: {response.usage}")
                return None
            
            logger.debug(f"Réponse OpenAI reçue ({len(response_text)} caractères) pour '{lesson_title}'")
            
            # Parser le JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_content = response_text[json_start:json_end]
                result = safe_json_loads(json_content)
                if result:
                    logger.info(f"TP généré avec succès pour '{lesson_title}' - {len(result.get('steps', []))} étapes")
                    return result
                else:
                    logger.error(f"Erreur de parsing JSON pour le TP de '{lesson_title}'")
                    logger.error(f"Contenu JSON problématique: {json_content[:500]}")
                    return None
            
            logger.warning(f"Impossible de trouver du JSON dans la réponse pour le TP de '{lesson_title}'. Réponse: {response_text[:500]}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du contenu TP: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def _create_pdf_from_td(td: Dict[str, Any], lesson_title: str) -> Optional[Path]:
        """Crée un fichier PDF à partir d'un TD"""
        try:
            logger.info(f"📄 Début de la création du PDF TD pour '{lesson_title}'...")
            # Utiliser reportlab ou une autre bibliothèque pour générer le PDF
            # Pour l'instant, créer un fichier texte simple (à remplacer par PDF réel)
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            filename = f"td_{uuid.uuid4()}.pdf"
            filepath = PDF_DIR / filename
            # S'assurer que le répertoire existe
            filepath.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"📄 Fichier PDF TD: {filepath}")
            
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            logger.info(f"📄 Document PDF TD créé pour '{lesson_title}'")
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor='#2563EB',
                spaceAfter=30,
                alignment=1  # Centré
            )
            story.append(Paragraph(f"TD - {lesson_title}", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Description
            if td.get("description"):
                story.append(Paragraph(f"<b>Description:</b> {td.get('description')}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Exercices
            exercises = td.get("exercises", [])
            for i, exercise in enumerate(exercises, 1):
                story.append(Paragraph(f"<b>Exercice {i}</b>", styles['Heading2']))
                story.append(Paragraph(exercise.get("question", ""), styles['Normal']))
                
                if exercise.get("hint"):
                    story.append(Paragraph(f"<i>Indice: {exercise.get('hint')}</i>", styles['Normal']))
                
                story.append(Spacer(1, 0.3*inch))
            
            logger.info(f"📄 Construction du PDF TD pour '{lesson_title}' (doc.build)...")
            doc.build(story)
            logger.info(f"✅ PDF TD créé avec succès: {filepath}")
            return filepath
            
        except ImportError:
            # Si reportlab n'est pas installé, créer un fichier texte simple
            logger.warning("reportlab non disponible, création d'un fichier texte")
            filename = f"td_{uuid.uuid4()}.txt"
            filepath = PDF_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"TD - {lesson_title}\n\n")
                f.write(f"{td.get('description', '')}\n\n")
                
                exercises = td.get("exercises", [])
                for i, exercise in enumerate(exercises, 1):
                    f.write(f"Exercice {i}\n")
                    f.write(f"{exercise.get('question', '')}\n")
                    if exercise.get("hint"):
                        f.write(f"Indice: {exercise.get('hint')}\n")
                    f.write("\n")
            
            return filepath
        except Exception as e:
            logger.error(f"Erreur lors de la création du PDF TD: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def _create_pdf_from_exam(exam: Dict[str, Any], module_title: str) -> Optional[Path]:
        """Crée un fichier PDF à partir d'un examen"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.colors import HexColor
            
            filename = f"exam_{uuid.uuid4()}.pdf"
            # Utiliser un chemin absolu pour éviter les problèmes de chemin relatif
            filepath = Path(PDF_DIR).resolve() / filename
            # S'assurer que le répertoire existe
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            logger.info(f"📄 Document PDF Examen créé pour '{module_title}'")
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor='#DC2626',
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph(f"EXAMEN - {module_title}", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Informations de l'examen
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor='#666666'
            )
            
            exam_type = exam.get('exam_type', 'standard')
            if exam_type == 'mathematics':
                story.append(Paragraph(f"<b>Type d'examen:</b> Mathématiques (QCM 25% + Exercices pratiques 75%)", info_style))
                story.append(Paragraph(f"<b>Questions QCM:</b> {exam.get('num_questions', 0)}", info_style))
                practical_exercises = exam.get('practical_exercises', [])
                story.append(Paragraph(f"<b>Exercices pratiques:</b> {len(practical_exercises)}", info_style))
            else:
                story.append(Paragraph(f"<b>Nombre de questions:</b> {exam.get('num_questions', 0)}", info_style))
            
            story.append(Paragraph(f"<b>Score de passage:</b> {exam.get('passing_score', 70)}%", info_style))
            story.append(Paragraph(f"<b>Temps limite:</b> {exam.get('time_limit', 30)} minutes", info_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Style pour les questions
            question_style = ParagraphStyle(
                'QuestionStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor='#1F2937',
                spaceAfter=10
            )
            
            # Style pour les options
            option_style = ParagraphStyle(
                'OptionStyle',
                parent=styles['Normal'],
                fontSize=10,
                leftIndent=20,
                spaceAfter=5
            )
            
            exam_type = exam.get('exam_type', 'standard')
            
            # Partie QCM
            questions = exam.get("questions", [])
            if questions:
                if exam_type == 'mathematics':
                    story.append(Paragraph("<b>PARTIE 1 : QUESTIONS À CHOIX MULTIPLES (25% de la note)</b>", styles['Heading2']))
                    story.append(Spacer(1, 0.2*inch))
                
                for i, question_data in enumerate(questions, 1):
                    # Nouvelle page pour chaque question (sauf la première)
                    if i > 1:
                        story.append(PageBreak())
                    
                    story.append(Paragraph(f"<b>Question {i} ({question_data.get('points', 1)} point{'s' if question_data.get('points', 1) > 1 else ''})</b>", styles['Heading2']))
                    story.append(Spacer(1, 0.1*inch))
                    
                    # Énoncé de la question
                    question_text = question_data.get("question", "")
                    story.append(Paragraph(question_text, question_style))
                    story.append(Spacer(1, 0.15*inch))
                    
                    # Options
                    options = question_data.get("options", [])
                    correct_answer_index = question_data.get("correct_answer", 0)
                    
                    for j, option in enumerate(options):
                        marker = "✓" if j == correct_answer_index else "○"
                        color = "#059669" if j == correct_answer_index else "#6B7280"
                        story.append(Paragraph(
                            f"<font color='{color}'>{marker}</font> {option}",
                            option_style
                        ))
                    
                    story.append(Spacer(1, 0.1*inch))
                    
                    # Explication (si disponible)
                    explanation = question_data.get("explanation", "")
                    if explanation:
                        story.append(Paragraph(f"<i><b>Explication:</b> {explanation}</i>", styles['Italic']))
            
            # Partie Exercices pratiques (pour les examens de mathématiques)
            if exam_type == 'mathematics':
                practical_exercises = exam.get('practical_exercises', [])
                if practical_exercises:
                    story.append(PageBreak())
                    story.append(Paragraph("<b>PARTIE 2 : EXERCICES PRATIQUES (75% de la note)</b>", styles['Heading2']))
                    story.append(Spacer(1, 0.2*inch))
                    
                    # Style pour les exercices pratiques
                    exercise_style = ParagraphStyle(
                        'ExerciseStyle',
                        parent=styles['Normal'],
                        fontSize=11,
                        textColor='#1F2937',
                        spaceAfter=15,
                        leftIndent=0
                    )
                    
                    for i, exercise in enumerate(practical_exercises, 1):
                        if i > 1:
                            story.append(PageBreak())
                        
                        # Titre de l'exercice
                        exercise_title = exercise.get("title", f"Exercice {i}")
                        story.append(Paragraph(f"<b>Exercice {i} : {exercise_title}</b>", styles['Heading2']))
                        story.append(Spacer(1, 0.15*inch))
                        
                        # Vérifier si l'exercice a la nouvelle structure avec parties
                        if "parts" in exercise and exercise.get("parts"):
                            # Nouvelle structure : exercice avec parties et sous-questions
                            for part in exercise.get("parts", []):
                                part_label = part.get("part_label", "")
                                part_title = part.get("part_title", "")
                                
                                # En-tête de la partie
                                if part_title:
                                    story.append(Paragraph(f"<b>{part_label} : {part_title}</b>", styles['Heading3']))
                                else:
                                    story.append(Paragraph(f"<b>{part_label}</b>", styles['Heading3']))
                                story.append(Spacer(1, 0.1*inch))
                                
                                # Sous-questions
                                subquestions = part.get("subquestions", [])
                                for subq in subquestions:
                                    label = subq.get("label", "")
                                    question = subq.get("question", "")
                                    story.append(Paragraph(f"<b>{label}</b> {question}", exercise_style))
                                    story.append(Spacer(1, 0.15*inch))
                                    
                                    # Espace pour la réponse de la sous-question
                                    story.append(Paragraph("_" * 80, styles['Normal']))
                                    story.append(Spacer(1, 0.1*inch))
                                    story.append(Paragraph("_" * 80, styles['Normal']))
                                    story.append(Spacer(1, 0.15*inch))
                                
                                story.append(Spacer(1, 0.2*inch))
                        else:
                            # Ancienne structure : exercice simple (rétrocompatibilité)
                            exercise_question = exercise.get("question", "")
                            story.append(Paragraph(exercise_question, exercise_style))
                            story.append(Spacer(1, 0.15*inch))
                            
                            # Indice (si disponible)
                            hint = exercise.get("hint", "")
                            if hint:
                                story.append(Paragraph(f"<i><b>Indice:</b> {hint}</i>", styles['Italic']))
                                story.append(Spacer(1, 0.1*inch))
                            
                            # Espace pour la réponse
                            story.append(Paragraph("<b>Réponse :</b>", styles['Normal']))
                            story.append(Spacer(1, 0.3*inch))
                            story.append(Paragraph("_" * 80, styles['Normal']))
                            story.append(Spacer(1, 0.1*inch))
                            story.append(Paragraph("_" * 80, styles['Normal']))
                            story.append(Spacer(1, 0.1*inch))
                            story.append(Paragraph("_" * 80, styles['Normal']))
            
            logger.info(f"Construction du PDF Examen pour '{module_title}'...")
            doc.build(story)
            logger.info(f"PDF Examen créé: {filepath}")
            return filepath
            
        except ImportError:
            # Si reportlab n'est pas installé, créer un fichier texte simple
            logger.warning("reportlab non disponible, création d'un fichier texte")
            filename = f"exam_{uuid.uuid4()}.txt"
            filepath = PDF_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"EXAMEN - {module_title}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Nombre de questions: {exam.get('num_questions', 0)}\n")
                f.write(f"Score de passage: {exam.get('passing_score', 70)}%\n")
                f.write(f"Temps limite: {exam.get('time_limit', 30)} minutes\n\n")
                f.write("=" * 60 + "\n\n")
                
                questions = exam.get("questions", [])
                for i, question_data in enumerate(questions, 1):
                    f.write(f"Question {i} ({question_data.get('points', 1)} point{'s' if question_data.get('points', 1) > 1 else ''})\n")
                    f.write("-" * 60 + "\n")
                    f.write(f"{question_data.get('question', '')}\n\n")
                    
                    options = question_data.get("options", [])
                    correct_answer_index = question_data.get("correct_answer", 0)
                    for j, option in enumerate(options):
                        marker = "[✓]" if j == correct_answer_index else "[ ]"
                        f.write(f"  {marker} {option}\n")
                    
                    explanation = question_data.get("explanation", "")
                    if explanation:
                        f.write(f"\nExplication: {explanation}\n")
                    
                    f.write("\n" + "=" * 60 + "\n\n")
            
            return filepath
        except Exception as e:
            logger.error(f"Erreur lors de la création du PDF Examen: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def _create_pdf_from_tp(tp: Dict[str, Any], lesson_title: str) -> Optional[Path]:
        """Crée un fichier PDF à partir d'un TP"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            filename = f"tp_{uuid.uuid4()}.pdf"
            filepath = PDF_DIR / filename
            
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            logger.info(f"📄 Document PDF TP créé pour '{lesson_title}'")
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor='#2563EB',
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph(f"TP - {lesson_title}", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Description
            if tp.get("description"):
                story.append(Paragraph(f"<b>Description:</b> {tp.get('description')}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Langage de programmation
            if tp.get("programming_language"):
                story.append(Paragraph(f"<b>Langage de programmation:</b> {tp.get('programming_language')}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Objectifs
            objectives = tp.get("objectives", [])
            if objectives:
                story.append(Paragraph("<b>Objectifs:</b>", styles['Heading2']))
                for obj in objectives:
                    story.append(Paragraph(f"• {obj}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Matériel nécessaire
            materials = tp.get("materials_needed", [])
            if materials:
                story.append(Paragraph("<b>Matériel nécessaire:</b>", styles['Heading2']))
                for material in materials:
                    story.append(Paragraph(f"• {material}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
            
            # Style pour le code
            from reportlab.lib.colors import HexColor
            code_style = ParagraphStyle(
                'CodeStyle',
                parent=styles['Code'],
                fontSize=9,
                fontName='Courier',
                leftIndent=20,
                rightIndent=20,
                backColor=HexColor('#F5F5F5'),
                borderColor=HexColor('#CCCCCC'),
                borderWidth=1,
                borderPadding=10
            )
            
            # Exercices pratiques (steps)
            steps = tp.get("steps", [])
            for i, step in enumerate(steps, 1):
                step_num = step.get('step_number', i)
                step_title = step.get('title', f'Exercice {step_num}')
                story.append(Paragraph(f"<b>{step_title}</b>", styles['Heading2']))
                story.append(Spacer(1, 0.1*inch))
                
                # Instructions (énoncé du problème)
                instructions = step.get('instructions', '')
                if instructions:
                    story.append(Paragraph(f"<b>Instructions:</b>", styles['Normal']))
                    story.append(Paragraph(instructions.replace('\n', '<br/>'), styles['Normal']))
                    story.append(Spacer(1, 0.15*inch))
                
                # Exemple de code
                code_example = step.get("code_example")
                if code_example:
                    story.append(Paragraph("<b>Exemple de code / Pseudo-code:</b>", styles['Normal']))
                    from reportlab.platypus import Preformatted
                    story.append(Preformatted(code_example, code_style))
                    story.append(Spacer(1, 0.15*inch))
                
                # Tests à effectuer
                tests = step.get("tests", [])
                if tests:
                    story.append(Paragraph("<b>Tests à effectuer:</b>", styles['Normal']))
                    for test in tests:
                        story.append(Paragraph(f"• {test}", styles['Normal']))
                    story.append(Spacer(1, 0.15*inch))
                
                # Résultat attendu
                if step.get("expected_result"):
                    story.append(Paragraph(f"<b>Résultat attendu:</b> {step.get('expected_result')}", styles['Normal']))
                    story.append(Spacer(1, 0.15*inch))
                
                # Conseils
                tips = step.get("tips", [])
                if tips:
                    story.append(Paragraph("<b>Conseils:</b>", styles['Normal']))
                    for tip in tips:
                        story.append(Paragraph(f"💡 {tip}", styles['Italic']))
                
                story.append(Spacer(1, 0.3*inch))
            
            logger.info(f"Construction du PDF TP pour '{lesson_title}'...")
            doc.build(story)
            logger.info(f"PDF TP créé: {filepath}")
            return filepath
            
        except ImportError:
            # Si reportlab n'est pas installé, créer un fichier texte simple
            logger.warning("reportlab non disponible, création d'un fichier texte")
            filename = f"tp_{uuid.uuid4()}.txt"
            filepath = PDF_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"TP - {lesson_title}\n\n")
                f.write(f"{tp.get('description', '')}\n\n")
                
                objectives = tp.get("objectives", [])
                if objectives:
                    f.write("Objectifs:\n")
                    for obj in objectives:
                        f.write(f"- {obj}\n")
                    f.write("\n")
                
                # Langage de programmation
                if tp.get("programming_language"):
                    f.write(f"Langage de programmation: {tp.get('programming_language')}\n\n")
                
                steps = tp.get("steps", [])
                for step in steps:
                    step_num = step.get('step_number', 0)
                    step_title = step.get('title') or f"Exercice {step_num}"
                    f.write(f"{step_title}\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"{step.get('instructions', '')}\n\n")
                    
                    # Exemple de code
                    code_example = step.get("code_example")
                    if code_example:
                        f.write("Exemple de code / Pseudo-code:\n")
                        f.write("-" * 60 + "\n")
                        f.write(f"{code_example}\n")
                        f.write("-" * 60 + "\n\n")
                    
                    # Tests
                    tests = step.get("tests", [])
                    if tests:
                        f.write("Tests à effectuer:\n")
                        for test in tests:
                            f.write(f"  • {test}\n")
                        f.write("\n")
                    
                    if step.get("expected_result"):
                        f.write(f"Résultat attendu: {step.get('expected_result')}\n\n")
                    
                    tips = step.get("tips", [])
                    if tips:
                        f.write("Conseils:\n")
                        for tip in tips:
                            f.write(f"  💡 {tip}\n")
                        f.write("\n")
                    
                    f.write("\n")
            
            return filepath
        except Exception as e:
            logger.error(f"Erreur lors de la création du PDF TP: {e}", exc_info=True)
            return None
    
    @staticmethod
    async def generate_for_new_lessons(
        module_id: str,
        new_lessons: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Génère automatiquement des TD et TP en PDF pour de nouvelles leçons
        """
        results = {
            "tds": [],
            "tps": [],
            "errors": []
        }
        
        logger.info(f"Début de la génération pour {len(new_lessons)} leçon(s)")
        
        # Vérifier que le client OpenAI est disponible
        if not client:
            error_msg = "Client OpenAI non initialisé. Vérifiez que OPENAI_API_KEY est configuré dans .env et redémarrez le backend."
            logger.error(error_msg)
            results["errors"].append({
                "type": "openai_client",
                "error": error_msg
            })
            return results
        
        total_lessons = len(new_lessons)
        logger.info(f"📚 Génération de TDs pour {total_lessons} chapitre(s)/leçon(s) du module")
        
        for lesson_index, lesson in enumerate(new_lessons, 1):
            # Essayer plusieurs façons de récupérer le titre
            lesson_title = (
                lesson.get("title") or 
                lesson.get("name") or 
                lesson.get("heading") or
                ""
            )
            
            # Si le titre est toujours vide, essayer de le récupérer depuis les sections
            if not lesson_title:
                sections = lesson.get("sections", [])
                if sections and len(sections) > 0:
                    # Prendre le premier heading de la première section comme titre
                    first_section = sections[0]
                    lesson_title = first_section.get("heading", "") or first_section.get("title", "")
            
            lesson_content = lesson.get("content", "")
            lesson_summary = lesson.get("summary", "")
            
            logger.info(f"📖 [{lesson_index}/{total_lessons}] Traitement du chapitre: '{lesson_title}' (structure: {list(lesson.keys())})")
            
            # Extraire le contenu des sections si le contenu direct n'est pas disponible
            if not lesson_content or (isinstance(lesson_content, str) and not lesson_content.strip()):
                sections = lesson.get("sections", [])
                if sections:
                    lesson_content = "\n\n".join([
                        f"{section.get('heading', '')}\n" + "\n".join(section.get("paragraphs", []))
                        for section in sections
                    ])
                    logger.info(f"Contenu extrait des sections pour '{lesson_title}': {len(lesson_content)} caractères")
            
            # S'assurer que lesson_content est une string
            if not isinstance(lesson_content, str):
                lesson_content = str(lesson_content) if lesson_content else ""
            
            # Si toujours pas de titre, essayer de générer un titre à partir du contenu
            if not lesson_title or not lesson_title.strip():
                # Prendre les premiers mots du contenu comme titre
                if lesson_content and lesson_content.strip():
                    # Prendre les 50 premiers caractères comme titre
                    lesson_title = lesson_content[:50].strip()
                    if len(lesson_content) > 50:
                        lesson_title += "..."
                    logger.info(f"Titre généré à partir du contenu: '{lesson_title}'")
                else:
                    logger.warning(f"Leçon sans titre ni contenu ignorée: {lesson}")
                    continue
            
            if not lesson_content or not lesson_content.strip():
                logger.warning(f"Leçon '{lesson_title}' sans contenu, génération avec contenu minimal")
                lesson_content = f"Leçon: {lesson_title}"
            
            try:
                # Générer TD avec timeout (long pour permettre la génération de 6-10 exercices complexes par chapitre)
                logger.info(f"Génération du TD pour le chapitre '{lesson_title}' (6 à 10 exercices requis)")
                module = await ModuleRepository.find_by_id(module_id)
                module_subject = module.get("subject") if module else None
                # Timeout adapté pour permettre la génération de 6-10 exercices complexes par chapitre
                timeout_duration = 120.0  # 120 secondes pour tous les modules
                logger.info(f"Timeout TD pour '{lesson_title}': {timeout_duration}s (matière: {module_subject}, 6-10 exercices par chapitre)")
                try:
                    td_result = await asyncio.wait_for(
                        PDFGeneratorService.generate_td_pdf_for_lesson(
                            module_id=module_id,
                            lesson_title=lesson_title,
                            lesson_content=lesson_content,
                            lesson_summary=lesson_summary
                        ),
                        timeout=timeout_duration
                    )
                    if td_result and isinstance(td_result, dict):
                        td_exercises = td_result.get("td", {}).get("exercises", [])
                        num_exercises = len(td_exercises) if td_exercises else 0
                        results["tds"].append({
                            "lesson_title": lesson_title,
                            "td_id": str(td_result.get("td", {}).get("_id", "")) if td_result.get("td") else None,
                            "pdf_path": td_result.get("pdf_path"),
                            "num_exercises": num_exercises
                        })
                        logger.info(f"✅ TD généré avec succès pour '{lesson_title}' : {num_exercises} exercices ({lesson_index}/{total_lessons} chapitres traités)")
                    else:
                        error_msg = f"TD non généré pour '{lesson_title}' (résultat: {td_result})"
                        logger.warning(f"⚠️ {error_msg}")
                        results["errors"].append({
                            "lesson": lesson_title,
                            "type": "td_generation_failed",
                            "error": error_msg
                        })
                except asyncio.TimeoutError:
                    error_msg = f"Timeout lors de la génération du TD pour '{lesson_title}' (dépassement de {timeout_duration} secondes)"
                    logger.error(f"❌ {error_msg}")
                    results["errors"].append({
                        "lesson": lesson_title,
                        "type": "td_generation_timeout",
                        "error": error_msg
                    })
                
                # Générer TP (seulement si ce n'est pas anglais ou mathématiques)
                logger.info(f"🔄 Passage à la génération du TP pour '{lesson_title}'...")
                if not module:
                    module = await ModuleRepository.find_by_id(module_id)
                module_subject = module.get("subject") if module else None
                logger.info(f"Vérification TP pour '{lesson_title}': module trouvé={module is not None}, subject={module_subject}")
                
                if module and module_subject not in ["english", "mathematics"]:
                    logger.info(f"Génération du TP pour la leçon '{lesson_title}' (matière: {module_subject})")
                    # Timeout plus long pour les TP (120s) car ils nécessitent plus de code et d'instructions
                    tp_timeout = 120.0
                    try:
                        tp_result = await asyncio.wait_for(
                            PDFGeneratorService.generate_tp_pdf_for_lesson(
                                module_id=module_id,
                                lesson_title=lesson_title,
                                lesson_content=lesson_content,
                                lesson_summary=lesson_summary
                            ),
                            timeout=tp_timeout
                        )
                        if tp_result and isinstance(tp_result, dict):
                            results["tps"].append({
                                "lesson_title": lesson_title,
                                "tp_id": str(tp_result.get("tp", {}).get("_id", "")) if tp_result.get("tp") else None,
                                "pdf_path": tp_result.get("pdf_path")
                            })
                            logger.info(f"✅ TP généré avec succès pour '{lesson_title}'")
                        else:
                            error_msg = f"TP non généré pour '{lesson_title}' (résultat: {tp_result})"
                            logger.warning(f"⚠️ {error_msg}")
                            results["errors"].append({
                                "lesson": lesson_title,
                                "type": "tp_generation_failed",
                                "error": error_msg
                            })
                    except Exception as tp_error:
                        error_msg = f"Erreur lors de la génération du TP pour '{lesson_title}': {str(tp_error)}"
                        logger.error(f"❌ {error_msg}", exc_info=True)
                        results["errors"].append({
                            "lesson": lesson_title,
                            "type": "tp_generation_exception",
                            "error": error_msg
                        })
                else:
                    logger.info(f"TP ignoré pour '{lesson_title}' (matière: {module_subject if module else 'N/A'})")
                
                logger.info(f"✅ Traitement terminé pour la leçon '{lesson_title}'")
                        
            except Exception as e:
                logger.error(f"❌ Erreur lors de la génération pour la leçon {lesson_title}: {e}", exc_info=True)
                results["errors"].append({
                    "lesson": lesson_title,
                    "error": str(e)
                })
        
        logger.info(f"✅ Génération terminée pour toutes les leçons: {len(results['tds'])} TD, {len(results['tps'])} TP, {len(results['errors'])} erreur(s)")
        return results

