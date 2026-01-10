# 🚀 Démarrage Rapide - Application Web Kaïros

## Méthode 1 : Script Automatique (Recommandé)

### Windows PowerShell

```powershell
.\demarrer-application.ps1
```

Ce script va :
1. ✅ Démarrer MongoDB (Docker)
2. ✅ Démarrer le Backend (port 8000)
3. ✅ Démarrer le Frontend (port 3000)

---

## Méthode 2 : Scripts Batch (Windows)

### Terminal 1 : MongoDB
```bash
demarrer-mongodb.bat
```

### Terminal 2 : Backend
```bash
demarrer-backend.bat
```

### Terminal 3 : Frontend
```bash
cd frontend
npm install  # Si première fois
npm run dev
```

---

## Méthode 3 : Démarrage Manuel

### 1. MongoDB

**Avec Docker** :
```bash
docker run -d --name eduverse-mongodb -p 27017:27017 -v mongodb_data:/data/db mongo:7.0
```

**Ou MongoDB local** : Assurez-vous que MongoDB est démarré sur le port 27017

### 2. Backend

```bash
cd backend

# Créer l'environnement virtuel (première fois)
python -m venv venv

# Activer l'environnement virtuel
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances (première fois)
pip install -r requirements.txt

# Démarrer le serveur
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend

```bash
cd frontend

# Installer les dépendances (première fois)
npm install

# Démarrer le serveur de développement
npm run dev
```

---

## ✅ Vérification

Une fois tout démarré, ouvrez dans votre navigateur :

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health

---

## 🐛 Problèmes Courants

### MongoDB ne démarre pas
- Vérifier que Docker Desktop est démarré
- Vérifier le port 27017 : `netstat -an | findstr 27017`

### Backend ne démarre pas
- Vérifier Python : `python --version` (doit être 3.10+)
- Vérifier les dépendances : `pip install -r requirements.txt`
- Vérifier le port 8000 : `netstat -an | findstr 8000`

### Frontend ne démarre pas
- Vérifier Node.js : `node --version` (doit être 18+)
- Installer les dépendances : `npm install`
- Vérifier le port 3000 (Vite utilisera un autre port si occupé)

---

## 📝 Première Utilisation

1. **Créer un compte** : http://localhost:3000/register
2. **Se connecter** : http://localhost:3000/login
3. **Explorer les modules** : http://localhost:3000/modules
4. **Tester le chat IA** : Dans un module, utiliser le tutorat IA

---

*Application prête ! Bon développement ! 🚀*



