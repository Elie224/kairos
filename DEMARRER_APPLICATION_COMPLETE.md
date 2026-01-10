# 🚀 Guide de Démarrage Complet - Application Kaïros

## 📋 Prérequis

- ✅ Python 3.10+ installé
- ✅ Node.js 18+ installé
- ✅ Docker Desktop installé et démarré (pour MongoDB et Redis)
- ✅ npm installé

---

## 🎯 Démarrage en 3 Étapes

### Étape 1 : Démarrer MongoDB (Obligatoire)

**Option A : Avec Docker Compose (Recommandé)**
```powershell
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
docker-compose up -d mongodb
```

**Option B : Avec le script batch**
```powershell
.\demarrer-mongodb.bat
```

**Option C : Docker manuel**
```powershell
docker run -d --name kaïros-mongodb -p 27017:27017 -v mongodb_data:/data/db mongo:7.0
```

**Vérification** :
```powershell
docker ps | findstr mongodb
```

---

### Étape 2 : Démarrer le Backend

**Option A : Avec PowerShell (Recommandé)**
```powershell
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
.\start_backend.ps1
```

**Option B : Manuellement**
```powershell
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós\backend"

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Installer les dépendances (si première fois)
pip install -r requirements.txt

# Démarrer le serveur
python main.py
```

**Le backend sera accessible sur** : http://localhost:8000

---

### Étape 3 : Démarrer le Frontend

**Dans un nouveau terminal** :
```powershell
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós\frontend"

# Installer les dépendances (si première fois)
npm install

# Démarrer le serveur de développement
npm run dev
```

**Le frontend sera accessible sur** : http://localhost:5173 (ou 3000)

---

## ✅ Vérification

Une fois tout démarré, vérifiez :

1. **MongoDB** : 
   - Conteneur actif : `docker ps | findstr mongodb`
   - Test : `docker exec kaïros-mongodb mongosh --eval "db.adminCommand('ping')"`

2. **Backend** :
   - Health check : http://localhost:8000/health
   - Documentation API : http://localhost:8000/docs

3. **Frontend** :
   - Application : http://localhost:5173
   - Vérifier la console du navigateur pour les erreurs

---

## 🔧 Services Optionnels

### Redis (Recommandé pour la performance)

```powershell
# Avec Docker Compose
docker-compose up -d redis

# Ou manuellement
docker run -d --name kaïros-redis -p 6379:6379 redis:7.0-alpine
```

**Configuration** : Ajouter dans `.env` du backend :
```
REDIS_URL=redis://localhost:6379/0
```

### PostgreSQL (Optionnel)

```powershell
docker run -d --name kaïros-postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=eduverse postgres:15-alpine
```

---

## 🐛 Résolution de Problèmes

### MongoDB ne démarre pas

1. **Vérifier Docker Desktop** :
   ```powershell
   docker ps
   ```

2. **Vérifier le port 27017** :
   ```powershell
   netstat -an | findstr 27017
   ```

3. **Redémarrer le conteneur** :
   ```powershell
   docker start kaïros-mongodb
   ```

### Backend ne démarre pas

1. **Vérifier Python** :
   ```powershell
   python --version  # Doit être 3.10+
   ```

2. **Vérifier les dépendances** :
   ```powershell
   cd backend
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Vérifier le port 8000** :
   ```powershell
   netstat -an | findstr 8000
   ```

4. **Vérifier MongoDB** :
   - Le backend doit pouvoir se connecter à MongoDB
   - Vérifier les logs du backend pour les erreurs de connexion

### Frontend ne démarre pas

1. **Vérifier Node.js** :
   ```powershell
   node --version  # Doit être 18+
   ```

2. **Réinstaller les dépendances** :
   ```powershell
   cd frontend
   rm -r node_modules
   npm install
   ```

3. **Vérifier le port** :
   - Vite utilisera automatiquement un autre port si 5173 est occupé
   - Vérifier la console pour le port utilisé

---

## 📝 Configuration Environnement

### Fichier `.env` (Backend)

Créer un fichier `.env` dans `backend/` :

```env
# MongoDB (Obligatoire)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros

# Sécurité (Obligatoire en production)
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

---

## 🎯 Commandes Utiles

### Arrêter les services

```powershell
# Arrêter MongoDB
docker stop kaïros-mongodb

# Arrêter Redis
docker stop kaïros-redis

# Arrêter le backend : Ctrl+C dans le terminal

# Arrêter le frontend : Ctrl+C dans le terminal
```

### Redémarrer les services

```powershell
# Redémarrer MongoDB
docker start kaïros-mongodb

# Redémarrer Redis
docker start kaïros-redis
```

### Voir les logs

```powershell
# Logs MongoDB
docker logs kaïros-mongodb

# Logs Redis
docker logs kaïros-redis
```

---

## 🚀 Démarrage Rapide (Tout en une fois)

Si vous avez Docker Compose et tous les prérequis :

```powershell
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"

# Démarrer MongoDB et Redis
docker-compose up -d mongodb redis

# Attendre 10 secondes que MongoDB démarre
Start-Sleep -Seconds 10

# Démarrer le backend (dans un terminal séparé)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\KOURO\OneDrive\Desktop\Kairós'; .\start_backend.ps1"

# Démarrer le frontend (dans un terminal séparé)
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\KOURO\OneDrive\Desktop\Kairós\frontend'; npm run dev"
```

---

## ✅ Checklist de Démarrage

- [ ] Docker Desktop démarré
- [ ] MongoDB démarré et accessible (port 27017)
- [ ] Redis démarré (optionnel, port 6379)
- [ ] Backend démarré (port 8000)
- [ ] Frontend démarré (port 5173)
- [ ] Health check backend OK : http://localhost:8000/health
- [ ] Application frontend accessible : http://localhost:5173

---

*Bon développement ! 🚀*


