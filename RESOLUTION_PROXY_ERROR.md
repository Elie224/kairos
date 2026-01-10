# 🔧 Résolution Erreur Proxy Vite - ECONNREFUSED

## Problème identifié

```
[vite] http proxy error: /api/auth/login
AggregateError [ECONNREFUSED]
```

**Cause** : Le backend n'est pas démarré ou n'est pas accessible sur `http://localhost:8000`

## Solution

### Étape 1 : Démarrer le Backend

Le frontend Vite essaie de faire un proxy vers le backend sur le port 8000, mais le backend n'est pas démarré.

**Démarrer le backend** :

```bash
# Option 1 : Script automatique
demarrer-backend.bat

# Option 2 : Manuel
cd backend
venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Étape 2 : Vérifier que le backend est accessible

Une fois le backend démarré, vous devriez voir :
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Étape 3 : Tester la connexion

Ouvrir dans le navigateur :
- **Backend API** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health

### Étape 4 : Réessayer la connexion

Une fois le backend démarré, retourner sur http://localhost:3000/login et réessayer de vous connecter.

## Vérification rapide

Pour vérifier si le backend tourne :

```bash
# Windows PowerShell
netstat -an | findstr ":8000"

# Si vous voyez une ligne avec LISTENING, le backend tourne
```

## Configuration du proxy Vite

Le proxy est configuré dans `frontend/vite.config.ts` :

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
}
```

Cela signifie que toutes les requêtes vers `/api/*` sont automatiquement redirigées vers `http://localhost:8000/api/*`.

## Ordre de démarrage recommandé

1. **MongoDB** (si Docker) :
   ```bash
   demarrer-mongodb.bat
   ```

2. **Backend** :
   ```bash
   demarrer-backend.bat
   ```

3. **Frontend** :
   ```bash
   cd frontend
   npm run dev
   ```

## Dépannage

### Le backend démarre mais l'erreur persiste

1. Vérifier que le backend écoute bien sur le port 8000
2. Vérifier qu'aucun firewall ne bloque le port 8000
3. Vérifier les logs du backend pour des erreurs

### Le backend ne démarre pas

1. Vérifier que Python est installé : `python --version`
2. Vérifier que les dépendances sont installées : `pip install -r requirements.txt`
3. Vérifier que MongoDB est démarré
4. Vérifier les logs d'erreur dans la console

---

*Une fois le backend démarré, l'erreur ECONNREFUSED devrait disparaître.*



