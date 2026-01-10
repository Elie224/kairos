"""
Script pour initialiser des contenus de démonstration
"""
import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_to_mongo
from app.services.module_service import ModuleService
from app.models import ModuleCreate, Subject, Difficulty
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Contenus de démonstration
DEMO_MODULES = [
    {
        "title": "Introduction à la Mécanique Classique",
        "description": "Découvrez les fondamentaux de la mécanique classique : mouvement, forces, énergie et lois de Newton. Ce module interactif vous permettra de visualiser et comprendre les concepts de base de la physique.",
        "subject": Subject.PHYSICS,
        "difficulty": Difficulty.BEGINNER,
        "estimated_time": 45,
        "learning_objectives": [
            "Comprendre les concepts de mouvement et de vitesse",
            "Maîtriser les lois de Newton",
            "Appliquer les principes de conservation de l'énergie",
            "Visualiser les forces en action dans des scénarios réels"
        ],
        "content": {
            "type": "interactive",
            "scenes": [
                {
                    "id": "scene_1",
                    "title": "Mouvement rectiligne uniforme",
                    "description": "Visualisez un objet se déplaçant à vitesse constante",
                    "interactive_elements": [
                        {
                            "type": "slider",
                            "label": "Vitesse (m/s)",
                            "min": 0,
                            "max": 50,
                            "default": 10
                        }
                    ]
                },
                {
                    "id": "scene_2",
                    "title": "Forces et accélération",
                    "description": "Explorez la relation entre force, masse et accélération",
                    "interactive_elements": [
                        {
                            "type": "slider",
                            "label": "Force appliquée (N)",
                            "min": 0,
                            "max": 100,
                            "default": 20
                        },
                        {
                            "type": "slider",
                            "label": "Masse (kg)",
                            "min": 1,
                            "max": 50,
                            "default": 10
                        }
                    ]
                }
            ],
            "resources": {
                "videos": [],
                "images": [],
                "3d_models": []
            }
        }
    },
    {
        "title": "Les Bases de l'Algèbre Linéaire",
        "description": "Plongez dans le monde des vecteurs, matrices et transformations linéaires. Ce module vous guidera à travers les concepts essentiels de l'algèbre linéaire avec des visualisations interactives.",
        "subject": Subject.MATHEMATICS,
        "difficulty": Difficulty.INTERMEDIATE,
        "estimated_time": 60,
        "learning_objectives": [
            "Comprendre les opérations sur les vecteurs",
            "Maîtriser les matrices et leurs propriétés",
            "Appliquer les transformations linéaires",
            "Résoudre des systèmes d'équations linéaires"
        ],
        "content": {
            "type": "interactive",
            "scenes": [
                {
                    "id": "scene_1",
                    "title": "Vecteurs dans l'espace 2D",
                    "description": "Manipulez des vecteurs et observez leurs propriétés",
                    "interactive_elements": [
                        {
                            "type": "vector_editor",
                            "label": "Vecteur",
                            "dimensions": 2
                        }
                    ]
                },
                {
                    "id": "scene_2",
                    "title": "Multiplication matricielle",
                    "description": "Visualisez l'effet des transformations matricielles",
                    "interactive_elements": [
                        {
                            "type": "matrix_editor",
                            "label": "Matrice 2x2",
                            "rows": 2,
                            "cols": 2
                        }
                    ]
                }
            ],
            "resources": {
                "videos": [],
                "images": [],
                "3d_models": []
            }
        }
    },
    {
        "title": "Structure Atomique et Tableau Périodique",
        "description": "Explorez la structure des atomes, les électrons, protons et neutrons. Découvrez comment les éléments sont organisés dans le tableau périodique et leurs propriétés.",
        "subject": Subject.CHEMISTRY,
        "difficulty": Difficulty.BEGINNER,
        "estimated_time": 50,
        "learning_objectives": [
            "Comprendre la structure de l'atome",
            "Maîtriser la configuration électronique",
            "Connaître l'organisation du tableau périodique",
            "Relier les propriétés aux positions dans le tableau"
        ],
        "content": {
            "type": "interactive",
            "scenes": [
                {
                    "id": "scene_1",
                    "title": "Modèle de Bohr",
                    "description": "Visualisez la structure atomique selon le modèle de Bohr",
                    "interactive_elements": [
                        {
                            "type": "element_selector",
                            "label": "Élément",
                            "elements": ["H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne"]
                        }
                    ]
                },
                {
                    "id": "scene_2",
                    "title": "Tableau périodique interactif",
                    "description": "Explorez les éléments et leurs propriétés",
                    "interactive_elements": [
                        {
                            "type": "periodic_table",
                            "label": "Tableau périodique",
                            "show_properties": True
                        }
                    ]
                }
            ],
            "resources": {
                "videos": [],
                "images": [],
                "3d_models": []
            }
        }
    },
    {
        "title": "Introduction à la Programmation Python",
        "description": "Apprenez les bases de la programmation avec Python. Ce module couvre les variables, structures de contrôle, fonctions et structures de données fondamentales.",
        "subject": Subject.COMPUTER_SCIENCE,
        "difficulty": Difficulty.BEGINNER,
        "estimated_time": 90,
        "learning_objectives": [
            "Maîtriser les types de données de base",
            "Comprendre les structures de contrôle (if, for, while)",
            "Créer et utiliser des fonctions",
            "Manipuler les listes, dictionnaires et tuples"
        ],
        "content": {
            "type": "interactive",
            "scenes": [
                {
                    "id": "scene_1",
                    "title": "Environnement de programmation",
                    "description": "Codez et exécutez vos premiers programmes Python",
                    "interactive_elements": [
                        {
                            "type": "code_editor",
                            "label": "Éditeur de code",
                            "language": "python"
                        }
                    ]
                },
                {
                    "id": "scene_2",
                    "title": "Visualisation des structures de données",
                    "description": "Comprenez visuellement comment fonctionnent les structures de données",
                    "interactive_elements": [
                        {
                            "type": "data_structure_visualizer",
                            "label": "Visualiseur",
                            "structures": ["list", "dict", "tuple", "set"]
                        }
                    ]
                }
            ],
            "resources": {
                "videos": [],
                "images": [],
                "3d_models": []
            }
        }
    },
    {
        "title": "Grammaire Anglaise : Les Temps Verbaux",
        "description": "Maîtrisez les temps verbaux en anglais : présent, passé, futur. Apprenez à les utiliser correctement dans différents contextes avec des exemples pratiques et interactifs.",
        "subject": Subject.ENGLISH,
        "difficulty": Difficulty.INTERMEDIATE,
        "estimated_time": 40,
        "learning_objectives": [
            "Comprendre les différents temps verbaux",
            "Savoir quand utiliser chaque temps",
            "Construire correctement les phrases",
            "Pratiquer avec des exercices interactifs"
        ],
        "content": {
            "type": "interactive",
            "scenes": [
                {
                    "id": "scene_1",
                    "title": "Présent simple et continu",
                    "description": "Apprenez à utiliser le présent simple et le présent continu",
                    "interactive_elements": [
                        {
                            "type": "exercise_generator",
                            "label": "Exercices",
                            "type": "fill_in_blank"
                        }
                    ]
                },
                {
                    "id": "scene_2",
                    "title": "Passé et futur",
                    "description": "Maîtrisez le passé simple et le futur",
                    "interactive_elements": [
                        {
                            "type": "exercise_generator",
                            "label": "Exercices",
                            "type": "sentence_transformation"
                        }
                    ]
                }
            ],
            "resources": {
                "videos": [],
                "images": [],
                "3d_models": []
            }
        }
    },
    {
        "title": "Électromagnétisme Avancé",
        "description": "Approfondissez vos connaissances en électromagnétisme : champs électriques et magnétiques, induction, ondes électromagnétiques. Module avancé avec simulations complexes.",
        "subject": Subject.PHYSICS,
        "difficulty": Difficulty.ADVANCED,
        "estimated_time": 120,
        "learning_objectives": [
            "Comprendre les équations de Maxwell",
            "Maîtriser les concepts de champ électromagnétique",
            "Appliquer les lois de l'induction",
            "Analyser les ondes électromagnétiques"
        ],
        "content": {
            "type": "interactive",
            "scenes": [
                {
                    "id": "scene_1",
                    "title": "Champs électriques et magnétiques",
                    "description": "Visualisez les lignes de champ et leurs interactions",
                    "interactive_elements": [
                        {
                            "type": "field_visualizer",
                            "label": "Visualiseur de champs",
                            "field_type": "electromagnetic"
                        }
                    ]
                },
                {
                    "id": "scene_2",
                    "title": "Ondes électromagnétiques",
                    "description": "Explorez la propagation des ondes EM",
                    "interactive_elements": [
                        {
                            "type": "wave_simulator",
                            "label": "Simulateur d'ondes",
                            "parameters": ["frequency", "amplitude", "wavelength"]
                        }
                    ]
                }
            ],
            "resources": {
                "videos": [],
                "images": [],
                "3d_models": []
            }
        }
    }
]


async def init_demo_content():
    """Initialise les contenus de démonstration"""
    try:
        # Initialiser la connexion à la base de données
        await connect_to_mongo()
        logger.info("Connexion à la base de données établie")
        
        # Vérifier si des modules existent déjà
        existing_modules = await ModuleService.get_modules(limit=1)
        if existing_modules:
            logger.warning(f"Des modules existent déjà ({len(existing_modules)} trouvé(s)).")
            # En mode non-interactif, continuer automatiquement
            try:
                response = input("Voulez-vous continuer et ajouter les modules de démonstration ? (o/n): ")
                if response.lower() != 'o':
                    logger.info("Opération annulée")
                    return
            except EOFError:
                # Mode non-interactif, continuer automatiquement
                logger.info("Mode non-interactif détecté, ajout des modules...")
        
        # Créer les modules de démonstration
        created_count = 0
        for module_data in DEMO_MODULES:
            try:
                module_create = ModuleCreate(**module_data)
                created_module = await ModuleService.create_module(module_create)
                created_count += 1
                logger.info(f"✓ Module créé: {created_module['title']}")
            except Exception as e:
                logger.error(f"✗ Erreur lors de la création du module '{module_data['title']}': {e}")
                continue
        
        logger.info(f"\n✅ Initialisation terminée: {created_count}/{len(DEMO_MODULES)} modules créés avec succès")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(init_demo_content())

