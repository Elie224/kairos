# 🔍 Diagnostic Problème de Connexion

## ❌ Symptômes

- Le build s'est bien passé ✅
- Les redirects sont configurés ✅
- Mais "la connexion à l'application échoue" ❌

## 🔍 Points à Vérifier

### 1. Console du Navigateur (F12)

Ouvrez la console du navigateur (F12) et vérifiez :

1. **Erreurs CORS** :
   ```
   Access to XMLHttpRequest at '...' from origin '...' has been blocked by CORS policy
   ```
   → Le backend doit autoriser le frontend dans CORS

2. **Erreurs 404 sur l'API** :
   ```
   GET https://kairos-0aoy.onrender.com/api/... 404 (Not Found)
   ```
   → Vérifier que l'URL de l'API est correcte

3. **Erreurs 401 (Non autorisé)** :
   ```
   GET https://kairos-0aoy.onrender.com/api/... 401 (Unauthorized)
   ```
   → Normal si vous n'êtes pas connecté

4. **Erreurs de réseau** :
   ```
   Failed to fetch
   Network Error
   ```
   → Le backend n'est pas accessible ou est en cours de démarrage

### 2. Vérifier l'URL de l'API

Dans Render Dashboard > Service `kairos-frontend` > Environment Variables :

- **VITE_API_URL** doit être : `https://kairos-0aoy.onrender.com/api`
- ⚠️ **IMPORTANT** : Avec `/api` à la fin

### 3. Vérifier que le Backend est Actif

1. Allez sur : https://kairos-0aoy.onrender.com/health
2. Vous devriez voir : `{"status":"healthy",...}`
3. Si vous voyez une erreur, le backend n'est pas démarré

### 4. Vérifier les Logs du Backend

Dans Render Dashboard > Service `kairos-backend` > Logs :

- Vérifiez qu'il n'y a pas d'erreurs de démarrage
- Vérifiez que MongoDB est connecté
- Vérifiez les erreurs CORS

### 5. Tester la Connexion Directement

Ouvrez la console du navigateur (F12) et tapez :

```javascript
fetch('https://kairos-0aoy.onrender.com/api/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

Si cela fonctionne, l'API est accessible.
Si cela échoue, il y a un problème réseau ou CORS.

## ✅ Solutions Possibles

### Solution 1 : Vérifier CORS dans le Backend

Le backend doit autoriser le frontend. Vérifiez dans `backend/main.py` :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kairos-frontend-hjg9.onrender.com",
        "http://localhost:5173",  # Pour le dev local
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Solution 2 : Vérifier l'URL de l'API

Dans Render Dashboard > `kairos-frontend` > Environment Variables :

- **VITE_API_URL** = `https://kairos-0aoy.onrender.com/api`

### Solution 3 : Vérifier que le Backend est Démarré

Le backend peut être en "sleep mode" sur Render (gratuit). Attendez 30-60 secondes après la première requête.

## 📋 Checklist

- [ ] Console du navigateur ouverte (F12)
- [ ] Erreurs identifiées dans la console
- [ ] URL de l'API vérifiée dans Render
- [ ] Backend accessible via `/health`
- [ ] CORS configuré correctement
- [ ] Backend démarré (pas en sleep mode)
