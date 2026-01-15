# 🐘 Configuration PostgreSQL sur Render

## Problème Actuel

Les logs montrent que PostgreSQL essaie de se connecter à `localhost:5432`, mais sur Render, il n'y a pas de serveur PostgreSQL local. Il faut utiliser un service PostgreSQL externe.

```
2026-01-15 15:09:06,176 - app.database.postgres - ERROR - ❌ PostgreSQL n'est pas accessible à localhost:5432
```

## Solutions pour Activer PostgreSQL sur Render

### Option 1 : Service PostgreSQL Render (Recommandé)

1. **Créer un service PostgreSQL sur Render** :
   - Allez sur [Render Dashboard](https://dashboard.render.com)
   - Cliquez sur "New +" → "PostgreSQL"
   - Choisissez un nom (ex: `kairos-postgres`)
   - Sélectionnez un plan (Free tier disponible)
   - Cliquez sur "Create Database"

2. **Récupérer les informations de connexion** :
   - Une fois créé, Render affiche :
     - **Internal Database URL** (pour les services Render)
     - **External Database URL** (pour les connexions externes)
   
3. **Configurer les variables d'environnement** :
   - Dans votre service backend Render, allez dans "Environment"
   - Ajoutez/modifiez ces variables :
   
   ```
   POSTGRES_HOST=dpg-xxxxx-a.oregon-postgres.render.com
   POSTGRES_PORT=5432
   POSTGRES_USER=kairos_user
   POSTGRES_PASSWORD=votre_mot_de_passe
   POSTGRES_DB=kairos_db
   ```
   
   **OU** utilisez directement l'URL complète :
   
   ```
   POSTGRES_URL=postgresql://kairos_user:password@dpg-xxxxx-a.oregon-postgres.render.com:5432/kairos_db
   ```

### Option 2 : ElephantSQL (Gratuit jusqu'à 20MB)

1. **Créer un compte** :
   - Allez sur [ElephantSQL](https://www.elephantsql.com/)
   - Créez un compte gratuit
   - Créez une nouvelle instance (plan "Tiny Turtle" gratuit)

2. **Récupérer les informations** :
   - Dans le dashboard ElephantSQL, cliquez sur votre instance
   - Copiez les informations :
     - **Server** : `xxxxx.elephantsql.com`
     - **User & Default database** : `xxxxx`
     - **Password** : (affiché dans le dashboard)
     - **Port** : `5432`

3. **Configurer dans Render** :
   ```
   POSTGRES_HOST=xxxxx.elephantsql.com
   POSTGRES_PORT=5432
   POSTGRES_USER=xxxxx
   POSTGRES_PASSWORD=votre_mot_de_passe
   POSTGRES_DB=xxxxx
   ```

### Option 3 : Supabase (Gratuit jusqu'à 500MB)

1. **Créer un projet** :
   - Allez sur [Supabase](https://supabase.com/)
   - Créez un nouveau projet
   - Attendez que la base de données soit prête

2. **Récupérer les informations** :
   - Allez dans "Settings" → "Database"
   - Copiez :
     - **Host** : `db.xxxxx.supabase.co`
     - **Port** : `5432`
     - **Database** : `postgres`
     - **User** : `postgres`
     - **Password** : (affiché dans les paramètres)

3. **Configurer dans Render** :
   ```
   POSTGRES_HOST=db.xxxxx.supabase.co
   POSTGRES_PORT=5432
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=votre_mot_de_passe
   POSTGRES_DB=postgres
   ```

## Configuration dans Render

### Étapes pour Configurer les Variables

1. **Allez dans votre service backend Render** :
   - Ouvrez votre service backend sur [Render Dashboard](https://dashboard.render.com)
   - Cliquez sur "Environment" dans le menu de gauche

2. **Ajoutez/Modifiez les variables** :
   - Cliquez sur "Add Environment Variable"
   - Ajoutez chaque variable une par une :
     - `POSTGRES_HOST` : Le hostname du serveur PostgreSQL
     - `POSTGRES_PORT` : `5432` (généralement)
     - `POSTGRES_USER` : Le nom d'utilisateur
     - `POSTGRES_PASSWORD` : Le mot de passe
     - `POSTGRES_DB` : Le nom de la base de données

3. **Redéployez** :
   - Après avoir ajouté les variables, Render redéploiera automatiquement
   - Vérifiez les logs pour confirmer la connexion :
     ```
     ✅ PostgreSQL tables initialisées avec succès
     ```

## Vérification

Après configuration, les logs devraient afficher :

```
✅ Connexion PostgreSQL réussie - Version: PostgreSQL X.X
✅ PostgreSQL tables initialisées avec succès
```

Au lieu de :

```
❌ PostgreSQL n'est pas accessible à localhost:5432
```

## Notes Importantes

- **Ne jamais utiliser `localhost` en production** : Sur Render, `localhost` pointe vers le conteneur lui-même, pas vers un service externe
- **Sécurité** : Ne partagez jamais vos mots de passe PostgreSQL publiquement
- **Backup** : Configurez des sauvegardes automatiques si possible (ElephantSQL et Supabase le font automatiquement)
- **Limites** : Les plans gratuits ont des limites (taille, connexions, etc.)

## Support

Si vous avez des problèmes :
1. Vérifiez que toutes les variables sont correctement configurées
2. Vérifiez que le service PostgreSQL est accessible depuis Internet (pas seulement en interne)
3. Vérifiez les logs Render pour les erreurs de connexion
4. Testez la connexion avec un client PostgreSQL (pgAdmin, DBeaver, etc.)
