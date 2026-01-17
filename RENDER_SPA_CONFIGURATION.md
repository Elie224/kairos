# Configuration Render Static Site pour SPA

## Problème MIME Type

Le fichier `_redirects` avec `/* /index.html 200` redirige TOUT vers `index.html`, y compris les fichiers statiques (.js, .css), ce qui cause l'erreur :
```
Failed to load module script: Expected a JavaScript-or-Wasm module script but the server responded with a MIME type of "text/html"
```

## Solution

### Option 1 : Configuration Render Dashboard (RECOMMANDÉ)

1. Aller dans Render Dashboard > Static Site > Settings
2. Dans la section "Routes", configurer :
   - **Fallback Route**: `/index.html`
   - Cela permet à Render de servir `index.html` pour les routes non trouvées, sans affecter les fichiers statiques

### Option 2 : Utiliser un fichier `_redirects` conditionnel

Le fichier `_redirects` actuel est vide car Render gère automatiquement les fichiers statiques.

### Option 3 : Serveur web custom

Pour un contrôle total, on peut utiliser un serveur web (Nginx, Apache) qui :
- Sert directement les fichiers statiques (.js, .css, /assets/*)
- Sert `index.html` uniquement pour les routes non trouvées

## Fichiers modifiés

- `frontend/public/_redirects` : Vide (pas de réécriture SPA)
- `frontend/public/_headers` : Headers pour forcer les bons MIME types
- `frontend/public/render-headers.json` : Configuration alternative pour Render

## Action requise

**CONFIGURER dans Render Dashboard** :
1. Static Site > Settings
2. Routes > Fallback Route : `/index.html`
3. Cette configuration permet les routes SPA sans affecter les fichiers statiques
