# 🔧 Correction URLs Backend et Frontend sur Render

## 🚨 Problème Identifié

### Erreur dans les logs frontend :
```
Access to XMLHttpRequest at 'https://kairos-backend.onrender.com/auth/login' 
from origin 'https://kairos-frontend-hjg9.onrender.com' 
has been blocked by CORS policy
```

### Problèmes :
1. ❌ Le frontend appelle `https://kairos-backend.onrender.com` (mauvais backend)
2. ✅ Le backend réel est sur `https://kairos-0aoy.onrender.com`
3. ⚠️ Le backend a `FRONTEND_URL=https://kairos-frontend.onrender.com` au lieu de `https://kairos-frontend-hjg9.onrender.com`

## ✅ Solution : Configuration sur Render Dashboard

### Étape 1 : Configurer VITE_API_URL sur le Frontend

1. **Allez sur Render Dashboard** : https://dashboard.render.com
2. **Accédez au service frontend** : Cliquez sur `kairos-frontend-hjg9` (ou votre service frontend)
3. **Allez dans l'onglet "Environment"** (Variables d'environnement)
4. **Ajoutez ou modifiez la variable** :
   - **Key** : `VITE_API_URL`
   - **Value** : `https://kairos-0aoy.onrender.com`
   - ✅ **Important** : Pas de slash `/` à la fin !
5. **Cliquez sur "Save Changes"**
6. **Le service redémarre automatiquement** (nouveau build)

### Étape 2 : Configurer FRONTEND_URL sur le Backend

1. **Allez sur Render Dashboard** : https://dashboard.render.com
2. **Accédez au service backend** : Cliquez sur `kairos-0aoy` (ou votre service backend)
3. **Allez dans l'onglet "Environment"**
4. **Modifiez la variable `FRONTEND_URL`** :
   - **Key** : `FRONTEND_URL`
   - **Value** : `https://kairos-frontend-hjg9.onrender.com`
   - ✅ **Important** : Utilisez l'URL **exacte** du frontend (avec le hash)
5. **Cliquez sur "Save Changes"**
6. **Le service redémarre automatiquement**

## 🔍 Vérification

### 1. Vérifier que VITE_API_URL est bien utilisé

Après le redéploiement du frontend, vérifiez dans la console du navigateur que les requêtes vont vers le bon backend :
- ✅ Doit être : `https://kairos-0aoy.onrender.com/auth/login`
- ❌ Ne doit PAS être : `https://kairos-backend.onrender.com/auth/login`

### 2. Vérifier les logs du backend

Dans les logs Render du backend, vous devriez voir :
```
✅ FRONTEND_URL configuré: https://kairos-frontend-hjg9.onrender.com
🌐 CORS autorisé pour les origines en production (4 origines): [...]
```

### 3. Tester la connexion

1. Ouvrez votre frontend : `https://kairos-frontend-hjg9.onrender.com`
2. Ouvrez la console du navigateur (F12)
3. Essayez de vous connecter
4. ✅ Si ça fonctionne sans erreur CORS, **c'est bon !**

## 📋 Checklist de Configuration

### Frontend (`kairos-frontend-hjg9`) ✅
- [ ] `VITE_API_URL` = `https://kairos-0aoy.onrender.com` (sans slash final)

### Backend (`kairos-0aoy`) ✅
- [ ] `ALLOWED_HOSTS` = `*` (déjà configuré dans `.render.yaml`)
- [ ] `ENVIRONMENT` = `production` (déjà configuré dans `.render.yaml`)
- [ ] `FRONTEND_URL` = `https://kairos-frontend-hjg9.onrender.com` (avec hash, sans slash final)

## 🚨 Notes Importantes

1. **Variables d'environnement Vite** : Les variables `VITE_*` doivent être définies **avant** le build. Si vous les modifiez après le build, vous devez **redéclencher un build** :
   - Render le fait automatiquement quand vous sauvegardez les variables
   - OU allez dans "Manual Deploy" → "Deploy latest commit"

2. **URL sans slash final** : 
   - ✅ Bon : `https://kairos-0aoy.onrender.com`
   - ❌ Mauvais : `https://kairos-0aoy.onrender.com/`

3. **URL exacte avec hash** : Utilisez l'URL exacte du frontend telle qu'elle apparaît dans l'URL de votre navigateur :
   - ✅ Bon : `https://kairos-frontend-hjg9.onrender.com`
   - ❌ Mauvais : `https://kairos-frontend.onrender.com` (sans hash)

## ✅ Résumé

1. ✅ Configurez `VITE_API_URL` sur le frontend avec `https://kairos-0aoy.onrender.com`
2. ✅ Configurez `FRONTEND_URL` sur le backend avec `https://kairos-frontend-hjg9.onrender.com`
3. ✅ Attendez que les services redémarrent
4. ✅ Testez la connexion depuis le frontend

Une fois ces configurations faites, CORS devrait fonctionner parfaitement ! 🎉
