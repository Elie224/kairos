# 🗄️ Guide de Migration PostgreSQL - Kaïros

## 📋 Prérequis

1. **PostgreSQL installé** et en cours d'exécution
2. **Base de données créée** (par défaut: `eduverse`)
3. **Variables d'environnement configurées** dans `backend/.env`

## ⚙️ Configuration

Ajoutez ces variables dans `backend/.env` :

```env
# PostgreSQL Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse
```

## 🚀 Création des Tables

### Méthode 1 : Script de migration (Recommandé)

```bash
cd backend
python scripts/migrate_postgres.py create
```

### Méthode 2 : Automatique au démarrage

Les tables sont créées automatiquement au démarrage de l'application si PostgreSQL est configuré.

### Méthode 3 : Python direct

```bash
cd backend
python -c "from app.database.migrations import create_tables; create_tables()"
```

## 📊 Tables Créées

Les tables suivantes seront créées :

1. **users** - Utilisateurs
2. **courses** - Cours
3. **modules** - Modules d'apprentissage
4. **enrollments** - Inscriptions utilisateur-cours
5. **user_progress** - Progression utilisateur

## 🔄 Commandes Disponibles

### Créer les tables
```bash
python scripts/migrate_postgres.py create
```

### Supprimer les tables (ATTENTION: supprime toutes les données)
```bash
python scripts/migrate_postgres.py drop
```

### Reset complet (supprimer + recréer)
```bash
python scripts/migrate_postgres.py reset
```

## ✅ Vérification

Pour vérifier que les tables sont créées :

```sql
-- Se connecter à PostgreSQL
psql -U postgres -d eduverse

-- Lister les tables
\dt

-- Vérifier la structure d'une table
\d users
```

## 🔧 Dépannage

### Erreur : "could not connect to server"
- Vérifiez que PostgreSQL est démarré
- Vérifiez les variables d'environnement (host, port)

### Erreur : "database does not exist"
- Créez la base de données : `CREATE DATABASE eduverse;`

### Erreur : "password authentication failed"
- Vérifiez le mot de passe dans `.env`

## 📝 Notes

- Les tables sont créées automatiquement au démarrage si PostgreSQL est configuré
- MongoDB reste la base principale pour le contenu flexible
- PostgreSQL est utilisé pour les relations structurées
- Les deux bases fonctionnent en parallèle sans conflit











