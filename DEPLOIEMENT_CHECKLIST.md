# Checklist de Déploiement Render

## ✅ Préparation GitHub

- [ ] Repository GitHub créé
- [ ] Code poussé sur GitHub
- [ ] `.render.yaml` présent dans le repo
- [ ] `env.example` présent (sans valeurs sensibles)
- [ ] `backend/build.sh` présent et exécutable
- [ ] `.gitignore` à jour (exclut .env, node_modules, venv)
- [ ] `README_DEPLOIEMENT_GITHUB.md` consulté

## ✅ Configuration Render - Backend

- [ ] Service web créé sur Render
- [ ] Repository GitHub connecté
- [ ] **Variables d'environnement configurées** :
  - [ ] `ENVIRONMENT=production`
  - [ ] `MONGODB_URL` (MongoDB Atlas ou autre)
  - [ ] `MONGODB_DB_NAME=kairos`
  - [ ] `SECRET_KEY` (générée avec `secrets.token_urlsafe(32)`)
  - [ ] `OPENAI_API_KEY`
  - [ ] `FRONTEND_URL` (URL du frontend Render)
  - [ ] `ALLOWED_HOSTS=*`
  - [ ] Optionnel : `REDIS_URL`
  - [ ] Optionnel : `POSTGRES_HOST`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
  - [ ] Optionnel : `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- [ ] **Build Command**: `cd backend && pip install -r requirements.txt`
- [ ] **Start Command**: `cd backend && gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
- [ ] **Health Check Path**: `/health`

## ✅ Configuration Render - Frontend

- [ ] Service Static Site créé sur Render
- [ ] Repository GitHub connecté
- [ ] **Variables d'environnement configurées** :
  - [ ] `VITE_API_URL` (URL du backend Render)
- [ ] **Root Directory**: `frontend`
- [ ] **Build Command**: `npm ci && npm run build`
- [ ] **Publish Directory**: `dist`

## ✅ MongoDB Atlas (Recommandé)

- [ ] Cluster MongoDB créé sur Atlas
- [ ] Utilisateur de base de données créé
- [ ] IP de Render autorisée (0.0.0.0/0 ou IPs spécifiques)
- [ ] Connection string récupérée et utilisée dans `MONGODB_URL`
- [ ] Base de données `kairos` créée (ou le nom configuré)

## ✅ Génération SECRET_KEY

- [ ] SECRET_KEY générée avec :
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
- [ ] SECRET_KEY ajoutée aux variables d'environnement Render
- [ ] SECRET_KEY **NE JAMAIS** commitée sur GitHub

## ✅ Déploiement

- [ ] Build backend réussi (vérifier les logs)
- [ ] Build frontend réussi (vérifier les logs)
- [ ] Service backend démarré sans erreur
- [ ] Service frontend déployé

## ✅ Vérifications Post-Déploiement

- [ ] **Health Check Backend** :
  ```bash
  curl https://kairos-backend.onrender.com/health
  ```
  Doit retourner `{"status": "healthy", ...}`

- [ ] **API Docs** :
  ```bash
  curl https://kairos-backend.onrender.com/docs
  ```
  Doit retourner la page de documentation Swagger

- [ ] **Frontend** :
  ```bash
  curl https://kairos-frontend.onrender.com
  ```
  Doit retourner la page HTML

- [ ] **Test Connexion MongoDB** :
  - Vérifier les logs Render pour "Connexion MongoDB réussie"
  - Vérifier dans MongoDB Atlas que des connexions sont actives

- [ ] **Test API** :
  ```bash
  curl https://kairos-backend.onrender.com/api/
  ```
  Doit retourner une réponse JSON

- [ ] **Test Frontend -> Backend** :
  - Ouvrir le frontend dans un navigateur
  - Vérifier qu'il peut communiquer avec le backend
  - Vérifier qu'il n'y a pas d'erreurs CORS dans la console

## ⚠️ Problèmes Courants

### Build échoue

- [ ] Vérifier les logs de build dans Render
- [ ] Vérifier que toutes les dépendances sont dans `requirements.txt` / `package.json`
- [ ] Vérifier la version de Python/Node
- [ ] Vérifier les erreurs de syntaxe dans le code

### Service ne démarre pas

- [ ] Vérifier les logs runtime dans Render
- [ ] Vérifier que toutes les variables d'environnement sont configurées
- [ ] Vérifier que le `startCommand` est correct
- [ ] Vérifier que le port est `$PORT` et non un port fixe

### Erreurs de connexion MongoDB

- [ ] Vérifier que l'IP de Render est autorisée dans MongoDB Atlas
- [ ] Vérifier que `MONGODB_URL` est correct
- [ ] Vérifier les credentials MongoDB
- [ ] Vérifier que le cluster MongoDB est actif

### Erreurs CORS

- [ ] Vérifier que `FRONTEND_URL` est correct dans le backend
- [ ] Vérifier que `ALLOWED_HOSTS` inclut le domaine du frontend
- [ ] Vérifier la configuration CORS dans `main.py`
- [ ] Vérifier que `VITE_API_URL` est correct dans le frontend

### Erreurs 404 sur les routes API

- [ ] Vérifier que le proxy Vite est correctement configuré
- [ ] Vérifier que `VITE_API_URL` pointe vers le bon backend
- [ ] Vérifier que les routes API commencent par `/api` ou sont configurées correctement

## 📚 Documentation

- [ ] `DEPLOIEMENT_RENDER.md` consulté
- [ ] `README_DEPLOIEMENT_GITHUB.md` consulté
- [ ] `env.example` consulté pour la liste des variables

## 🔗 Liens Utiles

- Render Dashboard: https://dashboard.render.com
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas
- OpenAI API: https://platform.openai.com/docs

## 📝 Notes

- Les services Render gratuits peuvent avoir des limitations (sleep après inactivité, timeouts, etc.)
- Pour la production, considérer les plans payants
- Les builds peuvent prendre 5-10 minutes
- Le premier démarrage peut être plus lent (cold start)
