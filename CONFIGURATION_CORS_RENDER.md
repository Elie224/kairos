# 🔧 Configuration CORS sur Render - Guide Complet

## 🎯 Problème CORS Résolu Automatiquement

Le code détecte **automatiquement** si vous êtes sur Render et autorise les domaines Render **sans configuration supplémentaire**.

## ✅ Configuration Automatique

Le backend détecte automatiquement :
- ✅ Si vous êtes sur Render (via variable `RENDER=true` ou `RENDER_EXTERNAL_HOSTNAME`)
- ✅ Si `ALLOWED_HOSTS=*` est configuré
- ✅ Autorise automatiquement tous les domaines `*.onrender.com`

**Donc vous n'avez PAS besoin de configurer `FRONTEND_URL` pour que CORS fonctionne !**

## 📝 Variables d'Environnement Recommandées (Optionnel)

Si vous voulez être plus précis, vous pouvez configurer sur Render :

### Backend (`kairos-backend` ou `kairos-0aoy`)

1. **FRONTEND_URL** (Optionnel mais recommandé)
   ```
   https://kairos-frontend-hjg9.onrender.com
   ```
   *Note: Remplacez par votre URL frontend réelle*

2. **ALLOWED_HOSTS** (Déjà configuré dans `.render.yaml`)
   ```
   *
   ```

3. **ENVIRONMENT** (Déjà configuré dans `.render.yaml`)
   ```
   production
   ```

### Frontend (`kairos-frontend-hjg9`)

1. **VITE_API_URL** (OBLIGATOIRE pour que le frontend sache où appeler l'API)
   ```
   https://kairos-0aoy.onrender.com
   ```
   *Note: Remplacez par votre URL backend réelle*

## 🔍 Vérification

### 1. Vérifier que CORS est configuré

Dans les logs du backend sur Render, vous devriez voir :
```
🌐 Détection Render : Autorisation automatique des domaines *.onrender.com
🌐 CORS autorisé pour les origines en production: ['https://kairos-frontend-hjg9.onrender.com', ...]
```

### 2. Tester depuis le navigateur

Ouvrez la console du navigateur (F12) et vérifiez qu'il n'y a plus d'erreur CORS :
```javascript
// Devrait fonctionner sans erreur CORS
fetch('https://kairos-0aoy.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
```

## 🚨 Si CORS ne fonctionne toujours pas

1. **Vérifier les logs du backend** :
   - Connectez-vous à Render Dashboard : https://dashboard.render.com
   - Allez dans votre service backend (`kairos-backend` ou `kairos-0aoy`)
   - Cliquez sur "Logs"
   - Cherchez la ligne `🌐 CORS autorisé pour les origines...`
   - Vérifiez que `https://kairos-frontend-hjg9.onrender.com` est dans la liste

2. **Vérifier les variables d'environnement sur Render** :
   
   **Dans Render Dashboard → Service Backend → Environment** :
   - ✅ `ALLOWED_HOSTS` = `*` (déjà configuré dans `.render.yaml`)
   - ✅ `ENVIRONMENT` = `production` (déjà configuré dans `.render.yaml`)
   - ⚠️ `FRONTEND_URL` = `https://kairos-frontend-hjg9.onrender.com` (optionnel mais recommandé)
   
   **Pour ajouter `FRONTEND_URL`** :
   1. Allez dans Render Dashboard
   2. Service backend → "Environment"
   3. Cliquez sur "Add Environment Variable"
   4. Key : `FRONTEND_URL`
   5. Value : `https://kairos-frontend-hjg9.onrender.com` (remplacez par votre URL frontend réelle)
   6. Cliquez sur "Save Changes"
   7. Le service redémarrera automatiquement

3. **Redémarrer le backend** :
   - Allez dans Render Dashboard
   - Service backend → "Manual Deploy" → "Deploy latest commit"
   - OU simplement "Save Changes" dans Environment pour redémarrer automatiquement

4. **Vérifier l'URL du frontend** :
   - L'URL dans la console du navigateur doit correspondre à une des origines autorisées
   - Exemple : Si votre frontend est sur `https://kairos-frontend-hjg9.onrender.com`, cette URL doit être dans la liste des origines CORS

5. **Vérifier que VITE_API_URL est configuré sur le frontend** :
   
   **Dans Render Dashboard → Service Frontend → Environment** :
   - ⚠️ `VITE_API_URL` = `https://kairos-0aoy.onrender.com` (OBLIGATOIRE)
   - Remplacez par votre URL backend réelle
   
   **Pour ajouter `VITE_API_URL`** :
   1. Allez dans Render Dashboard
   2. Service frontend → "Environment"
   3. Cliquez sur "Add Environment Variable"
   4. Key : `VITE_API_URL`
   5. Value : `https://kairos-0aoy.onrender.com` (remplacez par votre URL backend réelle)
   6. Cliquez sur "Save Changes"
   7. Le service redémarrera automatiquement

## 📚 Documentation Render

- [Variables d'environnement Render](https://render.com/docs/environment-variables)
- [Static Sites sur Render](https://render.com/docs/static-sites)
- [Web Services sur Render](https://render.com/docs/web-services)

## ✅ Résumé

- ✅ CORS fonctionne automatiquement sur Render
- ✅ Pas besoin de configurer `FRONTEND_URL` (mais c'est recommandé)
- ✅ Le code détecte automatiquement Render
- ✅ Tous les domaines `*.onrender.com` sont autorisés

**Action requise** : Configurez seulement `VITE_API_URL` sur le frontend avec l'URL de votre backend.
