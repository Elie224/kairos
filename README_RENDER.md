# 🚀 Configuration Render - Instructions Rapides

## 🔗 Connection String MongoDB - PRÊTE POUR RENDER

### Vos Informations MongoDB Atlas

- **Cluster** : `cluster0.u3cxqhm.mongodb.net`
- **Base de données** : `kairos`
- **Mot de passe** : `92GB9ySeL0tf04kn`
- **Nom d'utilisateur MongoDB** : `<À-VÉRIFIER>` (probablement `kairos` ou `kairos_user`)

### Connection String Complète

**Option 1 : Si votre utilisateur MongoDB est `kairos` (même nom que la base)**
```
mongodb+srv://kairos:92GB9ySeL0tf04kn@cluster0.u3cxqhm.mongodb.net/kairos?retryWrites=true&w=majority
```

**Option 2 : Si votre utilisateur MongoDB est différent (ex: `kairos_user`)**
```
mongodb+srv://kairos_user:92GB9ySeL0tf04kn@cluster0.u3cxqhm.mongodb.net/kairos?retryWrites=true&w=majority
```

**Format général (remplacer `<USERNAME>` par votre username MongoDB) :**
```
mongodb+srv://<USERNAME>:92GB9ySeL0tf04kn@cluster0.u3cxqhm.mongodb.net/kairos?retryWrites=true&w=majority
```

## 🔍 Comment Trouver votre Nom d'Utilisateur MongoDB ?

1. Aller sur https://cloud.mongodb.com
2. Se connecter à votre compte
3. Cliquer sur **"Security"** dans le menu de gauche
4. Cliquer sur **"Database Access"**
5. Voir la liste des utilisateurs
6. **Noter le nom d'utilisateur** (ex: `kairos`, `kairos_user`, `admin`, etc.)

**Si aucun utilisateur n'existe :**

1. Cliquer sur **"Add New Database User"**
2. **Authentication Method** : Password
3. **Username** : Entrer `kairos_user` (ou un autre nom)
4. **Password** : Entrer `92GB9ySeL0tf04kn`
5. **Database User Privileges** : `Atlas Admin` ou `Read and write to any database`
6. Cliquer sur **"Add User"**
7. **Noter le nom d'utilisateur** créé

## 🔒 ÉTAPE CRITIQUE : Autoriser l'Accès depuis Render

**⚠️ OBLIGATOIRE - À faire AVANT de configurer Render !**

Sans cette étape, Render ne pourra PAS se connecter à MongoDB Atlas !

1. Aller sur https://cloud.mongodb.com
2. Se connecter à votre compte
3. Cliquer sur **"Security"** dans le menu de gauche
4. Cliquer sur **"Network Access"**
5. Vérifier si une entrée existe avec `0.0.0.0/0` (Allow Access from Anywhere)

**Si PAS d'entrée :**

1. Cliquer sur **"Add IP Address"** (bouton vert en haut à droite)
2. Dans la fenêtre qui s'ouvre, cliquer sur **"Allow Access from Anywhere"**
   - Cela ajoutera automatiquement `0.0.0.0/0` (toutes les IPs)
3. Cliquer sur **"Confirm"**
4. **Attendre 1-2 minutes** pour que les changements prennent effet

## ⚙️ Configuration Render - Étapes Exactes

### Sur votre Écran Render "New Web Service"

#### 1. Language (À CORRIGER)

**Actuellement :** `Docker`

**À changer pour :**
- Cliquer sur le dropdown "Language"
- Sélectionner **"Python 3"** (pas Docker)
- Si un sous-menu apparaît : Sélectionner **Python 3.11** ou la dernière version

#### 2. Build Command

**Chercher** la section "Build Command" ou "Build" :

**Entrer :**
```
pip install -r requirements.txt
```

#### 3. Start Command

**Chercher** la section "Start Command" ou "Start" :

**Entrer :**
```
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

⚠️ **IMPORTANT** : Utilisez `$PORT` et non `8000` !

#### 4. Health Check Path

**Chercher** "Health Check Path" ou "Health Check" :

**Entrer :**
```
/health
```

#### 5. Root Directory (si option disponible)

**Chercher** "Root Directory" :

**Entrer :**
```
backend
```

### Variables d'Environnement

**Cliquer sur "Advanced" ou "Environment"** (en bas de la page ou dans les settings)

**Ajouter ces variables :**

#### Variable 1 : ENVIRONMENT
```
Key: ENVIRONMENT
Value: production
```

#### Variable 2 : MONGODB_URL

**Si votre utilisateur MongoDB est `kairos` :**
```
Key: MONGODB_URL
Value: mongodb+srv://kairos:92GB9ySeL0tf04kn@cluster0.u3cxqhm.mongodb.net/kairos?retryWrites=true&w=majority
```

**Si votre utilisateur MongoDB est différent (remplacer <USERNAME>) :**
```
Key: MONGODB_URL
Value: mongodb+srv://<USERNAME>:92GB9ySeL0tf04kn@cluster0.u3cxqhm.mongodb.net/kairos?retryWrites=true&w=majority
```

⚠️ **Vérifier votre username MongoDB dans Atlas > Security > Database Access !**

#### Variable 3 : MONGODB_DB_NAME
```
Key: MONGODB_DB_NAME
Value: kairos
```

#### Variable 4 : SECRET_KEY

**Générer d'abord une nouvelle clé :**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Puis configurer :**
```
Key: SECRET_KEY
Value: <COLLER-LA-CLÉ-GÉNÉRÉE-ICI>
```

#### Variable 5 : OPENAI_API_KEY
```
Key: OPENAI_API_KEY
Value: sk-proj-VOTRE-CLÉ-API-ICI
```

#### Variable 6 : FRONTEND_URL
```
Key: FRONTEND_URL
Value: https://kairos-frontend.onrender.com
```

⚠️ **Note** : À mettre à jour après déploiement du frontend avec l'URL réelle

#### Variable 7 : ALLOWED_HOSTS
```
Key: ALLOWED_HOSTS
Value: *
```

## ✅ Créer le Service

Une fois toutes les configurations faites :

1. **Vérifier** toutes les configurations
2. **Faire défiler** vers le bas de la page
3. **Cliquer** sur **"Create Web Service"** (bouton vert ou bleu)
4. **Attendre** 5-10 minutes pour le déploiement

## 🧪 Test après Déploiement

### Test 1 : Health Check

Une fois le déploiement terminé, tester :

```
https://kairos.onrender.com/health
```

**Résultat attendu :**
```json
{
  "status": "healthy",
  "mongodb": "connected",
  "timestamp": ...,
  "version": "1.0.0"
}
```

### Test 2 : API Documentation

```
https://kairos.onrender.com/docs
```

Doit afficher la documentation Swagger/OpenAPI.

### Test 3 : Vérifier les Logs

Dans Render Dashboard > Service `kairos` > **"Logs"** :

**Chercher :**
- ✅ `"Connexion MongoDB réussie"` ou `"MongoDB connected"`
- ✅ `"Connexion à MongoDB..."`
- ❌ **PAS** : `"Erreur de connexion MongoDB"` ou `"MongoDB connection failed"`

## 🐛 Problèmes et Solutions

### Erreur : "MongoDB connection failed"

**Solutions :**
1. ✅ Vérifier Network Access dans MongoDB Atlas (Allow Access from Anywhere)
2. ✅ Vérifier que le nom d'utilisateur et le mot de passe sont corrects
3. ✅ Vérifier que `/kairos` est présent dans la connection string avant le `?`
4. ✅ Vérifier que les paramètres sont `?retryWrites=true&w=majority`

### Erreur : "Authentication failed"

**Solutions :**
1. ✅ Vérifier le nom d'utilisateur MongoDB dans Atlas > Security > Database Access
2. ✅ Vérifier que le mot de passe est exactement `92GB9ySeL0tf04kn`
3. ✅ Vérifier que l'utilisateur a les permissions `Atlas Admin` ou `Read and write`

## 📋 Checklist Finale

### MongoDB Atlas
- [ ] Username MongoDB identifié (Security > Database Access)
- [ ] Network Access autorisé : Allow Access from Anywhere (0.0.0.0/0)
- [ ] Connection string complète construite avec le bon username

### Render - Service
- [ ] Language : Python 3 (pas Docker)
- [ ] Root Directory : backend (si option disponible)
- [ ] Build Command : `pip install -r requirements.txt`
- [ ] Start Command : `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
- [ ] Health Check : `/health`

### Render - Variables
- [ ] ENVIRONMENT=production
- [ ] MONGODB_URL (avec votre username MongoDB)
- [ ] MONGODB_DB_NAME=kairos
- [ ] SECRET_KEY (générée)
- [ ] OPENAI_API_KEY
- [ ] FRONTEND_URL
- [ ] ALLOWED_HOSTS=*

### Après Déploiement
- [ ] Service déployé avec succès
- [ ] Health check fonctionne : `/health`
- [ ] MongoDB connecté (vérifier dans les logs)
- [ ] API Docs accessible : `/docs`

## 🔐 SÉCURITÉ

- ✅ Les fichiers avec secrets sont dans `.gitignore` - Ne seront PAS commités
- ✅ Les variables d'environnement sur Render sont privées
- ❌ NE JAMAIS commiter ces fichiers sur GitHub
- ❌ NE JAMAIS partager publiquement ces informations

## 📚 Guides Détaillés

- Guide complet : `CONFIGURATION_RENDER_COMPLETE.md`
- Guide simple : `CONFIGURATION_RENDER_SIMPLE.md`
- MongoDB Atlas : `MONGODB_CONFIGURATION_FINALE.md`
