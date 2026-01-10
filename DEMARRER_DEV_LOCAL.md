# 🚀 Démarrer l'Application en Local - Mode Développement

## 📋 Checklist de Démarrage

### ✅ Prérequis Vérifiés

- [x] Docker Desktop installé et démarré
- [x] MongoDB démarré
- [x] Python 3.10+ installé
- [x] Node.js 18+ installé
- [x] Environnement virtuel Python créé
- [x] Dépendances backend installées

---

## 🗄️ Étape 1 : Démarrer MongoDB

**Option A : Docker Compose (Recommandé)**
```cmd
docker-compose up -d mongodb
```

**Option B : Script Batch**
```cmd
demarrer-mongodb.bat
```

**Vérification** :
```cmd
docker ps | findstr mongodb
```

---

## 🔧 Étape 2 : Démarrer le Backend

**Ouvrez un terminal CMD** et exécutez :

```cmd
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
demarrer-backend.bat
```

**OU manuellement** :
```cmd
cd backend
venv\Scripts\activate
python main.py
```

**Le backend sera accessible sur** : 
- API : http://localhost:8000
- Documentation : http://localhost:8000/docs
- Health Check : http://localhost:8000/health

---

## 🎨 Étape 3 : Démarrer le Frontend

**Ouvrez un NOUVEAU terminal CMD** et exécutez :

```cmd
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
cd frontend
npm install
npm run dev
```

**OU utilisez le script** :
```cmd
demarrer-frontend-cmd.bat
```

**Le frontend sera accessible sur** : http://localhost:5173

---

## ✅ Vérification Complète

Une fois tous les services démarrés :

1. **MongoDB** : Conteneur actif
   ```cmd
   docker ps | findstr mongodb
   ```

2. **Backend** : http://localhost:8000/health
   - Devrait retourner `{"status": "healthy"}`

3. **Frontend** : http://localhost:5173
   - Devrait afficher la page d'accueil

4. **Documentation API** : http://localhost:8000/docs
   - Interface Swagger interactive

---

## 🔧 Configuration pour le Développement

### Variables d'Environnement (Backend)

Créez un fichier `.env` dans `backend/` :

```env
# MongoDB (Obligatoire)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros

# Sécurité (Générer une clé secrète)
SECRET_KEY=votre_clé_secrète_32_caractères_minimum

# OpenAI (Optionnel - pour fonctionnalités IA)
OPENAI_API_KEY=sk-proj-...

# Redis (Optionnel mais recommandé)
REDIS_URL=redis://localhost:6379/0

# Environnement
ENVIRONMENT=development

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

### Générer une SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## 🛠️ Services Optionnels

### Redis (Recommandé pour la performance)

```cmd
docker-compose up -d redis
```

### PostgreSQL (Optionnel)

```cmd
docker run -d --name kaïros-postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=eduverse postgres:15-alpine
```

---

## 📝 Commandes Utiles pour le Développement

### Backend

```cmd
# Activer l'environnement virtuel
cd backend
venv\Scripts\activate

# Installer une nouvelle dépendance
pip install nom-du-package
pip freeze > requirements.txt

# Lancer avec rechargement automatique (déjà activé avec --reload)
python main.py

# Voir les logs
# Les logs s'affichent directement dans le terminal
```

### Frontend

```cmd
# Installer une nouvelle dépendance
npm install nom-du-package

# Build de production
npm run build

# Preview du build
npm run preview

# Voir les logs
# Les logs s'affichent directement dans le terminal
```

### MongoDB

```cmd
# Voir les logs MongoDB
docker logs kaïros-mongodb

# Accéder à MongoDB Shell
docker exec -it kaïros-mongodb mongosh

# Arrêter MongoDB
docker stop kaïros-mongodb

# Redémarrer MongoDB
docker start kaïros-mongodb
```

---

## 🐛 Dépannage

### Backend ne démarre pas

1. **Vérifier MongoDB** :
   ```cmd
   docker ps | findstr mongodb
   ```

2. **Vérifier les dépendances** :
   ```cmd
   cd backend
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Vérifier le port 8000** :
   ```cmd
   netstat -an | findstr 8000
   ```

### Frontend ne démarre pas

1. **Vérifier Node.js** :
   ```cmd
   node --version
   npm --version
   ```

2. **Réinstaller les dépendances** :
   ```cmd
   cd frontend
   rm -r node_modules
   npm install
   ```

3. **Vérifier le port 5173** :
   - Vite utilisera automatiquement un autre port si occupé

### MongoDB ne répond pas

1. **Vérifier Docker Desktop** :
   - Assurez-vous que Docker Desktop est démarré

2. **Redémarrer MongoDB** :
   ```cmd
   docker restart kaïros-mongodb
   ```

---

## 🎯 Workflow de Développement

### 1. Démarrage Quotidien

```cmd
# Terminal 1 : MongoDB
docker start kaïros-mongodb

# Terminal 2 : Backend
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
demarrer-backend.bat

# Terminal 3 : Frontend
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
cd frontend
npm run dev
```

### 2. Développement Backend

- Modifiez les fichiers dans `backend/app/`
- Le serveur se recharge automatiquement (--reload)
- Vérifiez les logs dans le terminal
- Testez via http://localhost:8000/docs

### 3. Développement Frontend

- Modifiez les fichiers dans `frontend/src/`
- Le serveur se recharge automatiquement (Hot Module Replacement)
- Vérifiez les logs dans le terminal
- Ouvrez http://localhost:5173 dans le navigateur

### 4. Tests

```cmd
# Backend
cd backend
venv\Scripts\activate
pytest

# Frontend
cd frontend
npm test
```

---

## 📊 Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Application React |
| Backend API | http://localhost:8000 | API FastAPI |
| API Docs | http://localhost:8000/docs | Documentation Swagger |
| Health Check | http://localhost:8000/health | État des services |

---

## 🚀 Prêt pour le Développement !

Une fois tous les services démarrés, vous pouvez :

1. **Modifier le code** : Les changements se rechargent automatiquement
2. **Tester les APIs** : Via http://localhost:8000/docs
3. **Développer de nouvelles fonctionnalités** : Suivez le `PLAN_DEVELOPPEMENT.md`
4. **Voir les logs** : Directement dans les terminaux

**Bon développement ! 🎉**
