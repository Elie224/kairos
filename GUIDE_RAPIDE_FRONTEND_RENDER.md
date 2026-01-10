# ⚡ Guide Rapide - Déploiement Frontend Render (Static Site)

## ✅ Configuration Terminée

Tous les fichiers nécessaires ont été configurés :

- ✅ `frontend/src/services/api.ts` - Utilise `VITE_API_URL` en production
- ✅ `frontend/public/_redirects` - Routing SPA configuré
- ✅ `.render.yaml` - Mis à jour pour Static Site
- ✅ Guide complet : `DEPLOIEMENT_FRONTEND_RENDER.md`

## 🚀 Déploiement en 5 Étapes

### Étape 1 : Pousser sur GitHub

```bash
git add .
git commit -m "Configure frontend for Render Static Site"
git push origin main
```

### Étape 2 : Créer le Service Static Site sur Render

**Option A : Via Blueprint (.render.yaml) - Recommandé**

1. Aller sur https://dashboard.render.com/
2. Cliquer sur **"New +"** > **"Blueprint"**
3. Connecter le repository `Elie224/kairos`
4. Render détectera automatiquement `.render.yaml`
5. Cliquer sur **"Apply"**

**Option B : Manuellement**

1. Aller sur https://dashboard.render.com/
2. Cliquer sur **"New +"** > **"Static Site"**
3. Connecter le repository `Elie224/kairos`
4. Configuration :
   - **Name:** `kairos-frontend`
   - **Branch:** `main`
   - **Root Directory:** `frontend`
   - **Build Command:** `npm ci && npm run build`
   - **Publish Directory:** `dist`

### Étape 3 : Configurer VITE_API_URL

**Après la création du service :**

1. Aller sur le service `kairos-frontend`
2. Cliquer sur **"Environment"** (ou **"Environment Variables"**)
3. Cliquer sur **"Add Environment Variable"**
4. Ajouter :
   - **Key:** `VITE_API_URL`
   - **Value:** `https://kairos-backend.onrender.com`
     ⚠️ **Remplacer par votre URL backend réelle !**
5. Cliquer sur **"Save Changes"**

### Étape 4 : Redéployer

Après avoir ajouté `VITE_API_URL` :

1. Dans le service `kairos-frontend`
2. Cliquer sur **"Manual Deploy"** > **"Deploy latest commit"**
3. Attendre 5-10 minutes

### Étape 5 : Vérifier

✅ **Site accessible :** `https://kairos-frontend.onrender.com`

✅ **Tester :**
- Site se charge sans erreur
- Console navigateur (F12) : pas d'erreur CORS
- Navigation fonctionne (routes SPA)
- Données se chargent depuis l'API

## 🔧 Variables Requises

### Frontend (Static Site)

| Variable | Valeur | Où la configurer |
|----------|--------|------------------|
| `VITE_API_URL` | `https://kairos-backend.onrender.com` | Render Dashboard > Service Frontend > Environment |

### Backend (À vérifier/mettre à jour)

| Variable | Valeur | Où la configurer |
|----------|--------|------------------|
| `FRONTEND_URL` | `https://kairos-frontend.onrender.com` | Render Dashboard > Service Backend > Environment |

⚠️ **IMPORTANT:** Après le déploiement du frontend, mettre à jour `FRONTEND_URL` dans le backend avec l'URL réelle du frontend !

## 📋 Checklist Rapide

### Avant le Déploiement

- [ ] Backend déployé et fonctionnel sur Render
- [ ] URL du backend connue (ex: `https://kairos-backend.onrender.com`)
- [ ] Code poussé sur GitHub (`git push`)

### Pendant le Déploiement

- [ ] Service Static Site créé sur Render
- [ ] Variable `VITE_API_URL` configurée avec l'URL du backend
- [ ] Build réussi (vérifier dans les logs)
- [ ] Site accessible

### Après le Déploiement

- [ ] Site accessible : `https://kairos-frontend.onrender.com`
- [ ] Routes SPA fonctionnent (pas d'erreur 404)
- [ ] API backend connectée (données se chargent)
- [ ] `FRONTEND_URL` mis à jour dans le backend

## 🐛 Problèmes Courants

### Erreur : Build Failed

**Solution :** Vérifier les logs Render pour l'erreur exacte. Généralement :
- Vérifier que `package.json` contient le script `build`
- Vérifier que `package-lock.json` est présent
- Tester le build localement : `cd frontend && npm run build`

### Erreur : 404 sur les Routes

**Solution :** Vérifier que `frontend/public/_redirects` existe et contient :
```
/*    /index.html   200
```

Vite copie automatiquement ce fichier dans `dist/` lors du build.

### Erreur : CORS

**Solution :** Vérifier dans le backend Render :
- `FRONTEND_URL=https://kairos-frontend.onrender.com`
- `ALLOWED_HOSTS=*`

### Erreur : API Non Accessible

**Solution :** Vérifier :
- `VITE_API_URL` est correcte (sans slash final `/`)
- Le backend est déployé et fonctionnel
- Tester l'URL backend directement : `https://kairos-backend.onrender.com/health`

## 📚 Documentation Complète

Pour plus de détails, voir : **`DEPLOIEMENT_FRONTEND_RENDER.md`**

## 🎯 Prochaines Étapes

1. ✅ **Configuration terminée** - **FAIT**
2. ⚠️ **Déployer sur Render** - **À FAIRE**
3. ⚠️ **Tester l'application**
4. ⚠️ **Mettre à jour FRONTEND_URL dans le backend**
5. ⚠️ **Configurer un domaine personnalisé** (optionnel)

## 🎉 Résumé

**Configuration actuelle :**

- Type : Static Site
- Build : `npm ci && npm run build`
- Publish : `dist/`
- Variable : `VITE_API_URL=https://kairos-backend.onrender.com`
- Routing : `_redirects` configuré

**Prêt à déployer !** 🚀
