"""
Prompts officiels Kairos AI - Système de prompts structurés pour toutes les matières
"""

# ============================================================================
# PROMPT SYSTÈME GLOBAL - KAIROS AI
# ============================================================================

SYSTEM_PROMPT = """Tu es Kairos AI, un tuteur pédagogique intelligent intégré dans une application d'apprentissage.
Ton objectif est de faciliter l'apprentissage par :
- des visualisations interactives (2D et 3D),
- des simulations pédagogiques,
- une explication claire, progressive et adaptée au niveau de l'apprenant,
- une gamification motivante (quêtes, badges, points).

Tu adaptes automatiquement :
- le niveau (collège, lycée, université),
- la difficulté,
- le langage,
- les exemples.

Tu privilégies :
- l'intuition avant la formalisation,
- l'interaction avant la mémorisation,
- la motivation et la progression personnelle.

Après chaque activité, tu donnes :
- un feedback pédagogique clair,
- des recommandations personnalisées,
- une proposition de défi ou de visualisation supplémentaire."""


# ============================================================================
# PROMPTS - MATHÉMATIQUES
# ============================================================================

MATHEMATICS_PROMPTS = {
    "functions_trigonometry": """Explique le concept suivant : {concept}.
Génère :
1. Une explication intuitive
2. Une visualisation interactive (curseurs modifiables)
3. Un exemple concret
4. Un mini-quiz de validation
5. Une quête adaptée au niveau {niveau}

Format de réponse JSON :
{{
    "explanation": "explication intuitive",
    "visualization": {{
        "type": "interactive",
        "parameters": ["param1", "param2"],
        "description": "description de la visualisation"
    }},
    "example": "exemple concret",
    "quiz": {{
        "question": "question",
        "options": ["option1", "option2", "option3", "option4"],
        "correct": 0,
        "explanation": "explication de la réponse"
    }},
    "quest": {{
        "title": "titre de la quête",
        "description": "description",
        "objective": "objectif",
        "reward": "récompense"
    }}
}}""",

    "sequences": """Génère une visualisation interactive d'une suite mathématique.
Explique la convergence ou divergence.
Propose une manipulation dynamique et une question guidée.

Format de réponse JSON :
{{
    "sequence_type": "arithmetic|geometric|other",
    "formula": "formule de la suite",
    "convergence": "convergent|divergent",
    "explanation": "explication de la convergence/divergence",
    "visualization": {{
        "type": "sequence_graph",
        "interactive": true,
        "parameters": ["first_term", "common_difference", "n_terms"]
    }},
    "guided_question": {{
        "question": "question guidée",
        "hints": ["indice1", "indice2"],
        "answer": "réponse"
    }}
}}""",

    "linear_algebra": """Explique un concept d'algèbre linéaire : {concept}.
Génère une visualisation 3D des vecteurs et matrices.
Montre les transformations (rotation, translation, homothétie).

Format de réponse JSON :
{{
    "concept": "nom du concept",
    "explanation": "explication intuitive",
    "visualization_3d": {{
        "type": "vectors_matrices",
        "vectors": [{{"x": 1, "y": 2, "z": 3}}],
        "transformations": ["rotation", "translation"],
        "interactive": true
    }},
    "example": "exemple concret",
    "application": "application pratique"
}}""",

    "analysis": """Explique un concept d'analyse : {concept} (dérivées, intégrales).
Génère une interprétation géométrique interactive.
Montre la relation entre fonction, dérivée et intégrale.

Format de réponse JSON :
{{
    "concept": "dérivée|intégrale",
    "geometric_interpretation": "interprétation géométrique",
    "visualization": {{
        "type": "function_graph",
        "show_derivative": true,
        "show_integral": true,
        "interactive": true
    }},
    "example": "exemple avec calculs",
    "intuition": "explication intuitive"
}}""",

    "probability_statistics": """Explique un concept de probabilités ou statistiques : {concept}.
Visualise les distributions de probabilité.
Montre les lois de probabilité avec des exemples interactifs.

Format de réponse JSON :
{{
    "concept": "nom du concept",
    "distribution": {{
        "type": "normal|binomial|poisson|other",
        "parameters": {{"mean": 0, "std": 1}},
        "visualization": "graphique de distribution"
    }},
    "explanation": "explication",
    "example": "exemple pratique",
    "interactive_demo": "démonstration interactive"
}}"""
}


# ============================================================================
# PROMPTS - PHYSIQUE
# ============================================================================

PHYSICS_PROMPTS = {
    "mechanics_dynamics": """Explique un phénomène de mécanique ou de dynamique : {concept}.
Génère une simulation interactive avec forces, vecteurs et mouvements.
Permets à l'apprenant de modifier les paramètres.
Termine par une analyse et un défi pratique.

Format de réponse JSON :
{{
    "concept": "nom du concept",
    "explanation": "explication du phénomène",
    "simulation": {{
        "type": "mechanics",
        "forces": [{{"name": "force1", "magnitude": 10, "direction": "x"}}],
        "vectors": true,
        "interactive": true,
        "parameters": ["mass", "velocity", "acceleration"]
    }},
    "analysis": "analyse du mouvement",
    "challenge": {{
        "title": "titre du défi",
        "description": "description",
        "solution": "solution"
    }}
}}""",

    "waves": """Explique les ondes mécaniques ou électromagnétiques : {concept}.
Crée une visualisation animée.
Montre les phénomènes d'interférence et diffraction.
Pose une question exploratoire.

Format de réponse JSON :
{{
    "concept": "type d'onde",
    "explanation": "explication",
    "visualization": {{
        "type": "wave_animation",
        "show_interference": true,
        "show_diffraction": true,
        "interactive": true
    }},
    "interference": "explication des interférences",
    "diffraction": "explication de la diffraction",
    "exploratory_question": {{
        "question": "question exploratoire",
        "hints": ["indice1", "indice2"]
    }}
}}""",

    "electricity_electromagnetism": """Génère un circuit électrique interactif : {concept}.
Explique les lois physiques associées (Ohm, Kirchhoff).
Permets la modification des composants.
Évalue la compréhension par un mini-défi.

Format de réponse JSON :
{{
    "concept": "circuit|champ électrique|champ magnétique",
    "circuit": {{
        "components": [{{"type": "resistor", "value": 100, "position": "x,y"}}],
        "interactive": true,
        "laws": ["ohm", "kirchhoff"]
    }},
    "explanation": "explication des lois",
    "interactive_modification": "comment modifier les composants",
    "mini_challenge": {{
        "question": "question",
        "solution": "solution"
    }}
}}""",

    "quantum_physics": """Explique un concept de physique quantique de manière intuitive : {concept}.
Utilise des métaphores visuelles.
Génère une visualisation simplifiée.
Évite le formalisme excessif.

Format de réponse JSON :
{{
    "concept": "dualité onde-corpuscule|niveaux d'énergie|fonction d'onde",
    "intuitive_explanation": "explication intuitive avec métaphores",
    "visual_metaphor": "métaphore visuelle",
    "simplified_visualization": {{
        "type": "quantum_concept",
        "simplified": true,
        "interactive": true
    }},
    "avoid_formalism": true,
    "key_insights": ["insight1", "insight2"]
}}"""
}


# ============================================================================
# PROMPTS - CHIMIE
# ============================================================================

CHEMISTRY_PROMPTS = {
    "general_chemistry": """Explique une réaction chimique étape par étape : {reaction}.
Génère une visualisation moléculaire.
Montre l'évolution de la réaction dans le temps.

Format de réponse JSON :
{{
    "reaction": "équation de la réaction",
    "step_by_step": ["étape1", "étape2", "étape3"],
    "molecular_visualization": {{
        "type": "reaction_3d",
        "reactants": [{{"molecule": "H2O", "structure": "3d_data"}}],
        "products": [{{"molecule": "H2", "structure": "3d_data"}}],
        "interactive": true
    }},
    "reaction_evolution": {{
        "time_steps": ["t0", "t1", "t2"],
        "concentrations": {{"reactant": [1, 0.5, 0], "product": [0, 0.5, 1]}}
    }},
    "conservation_laws": "lois de conservation"
}}""",

    "organic_chemistry": """Génère une molécule organique en 3D : {molecule}.
Explique les groupes fonctionnels.
Montre une réaction organique interactive.

Format de réponse JSON :
{{
    "molecule": "nom de la molécule",
    "structure_3d": {{
        "atoms": [{{"element": "C", "position": "x,y,z", "bonds": []}}],
        "functional_groups": ["groupe1", "groupe2"],
        "interactive": true
    }},
    "functional_groups_explanation": "explication des groupes fonctionnels",
    "organic_reaction": {{
        "reaction_type": "substitution|addition|elimination",
        "mechanism": "mécanisme de la réaction",
        "visualization": "visualisation interactive"
    }}
}}""",

    "aqueous_solutions": """Explique les solutions aqueuses : {concept} (pH, concentration).
Génère une simulation de dissolution.
Propose une expérience virtuelle.

Format de réponse JSON :
{{
    "concept": "pH|concentration|dissolution",
    "explanation": "explication",
    "dissolution_simulation": {{
        "type": "aqueous_solution",
        "solute": "nom du soluté",
        "solvent": "eau",
        "interactive": true,
        "ph_scale": true
    }},
    "virtual_experiment": {{
        "title": "titre de l'expérience",
        "steps": ["étape1", "étape2"],
        "observations": "observations"
    }},
    "acid_base_reactions": "réactions acide-base si applicable"
}}""",

    "periodic_table": """Génère une représentation interactive du tableau périodique.
Explique les tendances périodiques.
Permets l'exploration élément par élément.

Format de réponse JSON :
{{
    "periodic_table": {{
        "type": "interactive",
        "elements": [{{"symbol": "H", "properties": {{"atomic_number": 1, "atomic_mass": 1.008}}}}],
        "trends": ["tendance1", "tendance2"]
    }},
    "periodic_trends": {{
        "electronegativity": "tendance",
        "atomic_radius": "tendance",
        "ionization_energy": "tendance"
    }},
    "element_exploration": {{
        "selected_element": "H",
        "properties": {{"physical": {}, "chemical": {}}},
        "applications": "applications concrètes"
    }}
}}"""
}


# ============================================================================
# PROMPTS - IA & MACHINE LEARNING
# ============================================================================

AI_ML_PROMPTS = {
    "machine_learning": """Explique le concept de machine learning : {concept}.
Génère une visualisation du processus d'entraînement.
Montre les erreurs, le biais et l'amélioration du modèle.
Adapte le niveau à {niveau}.

Format de réponse JSON :
{{
    "concept": "nom du concept ML",
    "explanation": "explication adaptée au niveau",
    "training_visualization": {{
        "type": "training_process",
        "epochs": [1, 2, 3],
        "loss": [0.5, 0.3, 0.1],
        "accuracy": [0.6, 0.8, 0.95],
        "interactive": true
    }},
    "errors_analysis": {{
        "overfitting": "explication de l'overfitting",
        "underfitting": "explication de l'underfitting",
        "bias": "explication du biais"
    }},
    "model_improvement": "comment améliorer le modèle"
}}""",

    "neural_networks": """Explique le fonctionnement d'un réseau de neurones : {concept}.
Visualise les couches, poids et sorties.
Simule une propagation avant.

Format de réponse JSON :
{{
    "concept": "réseau de neurones|propagation|backpropagation",
    "explanation": "explication du fonctionnement",
    "network_visualization": {{
        "type": "neural_network",
        "layers": [{{"type": "input", "neurons": 784}}, {{"type": "hidden", "neurons": 128}}],
        "weights": "visualisation des poids",
        "outputs": "visualisation des sorties",
        "interactive": true
    }},
    "forward_propagation": {{
        "simulation": true,
        "step_by_step": ["étape1", "étape2"]
    }},
    "intuition": "intuition derrière les réseaux de neurones"
}}""",

    "algorithms": """Explique un algorithme : {algorithm}.
Visualise le flux de données.
Montre l'exécution étape par étape.

Format de réponse JSON :
{{
    "algorithm": "nom de l'algorithme",
    "explanation": "explication",
    "data_flow": {{
        "type": "algorithm_visualization",
        "steps": ["étape1", "étape2"],
        "interactive": true
    }},
    "step_by_step_execution": {{
        "input": "données d'entrée",
        "steps": [{{"step": 1, "action": "action", "result": "résultat"}}],
        "output": "résultat final"
    }},
    "complexity": "complexité de l'algorithme"
}}"""
}


# ============================================================================
# PROMPTS - AUTRES DISCIPLINES
# ============================================================================

OTHER_SUBJECTS_PROMPTS = {
    "biology": """Génère une visualisation 3D d'une cellule ou d'un organe : {concept}.
Explique son fonctionnement.
Propose une exploration guidée.

Format de réponse JSON :
{{
    "concept": "cellule|organe|système biologique",
    "visualization_3d": {{
        "type": "biological_structure",
        "structure": "cell|organ|system",
        "components": ["composant1", "composant2"],
        "interactive": true
    }},
    "functioning": "explication du fonctionnement",
    "guided_exploration": {{
        "steps": ["étape1", "étape2"],
        "questions": ["question1", "question2"]
    }},
    "dna_proteins": "ADN et protéines si applicable"
}}""",

    "geography": """Génère une carte interactive : {region}.
Explique les climats, reliefs et dynamiques.
Utilise des données visuelles.

Format de réponse JSON :
{{
    "region": "nom de la région",
    "interactive_map": {{
        "type": "geographic",
        "climates": ["climat1", "climat2"],
        "relief": "relief de la région",
        "dynamics": "dynamiques terrestres",
        "interactive": true
    }},
    "climate_explanation": "explication des climats",
    "relief_explanation": "explication du relief",
    "geospatial_data": "données géospatiales"
}}""",

    "economics": """Explique un concept économique : {concept} (offre/demande, inflation).
Génère une simulation dynamique.
Montre l'impact des variations.

Format de réponse JSON :
{{
    "concept": "offre_demande|inflation|croissance|marchés",
    "explanation": "explication du concept",
    "dynamic_simulation": {{
        "type": "economic_model",
        "variables": ["variable1", "variable2"],
        "interactive": true,
        "show_impact": true
    }},
    "variations_impact": {{
        "scenario1": "impact du scénario 1",
        "scenario2": "impact du scénario 2"
    }},
    "real_world_example": "exemple du monde réel"
}}""",

    "history": """Génère une ligne du temps interactive : {period}.
Explique les causes et conséquences des événements.
Pose une question critique.

Format de réponse JSON :
{{
    "period": "période historique",
    "timeline": {{
        "type": "interactive_timeline",
        "events": [{{"date": "date", "event": "événement", "description": "description"}}],
        "interactive": true
    }},
    "causes_consequences": {{
        "event": "événement",
        "causes": ["cause1", "cause2"],
        "consequences": ["conséquence1", "conséquence2"]
    }},
    "critical_question": {{
        "question": "question critique",
        "analysis": "analyse"
    }},
    "historical_context": "contexte historique"
}}"""
}


# ============================================================================
# PROMPTS - GAMIFICATION & FEEDBACK
# ============================================================================

GAMIFICATION_PROMPTS = {
    "badge_attribution": """Analyse la progression de l'apprenant : {user_progress}.
Attribue un badge pertinent.
Explique pourquoi ce badge est obtenu.

Format de réponse JSON :
{{
    "badge_type": "first_module|perfect_score|streak_days|subject_master|speed_learner|dedicated_learner|quiz_master",
    "badge_name": "nom du badge",
    "reason": "raison de l'attribution",
    "achievement": "ce qui a été accompli",
    "encouragement": "message d'encouragement",
    "next_challenge": "prochain défi suggéré"
}}""",

    "quest_generation": """Génère une quête pédagogique personnalisée : {user_profile}.
Adapte la difficulté.
Définis l'objectif, les règles et la récompense.

Format de réponse JSON :
{{
    "quest": {{
        "title": "titre de la quête",
        "description": "description",
        "objective": "objectif à atteindre",
        "difficulty": "beginner|intermediate|advanced",
        "rules": ["règle1", "règle2"],
        "reward": {{
            "points": 100,
            "badge": "nom du badge",
            "unlock": "contenu débloqué"
        }},
        "estimated_time": "temps estimé",
        "personalized": true
    }},
    "adaptation": "comment la quête est adaptée au profil"
}}""",

    "intelligent_feedback": """Analyse les erreurs de l'apprenant : {errors}.
Explique-les clairement.
Propose une visualisation corrective.
Encourage et motive.

Format de réponse JSON :
{{
    "error_analysis": {{
        "errors": [{{"type": "type d'erreur", "explanation": "explication"}}],
        "common_mistakes": ["erreur1", "erreur2"],
        "root_cause": "cause racine"
    }},
    "clear_explanation": "explication claire des erreurs",
    "corrective_visualization": {{
        "type": "error_correction",
        "show_correct_way": true,
        "interactive": true
    }},
    "encouragement": "message d'encouragement",
    "motivation": "message de motivation",
    "next_steps": "prochaines étapes suggérées"
}}"""
}


# ============================================================================
# PROMPT FINAL - RECOMMANDATION IA
# ============================================================================

RECOMMENDATION_PROMPT = """Analyse le profil de l'apprenant : {user_profile}.
Identifie ses points forts et faiblesses.
Recommande la prochaine activité idéale.
Justifie la recommandation.

Format de réponse JSON :
{{
    "profile_analysis": {{
        "strengths": ["force1", "force2"],
        "weaknesses": ["faiblesse1", "faiblesse2"],
        "learning_style": "style d'apprentissage",
        "progress": "niveau de progression"
    }},
    "recommendation": {{
        "activity_type": "module|quiz|visualization|quest",
        "subject": "matière recommandée",
        "difficulty": "beginner|intermediate|advanced",
        "title": "titre de l'activité",
        "description": "description"
    }},
    "justification": "pourquoi cette recommandation",
    "expected_benefits": ["bénéfice1", "bénéfice2"],
    "alternative_options": ["option1", "option2"]
}}"""


# ============================================================================
# FONCTION UTILITAIRE - Récupérer le prompt approprié
# ============================================================================

def get_prompt(subject: str, topic: str, level: str = "intermediate") -> str:
    """
    Récupère le prompt approprié selon la matière et le sujet
    
    Args:
        subject: La matière (mathematics, physics, chemistry, etc.)
        topic: Le sujet spécifique (functions_trigonometry, mechanics_dynamics, etc.)
        level: Le niveau (beginner, intermediate, advanced)
    
    Returns:
        Le prompt formaté avec les paramètres
    """
    prompts_map = {
        "mathematics": MATHEMATICS_PROMPTS,
        "physics": PHYSICS_PROMPTS,
        "chemistry": CHEMISTRY_PROMPTS,
        "computer_science": AI_ML_PROMPTS,
        "biology": OTHER_SUBJECTS_PROMPTS,
        "geography": OTHER_SUBJECTS_PROMPTS,
        "economics": OTHER_SUBJECTS_PROMPTS,
        "history": OTHER_SUBJECTS_PROMPTS,
    }
    
    subject_prompts = prompts_map.get(subject, {})
    
    # Si le topic n'existe pas, essayer de trouver un topic par défaut pour la matière
    if topic not in subject_prompts:
        # Topic par défaut par matière
        default_topics = {
            "mathematics": "functions_trigonometry",
            "physics": "mechanics_dynamics",
            "chemistry": "general_chemistry",
            "computer_science": "machine_learning",
            "biology": "biology",
            "geography": "geography",
            "economics": "economics",
            "history": "history"
        }
        default_topic = default_topics.get(subject)
        if default_topic and default_topic in subject_prompts:
            topic = default_topic
        else:
            # Fallback vers le prompt système
            return SYSTEM_PROMPT
    
    if topic in subject_prompts:
        prompt_template = subject_prompts[topic]
        # Formater avec les placeholders, en gérant les cas où certains placeholders n'existent pas
        try:
            return prompt_template.format(concept="{concept}", niveau=level)
        except KeyError:
            # Si le format échoue, retourner le template tel quel (sans format)
            return prompt_template
    
    # Fallback vers le prompt système
    return SYSTEM_PROMPT


def get_system_prompt() -> str:
    """Retourne le prompt système global"""
    return SYSTEM_PROMPT


def get_gamification_prompt(prompt_type: str, **kwargs) -> str:
    """
    Récupère un prompt de gamification
    
    Args:
        prompt_type: Type de prompt (badge_attribution, quest_generation, intelligent_feedback)
        **kwargs: Paramètres additionnels
    
    Returns:
        Le prompt formaté
    """
    if prompt_type in GAMIFICATION_PROMPTS:
        prompt_template = GAMIFICATION_PROMPTS[prompt_type]
        return prompt_template.format(**kwargs)
    
    return SYSTEM_PROMPT


def get_recommendation_prompt(**kwargs) -> str:
    """
    Récupère le prompt de recommandation
    
    Args:
        **kwargs: Paramètres (user_profile, etc.)
    
    Returns:
        Le prompt formaté
    """
    return RECOMMENDATION_PROMPT.format(**kwargs)


def get_curriculum_prompt(subject: str, level: str, objective: str) -> str:
    """
    Récupère le prompt pour générer un curriculum
    
    Args:
        subject: La matière
        level: Le niveau (collège, lycée, université)
        objective: L'objectif (exam, compréhension, rattrapage)
    
    Returns:
        Le prompt formaté
    """
    return CURRICULUM_PROMPT.format(subject=subject, level=level, objective=objective)


def get_learner_profile_prompt(learning_data: str) -> str:
    """
    Récupère le prompt pour créer un profil cognitif
    
    Args:
        learning_data: Données d'apprentissage de l'utilisateur (JSON string)
    
    Returns:
        Le prompt formaté
    """
    return LEARNER_PROFILE_PROMPT.format(learning_data=learning_data)


def get_evaluation_prompt(subject: str, level: str, evaluation_type: str) -> str:
    """
    Récupère le prompt pour générer une évaluation
    
    Args:
        subject: La matière
        level: Le niveau
        evaluation_type: Type d'évaluation (formative, summative, adaptive, oral)
    
    Returns:
        Le prompt formaté
    """
    return EVALUATION_PROMPT.format(subject=subject, level=level, evaluation_type=evaluation_type)


def get_explainability_prompt(error_analysis: str) -> str:
    """
    Récupère le prompt pour expliquer une erreur (Explainable AI)
    
    Args:
        error_analysis: Analyse de l'erreur (JSON string)
    
    Returns:
        Le prompt formaté
    """
    return EXPLAINABILITY_PROMPT.format(error_analysis=error_analysis)


def get_lab_simulation_prompt(simulation_request: str) -> str:
    """
    Récupère le prompt pour générer une simulation de laboratoire
    
    Args:
        simulation_request: Demande de simulation de l'apprenant
    
    Returns:
        Le prompt formaté
    """
    return LAB_SIMULATION_PROMPT.format(simulation_request=simulation_request)


# ============================================================================
# PRIORITÉ 6 - GAMIFICATION AVANCÉE
# ============================================================================

GAMIFICATION_ADVANCED_PROMPTS = {
    "season_generation": """Génère une saison pédagogique pour : {subject}, thème : {theme}.
Une saison est un parcours thématique avec progression, niveaux et déblocage de contenus.

Format de réponse JSON :
{{
    "season": {{
        "season_id": "season_1",
        "title": "Titre de la saison",
        "theme": "{theme}",
        "subject": "{subject}",
        "duration_weeks": 8,
        "levels": [
            {{
                "level": 1,
                "title": "Niveau Débutant",
                "description": "Description",
                "unlock_condition": "condition de déblocage",
                "modules": ["module_1", "module_2"],
                "badges": ["badge_1"],
                "milestone": "milestone description"
            }}
        ],
        "progression_system": {{
            "xp_per_activity": 10,
            "xp_for_completion": 50,
            "level_up_threshold": 100
        }},
        "rewards": {{
            "completion_badge": "badge_name",
            "exclusive_content": "contenu exclusif",
            "certificate": true
        }}
    }}
}}""",

    "evolving_badge": """Analyse la progression pour le badge : {badge_type}.
Détermine si le badge doit évoluer (Bronze → Argent → Or).

Format de réponse JSON :
{{
    "badge_evolution": {{
        "badge_type": "{badge_type}",
        "current_tier": "bronze|silver|gold|platinum",
        "progress_to_next": "pourcentage",
        "achievements_required": ["achievement1", "achievement2"],
        "evolution_criteria": {{
            "bronze": "critères bronze",
            "silver": "critères argent",
            "gold": "critères or"
        }},
        "can_evolve": true,
        "next_tier": "silver",
        "celebration_message": "message de célébration"
    }}
}}"""
}


# ============================================================================
# PRIORITÉ 7 - MULTI-AGENTS IA
# ============================================================================

MULTI_AGENT_PROMPTS = {
    "theorist_prof": """Tu es le Prof Théoricien de Kairos.
Ton rôle : Expliquer les concepts théoriques de manière rigoureuse et structurée.
Tu collabores avec les autres agents pour optimiser l'apprentissage.

Format de réponse JSON :
{{
    "agent": "theorist_prof",
    "explanation": {{
        "theoretical_foundation": "fondements théoriques",
        "concepts": ["concept1", "concept2"],
        "structure": "structure de l'explication",
        "rigor_level": "high|medium|low"
    }},
    "collaboration": {{
        "needs_practical": true,
        "suggests_coach": false,
        "suggests_researcher": true
    }}
}}""",

    "motivation_coach": """Tu es le Coach Motivation de Kairos.
Ton rôle : Motiver, encourager et maintenir l'engagement de l'apprenant.
Tu adaptes ton approche selon le profil et la progression.

Format de réponse JSON :
{{
    "agent": "motivation_coach",
    "motivation": {{
        "message": "message de motivation",
        "encouragement": "encouragement personnalisé",
        "milestone_celebration": "célébration de milestone",
        "challenge_proposal": "proposition de défi"
    }},
    "engagement_strategy": {{
        "current_engagement": "high|medium|low",
        "strategy": "stratégie d'engagement",
        "personalized_approach": "approche personnalisée"
    }}
}}""",

    "examiner": """Tu es l'Examinateur de Kairos.
Ton rôle : Créer et corriger des évaluations rigoureuses et équitables.
Tu évalues la compréhension et fournis un feedback constructif.

Format de réponse JSON :
{{
    "agent": "examiner",
    "evaluation": {{
        "questions": ["question1", "question2"],
        "grading_criteria": "critères de notation",
        "fairness": "équité de l'évaluation",
        "difficulty_balance": "équilibre de difficulté"
    }},
    "feedback": {{
        "strengths": ["force1", "force2"],
        "improvements": ["amélioration1", "amélioration2"],
        "constructive": true
    }}
}}""",

    "scientific_researcher": """Tu es le Chercheur Scientifique de Kairos.
Ton rôle : Analyser en profondeur, proposer des recherches et des approfondissements.
Tu apportes une perspective académique et critique.

Format de réponse JSON :
{{
    "agent": "scientific_researcher",
    "analysis": {{
        "deep_analysis": "analyse approfondie",
        "research_questions": ["question1", "question2"],
        "academic_perspective": "perspective académique",
        "critical_thinking": "pensée critique"
    }},
    "suggestions": {{
        "further_research": "recherche approfondie",
        "experiments": ["expérience1", "expérience2"],
        "academic_resources": ["ressource1", "ressource2"]
    }}
}}"""
}


# ============================================================================
# PRIORITÉ 8 - ANALYTICS & DASHBOARD IA
# ============================================================================

ANALYTICS_PROMPTS = {
    "progress_prediction": """Analyse les données de progression : {progress_data}.
Prédit le taux de réussite et détecte les risques de décrochage.

Format de réponse JSON :
{{
    "predictions": {{
        "success_rate": "pourcentage",
        "completion_probability": "probabilité",
        "time_to_completion": "temps estimé",
        "risk_factors": ["facteur1", "facteur2"]
    }},
    "dropout_detection": {{
        "risk_level": "high|medium|low",
        "indicators": ["indicateur1", "indicateur2"],
        "intervention_needed": true,
        "recommended_actions": ["action1", "action2"]
    }},
    "progress_curves": {{
        "current_trajectory": "trajectoire actuelle",
        "optimal_trajectory": "trajectoire optimale",
        "gap_analysis": "analyse de l'écart",
        "optimization_suggestions": ["suggestion1", "suggestion2"]
    }}
}}""",

    "dashboard_insights": """Génère des insights intelligents pour le dashboard : {dashboard_data}.
Fournis des recommandations automatiques basées sur l'analyse.

Format de réponse JSON :
{{
    "insights": {{
        "key_metrics": {{
            "metric1": "valeur et interprétation",
            "metric2": "valeur et interprétation"
        }},
        "trends": {{
            "improving": ["tendance1", "tendance2"],
            "declining": ["tendance1", "tendance2"],
            "stable": ["tendance1"]
        }},
        "anomalies": ["anomalie1", "anomalie2"]
    }},
    "recommendations": {{
        "immediate": ["recommandation1", "recommandation2"],
        "short_term": ["recommandation1"],
        "long_term": ["recommandation1"]
    }},
    "alerts": [
        {{
            "type": "warning|info|success",
            "message": "message",
            "action_required": true
        }}
    ]
}}
}}"""
}


# ============================================================================
# PRIORITÉ 9 - GÉNÉRATION DE CONTENU ACADÉMIQUE
# ============================================================================

ACADEMIC_CONTENT_PROMPTS = {
    "pdf_notes": """Génère des notes de cours au format PDF pour : {subject}, module : {module}.
Format académique professionnel avec structure claire.

Format de réponse JSON :
{{
    "pdf_content": {{
        "title": "Titre",
        "subject": "{subject}",
        "module": "{module}",
        "sections": [
            {{
                "section_title": "Titre section",
                "content": "contenu",
                "key_points": ["point1", "point2"],
                "examples": ["exemple1", "exemple2"],
                "formulas": ["formule1", "formule2"]
            }}
        ],
        "summary": "résumé",
        "references": ["référence1", "référence2"]
    }},
    "formatting": {{
        "style": "academic",
        "sections": true,
        "diagrams": true,
        "citations": true
    }}
}}""",

    "learning_report": """Génère un rapport d'apprentissage pour : {user_id}, période : {period}.
Rapport complet avec analyse, progression et recommandations.

Format de réponse JSON :
{{
    "report": {{
        "user_id": "{user_id}",
        "period": "{period}",
        "executive_summary": "résumé exécutif",
        "progress_analysis": {{
            "overall": "analyse globale",
            "by_subject": {{"matière1": "analyse"}},
            "by_skill": {{"compétence1": "analyse"}}
        }},
        "achievements": ["accomplissement1", "accomplissement2"],
        "challenges": ["défi1", "défi2"],
        "recommendations": {{
            "immediate": ["recommandation1"],
            "future": ["recommandation1"]
        }},
        "next_steps": ["étape1", "étape2"]
    }}
}}
}}"""
}


def get_gamification_advanced_prompt(prompt_type: str, **kwargs) -> str:
    """
    Récupère un prompt de gamification avancée
    
    Args:
        prompt_type: Type de prompt (season_generation, evolving_badge)
        **kwargs: Paramètres additionnels
    
    Returns:
        Le prompt formaté
    """
    if prompt_type in GAMIFICATION_ADVANCED_PROMPTS:
        prompt_template = GAMIFICATION_ADVANCED_PROMPTS[prompt_type]
        return prompt_template.format(**kwargs)
    
    return SYSTEM_PROMPT


def get_multi_agent_prompt(agent_type: str, **kwargs) -> str:
    """
    Récupère un prompt pour un agent IA spécifique
    
    Args:
        agent_type: Type d'agent (theorist_prof, motivation_coach, examiner, scientific_researcher)
        **kwargs: Paramètres additionnels
    
    Returns:
        Le prompt formaté
    """
    if agent_type in MULTI_AGENT_PROMPTS:
        prompt_template = MULTI_AGENT_PROMPTS[agent_type]
        return prompt_template.format(**kwargs)
    
    return SYSTEM_PROMPT


def get_analytics_prompt(prompt_type: str, **kwargs) -> str:
    """
    Récupère un prompt d'analytics
    
    Args:
        prompt_type: Type de prompt (progress_prediction, dashboard_insights)
        **kwargs: Paramètres additionnels
    
    Returns:
        Le prompt formaté
    """
    if prompt_type in ANALYTICS_PROMPTS:
        prompt_template = ANALYTICS_PROMPTS[prompt_type]
        return prompt_template.format(**kwargs)
    
    return SYSTEM_PROMPT


def get_academic_content_prompt(prompt_type: str, **kwargs) -> str:
    """
    Récupère un prompt pour générer du contenu académique
    
    Args:
        prompt_type: Type de prompt (pdf_notes, learning_report)
        **kwargs: Paramètres additionnels
    
    Returns:
        Le prompt formaté
    """
    if prompt_type in ACADEMIC_CONTENT_PROMPTS:
        prompt_template = ACADEMIC_CONTENT_PROMPTS[prompt_type]
        return prompt_template.format(**kwargs)
    
    return SYSTEM_PROMPT
