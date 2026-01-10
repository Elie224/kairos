"""
Package models pour les modèles de données Pydantic et PostgreSQL
"""
import sys
import os
import importlib.util

# Charger directement le fichier models.py depuis le répertoire parent
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_file = os.path.join(parent_dir, 'models.py')

if os.path.exists(models_file):
    spec = importlib.util.spec_from_file_location("app.models_pydantic", models_file)
    models_pydantic = importlib.util.module_from_spec(spec)
    sys.modules["app.models_pydantic"] = models_pydantic
    spec.loader.exec_module(models_pydantic)
    
    # Réexporter tous les modèles Pydantic
    Subject = models_pydantic.Subject
    Difficulty = models_pydantic.Difficulty
    UserBase = models_pydantic.UserBase
    UserCreate = models_pydantic.UserCreate
    UserUpdate = models_pydantic.UserUpdate
    User = models_pydantic.User
    ModuleBase = models_pydantic.ModuleBase
    ModuleCreate = models_pydantic.ModuleCreate
    Module = models_pydantic.Module
    ProgressCreate = models_pydantic.ProgressCreate
    ProgressBase = models_pydantic.ProgressBase
    Progress = models_pydantic.Progress
    BadgeType = models_pydantic.BadgeType
    Badge = models_pydantic.Badge
    BadgeCreate = models_pydantic.BadgeCreate
    Favorite = models_pydantic.Favorite
    FavoriteCreate = models_pydantic.FavoriteCreate
    AIChatMessage = models_pydantic.AIChatMessage
    AIChatRequest = models_pydantic.AIChatRequest
    AIChatResponse = models_pydantic.AIChatResponse
    ImmersiveContextRequest = models_pydantic.ImmersiveContextRequest
    ImmersiveContextResponse = models_pydantic.ImmersiveContextResponse
    QuizQuestion = models_pydantic.QuizQuestion
    QuizGenerateRequest = models_pydantic.QuizGenerateRequest
    QuizResponse = models_pydantic.QuizResponse
    Quiz = models_pydantic.Quiz
    QuizCreate = models_pydantic.QuizCreate
    QuizAttemptCreate = models_pydantic.QuizAttemptCreate
    QuizAttempt = models_pydantic.QuizAttempt
    QuizStatistics = models_pydantic.QuizStatistics
    # Exam models
    ExamQuestion = models_pydantic.ExamQuestion
    ExamCreate = models_pydantic.ExamCreate
    Exam = models_pydantic.Exam
    ExamAttemptCreate = models_pydantic.ExamAttemptCreate
    ExamAnswer = models_pydantic.ExamAnswer
    ExamSubmission = models_pydantic.ExamSubmission
    ExamAttempt = models_pydantic.ExamAttempt
    ExamAttemptResponse = models_pydantic.ExamAttemptResponse
    # Validation models
    ModuleValidation = models_pydantic.ModuleValidation
    ModuleValidationResponse = models_pydantic.ModuleValidationResponse
    # TD models
    TDExercise = models_pydantic.TDExercise
    TDCreate = models_pydantic.TDCreate
    TD = models_pydantic.TD
    # TP models
    TPStep = models_pydantic.TPStep
    TPCreate = models_pydantic.TPCreate
    TP = models_pydantic.TP
    # Resource models
    ResourceType = models_pydantic.ResourceType
    ResourceCreate = models_pydantic.ResourceCreate
    Resource = models_pydantic.Resource
else:
    raise ImportError(f"Fichier models.py introuvable: {models_file}")

# Exporter aussi les modèles PostgreSQL
# Import PostgreSQL models (optionnel)
try:
    from app.models.postgres_models import User as PostgresUser, Course, Module as PostgresModule, Enrollment, UserProgress
except ImportError:
    # PostgreSQL est optionnel
    PostgresUser = None
    Course = None
    PostgresModule = None
    Enrollment = None
    UserProgress = None

__all__ = [
    # Enums
    "Subject",
    "Difficulty",
    "BadgeType",
    # User models
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "User",
    # Module models
    "ModuleBase",
    "ModuleCreate",
    "Module",
    # Progress models
    "ProgressCreate",
    "ProgressBase",
    "Progress",
    # Badge models
    "Badge",
    "BadgeCreate",
    # Favorite models
    "Favorite",
    "FavoriteCreate",
    # AI models
    "AIChatMessage",
    "AIChatRequest",
    "AIChatResponse",
    "ImmersiveContextRequest",
    "ImmersiveContextResponse",
    # Quiz models
    "QuizQuestion",
    "QuizGenerateRequest",
    "QuizResponse",
    "Quiz",
    "QuizCreate",
    "QuizAttemptCreate",
    "QuizAttempt",
    "QuizStatistics",
    # Exam models
    "ExamQuestion",
    "ExamCreate",
    "Exam",
    "ExamAttemptCreate",
    "ExamAnswer",
    "ExamSubmission",
    "ExamAttempt",
    "ExamAttemptResponse",
    # Validation models
    "ModuleValidation",
    "ModuleValidationResponse",
    # TD models
    "TDExercise",
    "TDCreate",
    "TD",
    # TP models
    "TPStep",
    "TPCreate",
    "TP",
    # Resource models
    "ResourceType",
    "ResourceCreate",
    "Resource",
    # PostgreSQL models (peuvent être None si PostgreSQL n'est pas disponible)
    "PostgresUser",
    "Course",
    "PostgresModule",
    "Enrollment",
    "UserProgress",
]

# Vérifier que les modèles PostgreSQL sont disponibles avant de les ajouter à __all__
if PostgresUser is None:
    # Retirer les modèles PostgreSQL de __all__ s'ils ne sont pas disponibles
    __all__ = [item for item in __all__ if item not in ["PostgresUser", "Course", "PostgresModule", "Enrollment", "UserProgress"]]
