# 🔧 Configuration des Variables d'Environnement

Ce document décrit toutes les variables d'environnement nécessaires pour configurer le backend Kaïros.

## 📋 Créer le fichier .env

Créez un fichier `.env` dans le répertoire `backend/` avec les variables suivantes :

```env
# ============================================
# Configuration Kaïros Backend
# ============================================

# ============================================
# MongoDB (OBLIGATOIRE)
# ============================================
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros
MONGODB_TIMEOUT_MS=5000

# ============================================
# PostgreSQL (OPTIONNEL mais recommandé)
# ============================================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse

# ============================================
# Redis (OPTIONNEL mais recommandé pour le cache)
# ============================================
REDIS_URL=redis://localhost:6379/0

# ============================================
# Sécurité JWT (OBLIGATOIRE en production)
# ============================================
# Générez une clé secrète avec: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=

# ============================================
# OpenAI API (OBLIGATOIRE pour les fonctionnalités IA)
# ============================================
OPENAI_API_KEY=

# ============================================
# Environnement
# ============================================
ENVIRONMENT=development
# Options: development, production

# ============================================
# CORS et Sécurité
# ============================================
ALLOWED_HOSTS=localhost,127.0.0.1
ENABLE_CSRF=false

# ============================================
# Frontend URL
# ============================================
FRONTEND_URL=http://localhost:5173

# ============================================
# Stripe (OPTIONNEL - pour les paiements)
# ============================================
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PREMIUM_PRICE_ID=
STRIPE_ENTERPRISE_PRICE_ID=

# ============================================
# AI Cost Guard (Limites de coûts IA)
# ============================================
AI_MONTHLY_TOKEN_LIMIT=10000000
AI_MONTHLY_COST_LIMIT_EUR=50.0
```

## 🚀 Démarrage des Bases de Données

### MongoDB

**Option 1: Docker (Recommandé)**
```bash
docker run -d -p 27017:27017 --name kaïros-mongo mongo:7.0
```

**Option 2: Installation locale**
- Téléchargez MongoDB depuis https://www.mongodb.com/try/download/community
- Démarrez le service MongoDB

### PostgreSQL

**Option 1: Docker (Recommandé)**
```bash
docker run -d -p 5432:5432 \
  -e POSTGRES_DB=eduverse \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  --name kaïros-postgres \
  postgres:15-alpine
```

**Option 2: Installation locale**
- Téléchargez PostgreSQL depuis https://www.postgresql.org/download/
- Créez la base de données: `CREATE DATABASE eduverse;`

### Redis

**Option 1: Docker (Recommandé)**
```bash
docker run -d -p 6379:6379 --name kaïros-redis redis:7-alpine
```

**Option 2: Installation locale**
- Windows: Téléchargez Redis depuis https://github.com/microsoftarchive/redis/releases
- Linux/Mac: `sudo apt-get install redis-server` ou `brew install redis`

## 🔍 Vérification de la Configuration

Utilisez le script de diagnostic pour vérifier toutes les bases de données :

```bash
cd backend
python scripts/check_databases.py
```

Ou utilisez l'endpoint de santé de l'API :

```bash
curl http://localhost:8000/health
```

## ⚠️ Problèmes Courants

### MongoDB ne se connecte pas
- Vérifiez que MongoDB est démarré: `docker ps` ou vérifiez le service Windows
- Vérifiez `MONGODB_URL` dans `.env`
- Testez la connexion: `mongosh mongodb://localhost:27017`

### PostgreSQL ne se connecte pas
- Vérifiez que PostgreSQL est démarré
- Créez la base de données si elle n'existe pas
- Vérifiez les variables `POSTGRES_*` dans `.env`

### Redis ne se connecte pas
- Vérifiez que Redis est démarré: `docker ps` ou vérifiez le service
- Vérifiez `REDIS_URL` dans `.env`
- Testez la connexion: `redis-cli ping`

## 📝 Notes Importantes

1. **MongoDB est obligatoire** - L'application ne fonctionnera pas sans MongoDB
2. **PostgreSQL est optionnel** - L'application fonctionne avec MongoDB uniquement
3. **Redis est optionnel** - L'application fonctionne sans cache mais avec des performances réduites
4. **SECRET_KEY est obligatoire en production** - Générez une clé sécurisée
5. **OPENAI_API_KEY est nécessaire** - Pour les fonctionnalités IA








