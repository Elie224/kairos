# 📋 Comment Afficher les Tables dans pgAdmin

## 🔍 Étapes pour Voir les Tables

D'après votre capture d'écran, vous êtes dans la bonne base de données (`eduverse`), mais vous devez développer le schéma `public` pour voir les tables.

### Étape par Étape :

1. **Dans le panneau de gauche (Object Explorer)** :
   - Vous êtes déjà sur `eduverse` ✅
   - Développez **`Schemas (1)`** (cliquez sur la flèche à gauche)
   - Développez **`public`** (cliquez sur la flèche à gauche)
   - Cliquez sur **`Tables`**

2. **Si vous ne voyez toujours pas les tables** :
   - Clic droit sur **`Tables`**
   - Cliquez sur **`Refresh`** (ou appuyez sur F5)

3. **Vérification alternative** :
   - Clic droit sur **`public`** → **`Query Tool`**
   - Exécutez cette requête SQL :
   ```sql
   SELECT table_name 
   FROM information_schema.tables 
   WHERE table_schema = 'public' 
   AND table_type = 'BASE TABLE'
   ORDER BY table_name;
   ```

## 🔧 Si les Tables N'Apparaissent Toujours Pas

### Solution 1 : Vérifier via Python (Confirmation)

Les tables existent bien (confirmé par le script). Exécutez :

```powershell
cd backend
.\venv\Scripts\python.exe scripts\verify_postgres_tables.py
```

### Solution 2 : Recréer les Tables

Si vraiment elles n'existent pas, recréons-les :

```powershell
cd backend
.\venv\Scripts\python.exe scripts\migrate_postgres.py create
```

### Solution 3 : Vérifier le Schéma

Assurez-vous que les tables sont dans le schéma `public` :

1. Dans pgAdmin, développez `eduverse` → `Schemas` → `public`
2. Si vous voyez d'autres schémas, vérifiez aussi dedans

## 📊 Vérification SQL Directe

Dans pgAdmin, ouvrez le Query Tool et exécutez :

```sql
-- Lister toutes les tables
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Voir les détails d'une table spécifique
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_schema = 'public' 
AND table_name = 'users'
ORDER BY ordinal_position;
```

## ✅ Résumé

1. **Développez** : `eduverse` → `Schemas` → `public` → `Tables`
2. **Rafraîchissez** : Clic droit sur `Tables` → `Refresh` (F5)
3. **Vérifiez** : Les 5 tables doivent apparaître

Les tables existent (confirmé par Python), il faut juste les afficher correctement dans pgAdmin !
