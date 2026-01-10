# 🔧 Configuration pour le Développement Local

## 🚨 Problème Identifié

L'erreur **501 "Unsupported method ('POST')"** sur `/api/auth/login` en local signifie que :

1. **Le backend local n'est pas démarré** sur `localhost:8000`, OU
2. **Le proxy Vite ne fonctionne pas correctement**

## ✅ Solutions

### Solution 1 : Démarrer le Backend Local (Recommandé pour développement complet)

**Étape 1 : Démarrer le backend local**

```powershell
# Dans le dossier backend
cd backend
.\venv\Scripts\python.exe main.py
```

Ou utilisez le script PowerShell :
```powershell
cd backend
.\redemarrer-backend.ps1
```

**Étape 2 : Vérifier que le backend est accessible**

Ouvrez http://localhost:8000/docs dans votre navigateur pour vérifier que l'API est accessible.

**Étape 3 : Redémarrer le frontend**

Le proxy Vite redirigera automatiquement `/api/*` vers `http://localhost:8000/api/*`.

### Solution 2 : Utiliser le Backend Render en Développement Local (Plus Simple)

**Créer un fichier `.env.local` dans `frontend/`** (ne sera pas committé dans Git) :

```env
VITE_API_URL=https://kairos-0aoy.onrender.com/api
```

**Puis redémarrer le serveur de développement** :

```powershell
cd frontend
npm run dev
```

Cela permettra au frontend local de se connecter directement au backend Render, sans avoir besoin de démarrer le backend localement.

### Solution 3 : Modifier temporairement le code

Si vous ne pouvez pas créer de fichier `.env.local`, vous pouvez temporairement modifier `frontend/src/services/api.ts` :

```typescript
const getBaseURL = () => {
  // Pour développement : utiliser le backend Render
  if (import.meta.env.DEV) {
    return 'https://kairos-0aoy.onrender.com/api'
  }
  // En production : utiliser VITE_API_URL
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  return '/api'
}
```

## 📝 Vérification

Après avoir configuré :

1. **Redémarrer le serveur de développement** (`npm run dev`)
2. **Tester la connexion** avec `kouroumaelisee@gmail.com`
3. **Vérifier la console** : l'appel devrait être fait vers le bon backend

## 🔍 Débogage

### Vérifier que le backend local fonctionne :

```powershell
# Tester l'endpoint de santé
Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing

# Tester l'endpoint login (doit retourner 422 car pas de credentials, pas 501)
Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login" -Method POST -UseBasicParsing
```

### Si vous obtenez toujours une erreur 501 :

1. **Vérifier que le backend est démarré** : `http://localhost:8000/docs`
2. **Vérifier le port** : Le backend doit être sur le port 8000
3. **Vérifier le proxy Vite** : Les logs du serveur dev devraient montrer les requêtes proxyées
4. **Utiliser directement le backend Render** : Créer `.env.local` avec `VITE_API_URL=https://kairos-0aoy.onrender.com/api`

## ⚠️ Important

- Le fichier `.env.local` n'est **pas committé** dans Git (déjà dans `.gitignore`)
- Le fichier `.env.development` **serait committé**, donc ne pas y mettre de secrets
- En production sur Render, `VITE_API_URL` est défini via les variables d'environnement Render
