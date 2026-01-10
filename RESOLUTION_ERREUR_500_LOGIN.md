# 🔧 Résolution Erreur 500 sur /api/auth/login

## Problèmes identifiés

1. ✅ **Attribut autocomplete manquant** - CORRIGÉ
   - Ajout de `autoComplete="email"` sur le champ email
   - Ajout de `autoComplete="current-password"` sur le champ password

2. ⚠️ **Erreur MetaMask** - Non critique
   - Ces erreurs viennent d'une extension de navigateur (MetaMask)
   - Elles n'affectent pas l'application
   - Solution : Désactiver temporairement l'extension MetaMask si elle gêne

3. 🔴 **Erreur 500 sur /api/auth/login** - À investiguer

## Diagnostic Erreur 500

L'erreur 500 indique un problème côté serveur. Causes possibles :

### 1. MongoDB non connecté

**Vérifier** :
```bash
# Vérifier que MongoDB est démarré
docker ps | findstr mongodb
# ou
mongosh --eval "db.adminCommand('ping')"
```

**Solution** :
```bash
# Démarrer MongoDB
demarrer-mongodb.bat
# ou
docker start eduverse-mongodb
```

### 2. SECRET_KEY manquante ou invalide

**Vérifier** : Le backend doit avoir une `SECRET_KEY` configurée pour créer les tokens JWT.

**Solution** : Créer un fichier `.env` dans `backend/` :
```env
SECRET_KEY=votre_clé_secrète_32_caractères_minimum_12345678901234567890
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros
```

### 3. Problème de connexion à la base de données

**Vérifier les logs du backend** pour voir l'erreur exacte.

**Solution** : Vérifier que MongoDB est accessible depuis le backend.

### 4. Utilisateur inexistant ou mot de passe incorrect

**Vérifier** : L'utilisateur existe-t-il dans la base de données ?

**Solution** : Créer un utilisateur via l'API d'inscription ou vérifier dans MongoDB.

## Étapes de dépannage

### Étape 1 : Vérifier les logs du backend

Regardez la console où le backend tourne pour voir l'erreur exacte.

### Étape 2 : Tester l'endpoint directement

```bash
# Avec curl ou Postman
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=votre_email@example.com&password=votre_mot_de_passe"
```

### Étape 3 : Vérifier la connexion MongoDB

```bash
# Dans le terminal backend
python -c "from app.database import db; import asyncio; asyncio.run(db.client.admin.command('ping'))"
```

### Étape 4 : Vérifier la configuration

Vérifier que `backend/app/config.py` charge bien les variables d'environnement.

## Solutions rapides

### Solution 1 : Redémarrer MongoDB
```bash
docker restart eduverse-mongodb
```

### Solution 2 : Redémarrer le backend
```bash
# Arrêter avec Ctrl+C puis redémarrer
demarrer-backend.bat
```

### Solution 3 : Vérifier les variables d'environnement

Créer `backend/.env` :
```env
SECRET_KEY=changez_cette_clé_par_une_clé_secrète_32_caractères_minimum
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros
```

## Test de connexion

Une fois les corrections appliquées, tester la connexion :

1. Ouvrir http://localhost:3000/login
2. Entrer email et mot de passe
3. Vérifier les logs du backend pour voir l'erreur exacte si elle persiste

## Logs à vérifier

Dans la console du backend, cherchez des erreurs comme :
- `Connection refused` → MongoDB non démarré
- `SECRET_KEY` → Clé secrète manquante
- `User not found` → Utilisateur inexistant
- `Invalid password` → Mot de passe incorrect

---

*Si l'erreur persiste, vérifiez les logs du backend pour l'erreur exacte.*



