# 🔧 Correction Erreur 404 - Routing SPA sur Render

## ❌ Problème

Erreur 404 sur les routes du frontend (ex: `/login`) après déploiement sur Render Static Site.

**Symptôme** : La page affiche "Not Found" au lieu de charger l'application React.

## 🔍 Cause

Le fichier `_redirects` n'est pas correctement reconnu par Render ou n'est pas au bon format.

## ✅ Solution

### 1. Vérifier le Format du Fichier `_redirects`

Le fichier `frontend/public/_redirects` doit contenir exactement :

```
/*    /index.html   200
```

**Important** :
- Pas de ligne vide à la fin
- Utiliser des tabulations ou espaces (4 espaces recommandés)
- Le fichier doit être dans `frontend/public/` (Vite le copiera automatiquement dans `dist/`)

### 2. Vérifier la Configuration Render

Dans Render Dashboard > Service `kairos-frontend` > Settings :

- **Build Command** : `cd frontend && npm ci && npm run build`
- **Publish Directory** : `frontend/dist`

### 3. Vérifier que le Fichier est Copié

Après le build, le fichier `_redirects` doit être présent dans `frontend/dist/`.

Pour vérifier localement :
```bash
cd frontend
npm run build
ls -la dist/_redirects  # Doit exister
cat dist/_redirects     # Doit contenir: /*    /index.html   200
```

### 4. Alternative : Utiliser `render.yaml`

Si le fichier `_redirects` ne fonctionne pas, vous pouvez aussi configurer les redirects dans `.render.yaml` :

```yaml
services:
  - type: static
    name: kairos-frontend
    # ... autres configs ...
    headers:
      - path: /*
        name: X-Content-Type-Options
        value: nosniff
    # Note: Render Static Sites utilise automatiquement _redirects
    # Pas besoin de configuration supplémentaire
```

## 🚀 Actions à Effectuer

### Étape 1 : Vérifier le Fichier `_redirects`

Le fichier `frontend/public/_redirects` doit contenir exactement :
```
/*    /index.html   200
```

### Étape 2 : Rebuild et Redéployer

1. **Pousser les modifications sur GitHub** :
   ```bash
   git add frontend/public/_redirects
   git commit -m "Fix: Correction format _redirects pour Render"
   git push
   ```

2. **Redéployer sur Render** :
   - Allez sur https://dashboard.render.com
   - Ouvrez votre service `kairos-frontend`
   - Cliquez sur "Manual Deploy" → "Deploy latest commit"
   - Attendez 5-10 minutes

### Étape 3 : Vérifier

1. **Ouvrez votre frontend** : `https://kairos-frontend-hjg9.onrender.com`
2. **Testez une route** : `https://kairos-frontend-hjg9.onrender.com/login`
3. **Vérifiez** : La page doit se charger correctement (pas "Not Found")

## 🔍 Vérification des Logs Render

Dans les logs du build frontend sur Render, vous devriez voir :
```
✓ built in Xs
dist/_redirects    0.00 kB
```

Le fichier `_redirects` doit être listé dans les fichiers générés.

## 🐛 Si l'Erreur Persiste

### Solution 1 : Vérifier le Format Exact

Le fichier `_redirects` doit utiliser des **tabulations** ou **4 espaces** entre les colonnes :

```
/*	/index.html	200
```

Ou avec espaces :
```
/*    /index.html   200
```

### Solution 2 : Créer le Fichier Manuellement dans `dist/`

Si Vite ne copie pas le fichier, vous pouvez créer un script de build :

Dans `frontend/package.json`, modifier le script build :
```json
{
  "scripts": {
    "build": "vite build && echo '/*    /index.html   200' > dist/_redirects"
  }
}
```

### Solution 3 : Vérifier les Permissions

Assurez-vous que le fichier `_redirects` a les bonnes permissions et n'est pas ignoré par `.gitignore`.

## ✅ Résultat Attendu

Après correction :

- ✅ Plus d'erreur 404 sur les routes (`/login`, `/dashboard`, etc.)
- ✅ Toutes les routes redirigent vers `index.html`
- ✅ L'application React se charge correctement
- ✅ Le routing SPA fonctionne

---

**Dernière mise à jour** : 2026-01-15
