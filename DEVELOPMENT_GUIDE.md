# 🛠️ Guide de Développement Kairos

Guide complet pour les développeurs travaillant sur Kairos.

## 📋 Table des Matières

1. [Structure du Projet](#structure-du-projet)
2. [Conventions de Code](#conventions-de-code)
3. [Gestion des Erreurs](#gestion-des-erreurs)
4. [Logging](#logging)
5. [Tests](#tests)
6. [Performance](#performance)
7. [Sécurité](#sécurité)
8. [Documentation](#documentation)

## 📁 Structure du Projet

Voir [CODE_STRUCTURE.md](./CODE_STRUCTURE.md) pour la structure détaillée.

### Frontend (`frontend/src/`)

- **`components/`** - Composants React réutilisables
- **`pages/`** - Pages de l'application (routes)
- **`hooks/`** - React Hooks personnalisés
- **`services/`** - Services API et logique métier
- **`store/`** - État global (Zustand)
- **`types/`** - Types TypeScript
- **`utils/`** - Utilitaires (logger, errorHandler, etc.)
- **`constants/`** - Constantes
- **`styles/`** - CSS globaux

### Backend (`backend/app/`)

- **`routers/`** - Routes FastAPI
- **`services/`** - Logique métier
- **`models/`** - Modèles de données
- **`repositories/`** - Accès aux données (pattern Repository)
- **`middleware/`** - Middlewares
- **`prompts/`** - Prompts AI (Kairos)

## 🎨 Conventions de Code

### TypeScript/JavaScript

```typescript
// ✅ BON - Types explicites, JSDoc
/**
 * Charge un module par ID
 * @param moduleId - ID du module à charger
 * @returns Promise résolue avec le module
 * @throws AppError si le module n'existe pas
 */
async function loadModule(moduleId: string): Promise<Module> {
  // Implementation
}

// ❌ MAUVAIS - Pas de types, pas de documentation
async function loadModule(id) {
  // Implementation
}
```

### Python

```python
# ✅ BON - Type hints, docstring
def load_module(module_id: str) -> Module:
    """
    Charge un module par ID.
    
    Args:
        module_id: ID du module à charger
        
    Returns:
        Module: Le module chargé
        
    Raises:
        HTTPException: Si le module n'existe pas
    """
    # Implementation

# ❌ MAUVAIS - Pas de types, pas de docstring
def load_module(id):
    # Implementation
```

## 🚨 Gestion des Erreurs

### Frontend

Utiliser le gestionnaire d'erreurs centralisé (`utils/errorHandler.ts`) :

```typescript
import { handleError, handleApiError } from '@/utils/errorHandler'

try {
  const data = await api.get('/endpoint')
} catch (error) {
  // Afficher un message utilisateur approprié
  const userMessage = handleApiError(error, '/endpoint')
  toast.error(userMessage)
}
```

### Backend

```python
import logging

logger = logging.getLogger(__name__)

try:
    # Code
except ValueError as e:
    logger.warning(f"Erreur de validation: {e}")
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    logger.error(f"Erreur inattendue: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Erreur interne du serveur")
```

## 📝 Logging

### Frontend

Utiliser le logger centralisé (`utils/logger.ts`) au lieu de `console.log` :

```typescript
import logger from '@/utils/logger'

// ✅ BON
logger.debug('Chargement des modules', { userId }, 'Modules')
logger.info('Module chargé avec succès', { moduleId }, 'Modules')
logger.warn('Cache expiré', { key }, 'CacheService')
logger.error('Erreur lors du chargement', error, 'Modules')

// ❌ MAUVAIS
console.log('Chargement des modules')
console.error('Erreur:', error)
```

### Backend

```python
import logging

logger = logging.getLogger(__name__)

logger.debug(f"Début du traitement: {data}")
logger.info(f"Opération réussie: {result}")
logger.warning(f"Avertissement: {message}")
logger.error(f"Erreur: {error}", exc_info=True)
```

## 🧪 Tests

### Frontend

```bash
# Tests unitaires
npm run test

# Tests avec couverture
npm run test:coverage
```

### Backend

```bash
# Tests unitaires
pytest backend/tests/

# Tests avec couverture
pytest --cov=backend/app backend/tests/
```

## ⚡ Performance

### Frontend

1. **Code Splitting** - Utiliser `lazy()` pour les pages
2. **Memoization** - Utiliser `React.memo`, `useMemo`, `useCallback`
3. **Caching** - Utiliser React Query avec `staleTime` approprié
4. **Images** - Utiliser `LazyImage` pour le lazy loading

### Backend

1. **Caching** - Utiliser Redis pour le cache
2. **Database Indexing** - Indexer les champs fréquemment utilisés
3. **Query Optimization** - Éviter les N+1 queries
4. **Async Tasks** - Utiliser Celery pour les tâches longues

## 🔒 Sécurité

1. **Authentication** - JWT avec refresh tokens
2. **Authorization** - Vérifier les permissions à chaque endpoint
3. **Input Validation** - Valider toutes les entrées utilisateur
4. **SQL Injection** - Utiliser des requêtes paramétrées
5. **XSS** - Échapper les entrées utilisateur
6. **CSRF** - Tokens CSRF pour les modifications
7. **Rate Limiting** - Limiter les requêtes par IP

## 📚 Documentation

### JSDoc (Frontend)

```typescript
/**
 * Description courte
 * 
 * Description longue si nécessaire
 * 
 * @param param1 - Description du paramètre 1
 * @param param2 - Description du paramètre 2
 * @returns Description de la valeur de retour
 * @throws AppError si une condition n'est pas remplie
 * @example
 * ```typescript
 * const result = myFunction('param1', 42)
 * ```
 */
```

### Docstring (Backend)

```python
def my_function(param1: str, param2: int) -> Result:
    """
    Description courte.
    
    Description longue si nécessaire.
    
    Args:
        param1: Description du paramètre 1
        param2: Description du paramètre 2
        
    Returns:
        Result: Description de la valeur de retour
        
    Raises:
        ValueError: Si une condition n'est pas remplie
        
    Example:
        >>> result = my_function('param1', 42)
        >>> print(result)
    """
```

## ✅ Checklist Avant Commit

- [ ] Code formaté (Prettier/Black)
- [ ] Pas d'erreurs TypeScript/Python
- [ ] Tous les `console.log` remplacés par `logger`
- [ ] JSDoc/Docstrings ajoutés aux nouvelles fonctions
- [ ] Types explicites pour toutes les fonctions
- [ ] Gestion d'erreurs appropriée
- [ ] Tests passent (si disponibles)
- [ ] Code review effectué
- [ ] Pas de code dupliqué
- [ ] Performance vérifiée (si applicable)

## 🔍 Outils Recommandés

### Frontend
- **ESLint** - Linting
- **Prettier** - Formatage
- **TypeScript** - Type checking
- **React DevTools** - Debugging

### Backend
- **flake8** - Linting
- **Black** - Formatage
- **mypy** - Type checking (optionnel)
- **pytest** - Tests

## 📖 Ressources

- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Best Practices](https://react.dev/learn)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
