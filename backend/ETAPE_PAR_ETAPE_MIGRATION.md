# 🚀 Migration PostgreSQL - Guide Étape par Étape

## ⚠️ IMPORTANT : Configuration de l'Encodage

**Avant d'exécuter les migrations**, vous devez configurer l'encodage UTF-8 dans PostgreSQL.

## 📋 Étape 1 : Configurer l'Encodage UTF-8

### Option A : Via psql (Recommandé)

Ouvrez PowerShell et exécutez :

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d eduverse
```

**Entrez votre mot de passe** (celui configuré dans `.env` : `Kourouma`)

Dans psql, exécutez ces commandes :

```sql
-- Configurer l'encodage UTF-8
ALTER DATABASE eduverse SET client_encoding = 'UTF8';

-- Vérifier que c'est bien configuré
SHOW client_encoding;

-- Vous devriez voir : UTF8

-- Quitter psql
\q
```

### Option B : Via pgAdmin

1. Ouvrez **pgAdmin**
2. Connectez-vous au serveur **PostgreSQL 18**
3. Clic droit sur la base `eduverse` → **Properties**
4. Onglet **Variables** → Cliquez sur **+**
5. **Name** : `client_encoding`
6. **Value** : `UTF8`
7. Cliquez sur **Save**

## 📋 Étape 2 : Exécuter les Migrations

Une fois l'encodage configuré, exécutez les migrations :

### Option A : Script BAT (Le Plus Simple)

```cmd
cd backend
migrate-postgres-simple.bat
```

### Option B : Python Direct

```powershell
cd backend
.\venv\Scripts\python.exe scripts\migrate_postgres.py create
```

### Option C : Script de Fix et Migration

```powershell
cd backend
.\venv\Scripts\python.exe scripts\fix_encoding_and_migrate.py
```

## ✅ Vérification

Après les migrations, vérifiez que les tables sont créées :

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d eduverse -c "\dt"
```

Vous devriez voir 5 tables :
- `users`
- `courses`
- `modules`
- `enrollments`
- `user_progress`

## 🔧 Si Vous Voyez Encore l'Erreur d'Encodage

1. **Vérifiez que l'encodage est bien configuré** :
   ```sql
   SHOW client_encoding;
   ```
   Doit afficher : `UTF8`

2. **Si ce n'est pas UTF8**, réexécutez :
   ```sql
   ALTER DATABASE eduverse SET client_encoding = 'UTF8';
   ```

3. **Redémarrez le service PostgreSQL 18** (Services Windows)

4. **Réessayez les migrations**

## 📝 Résumé des Commandes

```powershell
# 1. Configurer l'encodage
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d eduverse
# Puis dans psql :
ALTER DATABASE eduverse SET client_encoding = 'UTF8';
\q

# 2. Exécuter les migrations
cd backend
.\venv\Scripts\python.exe scripts\migrate_postgres.py create

# 3. Vérifier
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d eduverse -c "\dt"
```

## ✅ Après les Migrations

Redémarrez le backend :

```powershell
.\demarrer-backend.bat
```

Vous devriez voir dans les logs :
```
✅ PostgreSQL initialisé avec succès
Connexion PostgreSQL réussie - Version: PostgreSQL 18.x
Tables PostgreSQL initialisées avec succès
```
