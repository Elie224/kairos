# 🔍 Vérification des Variables d'Environnement Render

## ❌ Problème

Les erreurs CORS persistent avec l'URL `https://votre-backend-url.onrender.com/api/admin/migrate-quota-to-20gb`

Cette URL **N'EXISTE PAS** dans le code source, ce qui signifie qu'elle vient de :
1. **Variable d'environnement mal configurée** sur Render
2. **Code compilé obsolète** dans `dist/` sur Render

## ✅ Solution : Vérifier et Corriger sur Render

### Étape 1 : Vérifier les Variables d'Environnement

Sur **Render Dashboard** → Votre service frontend → **Environment** :

1. Vérifier que `VITE_API_URL` est définie :
   ```
   VITE_API_URL=https://kairos-0aoy.onrender.com/api
   ```

2. **❌ NE PAS UTILISER** :
   ```
   VITE_API_URL=https://votre-backend-url.onrender.com/api
   ```

3. Si la variable n'existe pas, **l'ajouter** :
   - Cliquer sur **"Add Environment Variable"**
   - Key: `VITE_API_URL`
   - Value: `https://kairos-0aoy.onrender.com/api`

### Étape 2 : Rebuild le Service

Après avoir corrigé la variable :

1. Aller dans **"Manual Deploy"** → **"Deploy latest commit"**
2. OU : Faire un commit vide pour déclencher un rebuild :
   ```bash
   git commit --allow-empty -m "chore: trigger rebuild"
   git push
   ```

### Étape 3 : Vérifier le Build

Après le rebuild, vérifier dans les logs Render que :
- ✅ `VITE_API_URL` est bien utilisée
- ✅ Aucune référence à `votre-backend-url`

## 🔍 Diagnostic

Si le problème persiste après rebuild :

1. **Vérifier les logs Render** : Chercher des références à `votre-backend-url`
2. **Vérifier le cache** : Vider le cache du navigateur (Ctrl+Shift+Delete)
3. **Vérifier le Service Worker** : Désactiver les service workers dans DevTools

## 📝 Note

Le code source utilise correctement :
- `api.ts` : `import.meta.env.VITE_API_URL || 'https://kairos-0aoy.onrender.com/api'`
- `chatService.ts` : `import.meta.env.VITE_API_URL || 'https://kairos-0aoy.onrender.com/api'`

Si `VITE_API_URL` n'est pas définie ou est incorrecte, le code utilisera l'URL par défaut correcte.
