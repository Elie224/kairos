# 🚀 Guide de Démarrage du Backend - Kaïros

## 📋 Méthodes de Démarrage

### Méthode 1 : Script Batch (Windows) - Recommandé
```bash
demarrer-backend.bat
```

### Méthode 2 : PowerShell
```powershell
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Méthode 3 : Python Direct
```bash
cd backend
python main.py
```

## ⚙️ Prérequis

1. **Python 3.8+** installé
2. **MongoDB** démarré (optionnel mais recommandé)
3. **PostgreSQL** démarré (optionnel)
4. **Redis** démarré (optionnel mais recommandé pour le cache)

## 🔧 Configuration

Assurez-vous que le fichier `backend/.env` contient au minimum :

```env
# MongoDB (Obligatoire)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros

# JWT Secret (Obligatoire en production)
SECRET_KEY=votre_secret_key_ici

# OpenAI (Optionnel)
OPENAI_API_KEY=sk-proj-...

# PostgreSQL (Optionnel)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse

# Redis (Optionnel)
REDIS_URL=redis://localhost:6379
```

## ✅ Vérification

Une fois démarré, le backend sera accessible sur :
- **API** : http://localhost:8000
- **Documentation Swagger** : http://localhost:8000/docs
- **Documentation ReDoc** : http://localhost:8000/redoc
- **Health Check** : http://localhost:8000/health

## 🐛 Dépannage

### Erreur : "ModuleNotFoundError"
```bash
cd backend
pip install -r requirements.txt
```

### Erreur : "MongoDB connection failed"
- Vérifiez que MongoDB est démarré
- Vérifiez l'URL dans `.env`

### Erreur : "Port 8000 already in use"
- Changez le port : `--port 8001`
- Ou arrêtez le processus utilisant le port 8000

## 📝 Notes

- Le mode `--reload` active le rechargement automatique lors des modifications
- Le backend démarre même si MongoDB/PostgreSQL/Redis ne sont pas disponibles (mode dégradé)
- Consultez les logs pour voir l'état des connexions











