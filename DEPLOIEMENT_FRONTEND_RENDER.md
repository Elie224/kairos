# 🚀 Déploiement Frontend sur Render - Static Site

## 📋 Vue d'ensemble

Le frontend React/Vite sera déployé comme **Static Site** sur Render (pas un Web Service). Cela signifie que le site sera servi comme des fichiers statiques (HTML, CSS, JS) après un build.

## ✅ Configuration Actuelle

### Fichiers Modifiés

1. **`frontend/src/services/api.ts`** ✅
   - Mis à jour pour utiliser `VITE_API_URL` en production
   - Utilise le proxy `/api` en développement

2. **`frontend/public/_redirects`** ✅
   - Créé pour le routing SPA (Single Page Application)
   - Toutes les routes redirigent vers `index.html`

3. **`.render.yaml`** ✅
   - Mis à jour pour utiliser `type: static` au lieu de `type: web`

## 🔧 Configuration Render

### Variables d'Environnement Requises

Dans Render Dashboard > Service `kairos-frontend` > Environment Variables :

#### Variable 1 : VITE_API_URL (OBLIGATOIRE)

**Key:** `VITE_API_URL`
**Value:** `https://kairos-backend.onrender.com`

⚠️ **IMPORTANT:** 
- Remplacez `kairos-backend` par le nom réel de votre service backend Render
- L'URL doit commencer par `https://`
- Pas de slash final (`/`) à la fin

#### Variable 2 : NODE_VERSION (Optionnel - déjà dans .render.yaml)

**Key:** `NODE_VERSION`
**Value:** `18.17.0`

## 📝 Instructions de Déploiement

### Option 1 : Déploiement via .render.yaml (Recommandé)

Si vous utilisez Render Blueprint (`.render.yaml`), le service sera créé automatiquement lors du push sur GitHub.

**Étapes :**

1. **Vérifier .render.yaml**
   - Vérifier que la section `kairos-frontend` utilise `type: static`
   - Vérifier que `staticPublishPath: frontend/dist`

2. **Pousser sur GitHub**
   ```bash
   git add .
   git commit -m "Configure frontend for Render Static Site deployment"
   git push origin main
   ```

3. **Dans Render Dashboard**
   - Aller sur https://dashboard.render.com/
   - Cliquer sur **"New +"** > **"Blueprint"**
   - Connecter votre repository GitHub (`Elie224/kairos`)
   - Render détectera automatiquement le fichier `.render.yaml`
   - Cliquer sur **"Apply"** pour créer les services

4. **Configurer VITE_API_URL**
   - Après la création du service, aller sur le service `kairos-frontend`
   - Aller dans **"Environment"** > **"Environment Variables"**
   - Ajouter `VITE_API_URL` avec l'URL de votre backend
   - Exemple : `https://kairos-backend.onrender.com`
   - **Sauvegarder**

5. **Redéployer**
   - Après avoir ajouté `VITE_API_URL`, cliquer sur **"Manual Deploy"** > **"Deploy latest commit"**
   - Attendre 5-10 minutes pour le déploiement

### Option 2 : Déploiement Manuel

Si vous préférez créer le service manuellement :

1. **Dans Render Dashboard**
   - Cliquer sur **"New +"** > **"Static Site"**

2. **Configuration du Service**
   - **Name:** `kairos-frontend`
   - **Region:** `Frankfurt` (ou la région la plus proche)
   - **Branch:** `main` (ou votre branche principale)
   - **Root Directory:** `frontend`
   - **Build Command:** `npm ci && npm run build`
   - **Publish Directory:** `dist`

3. **Variables d'Environnement**
   - Cliquer sur **"Add Environment Variable"**
   - Ajouter :
     - **Key:** `VITE_API_URL`
     - **Value:** `https://kairos-backend.onrender.com` (remplacer par votre URL backend)

4. **Créer le Service**
   - Cliquer sur **"Create Static Site"**
   - Attendre 5-10 minutes pour le build et le déploiement

## 🔍 Vérifications

### Vérification 1 : Build Réussi

Dans Render Dashboard > Service `kairos-frontend` > **"Logs"** :

✅ Rechercher :
```
✓ built in X.XXs
Build successful
```

❌ Si erreur, vérifier :
- Les dépendances sont installées (`npm ci`)
- Le build fonctionne localement (`npm run build`)
- Les variables d'environnement sont correctes

### Vérification 2 : Site Accessible

**URL du site:** `https://kairos-frontend.onrender.com`

✅ Le site doit :
- Charger sans erreur
- Afficher la page d'accueil
- Fonctionner en navigation (pas d'erreur 404 sur les routes)

### Vérification 3 : API Backend Connectée

✅ Ouvrir la console du navigateur (F12) :
- Pas d'erreur CORS
- Les requêtes vers l'API fonctionnent
- Les données se chargent correctement

❌ Si erreur CORS :
- Vérifier que `FRONTEND_URL` dans le backend est configurée
- Vérifier que `ALLOWED_HOSTS=*` dans le backend
- Vérifier que `VITE_API_URL` est correcte dans le frontend

### Vérification 4 : Routing SPA Fonctionnel

✅ Tester la navigation :
- Aller sur `https://kairos-frontend.onrender.com/login`
- Aller sur `https://kairos-frontend.onrender.com/dashboard`
- Vérifier que les routes fonctionnent (pas d'erreur 404)

❌ Si erreur 404 sur les routes :
- Vérifier que `_redirects` est dans `frontend/public/`
- Vérifier que le fichier est copié dans `dist/` après le build

## 🔐 Configuration Sécurité

### CORS (Backend)

Le backend doit autoriser le frontend Render. Vérifier dans Render Dashboard > Service Backend > Environment Variables :

```
FRONTEND_URL=https://kairos-frontend.onrender.com
ALLOWED_HOSTS=*
```

### VITE_API_URL (Frontend)

**IMPORTANT:** 
- Ne jamais commiter `VITE_API_URL` avec une valeur réelle dans le code
- Toujours utiliser les variables d'environnement Render
- Pour le développement local, utiliser `.env.local` (déjà dans `.gitignore`)

## 📊 Structure du Déploiement

```
Render Static Site
├── Build Command: npm ci && npm run build
├── Publish Directory: frontend/dist
├── Environment Variables:
│   ├── VITE_API_URL=https://kairos-backend.onrender.com
│   └── NODE_VERSION=18.17.0
└── URL: https://kairos-frontend.onrender.com
```

## 🐛 Résolution de Problèmes

### Problème 1 : Build Échoue

**Erreur:** `npm ERR! code ELIFECYCLE`

**Solution:**
- Vérifier que `package.json` contient le script `build`
- Vérifier que toutes les dépendances sont dans `package.json`
- Vérifier que `package-lock.json` est à jour

### Problème 2 : Erreur 404 sur les Routes

**Erreur:** Navigation vers `/dashboard` retourne 404

**Solution:**
- Vérifier que `frontend/public/_redirects` existe
- Vérifier que le fichier est copié dans `dist/` après le build
- Vérifier que Render supporte `_redirects` (oui, il le supporte)

### Problème 3 : Erreur CORS

**Erreur:** `Access-Control-Allow-Origin` dans la console

**Solution:**
- Vérifier `FRONTEND_URL` dans le backend Render
- Vérifier `ALLOWED_HOSTS=*` dans le backend Render
- Vérifier que `VITE_API_URL` est correcte (sans slash final)

### Problème 4 : API Non Accessible

**Erreur:** `Network Error` ou `ERR_CONNECTION_REFUSED`

**Solution:**
- Vérifier que le backend est déployé et fonctionnel
- Vérifier que l'URL du backend est correcte dans `VITE_API_URL`
- Tester l'URL backend directement : `https://kairos-backend.onrender.com/health`

## ✅ Checklist de Déploiement

### Avant le Déploiement

- [ ] Backend déployé et fonctionnel sur Render
- [ ] URL du backend connue (ex: `https://kairos-backend.onrender.com`)
- [ ] Fichier `_redirects` créé dans `frontend/public/`
- [ ] `api.ts` mis à jour pour utiliser `VITE_API_URL`
- [ ] `.render.yaml` mis à jour pour `type: static`
- [ ] Build local fonctionne (`npm run build`)

### Pendant le Déploiement

- [ ] Service créé sur Render (Static Site)
- [ ] Variable `VITE_API_URL` configurée avec l'URL du backend
- [ ] Build réussi (vérifier dans les logs)
- [ ] Site accessible (pas d'erreur 404)

### Après le Déploiement

- [ ] Site accessible : `https://kairos-frontend.onrender.com`
- [ ] Routes SPA fonctionnent (pas d'erreur 404)
- [ ] API backend connectée (données se chargent)
- [ ] Pas d'erreur CORS dans la console
- [ ] Navigation fonctionne (login, dashboard, etc.)

## 🎯 Prochaines Étapes

1. ✅ **Backend configuré** - À vérifier
2. ⚠️ **Déployer le frontend** - **EN COURS**
3. ⚠️ **Tester l'application complète**
4. ⚠️ **Mettre à jour FRONTEND_URL dans le backend** avec l'URL réelle du frontend
5. ⚠️ **Configurer le domaine personnalisé** (optionnel)

## 📚 Ressources

- **Documentation Render Static Sites:** https://render.com/docs/static-sites
- **Vite Environment Variables:** https://vitejs.dev/guide/env-and-mode.html
- **Render Blueprint:** https://render.com/docs/blueprint-spec

## 🎉 Résumé

**Configuration finale :**

- **Type de service:** Static Site
- **Build Command:** `npm ci && npm run build`
- **Publish Directory:** `frontend/dist`
- **Variable d'environnement:** `VITE_API_URL=https://kairos-backend.onrender.com`
- **Routing SPA:** Fichier `_redirects` configuré

Une fois déployé, le frontend sera accessible sur `https://kairos-frontend.onrender.com` ! 🚀
