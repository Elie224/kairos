# 🗄️ Configuration MongoDB et Redis sur Render - Guide Complet

Ce guide vous explique comment configurer et optimiser MongoDB et Redis pour l'application Kaïros sur Render.

---

## 🍃 MongoDB - Configuration et Optimisation

### ✅ Statut Actuel

D'après les logs, MongoDB est **déjà connecté et fonctionnel** :

```
✅ Connexion MongoDB réussie
✅ MongoDB ping réussi
```

### 📋 Variables d'Environnement MongoDB

Dans votre service backend Render, vérifiez ces variables :

| Variable | Valeur Recommandée | Description |
|----------|-------------------|-------------|
| `MONGODB_URL` | `mongodb+srv://user:password@cluster.mongodb.net/dbname` | URL de connexion MongoDB Atlas |
| `MONGODB_DB_NAME` | `kaïros` | Nom de la base de données |
| `MONGODB_TIMEOUT_MS` | `5000` | Timeout de connexion (ms) |
| `MONGODB_MAX_POOL_SIZE` | `200` | Taille max du pool de connexions |
| `MONGODB_MIN_POOL_SIZE` | `20` | Taille min du pool de connexions |

### 🔧 Optimisations Actives

MongoDB est déjà optimisé avec :

- ✅ **Connection Pooling** : 200 connexions max, 20 min
- ✅ **Compression** : Snappy (si disponible) ou Zlib
- ✅ **Retry Logic** : `retryWrites=True`, `retryReads=True`
- ✅ **Heartbeat** : Vérification toutes les 10 secondes
- ✅ **Timeouts Optimisés** : 5s connexion, 20s socket
- ✅ **Index Automatiques** : Tous les index sont créés automatiquement

### 📊 Vérification MongoDB

Pour vérifier que MongoDB fonctionne correctement :

1. **Vérifiez les logs Render** :
   ```
   ✅ Connexion MongoDB réussie
   ✅ MongoDB ping réussi
   ✅ Index unique créé sur 'users.email'
   ```

2. **Vérifiez MongoDB Atlas** :
   - Allez sur [MongoDB Atlas Dashboard](https://cloud.mongodb.com/)
   - Vérifiez les métriques de connexion
   - Vérifiez l'utilisation des ressources

### ⚙️ Configuration Recommandée MongoDB Atlas

Si vous utilisez MongoDB Atlas, configurez :

1. **Network Access** :
   - Ajoutez `0.0.0.0/0` pour autoriser toutes les IP (ou spécifiez les IP Render)
   - Ou utilisez "Allow Access from Anywhere" temporairement

2. **Database Access** :
   - Créez un utilisateur avec les permissions nécessaires
   - Utilisez un mot de passe fort

3. **Cluster Configuration** :
   - **M0 (Free)** : Pour développement/test
   - **M10+** : Pour production (recommandé)

---

## 🔴 Redis - Configuration et Activation

### ❌ Statut Actuel

Redis est **non configuré** actuellement :

```
ℹ️  Redis non configuré - Cache désactivé (optionnel)
```

### 🎯 Pourquoi Activer Redis ?

Redis apporte de nombreux avantages :

- ✅ **Cache** : Réponses instantanées pour les requêtes fréquentes
- ✅ **Rate Limiting** : Protection contre les abus et attaques
- ✅ **Sessions** : Stockage des sessions utilisateur
- ✅ **Performance** : Réduction de la charge sur MongoDB
- ✅ **Scalabilité** : Support de milliers d'utilisateurs simultanés

### 📋 Options pour Activer Redis sur Render

#### Option 1 : Service Redis Render (Recommandé pour Production)

**Avantages** :
- Intégration native avec Render
- Gestion automatique des backups
- Monitoring intégré

**Étapes** :

1. **Créer un service Redis** :
   - Allez sur [Render Dashboard](https://dashboard.render.com)
   - Cliquez sur **"+ New +"** → **"Redis"**
   - Configurez :
     - **Name** : `kairos-redis`
     - **Plan** : Free (pour test) ou Starter ($10/mois pour production)
     - **Region** : Même région que votre backend
   - Cliquez sur **"Create Redis"**

2. **Récupérer l'URL de connexion** :
   - Une fois créé, cliquez sur votre service Redis
   - Dans l'onglet **"Info"**, copiez :
     - **Internal Redis URL** : `redis://red-xxxxx:6379`
     - **External Redis URL** : `redis://red-xxxxx.render.com:6379`

3. **Configurer dans le backend** :
   - Allez dans votre service backend Render
   - Cliquez sur **"Environment"**
   - Ajoutez la variable :
     - **Key** : `REDIS_URL`
     - **Value** : L'URL Redis (Internal ou External selon vos besoins)
     - Cliquez sur **"Save Changes"**

4. **Redéployer** :
   - Render redéploiera automatiquement
   - Vérifiez les logs : `✅ Redis connecté avec succès`

#### Option 2 : Upstash Redis (Gratuit jusqu'à 10K commandes/jour)

**Avantages** :
- Gratuit jusqu'à 10K commandes/jour
- Serverless (pas de gestion de serveur)
- Globalement distribué

**Étapes** :

1. **Créer un compte** :
   - Allez sur [Upstash](https://upstash.com/)
   - Créez un compte gratuit
   - Créez une nouvelle base de données Redis

2. **Récupérer l'URL** :
   - Dans le dashboard Upstash, copiez l'**REST URL** ou **Redis URL**
   - Format : `redis://default:password@region.upstash.io:6379`

3. **Configurer dans Render** :
   - Ajoutez `REDIS_URL` dans les variables d'environnement de votre backend
   - Utilisez l'URL Redis d'Upstash

#### Option 3 : Redis Cloud (Gratuit jusqu'à 30MB)

**Avantages** :
- Gratuit jusqu'à 30MB
- Gestion automatique
- Monitoring intégré

**Étapes** :

1. **Créer un compte** :
   - Allez sur [Redis Cloud](https://redis.com/cloud/)
   - Créez un compte gratuit
   - Créez une nouvelle base de données

2. **Récupérer l'URL** :
   - Copiez l'URL de connexion Redis
   - Format : `redis://default:password@host:port`

3. **Configurer dans Render** :
   - Ajoutez `REDIS_URL` dans les variables d'environnement

---

## 🔧 Configuration Redis dans Render

### Variables d'Environnement

Dans votre service backend Render, ajoutez :

| Variable | Exemple de Valeur | Description |
|----------|------------------|-------------|
| `REDIS_URL` | `redis://red-xxxxx:6379` | URL de connexion Redis (Render) |
| `REDIS_URL` | `redis://default:password@region.upstash.io:6379` | URL de connexion Redis (Upstash) |
| `REDIS_URL` | `redis://localhost:6379/0` | URL de connexion Redis (local) |

### Configuration Optimale Redis

Le code est déjà optimisé avec :

- ✅ **Connection Pooling** : Gestion automatique des connexions
- ✅ **Health Checks** : Vérification toutes les 30 secondes
- ✅ **Retry Logic** : Tentatives automatiques en cas d'erreur
- ✅ **Timeouts** : 5 secondes pour connexion et socket
- ✅ **Encoding** : UTF-8 avec décodage automatique

---

## ✅ Checklist de Configuration

### MongoDB ✅

- [x] `MONGODB_URL` configuré
- [x] `MONGODB_DB_NAME` configuré
- [x] Connexion réussie
- [x] Index créés automatiquement
- [x] Optimisations activées

### Redis ⚠️

- [ ] Service Redis créé (Render, Upstash, ou Redis Cloud)
- [ ] `REDIS_URL` configuré dans le backend
- [ ] Redéploiement effectué
- [ ] Logs montrent : `✅ Redis connecté avec succès`

---

## 🧪 Test de Connexion

### Test MongoDB

Les logs Render devraient montrer :
```
✅ Connexion MongoDB réussie
✅ MongoDB ping réussi
```

### Test Redis

Après configuration, les logs Render devraient montrer :
```
✅ Redis connecté avec succès
```

Si vous voyez :
```
ℹ️  Redis non configuré - Cache désactivé (optionnel)
```

Cela signifie que `REDIS_URL` n'est pas configuré.

---

## 📊 Comparaison des Options Redis

| Option | Coût | Limites | Recommandation |
|--------|------|---------|----------------|
| **Render Redis** | Free / $10/mois | Free: 25MB | ✅ Production |
| **Upstash** | Gratuit | 10K commandes/jour | ✅ Développement/Test |
| **Redis Cloud** | Gratuit | 30MB | ✅ Développement/Test |

---

## 🚀 Prochaines Étapes

1. ✅ **MongoDB** : Déjà configuré et optimisé
2. ⚠️ **Redis** : 
   - Créez un service Redis (Render, Upstash, ou Redis Cloud)
   - Configurez `REDIS_URL` dans votre backend Render
   - Redéployez et vérifiez les logs

---

## 📚 Documentation

- **MongoDB Atlas** : [https://www.mongodb.com/docs/atlas/](https://www.mongodb.com/docs/atlas/)
- **Redis** : [https://redis.io/docs/](https://redis.io/docs/)
- **Render Databases** : [https://render.com/docs/databases](https://render.com/docs/databases)
- **Upstash** : [https://docs.upstash.com/](https://docs.upstash.com/)

---

**Dernière mise à jour** : 2026-01-15
