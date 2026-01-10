# 🚀 Lancer l'Application Kaïros - Guide Simple

## ⚠️ Important : Exécutez ces commandes dans votre terminal PowerShell

---

## 📋 Étape 1 : Vérifier les Prérequis

### 1.1 Vérifier Docker Desktop
```powershell
docker --version
```
**Si Docker n'est pas installé** : Installez Docker Desktop depuis https://www.docker.com/products/docker-desktop

**Si Docker est installé mais ne répond pas** : Démarrez Docker Desktop depuis le menu Démarrer

### 1.2 Vérifier Python
```powershell
python --version
```
**Doit être 3.10 ou supérieur**

### 1.3 Vérifier Node.js
```powershell
node --version
```
**Doit être 18 ou supérieur**

---

## 🗄️ Étape 2 : Démarrer MongoDB

**Ouvrez un terminal PowerShell et exécutez** :

```powershell
# Naviguer vers le dossier du projet
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"

# Démarrer MongoDB avec Docker
docker-compose up -d mongodb
```

**OU utilisez le script batch** :
```powershell
.\demarrer-mongodb.bat
```

**Vérifier que MongoDB est démarré** :
```powershell
docker ps | findstr mongodb
```

Vous devriez voir un conteneur `kaïros-mongodb` ou `eduverse-mongodb` en cours d'exécution.

---

## 🔧 Étape 3 : Démarrer le Backend

**Ouvrez un NOUVEAU terminal PowerShell** :

```powershell
# Naviguer vers le dossier backend
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós\backend"

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Si l'environnement virtuel n'existe pas, créez-le :
# python -m venv venv
# .\venv\Scripts\Activate.ps1
# pip install -r requirements.txt

# Démarrer le serveur FastAPI
python main.py
```

**OU utilisez le script PowerShell** :
```powershell
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
.\start_backend.ps1
```

**Le backend sera accessible sur** : http://localhost:8000

**Vérifier** : Ouvrez http://localhost:8000/health dans votre navigateur

---

## 🎨 Étape 4 : Démarrer le Frontend

**Ouvrez un NOUVEAU terminal PowerShell** :

```powershell
# Naviguer vers le dossier frontend
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós\frontend"

# Installer les dépendances (si première fois)
npm install

# Démarrer le serveur de développement
npm run dev
```

**Le frontend sera accessible sur** : http://localhost:5173 (ou 3000)

---

## ✅ Vérification Finale

1. **MongoDB** : 
   - Conteneur actif : `docker ps | findstr mongodb`
   - Test : `docker exec kaïros-mongodb mongosh --eval "db.adminCommand('ping')"`

2. **Backend** :
   - Health check : http://localhost:8000/health
   - Documentation API : http://localhost:8000/docs

3. **Frontend** :
   - Application : http://localhost:5173
   - Ouvrez dans votre navigateur

---

## 🐛 Problèmes Courants

### Docker Desktop n'est pas démarré
**Solution** : Démarrez Docker Desktop depuis le menu Démarrer de Windows

### MongoDB ne démarre pas
```powershell
# Vérifier si le conteneur existe déjà
docker ps -a | findstr mongodb

# Si le conteneur existe mais est arrêté, démarrez-le :
docker start kaïros-mongodb
# OU
docker start eduverse-mongodb
```

### Backend : "ModuleNotFoundError"
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Backend : "Connection refused" MongoDB
- Vérifiez que MongoDB est démarré : `docker ps | findstr mongodb`
- Vérifiez que le port 27017 est libre : `netstat -an | findstr 27017`

### Frontend : "npm n'est pas reconnu"
- Installez Node.js depuis https://nodejs.org/
- Redémarrez votre terminal après l'installation

---

## 🎯 Commandes Utiles

### Arrêter les services
- **Backend** : Appuyez sur `Ctrl+C` dans le terminal backend
- **Frontend** : Appuyez sur `Ctrl+C` dans le terminal frontend
- **MongoDB** : `docker stop kaïros-mongodb`

### Redémarrer MongoDB
```powershell
docker start kaïros-mongodb
```

### Voir les logs MongoDB
```powershell
docker logs kaïros-mongodb
```

---

## 📝 Configuration Optionnelle

### Redis (Recommandé pour la performance)

```powershell
# Démarrer Redis
docker-compose up -d redis

# OU manuellement
docker run -d --name kaïros-redis -p 6379:6379 redis:7.0-alpine
```

### Fichier .env (Backend)

Créez un fichier `.env` dans `backend/` :

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros
SECRET_KEY=votre_clé_secrète_32_caractères_minimum
ENVIRONMENT=development
REDIS_URL=redis://localhost:6379/0
```

---

## 🎉 C'est Prêt !

Une fois tous les services démarrés :

1. **Ouvrez votre navigateur** : http://localhost:5173
2. **Créez un compte** : Cliquez sur "S'inscrire"
3. **Explorez les modules** : Naviguez vers "Modules"
4. **Testez le chat IA** : Dans un module, utilisez le tutorat IA

**Bon développement ! 🚀**


