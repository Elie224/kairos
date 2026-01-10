"""
Repository pour la gestion des modules
"""
from typing import Optional, List, Dict, Any
from bson import ObjectId
from app.database import get_database
from app.schemas import serialize_doc
from app.models import Subject, Difficulty
import logging

logger = logging.getLogger(__name__)


class ModuleRepository:
    """Repository pour les opérations CRUD sur les modules"""
    
    @staticmethod
    async def find_all(
        subject: Optional[Subject] = None,
        difficulty: Optional[Difficulty] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Récupère tous les modules avec filtres optionnels et recherche"""
        try:
            db = get_database()
            if db is None:
                logger.error("Base de données non disponible")
                return []
            
            query = {}
            
            if subject:
                query["subject"] = subject.value
            if difficulty:
                query["difficulty"] = difficulty.value
            
            # Recherche textuelle optimisée
            if search:
                search_term = search.strip()[:100]  # Limiter la longueur
                if search_term:
                    # Utiliser regex pour la recherche (compatible même sans index texte)
                    import re
                    escaped_search = re.escape(search_term)
                    search_regex = {"$regex": escaped_search, "$options": "i"}
                    query["$or"] = [
                        {"title": search_regex},
                        {"description": search_regex}
                    ]
            
            # Trier par created_at (plus rapide avec index)
            sort_key = [("created_at", -1)]
            
            # Trier par created_at (plus rapide avec index)
            sort_key = [("created_at", -1)]
            
            # Projection pour exclure le contenu volumineux (optimisation performance)
            # Le contenu sera chargé uniquement si nécessaire (détail du module)
            projection = {
                "content": 0  # Exclure le contenu volumineux de la liste
            }
            
            cursor = db.modules.find(query, projection).skip(skip).limit(limit).sort(sort_key)
            modules = await cursor.to_list(length=limit)
            
            # Sérialiser les modules avec gestion d'erreurs et filtrage des sujets invalides
            serialized_modules = []
            valid_subjects = {"mathematics", "computer_science"}  # Seulement les 2 matières supportées
            
            for module in modules:
                try:
                    if module is None:
                        continue
                    
                    # Filtrer les modules avec des sujets invalides
                    module_subject = module.get("subject")
                    if module_subject and module_subject not in valid_subjects:
                        logger.debug(f"Module ignoré: sujet '{module_subject}' non supporté (ID: {module.get('_id')})")
                        continue
                    
                    serialized = serialize_doc(module)
                    if serialized:
                        # Vérifier à nouveau après sérialisation
                        if serialized.get("subject") in valid_subjects or serialized.get("subject") is None:
                            serialized_modules.append(serialized)
                        else:
                            logger.debug(f"Module ignoré après sérialisation: sujet invalide")
                except Exception as ser_error:
                    logger.warning(f"Erreur lors de la sérialisation d'un module: {ser_error}", exc_info=True)
                    # Continuer avec les autres modules
                    continue
            
            return serialized_modules
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modules: {e}", exc_info=True)
            # Retourner une liste vide au lieu de lever une exception
            return []
    
    @staticmethod
    async def find_by_id(module_id: str) -> Optional[Dict[str, Any]]:
        """Trouve un module par ID"""
        try:
            from app.utils.security import InputSanitizer
            # Valider l'ObjectId
            sanitized_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_id:
                return None
            
            db = get_database()
            module = await db.modules.find_one({"_id": ObjectId(sanitized_id)})
            return serialize_doc(module) if module else None
        except Exception as e:
            logger.error(f"Erreur lors de la recherche du module: {e}")
            raise
    
    @staticmethod
    async def find_by_subject(subject: Subject) -> List[Dict[str, Any]]:
        """Trouve tous les modules d'une matière"""
        try:
            db = get_database()
            cursor = db.modules.find({"subject": subject.value}).sort("created_at", -1)
            modules = await cursor.to_list(length=100)
            return [serialize_doc(module) for module in modules]
        except Exception as e:
            logger.error(f"Erreur lors de la recherche par matière: {e}")
            raise
    
    @staticmethod
    async def create(module_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un nouveau module"""
        try:
            db = get_database()
            result = await db.modules.insert_one(module_data)
            module_data["_id"] = result.inserted_id
            return serialize_doc(module_data)
        except Exception as e:
            logger.error(f"Erreur lors de la création du module: {e}")
            raise
    
    @staticmethod
    async def update(module_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Met à jour un module"""
        try:
            from app.utils.security import InputSanitizer
            # Valider l'ObjectId avant utilisation
            sanitized_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_id:
                return None
            
            db = get_database()
            await db.modules.update_one(
                {"_id": ObjectId(sanitized_id)},
                {"$set": update_data}
            )
            return await ModuleRepository.find_by_id(sanitized_id)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du module: {e}")
            raise
    
    @staticmethod
    async def delete(module_id: str) -> bool:
        """Supprime un module"""
        try:
            from app.utils.security import InputSanitizer
            # Valider l'ObjectId avant utilisation
            sanitized_id = InputSanitizer.sanitize_object_id(module_id)
            if not sanitized_id:
                return False
            
            db = get_database()
            result = await db.modules.delete_one({"_id": ObjectId(sanitized_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du module: {e}")
            raise
    
    @staticmethod
    async def count(subject: Optional[Subject] = None) -> int:
        """Compte le nombre de modules"""
        try:
            db = get_database()
            query = {}
            if subject:
                query["subject"] = subject.value
            return await db.modules.count_documents(query)
        except Exception as e:
            logger.error(f"Erreur lors du comptage des modules: {e}")
            raise
