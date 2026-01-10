# 🌐 Accès à l'Application Kaïros

## ⚠️ Important : Adresses Correctes

Le serveur écoute sur `0.0.0.0:8000` (toutes les interfaces), mais pour y accéder depuis votre navigateur, vous devez utiliser **`localhost`** ou **`127.0.0.1`**.

---

## ✅ Adresses Correctes

### Backend API
- ✅ **http://localhost:8000**
- ✅ **http://127.0.0.1:8000**

### Documentation API (Swagger)
- ✅ **http://localhost:8000/docs**
- ✅ **http://127.0.0.1:8000/docs**

### Health Check
- ✅ **http://localhost:8000/health**
- ✅ **http://127.0.0.1:8000/health**

### Frontend (une fois démarré)
- ✅ **http://localhost:5173**
- ✅ **http://127.0.0.1:5173**

---

## ❌ Adresses Incorrectes

- ❌ **http://0.0.0.0:8000** ← Ne fonctionne pas dans le navigateur
- ❌ **http://0.0.0.0:5173** ← Ne fonctionne pas dans le navigateur

---

## 🔍 Pourquoi ?

- `0.0.0.0` signifie "écouter sur toutes les interfaces réseau"
- C'est utilisé par le serveur pour accepter les connexions
- Mais depuis votre navigateur, vous devez utiliser `localhost` ou `127.0.0.1`

---

## ✅ Test Rapide

1. **Ouvrez votre navigateur**
2. **Allez sur** : http://localhost:8000/health
3. **Vous devriez voir** : `{"status": "healthy", ...}`

---

## 📝 Résumé

| Service | URL Correcte | Description |
|---------|-------------|-------------|
| Backend | http://localhost:8000 | API FastAPI |
| API Docs | http://localhost:8000/docs | Documentation Swagger |
| Health | http://localhost:8000/health | État des services |
| Frontend | http://localhost:5173 | Application React |

---

**Utilisez toujours `localhost` ou `127.0.0.1` dans votre navigateur ! 🚀**
