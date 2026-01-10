# Guide de Déploiement sur Render

Ce guide explique comment déployer l'application Kaïros sur Render.

## 📋 Prérequis

1. Compte GitHub avec le code poussé sur un repository
2. Compte Render (https://render.com)
3. Compte MongoDB Atlas (recommandé pour la production) ou MongoDB hébergé
4. Clé API OpenAI
5. Optionnel : Redis pour le cache

## 🚀 Étapes de Déploiement

### 1. Préparer le Repository GitHub

```bash
# Vérifier que tous les fichiers sont commités
git status

# Ajouter les fichiers de configuration
git add .render.yaml
git add env.example
git add backend/build.sh
git add .gitignore

# Commit
git commit -m "Préparation déploiement Render"

# Push vers GitHub
git push origin main
```

### 2. Configuration sur Render

#### 2.1 Créer le Service Backend

1. Aller sur https://dashboard.render.com
2. Cliquer sur "New +" > "Blueprint"
3. Connecter votre repository GitHub
4. Render détectera automatiquement le fichier `.render.yaml`
5. Cliquer sur "Apply" pour créer les services

**OU** créer manuellement :

1. "New +" > "Web Service"
2. Connecter votre repository GitHub
3. Configuration :
   - **Name**: `kairos-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`
   - **Health Check Path**: `/health`

#### 2.2 Créer le Service Frontend

1. "New +" > "Static Site"
2. Connecter votre repository GitHub
3. Configuration :
   - **Name**: `kairos-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm ci && npm run build`
   - **Publish Directory**: `dist`
   - **Environment**: `Node`

### 3. Configuration des Variables d'Environnement

#### Backend (dans Render Dashboard > Service > Environment)

```bash
# Obligatoires
ENVIRONMENT=production
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/kairos?retryWrites=true&w=majority
MONGODB_DB_NAME=kairos
SECRET_KEY=<générer-une-clé-secure-avec-secrets.token_urlsafe(32)>
OPENAI_API_KEY=sk-...
FRONTEND_URL=https://kairos-frontend.onrender.com

# Optionnels
REDIS_URL=redis://...
POSTGRES_HOST=...
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=...
STRIPE_SECRET_KEY=sk-...
STRIPE_WEBHOOK_SECRET=whsec_...
ALLOWED_HOSTS=*
```

#### Frontend (dans Render Dashboard > Service > Environment)

```bash
VITE_API_URL=https://kairos-backend.onrender.com
```

**Important**: Pour le frontend, vous devez aussi mettre à jour `vite.config.ts` pour utiliser cette variable.

### 4. Générer SECRET_KEY

Pour générer une SECRET_KEY sécurisée :

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Ou en ligne de commande :
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Configuration MongoDB Atlas (Recommandé)

1. Créer un cluster gratuit sur https://www.mongodb.com/cloud/atlas
2. Créer un utilisateur de base de données
3. Ajouter l'IP de Render (0.0.0.0/0 pour accepter toutes les IPs, ou les IPs spécifiques de Render)
4. Récupérer la connection string et l'utiliser pour `MONGODB_URL`

### 6. Déploiement

1. Après avoir configuré toutes les variables d'environnement
2. Cliquer sur "Manual Deploy" > "Deploy latest commit"
3. Attendre la fin du build et du déploiement
4. Vérifier les logs pour s'assurer qu'il n'y a pas d'erreurs

## 🔍 Vérification

### Endpoints de Santé

- Backend: `https://kairos-backend.onrender.com/health`
- Backend Docs: `https://kairos-backend.onrender.com/docs`

### Vérifier les Logs

Dans Render Dashboard > Service > Logs, vérifier :
- ✅ Build réussi
- ✅ Service démarré sans erreur
- ✅ Health check réussi
- ✅ Connexions MongoDB réussies

## 🔧 Configuration Vite pour la Production

Mettre à jour `frontend/vite.config.ts` :

```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  // ... reste de la config
})
```

## ⚠️ Points Importants

1. **Timeout**: Render a un timeout de 75 secondes pour les requêtes. Les opérations longues (génération TD/TP) peuvent nécessiter des ajustements.

2. **Stockage**: Les fichiers uploadés ne persistent pas sur Render. Utiliser un service de stockage externe (AWS S3, Cloudinary) pour la production.

3. **Redis**: Render propose un service Redis. Créer un service Redis sur Render et utiliser son URL.

4. **PostgreSQL**: Si nécessaire, créer un service PostgreSQL sur Render.

5. **Build Timeout**: Si le build prend plus de 10 minutes, considérer optimiser les dépendances.

6. **CORS**: S'assurer que `FRONTEND_URL` est correctement configuré pour éviter les erreurs CORS.

## 🐛 Dépannage

### Build échoue

- Vérifier les logs de build dans Render
- Vérifier que toutes les dépendances sont dans `requirements.txt` ou `package.json`
- Vérifier la version de Python/Node dans `.render.yaml`

### Service ne démarre pas

- Vérifier les logs de runtime
- Vérifier que toutes les variables d'environnement sont configurées
- Vérifier que le `startCommand` est correct

### Erreurs de connexion MongoDB

- Vérifier que l'IP de Render est autorisée dans MongoDB Atlas
- Vérifier que `MONGODB_URL` est correct
- Vérifier les credentials MongoDB

### Erreurs CORS

- Vérifier que `FRONTEND_URL` est correct dans le backend
- Vérifier que `ALLOWED_HOSTS` inclut le domaine du frontend
- Vérifier la configuration CORS dans `main.py`

## 📚 Ressources

- [Documentation Render](https://render.com/docs)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [OpenAI API](https://platform.openai.com/docs)
