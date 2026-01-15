# 🔧 Configuration Redirects Render Dashboard - Solution 404

## ❌ Problème

Erreur 404 sur les routes du frontend (ex: `/login`) après déploiement sur Render Static Site.

**Symptôme** : `GET https://kairos-frontend-hjg9.onrender.com/login 404 (Not Found)`

## ✅ Solution : Configurer les Redirects dans Render Dashboard

Le fichier `_redirects` seul ne suffit pas. Il faut **AUSSI** configurer les redirects dans le Dashboard Render.

### Étapes à Suivre

1. **Allez sur Render Dashboard** : https://dashboard.render.com

2. **Ouvrez votre service frontend** : `kairos-frontend` ou `kairos-frontend-hjg9`

3. **Cliquez sur "Settings"** (Paramètres) dans le menu de gauche

4. **Faites défiler jusqu'à "Redirects & Rewrites"** (Redirections et Réécritures)

5. **Cliquez sur "Add Redirect"** (Ajouter une redirection)

6. **Configurez la redirection** :
   - **Source Path** (Chemin source) : `/*`
   - **Destination Path** (Chemin destination) : `/index.html`
   - **Status Code** (Code de statut) : `200` (pas 301 ou 302 !)
   - **Force** (Forcer) : ✅ Cocher cette case

7. **Cliquez sur "Save"** (Enregistrer)

8. **Redéployez le service** :
   - Cliquez sur "Manual Deploy" → "Deploy latest commit"
   - Attendez 5-10 minutes

### Configuration Exacte

```
Source: /*
Destination: /index.html
Status Code: 200
Force: ✅ (coché)
```

**Important** :
- Le code de statut doit être **200** (pas 301/302)
- Cela permet de servir `index.html` pour toutes les routes
- React Router prendra ensuite le relais pour la navigation côté client

## 🔍 Vérification

Après configuration et redéploiement :

1. **Ouvrez votre frontend** : `https://kairos-frontend-hjg9.onrender.com`
2. **Testez une route** : `https://kairos-frontend-hjg9.onrender.com/login`
3. **Vérifiez** : La page doit se charger correctement (plus de 404)

## 📝 Note

- Le fichier `_redirects` dans `frontend/public/` est toujours utile comme backup
- Mais la configuration dans Render Dashboard est **OBLIGATOIRE** pour que ça fonctionne
- Les deux peuvent coexister sans problème

## 🐛 Si ça ne fonctionne toujours pas

1. **Vérifiez que le redirect est bien configuré** dans Render Dashboard
2. **Vérifiez que le code de statut est 200** (pas 301/302)
3. **Vérifiez que "Force" est coché**
4. **Redéployez manuellement** après avoir configuré les redirects
5. **Videz le cache du navigateur** (Ctrl+Shift+R)

---

**Dernière mise à jour** : 2026-01-15
