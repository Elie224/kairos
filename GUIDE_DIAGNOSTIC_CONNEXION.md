# 🔍 Guide de Diagnostic - Problème de Connexion

## ✅ Ce qui fonctionne

- Build réussi ✅
- Redirects configurés ✅
- Site déployé ✅

## ❌ Problème : "La connexion à l'application échoue"

## 🔍 Étapes de Diagnostic

### 1. Ouvrir la Console du Navigateur (F12)

**Ouvrez la console** (F12 → onglet "Console") et cherchez les erreurs :

#### Erreur Type 1 : CORS
```
Access to XMLHttpRequest at 'https://kairos-0aoy.onrender.com/api/...' 
from origin 'https://kairos-frontend-hjg9.onrender.com' 
has been blocked by CORS policy
```
**Solution** : Vérifier que le backend autorise le frontend dans CORS

#### Erreur Type 2 : Backend non accessible
```
Failed to fetch
Network Error
GET https://kairos-0aoy.onrender.com/api/... net::ERR_FAILED
```
**Solution** : Le backend est peut-être en "sleep mode" (gratuit). Attendez 30-60 secondes.

#### Erreur Type 3 : 404 sur l'API
```
GET https://kairos-0aoy.onrender.com/api/... 404 (Not Found)
```
**Solution** : Vérifier que l'URL de l'API est correcte

#### Erreur Type 4 : 503 Service Unavailable
```
GET https://kairos-0aoy.onrender.com/api/... 503 (Service Unavailable)
```
**Solution** : Le backend est en cours de démarrage. Attendez 1-2 minutes.

### 2. Tester le Backend Directement

Ouvrez dans votre navigateur :
```
https://kairos-0aoy.onrender.com/health
```

**Résultat attendu** :
```json
{"status":"healthy","timestamp":"...","services":{...}}
```

**Si erreur** :
- Le backend n'est pas démarré
- Le backend est en sleep mode (attendre 30-60 secondes)
- Vérifier les logs du backend dans Render Dashboard

### 3. Vérifier l'URL de l'API

Dans **Render Dashboard** > Service `kairos-frontend` > **Environment Variables** :

Vérifiez que **VITE_API_URL** est défini :
```
VITE_API_URL = https://kairos-0aoy.onrender.com/api
```

⚠️ **IMPORTANT** : Avec `/api` à la fin !

### 4. Vérifier les Logs du Backend

Dans **Render Dashboard** > Service `kairos-backend` > **Logs** :

Cherchez :
- ✅ `Application startup complete`
- ✅ `Connexion MongoDB réussie`
- ❌ Erreurs de démarrage
- ❌ Erreurs CORS

### 5. Tester la Connexion depuis la Console

Ouvrez la console du navigateur (F12) et tapez :

```javascript
// Test 1 : Health check
fetch('https://kairos-0aoy.onrender.com/api/health')
  .then(r => r.json())
  .then(data => {
    console.log('✅ Backend accessible:', data)
  })
  .catch(err => {
    console.error('❌ Erreur backend:', err)
  })

// Test 2 : Test de login (sans credentials)
fetch('https://kairos-0aoy.onrender.com/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=test&password=test'
})
  .then(r => r.json())
  .then(data => {
    console.log('✅ API login accessible:', data)
  })
  .catch(err => {
    console.error('❌ Erreur API login:', err)
  })
```

## 🛠️ Solutions selon l'Erreur

### Solution 1 : Backend en Sleep Mode (Gratuit)

Sur Render gratuit, le backend se met en veille après 15 minutes d'inactivité.

**Solution** :
1. Attendez 30-60 secondes après la première requête
2. Le backend va se réveiller automatiquement
3. Réessayez la connexion

### Solution 2 : Erreur CORS

Si vous voyez une erreur CORS, vérifiez dans `backend/main.py` que le frontend est autorisé :

```python
allowed_origins = [
    "https://kairos-frontend-hjg9.onrender.com",
    # ...
]
```

### Solution 3 : URL de l'API Incorrecte

Vérifiez dans Render Dashboard que `VITE_API_URL` est correct :
- ✅ `https://kairos-0aoy.onrender.com/api`
- ❌ `https://kairos-0aoy.onrender.com` (sans /api)
- ❌ `http://kairos-0aoy.onrender.com/api` (http au lieu de https)

### Solution 4 : Backend Non Démarré

Si le backend ne répond pas :
1. Allez dans Render Dashboard > `kairos-backend`
2. Vérifiez l'état : doit être "Live" (pas "Sleep")
3. Si "Sleep", cliquez sur "Manual Deploy" pour le réveiller
4. Vérifiez les logs pour les erreurs

## 📋 Checklist Rapide

- [ ] Console du navigateur ouverte (F12)
- [ ] Erreurs identifiées dans la console
- [ ] Backend accessible via `/health`
- [ ] `VITE_API_URL` correct dans Render
- [ ] Backend démarré (pas en sleep)
- [ ] CORS configuré correctement

## 🆘 Si Rien ne Fonctionne

1. **Vérifiez les logs du backend** dans Render Dashboard
2. **Vérifiez les logs du frontend** dans Render Dashboard
3. **Testez le backend directement** : `https://kairos-0aoy.onrender.com/health`
4. **Vérifiez les variables d'environnement** dans Render Dashboard
