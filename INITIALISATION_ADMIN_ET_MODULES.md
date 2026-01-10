# 🔧 Guide d'Initialisation : Admin Principal et Modules

## 📋 Problème Identifié

1. **L'utilisateur `kouroumaelisee@gmail.com` n'est pas encore promu admin principal**
2. **Les matières (modules) ne sont pas disponibles** car aucun module n'existe dans la base de données pour `mathematics` et `computer_science`

## ✅ Solutions Implémentées

### 1. Promotion de l'Admin Principal

Un endpoint d'initialisation a été créé pour promouvoir automatiquement `kouroumaelisee@gmail.com` en admin :

**Endpoint** : `POST /api/auth/initialize-main-admin`

**Utilisation** :
```bash
curl -X POST https://kairos-0aoy.onrender.com/api/auth/initialize-main-admin
```

**Réponse** :
```json
{
  "message": "Utilisateur 'kouroumaelisee@gmail.com' promu administrateur avec succès",
  "user": {
    "id": "...",
    "email": "kouroumaelisee@gmail.com",
    "username": "...",
    "is_admin": true
  }
}
```

### 2. Initialisation des Modules de Démonstration

Un endpoint a été créé pour initialiser des modules de base pour `mathematics` et `computer_science` :

**Endpoint** : `POST /api/modules/initialize-demo-modules`

**Utilisation** :
```bash
curl -X POST https://kairos-0aoy.onrender.com/api/modules/initialize-demo-modules
```

**Réponse** :
```json
{
  "message": "Initialisation terminée: 6/6 modules créés avec succès",
  "created_count": 6,
  "total_demo_modules": 6,
  "created": true
}
```

**Modules créés** :
- **Mathématiques** (3 modules) :
  - Algèbre Linéaire - Fondamentaux
  - Analyse - Limites et Continuité
  - Probabilités et Statistiques

- **Informatique** (3 modules) :
  - Introduction au Machine Learning
  - Réseaux de Neurones et Deep Learning
  - Algorithmes et Structures de Données

### 3. Script de Promotion Local

Un script Python est également disponible pour la promotion locale :

**Script** : `backend/scripts/set_main_admin.py`

**Utilisation** :
```bash
cd backend
python scripts/set_main_admin.py
```

## 🚀 Étapes pour Initialiser l'Application

### Option 1 : Via les Endpoints API (Recommandé pour Render)

1. **Promouvoir l'admin principal** :
   ```bash
   curl -X POST https://kairos-0aoy.onrender.com/api/auth/initialize-main-admin
   ```

2. **Initialiser les modules** :
   ```bash
   curl -X POST https://kairos-0aoy.onrender.com/api/modules/initialize-demo-modules
   ```

3. **Reconnectez-vous** avec `kouroumaelisee@gmail.com` pour voir le bouton Admin dans la navbar

### Option 2 : Via Script Local

1. **Promouvoir l'admin principal** :
   ```bash
   cd backend
   python scripts/set_main_admin.py
   ```

2. **Initialiser les modules** :
   - Utiliser l'endpoint API depuis le navigateur ou Postman
   - Ou créer un script similaire pour les modules

## 🔍 Vérification

### Vérifier que l'utilisateur est admin :

1. Connectez-vous avec `kouroumaelisee@gmail.com`
2. Vous devriez voir le bouton "🔐 Administration" dans la navbar
3. Cliquez dessus pour accéder à `/admin`

### Vérifier que les modules existent :

1. Allez sur `/modules`
2. Vous devriez voir deux matières :
   - **Mathématiques** (3 modules)
   - **Informatique** (3 modules)
3. Cliquez sur une matière pour voir ses modules

## 📝 Notes Importantes

- Les endpoints d'initialisation peuvent être appelés plusieurs fois en toute sécurité
- Si des modules existent déjà, l'endpoint `/initialize-demo-modules` ne les créera pas à nouveau
- L'utilisateur doit se **reconnecter** après avoir été promu admin pour que le frontend récupère la nouvelle valeur `is_admin`
- Les modules sont filtrés pour ne garder que ceux avec `subject` = `"mathematics"` ou `"computer_science"`

## 🔒 Sécurité

- L'endpoint `/initialize-main-admin` est **public** mais ne peut promouvoir que `kouroumaelisee@gmail.com`
- L'endpoint `/initialize-demo-modules` est **public** mais ne crée des modules que s'il n'en existe pas déjà
- Après l'initialisation, ces endpoints peuvent être désactivés ou protégés par authentification admin
