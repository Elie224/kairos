# 🚀 Instructions de Migration PostgreSQL - Kaïros

## ✅ Configuration Complète

Vous avez créé la base de données `eduverse` dans PostgreSQL 18. Voici les étapes pour configurer et exécuter les migrations.

## 📋 Étape 1 : Configurer l'Encodage de la Base de Données

**IMPORTANT** : Avant d'exécuter les migrations, configurez l'encodage UTF-8.

### Via psql (Recommandé)

```powershell
# Se connecter à PostgreSQL 18
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d eduverse
```

Dans psql, exécutez :

```sql
-- Configurer l'encodage UTF-8
ALTER DATABASE eduverse SET client_encoding = 'UTF8';

-- Vérifier
SHOW client_encoding;

-- Quitter
\q
```

### Via pgAdmin

1. Ouvrez **pgAdmin**
2. Connectez-vous au serveur **PostgreSQL 18**
3. Clic droit sur la base `eduverse` → **Properties**
4. Onglet **Variables** → Ajoutez :
   - **Name** : `client_encoding`
   - **Value** : `UTF8`
5. Cliquez sur **Save**

## 📋 Étape 2 : Vérifier la Configuration .env

Votre fichier `.env` doit contenir :

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=Kourouma
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse
```

✅ **Votre configuration est correcte !**

## 📋 Étape 3 : Exécuter les Migrations

### Option A : Script PowerShell (Recommandé)

```powershell
cd backend
.\migrate-postgres.ps1
```

### Option B : Script BAT

```cmd
cd backend
migrate-postgres.bat
```

### Option C : Python Direct

```powershell
cd backend
.\venv\Scripts\python.exe scripts\migrate_postgres.py create
```

## 📊 Tables qui Seront Créées

1. **users** - Utilisateurs
   - id, email, username, first_name, last_name, hashed_password, is_active, is_admin, created_at, updated_at

2. **courses** - Cours
   - id, title, description, subject, difficulty, created_at, updated_at

3. **modules** - Modules d'apprentissage
   - id, course_id, title, description, content, order, created_at, updated_at

4. **enrollments** - Inscriptions utilisateur-cours
   - id, user_id, course_id, enrolled_at, completed_at

5. **user_progress** - Progression utilisateur
   - id, user_id, module_id, completed, score, time_spent, started_at, completed_at

## 🔍 Vérification

### Vérifier que les Tables sont Créées

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d eduverse -c "\dt"
```

Vous devriez voir 5 tables listées.

### Vérifier la Structure d'une Table

```sql
\d users
```

## 🏗️ Architecture des Bases de Données

### MongoDB (Principal)
- **Base** : `eduverse` (selon votre config)
- **Collections** : modules, progress, quizzes, exams, users, etc.
- **Usage** : Contenu flexible, progression, quiz, badges, IA

### PostgreSQL (Relationnel)
- **Base** : `eduverse`
- **Tables** : users, courses, modules, enrollments, user_progress
- **Usage** : Relations structurées, inscriptions, progression relationnelle

## 🔧 Résolution des Problèmes

### Erreur : "codec can't decode byte"

**Solution :**
1. Configurez l'encodage UTF-8 sur la base de données (voir Étape 1)
2. Réessayez les migrations

### Erreur : "could not connect to server"

**Vérifiez :**
1. Que le service PostgreSQL 18 est démarré (Services Windows)
2. Le port dans `.env` (5432) correspond au port de PostgreSQL 18
3. Le mot de passe dans `.env` est correct

### Erreur : "password authentication failed"

**Solution :**
Vérifiez que `POSTGRES_PASSWORD=Kourouma` dans `.env` correspond au mot de passe de l'utilisateur `postgres`.

## ✅ Après les Migrations

Une fois les migrations réussies, redémarrez le backend :

```powershell
.\demarrer-backend.bat
```

Vous devriez voir dans les logs :
```
✅ PostgreSQL initialisé avec succès
Connexion PostgreSQL réussie - Version: PostgreSQL 18.x
Tables PostgreSQL initialisées avec succès
```

## 📝 Commandes Utiles

### Réinitialiser les Tables (ATTENTION: Supprime toutes les données)

```powershell
.\venv\Scripts\python.exe scripts\migrate_postgres.py reset
```

### Supprimer les Tables

```powershell
.\venv\Scripts\python.exe scripts\migrate_postgres.py drop
```

### Créer les Tables (si elles n'existent pas)

```powershell
.\venv\Scripts\python.exe scripts\migrate_postgres.py create
```
