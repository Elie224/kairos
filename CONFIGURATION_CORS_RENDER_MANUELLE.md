# 🔧 Configuration CORS sur Render - Guide Manuel

## ⚠️ IMPORTANT : Configuration Manuel dans Render Dashboard

Si vos services ont été créés **manuellement** sur Render (pas via `.render.yaml`), vous devez configurer les variables d'environnement **manuellement** dans le Dashboard Render.

## 📝 Configuration Backend sur Render

### Étape 1 : Accéder au Dashboard Render

1. Allez sur https://dashboard.render.com
2. Connectez-vous avec votre compte
3. Cliquez sur votre service backend (`kairos-backend` ou `kairos-0aoy`)

### Étape 2 : Configurer les Variables d'Environnement

1. Dans le service backend, cliquez sur l'onglet **"Environment"** (Variables d'environnement)
2. Cliquez sur **"Add Environment Variable"** (Ajouter une variable d'environnement)

#### Variables OBLIGATOIRES à ajouter :

**1. `ALLOWED_HOSTS`**
- Key : `ALLOWED_HOSTS`
- Value : `*`
- Cliquez sur "Save Changes"

**2. `ENVIRONMENT`**
- Key : `ENVIRONMENT`
- Value : `production`
- Cliquez sur "Save Changes"

**3. `FRONTEND_URL`** (Recommandé)
- Key : `FRONTEND_URL`
- Value : `https://kairos-frontend-hjg9.onrender.com` (remplacez par votre URL frontend réelle)
- Cliquez sur "Save Changes"

#### Variables OBLIGATOIRES (Secrets - Ne pas exposer) :

**4. `MONGODB_URL`**
- Key : `MONGODB_URL`
- Value : `mongodb+srv://<username>:<password>@cluster0.u3cxqhm.mongodb.net/kairos?retryWrites=true&w=majority`
  - Remplacez `<username>` par votre nom d'utilisateur MongoDB
  - Remplacez `<password>` par votre mot de passe MongoDB
- ✅ Cochez "Secret" pour masquer la valeur
- Cliquez sur "Save Changes"

**5. `MONGODB_DB_NAME`**
- Key : `MONGODB_DB_NAME`
- Value : `kairos`
- Cliquez sur "Save Changes"

**6. `SECRET_KEY`**
- Key : `SECRET_KEY`
- Value : Générez une clé avec `python -c "import secrets; print(secrets.token_urlsafe(32))"` (ou utilisez une clé existante)
- ✅ Cochez "Secret" pour masquer la valeur
- Cliquez sur "Save Changes"

**7. `OPENAI_API_KEY`**
- Key : `OPENAI_API_KEY`
- Value : Votre clé API OpenAI (commence par `sk-...`)
- ✅ Cochez "Secret" pour masquer la valeur
- Cliquez sur "Save Changes"

**8. `FRONTEND_URL`** (si pas déjà ajouté)
- Key : `FRONTEND_URL`
- Value : `https://kairos-frontend-hjg9.onrender.com` (remplacez par votre URL frontend réelle)
- Cliquez sur "Save Changes"

**9. `REDIS_URL`** (Optionnel)
- Key : `REDIS_URL`
- Value : `redis://...` (si vous utilisez Redis)
- ✅ Cochez "Secret" si c'est une URL sensible
- Cliquez sur "Save Changes"

**10. Variables PostgreSQL** (Optionnel - seulement si vous utilisez PostgreSQL)
- `POSTGRES_HOST`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD` (✅ Secret)
- `POSTGRES_DB`
- `POSTGRES_PORT`

**11. Variables Stripe** (Optionnel - seulement si vous utilisez Stripe)
- `STRIPE_SECRET_KEY` (✅ Secret)
- `STRIPE_WEBHOOK_SECRET` (✅ Secret)
- `STRIPE_PREMIUM_PRICE_ID`
- `STRIPE_ENTERPRISE_PRICE_ID`

### Étape 3 : Redémarrer le Service

Après avoir ajouté toutes les variables :
1. Le service redémarre automatiquement quand vous cliquez sur "Save Changes"
2. OU allez dans "Manual Deploy" → "Deploy latest commit"

### Étape 4 : Vérifier les Logs

1. Allez dans l'onglet **"Logs"** du service backend
2. Cherchez ces lignes :
   ```
   🌐 ALLOWED_HOSTS=* détecté : Autorisation de tous les domaines Render
   🌐 CORS autorisé pour les origines en production (4 origines): ['https://kairos-frontend-hjg9.onrender.com', ...]
   ```
3. Si vous voyez ces lignes, CORS est configuré correctement !

## 📝 Configuration Frontend sur Render

### Étape 1 : Accéder au Service Frontend

1. Allez sur https://dashboard.render.com
2. Cliquez sur votre service frontend (`kairos-frontend-hjg9`)

### Étape 2 : Configurer la Variable d'Environnement

1. Dans le service frontend, cliquez sur l'onglet **"Environment"**
2. Cliquez sur **"Add Environment Variable"**

#### Variable OBLIGATOIRE :

**`VITE_API_URL`**
- Key : `VITE_API_URL`
- Value : `https://kairos-0aoy.onrender.com` (remplacez par votre URL backend réelle)
- Cliquez sur "Save Changes"

### Étape 3 : Redémarrer le Service

1. Le service redémarre automatiquement
2. OU allez dans "Manual Deploy" → "Deploy latest commit"

## ✅ Vérification Finale

### 1. Vérifier CORS depuis le navigateur

1. Ouvrez votre frontend : `https://kairos-frontend-hjg9.onrender.com`
2. Ouvrez la console du navigateur (F12)
3. Testez la connexion :
   ```javascript
   fetch('https://kairos-0aoy.onrender.com/health')
     .then(r => r.json())
     .then(console.log)
     .catch(console.error)
   ```
4. Si vous voyez une réponse JSON sans erreur CORS, **c'est bon !** ✅

### 2. Tester la connexion

1. Allez sur la page de connexion : `https://kairos-frontend-hjg9.onrender.com/login`
2. Essayez de vous connecter
3. Si ça fonctionne, CORS est correctement configuré ! ✅

## 🚨 Problèmes Courants

### Erreur : "Access-Control-Allow-Origin header is missing"

**Solution** :
1. Vérifiez que `ALLOWED_HOSTS=*` est bien configuré dans le backend
2. Vérifiez les logs du backend pour voir les origines autorisées
3. Redémarrez le backend après avoir ajouté les variables

### Erreur : "CORS policy blocked"

**Solution** :
1. Vérifiez que l'URL du frontend dans la console correspond à une origine autorisée
2. Vérifiez que `FRONTEND_URL` est configuré avec l'URL exacte du frontend (avec le hash)
3. Videz le cache du navigateur (Ctrl+Shift+R)

### Le backend ne démarre pas

**Solution** :
1. Vérifiez que toutes les variables obligatoires sont configurées (`MONGODB_URL`, `SECRET_KEY`, `OPENAI_API_KEY`)
2. Vérifiez les logs pour voir les erreurs
3. Assurez-vous que `MONGODB_URL` est correctement formaté

## 📚 Ressources

- [Documentation Render - Variables d'environnement](https://render.com/docs/environment-variables)
- [Documentation Render - Web Services](https://render.com/docs/web-services)
- [Documentation Render - Static Sites](https://render.com/docs/static-sites)

## ✅ Checklist de Configuration

### Backend ✅
- [ ] `ALLOWED_HOSTS` = `*`
- [ ] `ENVIRONMENT` = `production`
- [ ] `FRONTEND_URL` = `https://kairos-frontend-hjg9.onrender.com`
- [ ] `MONGODB_URL` = (connection string MongoDB Atlas)
- [ ] `MONGODB_DB_NAME` = `kairos`
- [ ] `SECRET_KEY` = (clé secrète générée)
- [ ] `OPENAI_API_KEY` = (clé API OpenAI)

### Frontend ✅
- [ ] `VITE_API_URL` = `https://kairos-0aoy.onrender.com`

Une fois toutes ces variables configurées, CORS devrait fonctionner correctement ! 🎉
