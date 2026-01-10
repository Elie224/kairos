# 🔧 Résolution des Connexions Refusées

Ce document explique comment résoudre les problèmes de connexions refusées aux bases de données.

## 🔍 Diagnostic

D'après les logs, voici l'état actuel :

- ✅ **MongoDB** : Connecté avec succès
- ⚠️ **PostgreSQL** : Initialisé mais connexion réelle non vérifiée
- ❌ **Redis** : Connexion refusée (port 6379)

## 📋 Test des Connexions

Exécutez ce script pour tester toutes les connexions :

```bash
cd backend
python scripts/test_connections.py
```

Ou utilisez l'endpoint de santé de l'API :

```bash
curl http://localhost:8000/health
```

## 🚀 Solutions

### 1. Redis - Connexion Refusée

**Symptôme** : `Error 22 connecting to localhost:6379. Le système distant a refusé la connexion réseau`

**Solution** :

#### Option A : Docker (Recommandé)
```bash
docker run -d -p 6379:6379 --name kairos-redis redis:7-alpine
```

#### Option B : Installation Windows
1. Téléchargez Redis pour Windows : https://github.com/microsoftarchive/redis/releases
2. Démarrez le service Redis

#### Configuration
Ajoutez dans `backend/.env` :
```env
REDIS_URL=redis://localhost:6379/0
```

### 2. PostgreSQL - Vérification de la Connexion

**Symptôme** : Les logs indiquent "PostgreSQL initialisé avec succès" mais la connexion réelle n'est pas testée

**Solution** :

#### Option A : Docker (Recommandé)
```bash
docker run -d -p 5432:5432 \
  -e POSTGRES_DB=eduverse \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  --name kairos-postgres \
  postgres:15-alpine
```

#### Option B : Installation Windows
1. Téléchargez PostgreSQL : https://www.postgresql.org/download/windows/
2. Installez et démarrez le service PostgreSQL
3. Créez la base de données :
```sql
CREATE DATABASE eduverse;
```

#### Configuration
Vérifiez dans `backend/.env` :
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse
```

### 3. MongoDB - Vérification

**Symptôme** : MongoDB semble fonctionner mais vérifions

**Test** :
```bash
mongosh mongodb://localhost:27017
```

Si cela échoue, démarrez MongoDB :
```bash
docker run -d -p 27017:27017 --name kairos-mongo mongo:7.0
```

## 🔍 Vérification des Ports

Vérifiez si les ports sont ouverts :

### Windows PowerShell
```powershell
# MongoDB
Test-NetConnection -ComputerName localhost -Port 27017

# PostgreSQL
Test-NetConnection -ComputerName localhost -Port 5432

# Redis
Test-NetConnection -ComputerName localhost -Port 6379
```

### Linux/Mac
```bash
# MongoDB
nc -zv localhost 27017

# PostgreSQL
nc -zv localhost 5432

# Redis
nc -zv localhost 6379
```

## 📝 Fichier .env Complet

Créez `backend/.env` avec ce contenu :

```env
# MongoDB (OBLIGATOIRE)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros

# PostgreSQL (OPTIONNEL)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse

# Redis (OPTIONNEL mais recommandé)
REDIS_URL=redis://localhost:6379/0

# Sécurité
SECRET_KEY=votre_cle_secrete_ici

# OpenAI
OPENAI_API_KEY=votre_cle_openai_ici

# Environnement
ENVIRONMENT=development
```

## 🐳 Docker Compose (Solution Complète)

Pour démarrer toutes les bases de données d'un coup, utilisez Docker Compose :

```bash
# Depuis la racine du projet
docker-compose up -d mongodb redis postgres
```

Ou créez un fichier `docker-compose.databases.yml` :

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7.0
    container_name: kairos-mongo
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    container_name: kairos-postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=eduverse
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: kairos-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  mongo-data:
  postgres-data:
  redis-data:
```

Puis :
```bash
docker-compose -f docker-compose.databases.yml up -d
```

## ✅ Vérification Finale

Après avoir démarré toutes les bases de données, redémarrez le backend :

```bash
cd backend
python main.py
```

Vous devriez voir :
- ✅ MongoDB connecté
- ✅ PostgreSQL connecté (avec test de connexion réel)
- ✅ Redis connecté

Si des connexions sont toujours refusées, vérifiez :
1. Les services sont bien démarrés
2. Les ports ne sont pas bloqués par un firewall
3. Les variables d'environnement dans `.env` sont correctes








