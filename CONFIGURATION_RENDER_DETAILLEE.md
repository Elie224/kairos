# 🚀 Configuration Détaillée Render - Service Backend

## ⚠️ IMPORTANT : Configuration Actuelle

Sur votre écran Render, je vois que :
- ✅ Repository : `Elie224 / kairos` (correct)
- ✅ Name : `kairos` (correct)
- ✅ Branch : `main` (correct)
- ❌ **Language : Docker** (à changer en **Python**)
- ✅ Region : Oregon (US West) (ok, mais recommandé : Frankfurt pour la France)

## 📋 ÉTAPE 1 : Corriger la Configuration Backend

### 1.1 Modifier le Language

Sur la page Render, **changez** :

**AVANT (Actuel) :**
- Language : `Docker`

**APRÈS (Correct) :**
- Language : `Python 3`
- Python Version : `3.11` (ou laisser par défaut)

### 1.2 Configurer le Root Directory

Si vous utilisez la configuration manuelle (pas `.render.yaml`) :

- **Root Directory** : `backend`
  - Render cherchera les fichiers Python dans le dossier `backend/`

### 1.3 Configurer les Commandes

**Build Command :**
```bash
pip install -r requirements.txt
```

**Start Command :**
```bash
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

**Important** : Utilisez `$PORT` et non `8000` car Render attribue dynamiquement un port.

### 1.4 Configurer le Health Check

- **Health Check Path** : `/health`

### 1.5 Plan et Region

- **Plan** : `Starter` (gratuit, avec limitations)
- **Region** : `Frankfurt (EU)` (recommandé pour la France) ou garder `Oregon (US West)`

## 📋 ÉTAPE 2 : Configurer les Variables d'Environnement

Cliquez sur **"Advanced"** ou **"Environment"** pour ajouter les variables suivantes :

### Variables OBLIGATOIRES (doivent être configurées)

```bash
# Environnement
ENVIRONMENT=production
PYTHON_VERSION=3.11.0

# MongoDB (OBLIGATOIRE - Utilisez MongoDB Atlas pour la production)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/kairos?retryWrites=true&w=majority
MONGODB_DB_NAME=kairos

# Sécurité (OBLIGATOIRE - Générer une nouvelle clé)
SECRET_KEY=<GÉNÉRER-UNE-NOUVELLE-CLÉ-SECRÈTE>

# OpenAI (OBLIGATOIRE pour les fonctionnalités IA)
OPENAI_API_KEY=sk-proj-VOTRE-CLÉ-API-ICI

# Frontend URL (OBLIGATOIRE - À configurer après déploiement du frontend)
FRONTEND_URL=https://kairos-frontend.onrender.com

# Sécurité supplémentaire
ALLOWED_HOSTS=*
```

### Variables OPTIONNELLES (configurez si nécessaire)

```bash
# Redis (optionnel - pour le cache)
REDIS_URL=redis://...

# PostgreSQL (optionnel)
POSTGRES_HOST=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=...
POSTGRES_PORT=5432

# Stripe (optionnel - pour les paiements)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PREMIUM_PRICE_ID=price_...
STRIPE_ENTERPRISE_PRICE_ID=price_...
```

## 🔑 ÉTAPE 3 : Générer SECRET_KEY

**IMPORTANT** : Générer une nouvelle SECRET_KEY pour la production :

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiez la sortie et utilisez-la pour `SECRET_KEY` dans Render.

**NE JAMAIS** utiliser la même SECRET_KEY qu'en développement !

## 📋 ÉTAPE 4 : Configuration MongoDB Atlas (Recommandé)

Pour la production, utilisez MongoDB Atlas (gratuit jusqu'à 512MB) :

### 4.1 Créer un Cluster MongoDB Atlas

1. Aller sur https://www.mongodb.com/cloud/atlas
2. Créer un compte gratuit
3. Créer un cluster gratuit (M0 - Free)
4. Choisir une région (Frankfurt recommandé)

### 4.2 Créer un Utilisateur de Base de Données

1. Dans MongoDB Atlas : **Security > Database Access**
2. Cliquer sur **"Add New Database User"**
3. Choisir **"Password"** comme méthode d'authentification
4. Créer un nom d'utilisateur et un mot de passe **forts**
5. Rôle : `Atlas Admin` ou `Read and write to any database`
6. Cliquer sur **"Add User"**

### 4.3 Autoriser l'Accès depuis Render

1. Dans MongoDB Atlas : **Security > Network Access**
2. Cliquer sur **"Add IP Address"**
3. Cliquer sur **"Allow Access from Anywhere"** (0.0.0.0/0)
   - ⚠️ **OU** ajouter les IPs spécifiques de Render (voir documentation Render)
4. Cliquer sur **"Confirm"**

### 4.4 Récupérer la Connection String

1. Dans MongoDB Atlas : **Deployments > Clusters**
2. Cliquer sur **"Connect"** sur votre cluster
3. Choisir **"Connect your application"**
4. Driver : **Python**, Version : **3.6 or later**
5. **COPIER** la connection string (format : `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`)
6. **MODIFIER** la connection string :
   - Remplacer `<password>` par votre mot de passe réel
   - Ajouter le nom de la base de données : `...mongodb.net/kairos?retryWrites...`
7. **COPIER** la connection string complète dans `MONGODB_URL` sur Render

**Exemple de connection string complète :**
```
mongodb+srv://kairos_user:MonMotDePasse123!@cluster0.abc123.mongodb.net/kairos?retryWrites=true&w=majority
```

## 📋 ÉTAPE 5 : Finaliser la Configuration

### 5.1 Vérifier la Configuration

Avant de déployer, vérifiez :

- [ ] Language : **Python 3** (pas Docker)
- [ ] Root Directory : `backend` (si configuration manuelle)
- [ ] Build Command : `pip install -r requirements.txt`
- [ ] Start Command : `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
- [ ] Health Check Path : `/health`
- [ ] Toutes les variables d'environnement OBLIGATOIRES configurées

### 5.2 Déployer

1. Cliquer sur **"Create Web Service"** (ou **"Save Changes"** si vous modifiez)
2. Render va automatiquement :
   - Cloner le repository GitHub
   - Installer les dépendances Python
   - Démarrer le service

### 5.3 Vérifier le Déploiement

Une fois le déploiement terminé (5-10 minutes), vérifiez :

1. **Health Check** :
   ```
   https://kairos.onrender.com/health
   ```
   Doit retourner : `{"status": "healthy", ...}`

2. **API Documentation** :
   ```
   https://kairos.onrender.com/docs
   ```
   Doit afficher la documentation Swagger

3. **Logs** :
   - Dans Render Dashboard > Service > Logs
   - Vérifier qu'il n'y a pas d'erreurs
   - Vérifier "Connexion MongoDB réussie"

## 📋 ÉTAPE 6 : Configurer le Frontend (Séparément)

Le frontend doit être configuré comme un **Static Site** séparé :

1. Dans Render Dashboard : **"New +"** > **"Static Site"**
2. Connecter le même repository GitHub : `Elie224 / kairos`
3. Configuration :
   - **Name** : `kairos-frontend`
   - **Root Directory** : `frontend`
   - **Build Command** : `npm ci && npm run build`
   - **Publish Directory** : `dist`
4. Variables d'environnement :
   ```
   VITE_API_URL=https://kairos.onrender.com
   ```
   (Remplacer `kairos` par le nom réel de votre service backend)
5. Cliquer sur **"Create Static Site"**

## 🔄 ÉTAPE 7 : Mettre à Jour FRONTEND_URL

Une fois le frontend déployé :

1. Noter l'URL du frontend : `https://kairos-frontend.onrender.com`
2. Dans le service backend Render :
   - Aller dans **Environment**
   - Modifier `FRONTEND_URL` avec l'URL réelle du frontend
   - Sauvegarder

## ⚠️ IMPORTANT - Configuration Actuelle sur Votre Écran

**Sur votre écran Render, vous devez changer :**

1. **Language** : De `Docker` → `Python 3`
2. **Root Directory** : Ajouter `backend` (si option disponible)
3. **Build Command** : `pip install -r requirements.txt`
4. **Start Command** : `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`

## 📚 Résumé des Commandes Exactes

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

### Health Check Path
```
/health
```

## 🔗 URLs après Déploiement

Une fois déployé, vous aurez :

- **Backend** : `https://kairos.onrender.com`
  - API Docs : `https://kairos.onrender.com/docs`
  - Health : `https://kairos.onrender.com/health`

- **Frontend** : `https://kairos-frontend.onrender.com` (après configuration)

## 🐛 Dépannage

### Erreur : "Module not found"
- Vérifier que `requirements.txt` est dans le dossier `backend/`
- Vérifier que le Root Directory est `backend`

### Erreur : "Port already in use"
- Utiliser `$PORT` dans la commande start, pas `8000`

### Erreur : "MongoDB connection failed"
- Vérifier que l'IP de Render est autorisée dans MongoDB Atlas
- Vérifier que `MONGODB_URL` est correct
- Vérifier les credentials MongoDB

### Erreur : "SECRET_KEY required"
- Vérifier que `SECRET_KEY` est configurée dans les variables d'environnement
- Générer une nouvelle clé (voir ÉTAPE 3)

## ✅ Checklist Finale

- [ ] Language changé de `Docker` à `Python 3`
- [ ] Root Directory : `backend`
- [ ] Build Command configuré
- [ ] Start Command configuré avec `$PORT`
- [ ] Health Check Path : `/health`
- [ ] `ENVIRONMENT=production` configuré
- [ ] `MONGODB_URL` configuré (MongoDB Atlas)
- [ ] `SECRET_KEY` générée et configurée
- [ ] `OPENAI_API_KEY` configurée
- [ ] `FRONTEND_URL` configuré (après déploiement frontend)
- [ ] `ALLOWED_HOSTS=*` configuré

## 📞 Besoin d'Aide ?

Consultez :
- `DEPLOIEMENT_RENDER.md` : Guide complet
- `DEPLOIEMENT_CHECKLIST.md` : Checklist complète
- Render Documentation : https://render.com/docs
