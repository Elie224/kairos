# 🔧 Corriger VITE_API_URL sur le Frontend Render - Guide Urgent

## 🚨 Problème Actuel

Le frontend essaie d'appeler `https://kairos-backend.onrender.com` au lieu de `https://kairos-0aoy.onrender.com`.

**Erreur** :
```
Access to XMLHttpRequest at 'https://kairos-backend.onrender.com/auth/login' 
from origin 'https://kairos-frontend-hjg9.onrender.com' 
has been blocked by CORS policy
```

## ✅ Solution : Configurer VITE_API_URL et Redéployer

### ⚠️ IMPORTANT : Les Variables VITE_* doivent être définies AVANT le Build

Les variables `VITE_*` sont **injectées au moment du build** par Vite. Si vous ajoutez/modifiez `VITE_API_URL` après le build, **il faut redéclencher un nouveau build** pour que la variable soit prise en compte.

### Étape 1 : Ajouter VITE_API_URL sur Render Dashboard

1. **Allez sur Render Dashboard** : https://dashboard.render.com
2. **Cliquez sur votre service frontend** : `kairos-frontend-hjg9` (ou le nom de votre service frontend)
3. **Allez dans l'onglet "Environment"** (Variables d'environnement)
4. **Cliquez sur "Add Environment Variable"** :
   - **Key** : `VITE_API_URL`
   - **Value** : `https://kairos-0aoy.onrender.com`
   - ⚠️ **IMPORTANT** : Pas de slash `/` à la fin !
   - ✅ **IMPORTANT** : Pas de `https://` si vous utilisez déjà `https://` dans la value (mais ici c'est bon car c'est une URL complète)
5. **Cliquez sur "Save Changes"**

### Étape 2 : Redéployer le Frontend (OBLIGATOIRE)

Après avoir ajouté `VITE_API_URL`, vous **DEVEZ** redéployer le frontend pour que Vite utilise cette variable dans le build.

#### Option A : Déploiement Automatique (si activé)

Si Auto-Deploy est activé sur Render, il devrait redéployer automatiquement après avoir sauvegardé la variable. **Vérifiez dans les logs** qu'un nouveau build est déclenché.

#### Option B : Déploiement Manuel

1. **Dans Render Dashboard → Service Frontend** :
   - Cliquez sur **"Manual Deploy"** (Déploiement manuel)
   - Sélectionnez **"Deploy latest commit"** (Déployer le dernier commit)
   - Cliquez sur **"Deploy"**

2. **Attendez que le build se termine** (quelques minutes)

### Étape 3 : Vérifier que VITE_API_URL est Bien Utilisée

#### Méthode 1 : Vérifier dans les Logs de Build Render

Dans les logs de build du frontend, vous ne verrez pas directement `VITE_API_URL`, mais vous pouvez vérifier que le build s'est bien passé.

#### Méthode 2 : Vérifier dans le Code Compilé (Console Navigateur)

1. **Ouvrez votre frontend** : `https://kairos-frontend-hjg9.onrender.com`
2. **Ouvrez la console du navigateur** (F12)
3. **Allez dans l'onglet "Network"** (Réseau)
4. **Essayez de vous connecter**
5. **Vérifiez la requête** : Elle doit aller vers `https://kairos-0aoy.onrender.com/auth/login`
   - ✅ Si elle va vers `https://kairos-0aoy.onrender.com` → **C'est bon !**
   - ❌ Si elle va vers `https://kairos-backend.onrender.com` → Le build n'a pas pris en compte `VITE_API_URL`

#### Méthode 3 : Vérifier dans le Code Source (Inspection)

1. **Ouvrez votre frontend** : `https://kairos-frontend-hjg9.onrender.com`
2. **Ouvrez les outils de développement** (F12)
3. **Allez dans l'onglet "Sources"** (Sources) ou "Network"
4. **Cherchez un fichier JavaScript** (ex: `index-*.js`)
5. **Cherchez** : `kairos-backend.onrender.com` ou `kairos-0aoy.onrender.com`
   - ✅ Si vous trouvez `kairos-0aoy.onrender.com` → **C'est bon !**
   - ❌ Si vous trouvez `kairos-backend.onrender.com` → Le build n'a pas pris en compte `VITE_API_URL`

### Étape 4 : Vider le Cache du Navigateur

Même après le redéploiement, votre navigateur peut avoir mis en cache l'ancien build. **Videz le cache** :

1. **Chrome/Edge** : `Ctrl + Shift + R` (Windows) ou `Cmd + Shift + R` (Mac)
2. **OU** Ouvrez en navigation privée : `Ctrl + Shift + N` (Windows) ou `Cmd + Shift + N` (Mac)

### Étape 5 : Tester la Connexion

1. **Ouvrez votre frontend** : `https://kairos-frontend-hjg9.onrender.com`
2. **Ouvrez la console du navigateur** (F12)
3. **Essayez de vous connecter**
4. **Vérifiez les requêtes dans l'onglet "Network"** :
   - ✅ Doit être : `https://kairos-0aoy.onrender.com/auth/login`
   - ✅ Ne doit PAS avoir d'erreur CORS
   - ✅ Status doit être `200` ou `401` (pas `404` ou `CORS error`)

## 🚨 Si ça Ne Fonctionne Toujours Pas

### Vérifier que la Variable est Bien Configurée

1. **Dans Render Dashboard → Service Frontend → Environment** :
   - Vérifiez que `VITE_API_URL` est présente
   - Vérifiez que la valeur est exactement : `https://kairos-0aoy.onrender.com` (sans slash final)
   - Si elle n'est pas là ou mal configurée, **ajoutez-la/modifiez-la**

### Vérifier que le Build a Utilisé la Variable

1. **Dans Render Dashboard → Service Frontend → Logs** :
   - Vérifiez qu'un **nouveau build** a été déclenché après avoir ajouté la variable
   - Cherchez dans les logs : `Building...` ou `npm run build`

### Vérifier dans le Code Frontend

Le code frontend utilise `import.meta.env.VITE_API_URL`. Si cette variable n'est pas définie au moment du build, le code utilise `/api` comme fallback, ce qui ne fonctionne pas en production sur un Static Site.

### Forcer un Nouveau Build

Si le build ne s'est pas déclenché automatiquement :

1. **Dans Render Dashboard → Service Frontend** :
   - Cliquez sur **"Manual Deploy"**
   - Sélectionnez **"Deploy latest commit"**
   - Cliquez sur **"Deploy"**
   - **Attendez que le build se termine**

### Alternative : Modifier Temporairement le Code (Pas Recommandé)

Si `VITE_API_URL` ne fonctionne pas, vous pouvez temporairement modifier le code pour forcer l'URL :

```typescript
// frontend/src/services/api.ts
const getBaseURL = () => {
  // Forcer l'URL en production (TEMPORAIRE - À ENLEVER APRÈS)
  if (import.meta.env.PROD) {
    return 'https://kairos-0aoy.onrender.com'
  }
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  return '/api'
}
```

**⚠️ Cette solution est temporaire**. Il faut absolument configurer `VITE_API_URL` correctement sur Render.

## 📋 Checklist Complète

### Frontend (`kairos-frontend-hjg9`) ✅
- [ ] `VITE_API_URL` = `https://kairos-0aoy.onrender.com` (sans slash final) - **AJOUTÉE**
- [ ] **Nouveau build déclenché** après avoir ajouté la variable - **VÉRIFIÉ**
- [ ] Cache du navigateur vidé - **FAIT**
- [ ] Test de connexion : Requête vers `https://kairos-0aoy.onrender.com` - **TESTÉ**

### Backend (`kairos-0aoy`) ✅
- [ ] `ALLOWED_HOSTS` = `*` - **AJOUTÉE**
- [ ] `ENVIRONMENT` = `production` - **AJOUTÉE**
- [ ] `FRONTEND_URL` = `https://kairos-frontend-hjg9.onrender.com` - **AJOUTÉE**
- [ ] CORS autorisé pour les origines Render - **VÉRIFIÉ DANS LES LOGS**

## ✅ Résumé

1. ✅ **Ajoutez** `VITE_API_URL` = `https://kairos-0aoy.onrender.com` sur le frontend Render
2. ✅ **Redéployez** le frontend (build obligatoire pour que Vite utilise la variable)
3. ✅ **Videz le cache** du navigateur
4. ✅ **Testez** la connexion

Une fois ces étapes suivies, le frontend devrait appeler le bon backend et CORS devrait fonctionner ! 🎉
