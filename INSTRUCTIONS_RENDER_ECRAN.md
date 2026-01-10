# 📸 Instructions pour Configuration Render - Basé sur Votre Écran

## 🔍 Analyse de Votre Configuration Actuelle

Sur votre écran Render, je vois :

✅ **Correctement configuré :**
- Source Code : `Elie224 / kairos` ✓
- Name : `kairos` ✓
- Branch : `main` ✓
- Region : Oregon (US West) ✓ (OK, mais Frankfurt est recommandé)

❌ **À CORRIGER :**
- Language : `Docker` → **Doit être `Python 3`**

## 🚨 CORRECTION URGENTE - Language

### Action Immédiate

**Sur votre écran Render, cliquez sur le dropdown "Language" et changez :**

**AVANT :**
```
Language: Docker ▼
```

**APRÈS :**
```
Language: Python 3 ▼
```

**OU** si vous voyez plusieurs options Python, choisissez :
```
Python 3
Python Version: 3.11 (ou dernière version disponible)
```

## 📝 Configuration Complète à Faire

### 1. Cliquer sur "Advanced" ou "Environment" (en bas de la page)

Cherchez un bouton/lien qui dit **"Advanced"**, **"Environment Variables"**, ou **"Show advanced options"**.

### 2. Configurer les Variables d'Environnement

Une fois dans "Environment" ou "Advanced", ajoutez ces variables :

#### Section "Environment Variables" ou "Add Environment Variable"

Cliquez sur **"Add Environment Variable"** pour chaque variable :

**Variable 1 :**
- Key : `ENVIRONMENT`
- Value : `production`

**Variable 2 :**
- Key : `MONGODB_URL`
- Value : `mongodb+srv://username:password@cluster.mongodb.net/kairos?retryWrites=true&w=majority`
  - ⚠️ **IMPORTANT** : Remplacez `username`, `password`, et `cluster` par vos vraies valeurs MongoDB Atlas

**Variable 3 :**
- Key : `MONGODB_DB_NAME`
- Value : `kairos`

**Variable 4 :**
- Key : `SECRET_KEY`
- Value : `<GÉNÉRER-UNE-NOUVELLE-CLÉ>`
  - ⚠️ **IMPORTANT** : Générer avec : `python -c "import secrets; print(secrets.token_urlsafe(32))"`

**Variable 5 :**
- Key : `OPENAI_API_KEY`
- Value : `sk-proj-VOTRE-CLÉ-API-ICI`

**Variable 6 :**
- Key : `FRONTEND_URL`
- Value : `https://kairos-frontend.onrender.com`
  - ⚠️ **Note** : À configurer après avoir déployé le frontend

**Variable 7 :**
- Key : `ALLOWED_HOSTS`
- Value : `*`

### 3. Build & Start Commands

Cherchez les sections **"Build Command"** et **"Start Command"** :

**Build Command :**
```
pip install -r requirements.txt
```

**Start Command :**
```
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

**⚠️ IMPORTANT** : Utilisez `$PORT` et non `8000` !

### 4. Health Check Path

Cherchez **"Health Check Path"** ou **"Health Check URL"** :

- Health Check Path : `/health`

### 5. Root Directory (si option disponible)

Si vous voyez une option **"Root Directory"** :

- Root Directory : `backend`

Cela indique à Render où se trouve le code Python.

## 🎯 Actions Immédiates sur Votre Écran

### Étape 1 : Changer Language

1. Cliquez sur le dropdown **"Language"**
2. Sélectionnez **"Python 3"** (pas Docker)
3. Si un sous-menu apparaît, sélectionnez **Python 3.11** ou la dernière version

### Étape 2 : Configurer Build & Start (si visibles)

Si vous voyez les champs "Build Command" et "Start Command" :

1. **Build Command** : Entrez `pip install -r requirements.txt`
2. **Start Command** : Entrez `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`

### Étape 3 : Cliquer sur "Advanced" ou "Environment"

Cherchez un bouton en bas de la page qui dit :
- **"Show Advanced Options"**
- **"Environment"**
- **"Add Environment Variable"**
- Ou un bouton avec une icône de roue dentée ⚙️

### Étape 4 : Ajouter Variables d'Environnement

Pour chaque variable :
1. Cliquez sur **"Add Environment Variable"** ou **"Add Variable"**
2. Entrez le **Key** (nom de la variable)
3. Entrez la **Value** (valeur de la variable)
4. Cliquez sur **"Save"** ou **"Add"**

### Étape 5 : Cliquer sur "Create Web Service"

Une fois toutes les configurations faites :
1. Faites défiler vers le bas de la page
2. Cliquez sur le bouton **"Create Web Service"** (généralement vert ou bleu)
3. Attendez 5-10 minutes pour le déploiement

## ⚠️ Si Vous Ne Voyez Pas Certaines Options

Si certaines options ne sont pas visibles sur votre écran :

1. **Build/Start Commands** : Peut-être dans la section "Advanced" après avoir sélectionné Python
2. **Root Directory** : Peut-être dans "Advanced" ou automatiquement détecté
3. **Health Check** : Peut-être configuré après la création du service

## 🔄 Alternative : Utiliser .render.yaml (Recommandé)

Si vous voulez simplifier, Render peut utiliser automatiquement le fichier `.render.yaml` :

1. **Supprimer** le service actuel (si créé)
2. Dans Render Dashboard : **"New +"** > **"Blueprint"**
3. Connecter votre repository : `Elie224 / kairos`
4. Render détectera automatiquement `.render.yaml`
5. Cliquer sur **"Apply"**

Cette méthode configure automatiquement tout !

## 📋 Checklist Rapide

- [ ] Language : `Python 3` (pas Docker)
- [ ] Build Command : `pip install -r requirements.txt`
- [ ] Start Command : `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
- [ ] Health Check : `/health`
- [ ] `ENVIRONMENT=production` ajouté
- [ ] `MONGODB_URL` configuré (MongoDB Atlas)
- [ ] `SECRET_KEY` générée et ajoutée
- [ ] `OPENAI_API_KEY` ajoutée
- [ ] `ALLOWED_HOSTS=*` ajouté

## ✅ Après Déploiement

1. Noter l'URL du service : `https://kairos.onrender.com`
2. Tester : `https://kairos.onrender.com/health`
3. Vérifier les logs dans Render Dashboard

## 🔗 Ressources

- Guide complet : `CONFIGURATION_RENDER_DETAILLEE.md`
- Checklist : `DEPLOIEMENT_CHECKLIST.md`
- Render Docs : https://render.com/docs/python
