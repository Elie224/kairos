# 🔧 Configuration PostgreSQL pour Kaïros

## 📋 Prérequis

Vous avez installé **PostgreSQL 13** et **PostgreSQL 18** sur votre système Windows.

## 🎯 Objectif

Configurer PostgreSQL pour que l'application Kaïros puisse s'y connecter sans erreur d'encodage.

## 🔍 Problème Identifié

L'erreur `'utf-8' codec can't decode byte 0xe9 in position 103: invalid continuation byte` indique un problème d'encodage lors de la connexion PostgreSQL.

## ✅ Solution

### 1. Choisir une Version de PostgreSQL

**Recommandation : Utilisez PostgreSQL 18** (version la plus récente)

Si vous préférez PostgreSQL 13, c'est également possible, mais PostgreSQL 18 est recommandé pour de meilleures performances.

### 2. Vérifier les Services PostgreSQL

Ouvrez **Services** (services.msc) et vérifiez que :
- **PostgreSQL 18** est démarré (ou **PostgreSQL 13** si vous l'utilisez)
- L'autre version est **arrêtée** pour éviter les conflits de port

### 3. Identifier le Port PostgreSQL

Par défaut :
- **PostgreSQL 13** : Port `5432`
- **PostgreSQL 18** : Port `5433` (ou `5432` si 13 est arrêté)

**Vérifiez le port utilisé :**

```powershell
# Dans PowerShell, vérifiez les ports utilisés
netstat -ano | findstr :5432
netstat -ano | findstr :5433
```

### 4. Créer la Base de Données

#### Option A : Via pgAdmin (Interface Graphique)

1. Ouvrez **pgAdmin** (pour PostgreSQL 18 ou 13)
2. Connectez-vous au serveur PostgreSQL
3. Clic droit sur **Databases** → **Create** → **Database**
4. Nom : `eduverse`
5. Owner : `postgres`
6. Encoding : **UTF8**
7. Cliquez sur **Save**

#### Option B : Via psql (Ligne de Commande)

```powershell
# Pour PostgreSQL 18 (port 5433 par défaut, ou 5432 si 13 est arrêté)
# Trouvez le chemin d'installation, par exemple :
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -p 5432

# Ou pour PostgreSQL 13
& "C:\Program Files\PostgreSQL\13\bin\psql.exe" -U postgres -p 5432
```

Dans psql, exécutez :

```sql
-- Créer la base de données avec encodage UTF-8
CREATE DATABASE eduverse
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Vérifier que la base existe
\l

-- Quitter psql
\q
```

### 5. Configurer le Fichier .env

Créez ou modifiez le fichier `.env` dans le dossier `backend/` :

```env
# PostgreSQL Configuration
# Utilisez PostgreSQL 18 (recommandé) ou PostgreSQL 13
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe_postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse
```

**Important :**
- Remplacez `votre_mot_de_passe_postgres` par le mot de passe que vous avez défini lors de l'installation
- Si PostgreSQL 18 utilise le port 5433, changez `POSTGRES_PORT=5433`
- Si PostgreSQL 13 utilise le port 5432, gardez `POSTGRES_PORT=5432`

### 6. Tester la Connexion

#### Test Manuel avec psql

```powershell
# Pour PostgreSQL 18
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d eduverse -p 5432

# Pour PostgreSQL 13
& "C:\Program Files\PostgreSQL\13\bin\psql.exe" -U postgres -d eduverse -p 5432
```

Si la connexion fonctionne, vous verrez :
```
psql (18.x)
Type "help" for help.

eduverse=#
```

#### Test avec le Script Python

```powershell
cd backend
.\venv\Scripts\python.exe scripts\test_connections.py
```

### 7. Redémarrer le Backend

```powershell
# Arrêtez le backend actuel (Ctrl+C)
# Puis redémarrez
.\demarrer-backend.bat
```

Vous devriez voir :
```
✅ PostgreSQL initialisé avec succès
Connexion PostgreSQL réussie - Version: PostgreSQL 18.x
Tables PostgreSQL initialisées avec succès
```

## 🔧 Résolution des Problèmes

### Problème 1 : "password authentication failed"

**Solution :**
1. Vérifiez le mot de passe dans `.env`
2. Si vous avez oublié le mot de passe, réinitialisez-le :
   ```powershell
   # Modifiez le fichier pg_hba.conf pour autoriser les connexions locales sans mot de passe
   # Puis redémarrez PostgreSQL
   ```

### Problème 2 : "database does not exist"

**Solution :**
```sql
-- Créez la base de données
CREATE DATABASE eduverse;
```

### Problème 3 : "could not connect to server"

**Solution :**
1. Vérifiez que le service PostgreSQL est démarré
2. Vérifiez le port dans `.env`
3. Vérifiez que le firewall n'bloque pas le port

### Problème 4 : Conflit de Ports (13 et 18)

**Solution :**
1. Arrêtez un des deux services PostgreSQL
2. Modifiez le port de l'un des deux dans `postgresql.conf`
3. Utilisez le port correct dans `.env`

## 📝 Configuration Recommandée

### Pour PostgreSQL 18 (Recommandé)

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse
```

### Pour PostgreSQL 13

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse
```

## ✅ Vérification Finale

Après configuration, le backend devrait afficher :

```
✅ PostgreSQL initialisé avec succès
Connexion PostgreSQL réussie - Version: PostgreSQL 18.x (ou 13.x)
Tables PostgreSQL initialisées avec succès
```

Si vous voyez encore des erreurs, consultez les logs du backend pour plus de détails.
