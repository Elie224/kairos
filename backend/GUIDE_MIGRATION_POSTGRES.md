# 🚀 Guide de Migration PostgreSQL - Kaïros

## ✅ Étape 1 : Vérifier l'Encodage de la Base de Données

Avant d'exécuter les migrations, assurez-vous que la base de données `eduverse` utilise l'encodage UTF-8.

### Via psql (Ligne de Commande)

```powershell
# Se connecter à PostgreSQL 18
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d eduverse

# Dans psql, exécutez :
ALTER DATABASE eduverse SET client_encoding = 'UTF8';
\q
```

### Via pgAdmin

1. Ouvrez pgAdmin
2. Connectez-vous au serveur PostgreSQL 18
3. Clic droit sur la base `eduverse` → **Properties**
4. Onglet **Variables**
5. Cherchez `client_encoding` et définissez-le à `UTF8`
6. Cliquez sur **Save**

## ✅ Étape 2 : Exécuter les Migrations

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

## 📊 Tables Créées

Les migrations créeront les tables suivantes :

1. **users** - Utilisateurs (id, email, username, first_name, last_name, etc.)
2. **courses** - Cours (id, title, description, subject, difficulty)
3. **modules** - Modules d'apprentissage (id, course_id, title, description, content)
4. **enrollments** - Inscriptions utilisateur-cours (id, user_id, course_id, enrolled_at)
5. **user_progress** - Progression utilisateur (id, user_id, module_id, completed, score)

## 🔍 Vérification

### Vérifier que les Tables sont Créées

```powershell
# Via psql
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d eduverse -c "\dt"
```

Vous devriez voir :
```
          List of relations
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+----------
 public | courses         | table | postgres
 public | enrollments     | table | postgres
 public | modules         | table | postgres
 public | user_progress   | table | postgres
 public | users           | table | postgres
```

### Vérifier la Structure d'une Table

```sql
\d users
```

## 🏗️ Architecture des Bases de Données

### MongoDB (Principal)
- **Base** : `kaïros` (ou `eduverse` selon votre config)
- **Usage** : Contenu flexible, modules, progression, quiz, badges, IA

### PostgreSQL (Relationnel)
- **Base** : `eduverse`
- **Usage** : Relations structurées, inscriptions, progression relationnelle

## 🔧 Résolution des Problèmes

### Erreur : "codec can't decode byte"

**Solution :**
```sql
ALTER DATABASE eduverse SET client_encoding = 'UTF8';
```

Puis réessayez les migrations.

### Erreur : "could not connect to server"

**Vérifiez :**
1. Que PostgreSQL 18 est démarré (Services Windows)
2. Le port dans `.env` correspond au port de PostgreSQL 18
3. Le mot de passe dans `.env` est correct

### Erreur : "database does not exist"

**Solution :**
```sql
CREATE DATABASE eduverse
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252';
```

## ✅ Après les Migrations

Une fois les migrations réussies, redémarrez le backend :

```powershell
.\demarrer-backend.bat
```

Vous devriez voir :
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
