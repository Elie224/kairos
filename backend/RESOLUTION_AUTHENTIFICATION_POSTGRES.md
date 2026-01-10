# 🔐 Résolution Problème d'Authentification PostgreSQL

## ❌ Problème

L'authentification PostgreSQL échoue avec le message :
```
FATAL: authentification par mot de passe échouée pour l'utilisateur « postgres »
```

## 🔍 Causes Possibles

1. **Le mot de passe dans `.env` ne correspond pas au mot de passe PostgreSQL**
2. **PostgreSQL utilise une méthode d'authentification différente**
3. **Le mot de passe a des caractères spéciaux mal encodés**

## ✅ Solutions

### Solution 1 : Configurer l'Encodage via Python (Recommandé)

Utilisez le script Python qui évite les problèmes d'authentification psql :

```powershell
cd backend
.\venv\Scripts\python.exe scripts\configure_postgres_encoding.py
```

Ce script configure l'encodage directement via SQLAlchemy en utilisant les paramètres de `.env`.

### Solution 2 : Utiliser pgAdmin (Interface Graphique)

1. **Ouvrez pgAdmin**
2. **Connectez-vous au serveur PostgreSQL 18**
   - Si vous ne vous souvenez pas du mot de passe, utilisez celui que vous avez défini lors de l'installation
3. **Clic droit sur la base `eduverse`** → **Properties**
4. **Onglet Variables** → Cliquez sur **+**
5. **Name** : `client_encoding`
6. **Value** : `UTF8`
7. **Cliquez sur Save**

### Solution 3 : Réinitialiser le Mot de Passe PostgreSQL

Si vous avez oublié le mot de passe :

#### Via pgAdmin
1. Ouvrez pgAdmin
2. Clic droit sur le serveur PostgreSQL 18 → **Properties**
3. Onglet **Connection** → Modifiez le mot de passe
4. Mettez à jour `.env` avec le nouveau mot de passe

#### Via Services Windows
1. Arrêtez le service PostgreSQL 18
2. Modifiez `pg_hba.conf` pour autoriser les connexions locales sans mot de passe (temporairement)
3. Redémarrez PostgreSQL
4. Connectez-vous et changez le mot de passe
5. Remettez `pg_hba.conf` à son état original

### Solution 4 : Vérifier le Mot de Passe dans .env

Vérifiez que le mot de passe dans `backend/.env` correspond au mot de passe PostgreSQL :

```env
POSTGRES_PASSWORD=Kourouma
```

**Important** : 
- Le mot de passe est sensible à la casse
- Vérifiez qu'il n'y a pas d'espaces avant/après
- Si le mot de passe contient des caractères spéciaux, ils doivent être correctement encodés

## 🚀 Après Configuration de l'Encodage

Une fois l'encodage configuré (via Python ou pgAdmin), exécutez les migrations :

```powershell
cd backend
.\venv\Scripts\python.exe scripts\migrate_postgres.py create
```

## 🔍 Vérification

Vérifiez que l'encodage est bien configuré :

```powershell
# Via le script Python
.\venv\Scripts\python.exe scripts\configure_postgres_encoding.py
```

Ou via pgAdmin :
- Clic droit sur `eduverse` → **Properties** → **Variables**
- Vérifiez que `client_encoding = UTF8`

## 💡 Astuce

Si vous continuez à avoir des problèmes d'authentification :

1. **Utilisez pgAdmin** pour configurer l'encodage (plus simple)
2. **Puis exécutez les migrations via Python** (qui utilise les paramètres de `.env`)

Les migrations Python peuvent fonctionner même si psql ne fonctionne pas, car elles utilisent les paramètres de `.env` directement.
