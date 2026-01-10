# 🔧 Correction Erreur 501 en Développement Local

## 🚨 Problème Identifié

L'erreur **501 "Unsupported method ('POST')"** sur `http://localhost:5174/api/auth/login` indique que :
- Le frontend essaie de se connecter au backend via le proxy Vite
- Mais le backend local n'est **pas démarré** sur `localhost:8000`
- Le proxy Vite ne peut donc pas rediriger vers le backend

## ✅ Solution Appliquée

J'ai modifié `frontend/src/services/api.ts` pour utiliser **le backend Render par défaut** en développement local si le backend local n'est pas disponible.

### Changement Effectué

**Avant** :
```typescript
const getBaseURL = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  return '/api'  // Utilise le proxy vers localhost:8000
}
```

**Après** :
```typescript
const getBaseURL = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }
  // En développement, utiliser le backend Render par défaut
  if (import.meta.env.DEV) {
    return 'https://kairos-0aoy.onrender.com/api'
  }
  return '/api'  // Fallback pour le proxy local
}
```

## 🚀 Étapes pour Appliquer la Correction

### 1. Redémarrer le Serveur de Développement

**Arrêtez le serveur actuel** (Ctrl+C dans le terminal où il tourne), puis :

```powershell
cd frontend
npm run dev
```

### 2. Vérifier que ça fonctionne

1. **Tester la connexion** avec `kouroumaelisee@gmail.com`
2. **Vérifier la console** : l'appel devrait être fait vers `https://kairos-0aoy.onrender.com/api/auth/login`
3. **La connexion devrait fonctionner** maintenant

## 📝 Options Alternatives

### Option A : Utiliser le Backend Local (Pour développement complet)

Si vous voulez utiliser le backend local au lieu du backend Render :

1. **Démarrer le backend local** :
   ```powershell
   cd backend
   .\venv\Scripts\python.exe main.py
   ```

2. **Créer un fichier `.env.local` dans `frontend/`** :
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```

3. **Redémarrer le serveur de développement**

### Option B : Forcer l'utilisation du Backend Render (Recommandé)

Le code est maintenant configuré pour utiliser automatiquement le backend Render en développement. Aucune action supplémentaire n'est nécessaire, juste **redémarrer le serveur de développement**.

## ✅ Vérification

Après avoir redémarré le serveur :

- ✅ Le frontend devrait appeler `https://kairos-0aoy.onrender.com/api/auth/login`
- ✅ Plus d'erreur 501
- ✅ La connexion devrait fonctionner
- ✅ Le backend Render est déjà déployé et fonctionnel

## 📋 Résumé

**Problème** : Frontend local essaie de se connecter au backend local non démarré → erreur 501

**Solution** : Utiliser le backend Render par défaut en développement local

**Action requise** : **Redémarrer le serveur de développement** (`npm run dev`)

Les modifications sont déjà poussées sur GitHub et seront déployées automatiquement sur Render.
