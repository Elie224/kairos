# 🚀 Configuration Render - Guide Étape par Étape

## 📸 Basé sur Votre Écran Render Actuel

Sur votre écran, je vois que vous êtes sur la page "New Web Service". Voici les actions exactes à faire.

## ⚠️ CORRECTION URGENTE - Language

**Sur votre écran Render, vous devez changer :**

### Avant (Actuel) :
```
Language: Docker ▼
```

### Après (Correct) :
```
Language: Python 3 ▼
```

**Action :**
1. Cliquez sur le dropdown **"Language"**
2. Sélectionnez **"Python 3"** (pas Docker)
3. Si un sous-menu apparaît, sélectionnez **Python 3.11** ou la dernière version

## 📋 Configuration Complète

### ÉTAPE 1 : Language et Configuration de Base

Sur la page "New Web Service", configurez :

**1. Source Code :** ✅ Déjà correct (`Elie224 / kairos`)

**2. Name :** ✅ Déjà correct (`kairos`)

**3. Language :** ❌ **À CHANGER**
- Cliquez sur le dropdown "Language"
- Sélectionnez **"Python 3"** (pas Docker)
- Version : **3.11** (ou laissez par défaut)

**4. Branch :** ✅ Déjà correct (`main`)

**5. Region :** ✅ OK (`Oregon (US West)`)
   - ⚠️ **Optionnel** : Changez pour `Frankfurt (EU)` si vous voulez être plus proche de la France

**6. Root Directory :** 📝 **À AJOUTER**
   - Cherchez cette option (peut-être dans "Advanced")
   - Entrez : `backend`
   - ⚠️ Si l'option n'existe pas, ne vous inquiétez pas, Render détectera automatiquement

### ÉTAPE 2 : Build et Start Commands

Cherchez les sections **"Build Command"** et **"Start Command"**.

Ces options peuvent être :
- Directement visibles sur la page
- Dans une section "Advanced" (cliquez sur "Show Advanced Options")
- Configurables après la création du service

**Build Command :**
```bash
pip install -r requirements.txt
```

**Start Command :**
```bash
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

**⚠️ IMPORTANT :**
- Utilisez `$PORT` et non `8000`
- Render attribue dynamiquement un port à chaque service

**Health Check Path :**
```
/health
```

### ÉTAPE 3 : Variables d'Environnement (OBLIGATOIRE)

Cherchez la section **"Environment Variables"** ou **"Environment"**.

Cette section peut être :
- Un bouton **"Add Environment Variable"** sur la page principale
- Dans une section **"Advanced"** ou **"Environment"**
- Configurable après la création du service (dans les settings)

**Ajoutez ces variables OBLIGATOIRES :**

#### Variable 1 : ENVIRONMENT
```
Key: ENVIRONMENT
Value: production
```

#### Variable 2 : MONGODB_URL
```
Key: MONGODB_URL
Value: mongodb+srv://username:password@cluster.mongodb.net/kairos?retryWrites=true&w=majority
```
⚠️ **IMPORTANT** : Remplacez `username`, `password`, et `cluster` par vos vraies valeurs MongoDB Atlas.

#### Variable 3 : MONGODB_DB_NAME
```
Key: MONGODB_DB_NAME
Value: kairos
```

#### Variable 4 : SECRET_KEY
```
Key: SECRET_KEY
Value: <GÉNÉRER-UNE-NOUVELLE-CLÉ>
```
**Pour générer la clé :**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copiez la sortie et utilisez-la comme valeur.

#### Variable 5 : OPENAI_API_KEY
```
Key: OPENAI_API_KEY
Value: sk-proj-VOTRE-CLÉ-API-ICI
```
⚠️ Remplacez `VOTRE-CLÉ-API-ICI` par votre vraie clé API OpenAI.

#### Variable 6 : FRONTEND_URL
```
Key: FRONTEND_URL
Value: https://kairos-frontend.onrender.com
```
⚠️ **Note** : À configurer après avoir déployé le frontend. Utilisez une URL temporaire pour l'instant.

#### Variable 7 : ALLOWED_HOSTS
```
Key: ALLOWED_HOSTS
Value: *
```

### ÉTAPE 4 : MongoDB Atlas Configuration (OBLIGATOIRE)

Avant de déployer, vous devez configurer MongoDB Atlas :

#### 4.1 Créer un Cluster MongoDB Atlas (Gratuit)

1. Aller sur https://www.mongodb.com/cloud/atlas
2. Créer un compte gratuit (si pas déjà fait)
3. Créer un cluster gratuit **M0** (Free)
4. Choisir une région : **Frankfurt (EU)** ou **Oregon (US West)**
5. Cliquer sur **"Create Cluster"**

#### 4.2 Créer un Utilisateur de Base de Données

1. Dans MongoDB Atlas : **Security** > **Database Access**
2. Cliquer sur **"Add New Database User"**
3. **Authentication Method** : Password
4. Créer :
   - Username : `kairos_user` (ou un autre nom)
   - Password : **Générer un mot de passe fort** (cliquez sur "Autogenerate Secure Password" ou créez-en un)
   - **⚠️ COPIER LE MOT DE PASSE** (il ne sera affiché qu'une fois !)
   - **Database User Privileges** : `Atlas Admin` ou `Read and write to any database`
5. Cliquer sur **"Add User"**

#### 4.3 Autoriser l'Accès depuis Render

1. Dans MongoDB Atlas : **Security** > **Network Access**
2. Cliquer sur **"Add IP Address"**
3. Cliquer sur **"Allow Access from Anywhere"** (0.0.0.0/0)
   - ⚠️ **OU** ajouter les IPs spécifiques de Render (voir documentation)
4. Cliquer sur **"Confirm"**

#### 4.4 Récupérer la Connection String

1. Dans MongoDB Atlas : **Deployments** > **Clusters**
2. Cliquer sur **"Connect"** sur votre cluster
3. Choisir **"Connect your application"**
4. Driver : **Python**, Version : **3.6 or later**
5. **COPIER** la connection string affichée :
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. **MODIFIER** la connection string :
   - Remplacer `<username>` par votre nom d'utilisateur MongoDB
   - Remplacer `<password>` par votre mot de passe MongoDB
   - Ajouter le nom de la base de données : `...mongodb.net/kairos?retryWrites...`
   
**Exemple de connection string complète :**
```
mongodb+srv://kairos_user:MonMotDePasse123!@cluster0.abc123.mongodb.net/kairos?retryWrites=true&w=majority
```

7. **UTILISER** cette connection string complète pour `MONGODB_URL` dans Render

### ÉTAPE 5 : Créer le Service

Une fois toutes les configurations faites :

1. **Vérifier** que :
   - Language : `Python 3` ✓
   - Build Command : `pip install -r requirements.txt` ✓
   - Start Command : `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120` ✓
   - Health Check : `/health` ✓
   - Variables d'environnement configurées ✓

2. **Faire défiler** vers le bas de la page

3. **Cliquer** sur le bouton **"Create Web Service"** (généralement vert ou bleu)

4. **Attendre** 5-10 minutes pour le déploiement

### ÉTAPE 6 : Vérifier le Déploiement

Une fois le déploiement terminé :

1. **Aller dans** Render Dashboard > Votre service `kairos`

2. **Vérifier les logs** :
   - Cliquez sur l'onglet **"Logs"**
   - Vérifiez qu'il n'y a pas d'erreurs
   - Cherchez : `"Connexion MongoDB réussie"` ou `"MongoDB connected"`

3. **Tester les endpoints** :
   - **Health Check** : `https://kairos.onrender.com/health`
     - Doit retourner : `{"status": "healthy", ...}`
   - **API Docs** : `https://kairos.onrender.com/docs`
     - Doit afficher la documentation Swagger

4. **Noter l'URL** de votre service :
   - URL : `https://kairos.onrender.com` (ou l'URL affichée dans Render)

## 📋 Configuration Frontend (Après Backend)

Une fois le backend déployé, configurez le frontend :

### ÉTAPE 1 : Créer un Service Static Site

1. Dans Render Dashboard : **"New +"** > **"Static Site"**

2. Connecter le même repository GitHub : `Elie224 / kairos`

3. Configuration :
   - **Name** : `kairos-frontend`
   - **Root Directory** : `frontend`
   - **Build Command** : `npm ci && npm run build`
   - **Publish Directory** : `dist`

4. Variables d'environnement :
   ```
   Key: VITE_API_URL
   Value: https://kairos.onrender.com
   ```
   (Remplacer `kairos` par le nom réel de votre service backend)

5. Cliquer sur **"Create Static Site"**

### ÉTAPE 2 : Mettre à Jour FRONTEND_URL

Une fois le frontend déployé :

1. Noter l'URL du frontend : `https://kairos-frontend.onrender.com`

2. Dans le service backend Render :
   - Aller dans **Environment** ou **Settings** > **Environment**
   - Modifier `FRONTEND_URL` avec l'URL réelle du frontend
   - Sauvegarder

3. Le backend va redémarrer automatiquement

## ⚠️ OPTION : Utiliser Docker (Non Recommandé)

Si vous voulez absolument utiliser Docker (pas recommandé pour la simplicité) :

### Configuration Docker

**Root Directory :** `backend`

**Build Command :** (laissez vide ou : `docker build -t kairos-backend .`)

**Start Command :** (laissez vide - Render utilisera le Dockerfile)

⚠️ **Problème** : Le Dockerfile actuel utilise le port 8000 fixe. Il faut le modifier pour utiliser `$PORT`.

**Meilleure option** : Utilisez **Python 3** directement (plus simple et recommandé).

## 🔄 Alternative : Utiliser .render.yaml (Recommandé)

Pour simplifier, vous pouvez utiliser le fichier `.render.yaml` déjà créé :

### Option 1 : Blueprint (Recommandé)

1. Dans Render Dashboard : **"New +"** > **"Blueprint"**

2. Connecter votre repository GitHub : `Elie224 / kairos`

3. Render détectera automatiquement le fichier `.render.yaml`

4. Cliquer sur **"Apply"**

5. Render créera automatiquement :
   - Service Backend (`kairos-backend`)
   - Service Frontend (`kairos-frontend`)

6. Configurer les variables d'environnement dans chaque service

**Avantages** :
- ✅ Configuration automatique
- ✅ Moins d'erreurs
- ✅ Plus rapide

## 📋 Checklist Finale

Avant de cliquer sur "Create Web Service" :

- [ ] Language : `Python 3` (pas Docker)
- [ ] Root Directory : `backend` (si option disponible)
- [ ] Build Command : `pip install -r requirements.txt`
- [ ] Start Command : `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
- [ ] Health Check Path : `/health`
- [ ] `ENVIRONMENT=production` configuré
- [ ] `MONGODB_URL` configuré (MongoDB Atlas)
- [ ] `MONGODB_DB_NAME=kairos` configuré
- [ ] `SECRET_KEY` générée et configurée
- [ ] `OPENAI_API_KEY` configurée
- [ ] `FRONTEND_URL` configuré (temporaire)
- [ ] `ALLOWED_HOSTS=*` configuré

## 🔗 Après Déploiement

Une fois le service déployé :

1. **Backend URL** : `https://kairos.onrender.com` (ou l'URL affichée)
   - Health : `https://kairos.onrender.com/health`
   - Docs : `https://kairos.onrender.com/docs`

2. **Frontend URL** : `https://kairos-frontend.onrender.com` (après déploiement frontend)

3. **Mettre à jour `FRONTEND_URL`** dans le backend avec l'URL réelle du frontend

## 📚 Guides Détaillés

- **Guide complet** : `CONFIGURATION_RENDER_DETAILLEE.md`
- **Basé sur votre écran** : `INSTRUCTIONS_RENDER_ECRAN.md`
- **Checklist** : `DEPLOIEMENT_CHECKLIST.md`
- **Déploiement Render** : `DEPLOIEMENT_RENDER.md`

## 🆘 Problèmes Courants

### Erreur : "Module not found"
- Vérifier que `requirements.txt` est dans `backend/`
- Vérifier que Root Directory est `backend`

### Erreur : "Port already in use"
- Utiliser `$PORT` dans Start Command, pas `8000`

### Erreur : "MongoDB connection failed"
- Vérifier que l'IP de Render est autorisée dans MongoDB Atlas
- Vérifier que `MONGODB_URL` est correct
- Vérifier les credentials MongoDB

### Erreur : "SECRET_KEY required"
- Vérifier que `SECRET_KEY` est configurée
- Générer une nouvelle clé si nécessaire
