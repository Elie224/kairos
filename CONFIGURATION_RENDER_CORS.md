# 🔧 Configuration CORS sur Render - Guide Rapide

## ✅ Solution Automatique

Le code **autorise automatiquement** les domaines Render en production si :
- ✅ `ALLOWED_HOSTS=*` est configuré (déjà dans `.render.yaml`)
- ✅ `ENVIRONMENT=production` est configuré (déjà dans `.render.yaml`)

**Donc CORS devrait fonctionner automatiquement sans configuration supplémentaire !**

## 📋 Variables d'Environnement sur Render

### Backend (`kairos-backend` ou `kairos-0aoy`)

#### Variables OBLIGATOIRES (déjà configurées dans `.render.yaml`) :
- ✅ `ALLOWED_HOSTS` = `*`
- ✅ `ENVIRONMENT` = `production`

#### Variables OPTIONNELLES mais recommandées :
- ⚠️ `FRONTEND_URL` = `https://kairos-frontend-hjg9.onrender.com`

**Pour ajouter `FRONTEND_URL` sur Render** :
1. Allez sur https://dashboard.render.com
2. Cliquez sur votre service backend (`kairos-backend` ou `kairos-0aoy`)
3. Allez dans l'onglet "Environment"
4. Cliquez sur "Add Environment Variable"
5. Key : `FRONTEND_URL`
6. Value : `https://kairos-frontend-hjg9.onrender.com` (remplacez par votre URL frontend réelle)
7. Cliquez sur "Save Changes"
8. Le service redémarre automatiquement

### Frontend (`kairos-frontend-hjg9`)

#### Variable OBLIGATOIRE :
- ⚠️ `VITE_API_URL` = `https://kairos-0aoy.onrender.com` (remplacez par votre URL backend réelle)

**Pour ajouter `VITE_API_URL` sur Render** :
1. Allez sur https://dashboard.render.com
2. Cliquez sur votre service frontend (`kairos-frontend-hjg9`)
3. Allez dans l'onglet "Environment"
4. Cliquez sur "Add Environment Variable"
5. Key : `VITE_API_URL`
6. Value : `https://kairos-0aoy.onrender.com` (remplacez par votre URL backend réelle)
7. Cliquez sur "Save Changes"
8. Le service redémarre automatiquement

## 🔍 Vérification

### 1. Vérifier que CORS est configuré

**Dans les logs du backend** (Render Dashboard → Service Backend → Logs) :
```
🌐 ALLOWED_HOSTS=* détecté : Autorisation de tous les domaines Render
🌐 CORS autorisé pour les origines en production (4 origines): ['https://kairos-frontend-hjg9.onrender.com', ...]
```

### 2. Tester depuis le navigateur

Ouvrez la console du navigateur (F12) et testez :
```javascript
// Devrait fonctionner sans erreur CORS
fetch('https://kairos-0aoy.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

### 3. Vérifier que les variables sont bien configurées

**Dans Render Dashboard** :
- Service Backend → Environment → Vérifiez que `ALLOWED_HOSTS=*` est présent
- Service Frontend → Environment → Vérifiez que `VITE_API_URL` est présent avec l'URL du backend

## 🚨 Problème Persistant ?

Si CORS ne fonctionne toujours pas après le redéploiement :

1. **Vérifier les logs du backend** pour voir quelles origines sont autorisées
2. **Vérifier l'URL exacte du frontend** dans la console du navigateur (elle doit correspondre à une origine autorisée)
3. **Vider le cache du navigateur** (Ctrl+Shift+R ou Cmd+Shift+R)
4. **Tester avec un navigateur en navigation privée** pour éviter les problèmes de cache

## ✅ Résumé

- ✅ CORS fonctionne **automatiquement** avec `ALLOWED_HOSTS=*` et `ENVIRONMENT=production`
- ✅ Pas besoin de configurer `FRONTEND_URL` (mais c'est recommandé)
- ⚠️ **OBLIGATOIRE** : Configurer `VITE_API_URL` sur le frontend avec l'URL du backend
