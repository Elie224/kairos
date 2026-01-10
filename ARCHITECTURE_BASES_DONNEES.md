# 🗄️ Architecture des Bases de Données - Kaïros

## 📊 Stratégie Multi-Bases de Données

Kaïros utilise **deux bases de données complémentaires** pour optimiser les performances et la flexibilité :

### 🍃 MongoDB (Principal)
**Utilisation principale** : Stockage des données non-relationnelles et flexibles

**Avantages** :
- ✅ Flexibilité du schéma (parfait pour le contenu éducatif varié)
- ✅ Stockage de documents JSON complexes (scènes 3D, contenu immersif)
- ✅ Scalabilité horizontale facile
- ✅ Performance pour les requêtes de contenu

**Données stockées** :
- Modules d'apprentissage (avec contenu JSON complexe)
- Progression utilisateur
- Quiz et examens
- Badges et gamification
- Historique IA
- Abonnements Stripe
- Données d'apprentissage adaptatif

### 🐘 PostgreSQL (Relationnel)
**Utilisation** : Données relationnelles structurées

**Avantages** :
- ✅ Intégrité référentielle garantie
- ✅ Transactions ACID
- ✅ Requêtes SQL complexes et jointures efficaces
- ✅ Parfait pour les relations utilisateur-cours-modules

**Données stockées** :
- Relations utilisateur-cours-modules
- Inscriptions (enrollments)
- Progression structurée avec relations
- Données transactionnelles

## 🔄 Quand Utiliser Quelle Base ?

### MongoDB pour :
- Contenu de modules (JSON flexible)
- Données de progression simples
- Cache et sessions
- Données IA et analytics

### PostgreSQL pour :
- Relations complexes entre entités
- Requêtes avec jointures multiples
- Transactions critiques
- Reporting et analytics relationnels

## ⚙️ Configuration

### MongoDB (Obligatoire)
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros
```

### PostgreSQL (Optionnel)
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse
```

## 🚀 Démarrage

L'application fonctionne **avec MongoDB uniquement** si PostgreSQL n'est pas configuré.

Si PostgreSQL est configuré, les deux bases sont utilisées :
- MongoDB pour le contenu principal
- PostgreSQL pour les relations structurées

## 💡 Recommandation

Pour un projet de taille moyenne :
- **MongoDB uniquement** : Suffisant et plus simple
- **MongoDB + PostgreSQL** : Si vous avez besoin de relations complexes et de reporting avancé

Les deux approches sont valides ! 🎯











