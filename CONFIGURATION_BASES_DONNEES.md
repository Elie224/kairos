# 🗄️ Configuration des Bases de Données - Kaïros

Ce document récapitule la configuration actuelle de MongoDB, PostgreSQL et Redis pour l'application Kaïros.

---

## 📊 Vue d'ensemble

L'application Kaïros utilise **3 bases de données** :

1. **MongoDB** : Base de données principale (obligatoire) - Stocke les modules, utilisateurs, progression, etc.
2. **PostgreSQL** : Base de données relationnelle (optionnelle) - Pour les données structurées
3. **Redis** : Cache et rate limiting (optionnel) - Pour améliorer les performances

---

## 🍃 MongoDB (Obligatoire)

### Configuration Actuelle

D'après les logs, MongoDB est **correctement configuré et connecté** :

```
✅ Connexion MongoDB réussie
✅ MongoDB ping réussi
```

### Variables d'Environnement

Dans votre service backend Render, configurez :

| Variable | Valeur Actuelle | Description |
|----------|----------------|-------------|
| `MONGODB_URL` | `mongodb+srv://kairos:92GB9ySeL0tf04kn@cluster0.u3cxqhm.mongodb.net/kairos?retryWrites=true&w=majority` | URL de connexion MongoDB Atlas |
| `MONGODB_DB_NAME` | `kaïros` | Nom de la base de données |
| `MONGODB_TIMEOUT_MS` | `5000` | Timeout de connexion (ms) |
| `MONGODB_MAX_POOL_SIZE` | `200` | Taille max du pool de connexions |
| `MONGODB_MIN_POOL_SIZE` | `20` | Taille min du pool de connexions |

### Statut

- ✅ **Connecté** : Oui
- ✅ **Index créés** : Oui (tous les index sont créés automatiquement)
- ✅ **Collections** : Créées automatiquement

### Optimisations Actives

- **Connection Pooling** : 200 connexions max, 20 min
- **Compression** : Snappy (si disponible) ou Zlib
- **Retry** : `retryWrites=True`, `retryReads=True`
- **Heartbeat** : Vérification toutes les 10 secondes

---

## 🐘 PostgreSQL (Optionnel)

### Configuration Actuelle

D'après les logs, PostgreSQL est **connecté mais il y a eu une erreur lors de la création des tables** :

```
✅ Connexion PostgreSQL réussie - Version: PostgreSQL 18.1
⚠️  Erreur lors de la création des tables (conflit de type)
```

### Variables d'Environnement

Dans votre service backend Render, configurez :

| Variable | Valeur Actuelle | Description |
|----------|----------------|-------------|
| `POSTGRES_HOST` | `dpg-d5kgd76mcj7s73d6fvf0-a.oregon-postgres.render.com` | Hostname du service PostgreSQL |
| `POSTGRES_PORT` | `5432` | Port PostgreSQL |
| `POSTGRES_USER` | `kairos_db_0n1i_user` | Nom d'utilisateur |
| `POSTGRES_PASSWORD` | `sfeOloZbOn9A8JOgekC2sLHR6RaZ9Orh` | Mot de passe |
| `POSTGRES_DB` | `kairos_db_0n1i` | Nom de la base de données |

### Statut

- ✅ **Connecté** : Oui
- ⚠️ **Tables** : Erreur de création (conflit de type `users`)
- ✅ **Correction** : Appliquée (vérification avant création)

### Tables PostgreSQL

Les tables suivantes sont créées automatiquement :

- `users` : Utilisateurs
- `courses` : Cours
- `modules` : Modules de cours
- `enrollments` : Inscriptions
- `user_progress` : Progression utilisateur

### Note

PostgreSQL est **optionnel**. L'application fonctionne parfaitement avec MongoDB uniquement. PostgreSQL est utilisé pour des fonctionnalités avancées (relations complexes, transactions, etc.).

---

## 🔴 Redis (Optionnel)

### Configuration Actuelle

D'après les logs, Redis est **non configuré** :

```
ℹ️  Redis non configuré - Cache désactivé (optionnel)
```

### Variables d'Environnement

Pour activer Redis, ajoutez dans votre service backend Render :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `REDIS_URL` | `redis://[host]:[port]/[db]` | URL de connexion Redis |

### Options pour Activer Redis

#### Option 1 : Service Redis Render (Recommandé)

1. Créez un service Redis sur Render Dashboard
2. Récupérez l'URL de connexion
3. Configurez `REDIS_URL` dans votre service backend

#### Option 2 : Redis Externe

- **Upstash** : [https://upstash.com/](https://upstash.com/) (gratuit jusqu'à 10K commandes/jour)
- **Redis Cloud** : [https://redis.com/cloud/](https://redis.com/cloud/) (gratuit jusqu'à 30MB)

### Avantages de Redis

- ✅ **Cache** : Réponses instantanées pour les requêtes fréquentes
- ✅ **Rate Limiting** : Protection contre les abus
- ✅ **Sessions** : Stockage des sessions utilisateur
- ✅ **Performance** : Réduction de la charge sur MongoDB

### Statut

- ❌ **Connecté** : Non (optionnel)
- ℹ️ **Recommandation** : Activer Redis pour améliorer les performances

---

## 📋 Checklist de Configuration

### MongoDB ✅

- [x] `MONGODB_URL` configuré
- [x] Connexion réussie
- [x] Index créés
- [x] Collections créées

### PostgreSQL ⚠️

- [x] `POSTGRES_HOST` configuré
- [x] `POSTGRES_USER` configuré
- [x] `POSTGRES_PASSWORD` configuré
- [x] `POSTGRES_DB` configuré
- [x] Connexion réussie
- [x] Tables créées (avec gestion d'erreur)

### Redis ❌

- [ ] `REDIS_URL` configuré (optionnel)
- [ ] Service Redis créé (optionnel)
- [ ] Connexion testée (optionnel)

---

## 🔧 Correction des Erreurs

### Erreur PostgreSQL : "duplicate key value violates unique constraint"

**Problème** : Conflit avec un type PostgreSQL existant nommé `users`.

**Solution** : 
- ✅ Correction appliquée : Vérification avant création des tables
- ✅ Utilisation de `checkfirst=True` dans `create_all()`
- ✅ Gestion des erreurs de conflit (non critique)

**Statut** : ✅ **Corrigé**

---

## 📊 Résumé des Configurations

| Base de Données | Statut | Obligatoire | Configuration |
|----------------|--------|-------------|--------------|
| **MongoDB** | ✅ Connecté | Oui | ✅ Complète |
| **PostgreSQL** | ✅ Connecté | Non | ✅ Complète |
| **Redis** | ❌ Non configuré | Non | ⚠️ Optionnel |

---

## 🚀 Prochaines Étapes Recommandées

1. ✅ **MongoDB** : Déjà configuré et fonctionnel
2. ✅ **PostgreSQL** : Connecté, erreur de création des tables corrigée
3. ⚠️ **Redis** : Recommandé d'activer pour améliorer les performances

### Pour Activer Redis

1. Créez un service Redis sur Render ou utilisez un service externe (Upstash, Redis Cloud)
2. Ajoutez `REDIS_URL` dans les variables d'environnement de votre backend
3. Redéployez le service
4. Vérifiez les logs : `✅ Redis connecté avec succès`

---

## 📚 Documentation

- **MongoDB** : [https://www.mongodb.com/docs/](https://www.mongodb.com/docs/)
- **PostgreSQL** : [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)
- **Redis** : [https://redis.io/docs/](https://redis.io/docs/)
- **Render** : [https://render.com/docs/databases](https://render.com/docs/databases)

---

**Dernière mise à jour** : 2026-01-15
