# 🚀 Guide de Démarrage - Application Web Kaïros

## 📋 Prérequis

- ✅ Python 3.10+ (détecté: Python 3.13.5)
- ✅ Node.js 18+ (détecté: v22.17.0)
- ✅ MongoDB (à démarrer)
- ⚠️ Docker Desktop (pour MongoDB via Docker, optionnel)

## 🗄️ Étape 1 : Démarrer MongoDB

### Option A : Avec Docker (Recommandé)

1. **Démarrer Docker Desktop** (si pas déjà démarré)

2. **Exécuter le script de démarrage MongoDB** :
```bash
demarrer-mongodb.bat
```

Ou manuellement :
```bash
docker run -d --name eduverse-mongodb -p 27017:27017 -v mongodb_data:/data/db mongo:7.0
```

### Option B : MongoDB installé localement

Si MongoDB est installé localement, assurez-vous qu'il est démarré sur le port 27017.

**Vérifier que MongoDB fonctionne** :
```bash
mongosh --eval "db.adminCommand('ping')"
```

---

## 🔧 Étape 2 : Démarrer le Backend

### Méthode 1 : Script automatique (Windows)

```bash
demarrer-backend.bat
```

### Méthode 2 : Manuel

1. **Aller dans le dossier backend** :
```bash
cd backend
```

2. **Créer l'environnement virtuel** (si pas déjà créé) :
```bash
python -m venv venv
```

3. **Activer l'environnement virtuel** :
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Installer les dépendances** (si pas déjà installées) :
```bash
pip install -r requirements.txt
```

5. **Démarrer le serveur** :
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Le backend sera accessible sur** : http://localhost:8000
**Documentation API** : http://localhost:8000/docs

---

## 🎨 Étape 3 : Démarrer le Frontend

1. **Ouvrir un nouveau terminal** (garder le backend en cours d'exécution)

2. **Aller dans le dossier frontend** :
```bash
cd frontend
```

3. **Installer les dépendances** (si pas déjà installées) :
```bash
npm install
```

4. **Démarrer le serveur de développement** :
```bash
npm run dev
```

**Le frontend sera accessible sur** : http://localhost:3000 (ou le port indiqué par Vite)

---

## ✅ Vérification

Une fois tout démarré, vous devriez avoir :

1. ✅ **MongoDB** : Port 27017
2. ✅ **Backend API** : http://localhost:8000
3. ✅ **Frontend** : http://localhost:3000

### Tester l'API

Ouvrir dans le navigateur :
- **Documentation Swagger** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health

### Tester le Frontend

Ouvrir dans le navigateur :
- **Application** : http://localhost:3000

---

## 🔍 Dépannage

### Erreur : MongoDB non accessible

**Solution** :
1. Vérifier que MongoDB est démarré : `docker ps` (si Docker) ou vérifier le service MongoDB
2. Vérifier le port 27017 : `netstat -an | findstr 27017` (Windows)

### Erreur : Port 8000 déjà utilisé

**Solution** :
1. Trouver le processus : `netstat -ano | findstr :8000`
2. Arrêter le processus ou changer le port dans `main.py`

### Erreur : Port 3000 déjà utilisé

**Solution** :
Vite utilisera automatiquement un autre port (3001, 3002, etc.) ou modifier dans `vite.config.ts`

### Erreur : Module non trouvé (Python)

**Solution** :
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Erreur : Module non trouvé (Node.js)

**Solution** :
```bash
cd frontend
npm install
```

---

## 📝 Variables d'Environnement (Optionnel)

Si vous avez besoin de configurer des variables d'environnement, créer un fichier `.env` dans `backend/` :

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros

# OpenAI (pour les fonctionnalités IA)
OPENAI_API_KEY=sk-proj-...

# Sécurité
SECRET_KEY=votre_clé_secrète_32_caractères_minimum

# Redis (optionnel)
REDIS_URL=redis://localhost:6379/0
```

---

## 🛑 Arrêter l'Application

1. **Arrêter le frontend** : `Ctrl+C` dans le terminal frontend
2. **Arrêter le backend** : `Ctrl+C` dans le terminal backend
3. **Arrêter MongoDB** (si Docker) : `docker stop eduverse-mongodb`

---

## 🎯 Prochaines Étapes

Une fois l'application démarrée :

1. **Créer un compte** : http://localhost:3000/register
2. **Se connecter** : http://localhost:3000/login
3. **Explorer les modules** : http://localhost:3000/modules
4. **Tester le chat IA** : Dans un module, utiliser le tutorat IA

---

*Application Kaïros prête à l'emploi ! 🚀*



