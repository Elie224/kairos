# 🚀 Comment Lancer le Backend - Kaïros

## 📍 Depuis le répertoire backend

Si vous êtes déjà dans `backend/` :

```powershell
python main.py
```

OU

```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📍 Depuis la racine du projet

Si vous êtes à la racine (`Kairós/`) :

```powershell
cd backend
python main.py
```

OU utilisez le script batch :

```powershell
.\demarrer-backend.bat
```

## ✅ Vérification

Une fois démarré, le backend sera accessible sur :
- **API** : http://localhost:8000
- **Documentation Swagger** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health

## ⚠️ Erreurs Corrigées

- ✅ `logging_utils` supprimé de `auth_service.py`
- ✅ `login_lockout` supprimé de `auth_service.py`
- ✅ `PDFService` supprimé de `exam.py`

Le backend devrait maintenant démarrer sans erreur ! 🎉











