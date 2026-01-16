"""
Modèles de données Pydantic
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Subject(str, Enum):
    MATHEMATICS = "mathematics"
    COMPUTER_SCIENCE = "computer_science"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"

class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

# Modèles utilisateur
class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    date_of_birth: str  # Format ISO: YYYY-MM-DD
    country: str
    phone: str

class UserCreate(UserBase):
    password: str  # Obligatoire avec validation de force

class UserUpdate(BaseModel):
    """Modèle pour la mise à jour des informations utilisateur"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None  # Format ISO: YYYY-MM-DD
    country: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None  # Pour changer le mot de passe

class User(UserBase):
    id: str
    created_at: str  # ISO format string from serialize_doc
    is_active: bool = True
    is_admin: bool = False  # Par défaut, les utilisateurs ne sont pas admin
    google_id: Optional[str] = None  # Déprécié - conservé pour compatibilité
    auth_provider: Optional[str] = None  # Déprécié - conservé pour compatibilité
    avatar_url: Optional[str] = None  # Déprécié - conservé pour compatibilité
    
    class Config:
        from_attributes = True
        # Permettre les champs optionnels manquants
        populate_by_name = True

# Modèles de modules d'apprentissage
class ModuleBase(BaseModel):
    title: str
    description: str
    subject: Subject
    difficulty: Optional[Difficulty] = None
    estimated_time: int  # en minutes
    
    @field_validator('difficulty', mode='before')
    @classmethod
    def validate_difficulty(cls, v):
        """Valide difficulty, retourne None si absent ou None"""
        if v is None or v == '':
            return None
        return v
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Le titre doit contenir au moins 3 caractères")
        if len(v) > 200:
            raise ValueError("Le titre ne peut pas dépasser 200 caractères")
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        if not v or len(v.strip()) < 10:
            raise ValueError("La description doit contenir au moins 10 caractères")
        if len(v) > 2000:
            raise ValueError("La description ne peut pas dépasser 2000 caractères")
        return v.strip()
    
    @field_validator('estimated_time')
    @classmethod
    def validate_estimated_time(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Le temps estimé doit être d'au moins 1 minute")
        if v > 1000:
            raise ValueError("Le temps estimé ne peut pas dépasser 1000 minutes")
        return v

class ModuleCreate(ModuleBase):
    content: Dict[str, Any]  # Contenu JSON pour les scènes 3D/AR
    learning_objectives: List[str]
    
    @field_validator('learning_objectives')
    @classmethod
    def validate_learning_objectives(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("Au moins un objectif d'apprentissage est requis")
        if len(v) > 20:
            raise ValueError("Le nombre d'objectifs ne peut pas dépasser 20")
        for obj in v:
            if not obj or len(obj.strip()) < 5:
                raise ValueError("Chaque objectif doit contenir au moins 5 caractères")
            if len(obj) > 500:
                raise ValueError("Chaque objectif ne peut pas dépasser 500 caractères")
        return v
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Valide la taille et la structure du contenu"""
        import json
        
        # Vérifier la taille du contenu sérialisé (max 5MB)
        try:
            content_json = json.dumps(v)
            content_size_mb = len(content_json.encode('utf-8')) / (1024 * 1024)
            
            if content_size_mb > 5:
                raise ValueError(
                    f"Le contenu du module est trop volumineux ({content_size_mb:.2f}MB). "
                    f"Taille maximale autorisée: 5MB. "
                    f"Considérez stocker les assets lourds (scènes 3D) dans un object storage."
                )
        except (TypeError, ValueError) as e:
            if "trop volumineux" in str(e):
                raise
            # Si ce n'est pas une erreur de taille, c'est peut-être un problème de sérialisation
            raise ValueError("Le contenu du module n'est pas valide JSON")
        
        # Vérifier la profondeur de l'objet (max 10 niveaux pour éviter la récursion)
        def check_depth(obj, current_depth=0, max_depth=10):
            if current_depth > max_depth:
                raise ValueError(f"Le contenu du module est trop profond (max {max_depth} niveaux)")
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, current_depth + 1, max_depth)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, current_depth + 1, max_depth)
        
        check_depth(v)
        
        return v

class Module(ModuleBase):
    id: str
    content: Optional[Dict[str, Any]] = None  # Optionnel car exclu de la liste pour performance
    learning_objectives: Optional[List[str]] = []  # Liste vide par défaut si absent
    created_at: datetime  # Requis mais peut être converti depuis string ISO
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True  # Utiliser les valeurs de l'enum plutôt que l'enum lui-même
        # Permettre les champs optionnels manquants
        populate_by_name = True

# Modèles de progression
class ProgressCreate(BaseModel):
    """Modèle pour créer/mettre à jour une progression (sans user_id, obtenu via JWT)"""
    module_id: str
    completed: bool = False
    score: Optional[float] = None
    time_spent: int = 0  # en secondes

class ProgressBase(BaseModel):
    """Modèle de base avec user_id (pour les réponses)"""
    user_id: str
    module_id: str
    completed: bool = False
    score: Optional[float] = None
    time_spent: int = 0  # en secondes

class Progress(ProgressBase):
    id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    attempts: int = 1
    
    class Config:
        from_attributes = True

# Modèles pour les badges et récompenses
class BadgeType(str, Enum):
    FIRST_MODULE = "first_module"
    PERFECT_SCORE = "perfect_score"
    STREAK_DAYS = "streak_days"
    SUBJECT_MASTER = "subject_master"
    SPEED_LEARNER = "speed_learner"
    DEDICATED_LEARNER = "dedicated_learner"
    QUIZ_MASTER = "quiz_master"

class Badge(BaseModel):
    id: str
    user_id: str
    badge_type: BadgeType
    earned_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class BadgeCreate(BaseModel):
    badge_type: BadgeType
    metadata: Optional[Dict[str, Any]] = None

# Modèles pour les favoris
class Favorite(BaseModel):
    id: str
    user_id: str
    module_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class FavoriteCreate(BaseModel):
    module_id: str

# Modèles pour l'IA
class AIChatMessage(BaseModel):
    role: str  # "user" ou "assistant"
    content: str
    timestamp: Optional[datetime] = None

class AIChatRequest(BaseModel):
    message: str
    module_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    language: Optional[str] = "fr"  # Langue de la réponse (fr, en)
    expert_mode: Optional[bool] = False  # Si True, force l'utilisation de GPT-5.2 (Expert)
    research_mode: Optional[bool] = False  # Si True, force l'utilisation de GPT-5.2 Pro (Research AI)
    conversation_history: Optional[List[Dict[str, str]]] = None  # Historique de conversation au format OpenAI

class AIChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = None

class ImmersiveContextRequest(BaseModel):
    module_id: str
    mode: str  # 'ar', 'vr', 'unity'
    scene_type: Optional[str] = None

class ImmersiveContextResponse(BaseModel):
    guidance: str
    tips: Optional[List[str]] = None

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str

class QuizGenerateRequest(BaseModel):
    module_id: str
    num_questions: int = 50
    difficulty: Optional[Difficulty] = None
    
    @field_validator('num_questions')
    @classmethod
    def validate_num_questions(cls, v: int) -> int:
        """Valide le nombre de questions (max 50)"""
        if v < 1:
            raise ValueError("Le nombre de questions doit être au moins 1")
        if v > 50:
            raise ValueError("Le nombre de questions ne peut pas dépasser 50")
        return v
    
    class Config:
        from_attributes = True

class QuizResponse(BaseModel):
    questions: List[QuizQuestion]
    module_id: str
    quiz_id: Optional[str] = None

# Modèle pour stocker le quiz en base de données
class Quiz(BaseModel):
    id: str
    module_id: str
    questions: List[QuizQuestion]
    num_questions: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        populate_by_name = True

class QuizCreate(BaseModel):
    module_id: str
    questions: List[QuizQuestion]
    num_questions: int

# Modèles pour les tentatives de quiz
class QuizAttemptCreate(BaseModel):
    """Modèle pour créer une tentative de quiz"""
    module_id: str
    quiz_id: str
    answers: Dict[int, int]  # {question_index: answer_index}
    score: float
    time_spent: int  # en secondes
    num_questions: int
    num_correct: int

class QuizAttempt(BaseModel):
    """Modèle pour une tentative de quiz"""
    id: str
    user_id: str
    module_id: str
    quiz_id: str
    score: float
    time_spent: int
    num_questions: int
    num_correct: int
    answers: Dict[int, int]
    started_at: datetime
    completed_at: datetime
    
    class Config:
        from_attributes = True

class QuizStatistics(BaseModel):
    """Statistiques de quiz pour un utilisateur"""
    module_id: str
    total_attempts: int
    best_score: float
    average_score: float
    last_attempt_at: Optional[datetime] = None
    total_time_spent: int  # en secondes
    
    class Config:
        from_attributes = True

# Modèles pour les examens
class ExamQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    points: float = 1.0  # Points attribués pour cette question

class ExamCreate(BaseModel):
    """Modèle pour créer un examen"""
    module_id: str  # Module couvert par l'examen
    num_questions: int = 15
    passing_score: float = 70.0  # Score minimum pour valider (en pourcentage)
    time_limit: int = 30  # Temps limite en minutes
    
    @field_validator('num_questions')
    @classmethod
    def validate_num_questions(cls, v: int) -> int:
        if v < 5:
            raise ValueError("Un examen doit contenir au moins 5 questions")
        if v > 50:
            raise ValueError("Un examen ne peut pas dépasser 50 questions")
        return v
    
    @field_validator('passing_score')
    @classmethod
    def validate_passing_score(cls, v: float) -> float:
        if v < 0 or v > 100:
            raise ValueError("Le score de passage doit être entre 0 et 100")
        return v
    
    @field_validator('time_limit')
    @classmethod
    def validate_time_limit(cls, v: int) -> int:
        if v < 10:
            raise ValueError("Le temps limite doit être d'au moins 10 minutes")
        if v > 180:
            raise ValueError("Le temps limite ne peut pas dépasser 180 minutes")
        return v

class Exam(BaseModel):
    """Modèle pour un examen"""
    id: str
    module_id: str
    questions: List[ExamQuestion]  # Questions QCM (pour examens standards ou partie QCM des examens maths)
    num_questions: int
    passing_score: float
    time_limit: int
    pdf_url: Optional[str] = None  # URL du PDF associé
    # Pour les examens de mathématiques : structure en deux parties
    exam_type: Optional[str] = "standard"  # "standard" ou "mathematics"
    practical_exercises: Optional[List[Dict[str, Any]]] = None  # Exercices pratiques (75% pour maths)
    qcm_weight: Optional[float] = 1.0  # Poids de la partie QCM (0.25 pour maths, 1.0 pour standard)
    practical_weight: Optional[float] = 0.0  # Poids de la partie pratique (0.75 pour maths, 0.0 pour standard)
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

class ExamAttemptCreate(BaseModel):
    """Modèle pour démarrer une tentative d'examen"""
    exam_id: str

class ExamAnswer(BaseModel):
    """Réponse à une question d'examen"""
    question_index: int
    answer: int  # Index de la réponse choisie

class ExamSubmission(BaseModel):
    """Modèle pour soumettre les réponses d'un examen"""
    exam_id: str
    answers: List[ExamAnswer]  # Réponses QCM
    time_spent: int  # Temps passé en secondes
    practical_answers: Optional[List[Dict[str, Any]]] = None  # Réponses aux exercices pratiques (pour maths)

class ExamAttempt(BaseModel):
    """Modèle pour une tentative d'examen"""
    id: str
    user_id: str
    exam_id: str
    module_id: str
    score: float
    max_score: float
    percentage: float
    passed: bool
    answers: List[Dict[str, Any]]  # Réponses données
    time_spent: int  # Temps passé en secondes
    started_at: datetime
    completed_at: Optional[datetime] = None  # Optionnel car pas encore complété au démarrage
    
    class Config:
        from_attributes = True
        use_enum_values = True

class ExamAttemptResponse(BaseModel):
    """Réponse après soumission d'un examen"""
    attempt_id: str
    score: float
    max_score: float
    percentage: float
    passed: bool
    module_id: str
    module_validated: bool  # Si le module a été validé
    
    class Config:
        from_attributes = True
        use_enum_values = True

# Modèles pour la validation de module
class ModuleValidation(BaseModel):
    """Modèle pour une validation de module"""
    id: str
    user_id: str
    module_id: str
    exam_attempt_id: str  # ID de la tentative d'examen qui a validé
    validated_at: datetime
    score: float  # Score obtenu à l'examen
    
    class Config:
        from_attributes = True
        use_enum_values = True

class ModuleValidationResponse(BaseModel):
    """Réponse pour une validation de module"""
    module_id: str
    validated: bool
    validated_at: Optional[datetime] = None
    exam_score: Optional[float] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

# Modèles pour les Travaux Dirigés (TD)
class TDExercise(BaseModel):
    """Exercice dans un TD"""
    question: str
    answer: Optional[str] = None  # Réponse attendue (optionnel pour les exercices ouverts)
    solution: Optional[str] = None  # Solution détaillée
    points: Optional[int] = None  # Optionnel - la notation est désactivée
    difficulty: Optional[Difficulty] = None

class TDCreate(BaseModel):
    """Modèle pour créer un TD"""
    module_id: str
    title: str
    description: str
    exercises: List[TDExercise]
    estimated_time: int  # en minutes
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Le titre doit contenir au moins 3 caractères")
        if len(v) > 200:
            raise ValueError("Le titre ne peut pas dépasser 200 caractères")
        return v.strip()
    
    @field_validator('exercises')
    @classmethod
    def validate_exercises(cls, v: List[TDExercise]) -> List[TDExercise]:
        if not v or len(v) == 0:
            raise ValueError("Un TD doit contenir au moins un exercice")
        if len(v) > 50:
            raise ValueError("Un TD ne peut pas contenir plus de 50 exercices")
        return v

class TD(BaseModel):
    """Modèle TD complet"""
    id: str
    module_id: str
    title: str
    description: str
    exercises: List[TDExercise]
    estimated_time: int
    pdf_url: Optional[str] = None  # URL du PDF associé
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Modèles pour les Travaux Pratiques (TP)
class TPStep(BaseModel):
    """Étape dans un TP (exercice pratique)"""
    step_number: int
    title: str
    instructions: str
    expected_result: Optional[str] = None
    code_example: Optional[str] = None  # Exemple de code ou pseudo-code
    tests: Optional[List[str]] = None  # Tests à effectuer pour valider
    tips: Optional[List[str]] = None

class TPCreate(BaseModel):
    """Modèle pour créer un TP"""
    module_id: str
    title: str
    description: str
    objectives: List[str]
    steps: List[TPStep]
    estimated_time: int  # en minutes
    materials_needed: Optional[List[str]] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Le titre doit contenir au moins 3 caractères")
        if len(v) > 200:
            raise ValueError("Le titre ne peut pas dépasser 200 caractères")
        return v.strip()
    
    @field_validator('steps')
    @classmethod
    def validate_steps(cls, v: List[TPStep]) -> List[TPStep]:
        if not v or len(v) == 0:
            raise ValueError("Un TP doit contenir au moins une étape")
        if len(v) > 30:
            raise ValueError("Un TP ne peut pas contenir plus de 30 étapes")
        return v

class TP(BaseModel):
    """Modèle TP complet"""
    id: str
    module_id: str
    title: str
    description: str
    objectives: List[str]
    steps: List[TPStep]
    estimated_time: int
    materials_needed: Optional[List[str]] = None
    programming_language: Optional[str] = None  # Langage de programmation utilisé
    pdf_url: Optional[str] = None  # URL du PDF associé
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Modèles pour les Ressources de cours
class ResourceType(str, Enum):
    """Types de ressources disponibles"""
    PDF = "pdf"
    WORD = "word"
    PPT = "ppt"
    VIDEO = "video"
    LINK = "link"

class ResourceCreate(BaseModel):
    """Modèle pour créer une ressource"""
    module_id: str
    title: str
    description: Optional[str] = None
    resource_type: ResourceType
    file_url: Optional[str] = None  # Pour les fichiers uploadés
    external_url: Optional[str] = None  # Pour les liens externes
    file_size: Optional[int] = None  # Taille en bytes
    file_name: Optional[str] = None  # Nom du fichier original
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v.strip()) < 3:
            raise ValueError("Le titre doit contenir au moins 3 caractères")
        if len(v) > 200:
            raise ValueError("Le titre ne peut pas dépasser 200 caractères")
        return v.strip()
    
    @field_validator('external_url')
    @classmethod
    def validate_url(cls, v: Optional[str], info) -> Optional[str]:
        if v and info.data.get('resource_type') == ResourceType.LINK:
            if not v.startswith(('http://', 'https://')):
                raise ValueError("L'URL doit commencer par http:// ou https://")
        return v

class Resource(BaseModel):
    """Modèle ressource complète"""
    id: str
    module_id: str
    title: str
    description: Optional[str] = None
    resource_type: ResourceType
    file_url: Optional[str] = None
    external_url: Optional[str] = None
    file_size: Optional[int] = None
    file_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
