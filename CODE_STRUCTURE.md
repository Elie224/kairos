# 📁 Structure du Code - Guide de Développement Kairos

Ce document décrit l'architecture et l'organisation du code pour maintenir la qualité, la lisibilité et la maintenabilité.

## 🎯 Principes de Base

1. **Séparation des responsabilités** - Chaque module a une responsabilité claire
2. **DRY (Don't Repeat Yourself)** - Éviter la duplication de code
3. **SOLID** - Principes de programmation orientée objet
4. **Type Safety** - Utiliser TypeScript de manière stricte
5. **Documentation** - Commenter avec JSDoc toutes les fonctions publiques

## 📂 Structure Frontend (`frontend/src/`)

```
frontend/src/
├── components/          # Composants React réutilisables
│   ├── modules/        # Composants spécifiques aux modules
│   ├── admin/          # Composants d'administration
│   └── index.ts        # Exports centralisés
├── pages/              # Pages de l'application (routes)
├── hooks/              # React Hooks personnalisés
├── services/           # Services API et logique métier
├── store/              # État global (Zustand)
├── types/              # Types TypeScript partagés
├── utils/              # Fonctions utilitaires
├── constants/          # Constantes de l'application
├── styles/             # Fichiers CSS globaux
├── i18n/               # Internationalisation
├── theme.ts            # Configuration du thème Chakra UI
└── main.tsx            # Point d'entrée de l'application
```

### Composants (`components/`)

**Convention de nommage :** PascalCase (ex: `ModuleCard.tsx`)

- **Organisation :** Par domaine fonctionnel (modules, admin, etc.)
- **Props :** Toujours typées avec TypeScript
- **Documentation :** JSDoc pour les props et fonctions exposées
- **Exemple :**
```typescript
/**
 * Composant de carte de module
 * @param module - Module à afficher
 * @param onSelect - Callback appelé lors de la sélection
 */
interface ModuleCardProps {
  module: Module
  onSelect?: (moduleId: string) => void
}
```

### Pages (`pages/`)

**Convention de nommage :** PascalCase (ex: `Dashboard.tsx`)

- **Responsabilité :** Orchester les composants et la logique métier
- **Structure :**
  1. Imports
  2. Types/Interfaces
  3. Composant principal
  4. Hooks (useState, useEffect, useQuery)
  5. Handlers/fonctions
  6. Rendu JSX

### Services (`services/`)

**Convention de nommage :** camelCase (ex: `api.ts`, `chatService.ts`)

- **Responsabilité :** Communication avec l'API et logique métier
- **Structure :**
  - Classe ou objet avec méthodes statiques
  - Gestion d'erreurs centralisée
  - Types TypeScript stricts
  - Documentation JSDoc

### Hooks (`hooks/`)

**Convention de nommage :** camelCase avec préfixe `use` (ex: `useModules.ts`)

- **Responsabilité :** Logique réutilisable encapsulée dans des hooks
- **Structure :**
  - Type de retour typé
  - Gestion d'erreurs
  - Documentation JSDoc

### Utils (`utils/`)

**Convention de nommage :** camelCase (ex: `logger.ts`, `errorHandler.ts`)

- **Responsabilité :** Fonctions utilitaires pures
- **Type Safety :** Types stricts pour tous les paramètres
- **Documentation :** JSDoc pour toutes les fonctions

## 📂 Structure Backend (`backend/app/`)

```
backend/app/
├── routers/            # Routes API (FastAPI)
├── services/           # Logique métier
├── models/             # Modèles de données
├── repositories/       # Accès aux données (pattern Repository)
├── middleware/         # Middlewares (auth, logging, etc.)
├── prompts/            # Prompts AI (Kairos)
├── tasks/              # Tâches asynchrones (Celery)
├── utils/              # Utilitaires Python
├── schemas.py          # Schémas Pydantic
├── config.py           # Configuration
└── main.py             # Point d'entrée FastAPI
```

### Routers (`routers/`)

**Convention de nommage :** snake_case (ex: `modules.py`, `kairos_prompts.py`)

- **Responsabilité :** Définir les endpoints API
- **Structure :**
  - Imports
  - Router FastAPI
  - Endpoints avec documentation
  - Gestion d'erreurs

### Services (`services/`)

**Convention de nommage :** snake_case (ex: `ai_service.py`, `gamification_service.py`)

- **Responsabilité :** Logique métier complexe
- **Structure :**
  - Classe avec méthodes statiques ou d'instance
  - Documentation docstring
  - Gestion d'erreurs
  - Logging approprié

## 🔧 Conventions de Code

### TypeScript/JavaScript

1. **Types :** Toujours définir les types explicites
2. **Interfaces :** Préférer les interfaces aux types pour les objets
3. **Imports :** Organiser par catégories (React, libs externes, modules internes)
4. **Noms :**
   - Variables/fonctions : camelCase
   - Composants : PascalCase
   - Constantes : UPPER_SNAKE_CASE
   - Types/Interfaces : PascalCase

### Python

1. **Types :** Utiliser type hints partout
2. **Docstrings :** Google style ou NumPy style
3. **Imports :** Organiser (stdlib, third-party, local)
4. **Noms :**
   - Variables/fonctions : snake_case
   - Classes : PascalCase
   - Constantes : UPPER_SNAKE_CASE

### Commentaires et Documentation

1. **JSDoc/Docstring :** Pour toutes les fonctions publiques
2. **Commentaires inline :** Expliquer le "pourquoi", pas le "quoi"
3. **README :** Dans chaque dossier majeur si nécessaire

**Exemple JSDoc :**
```typescript
/**
 * Charge les modules depuis l'API avec filtrage
 * @param filters - Filtres à appliquer (sujet, recherche, etc.)
 * @returns Promise résolue avec les modules filtrés
 * @throws AppError si la requête échoue
 */
async function loadModules(filters: ModuleFilters): Promise<Module[]> {
  // Implementation
}
```

## 🚨 Gestion des Erreurs

### Frontend

Utiliser le système de logging centralisé (`utils/logger.ts`) et le gestionnaire d'erreurs (`utils/errorHandler.ts`):

```typescript
import logger from '@/utils/logger'
import { handleError, handleApiError } from '@/utils/errorHandler'

// Dans un try/catch
try {
  const data = await api.get('/endpoint')
} catch (error) {
  const userMessage = handleApiError(error, '/endpoint')
  // Afficher userMessage à l'utilisateur
}
```

### Backend

Utiliser le logging Python standard avec contexte :

```python
import logging

logger = logging.getLogger(__name__)

try:
    # Code
except Exception as e:
    logger.error(f"Erreur dans le service: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Erreur interne")
```

## 📝 Checklist Avant Commit

- [ ] Code formaté (Prettier/Black)
- [ ] Pas d'erreurs TypeScript/Python
- [ ] Tous les console.log remplacés par logger
- [ ] JSDoc/Docstrings ajoutés aux nouvelles fonctions
- [ ] Types explicites pour toutes les fonctions
- [ ] Gestion d'erreurs appropriée
- [ ] Tests passent (si disponibles)
- [ ] Code review effectué

## 🔍 Outils de Qualité

- **Frontend :** ESLint, Prettier, TypeScript strict
- **Backend :** flake8, Black, mypy (optionnel)
- **Git :** Conventional Commits pour les messages

## 📚 Ressources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Best Practices](https://react.dev/learn)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
