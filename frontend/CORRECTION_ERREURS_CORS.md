# 🔧 Correction des Erreurs CORS

## ❌ Problème Identifié

Des erreurs CORS répétées apparaissent dans la console :
```
Access to fetch at 'https://votre-backend-url.onrender.com/api/admin/migrate-quota-to-20gb' 
from origin 'https://kairos-frontend-hjg9.onrender.com' has been blocked by CORS policy
```

## 🔍 Analyse

1. **URL Placeholder** : `votre-backend-url.onrender.com` est un placeholder qui n'a pas été remplacé
2. **Endpoint Inexistant** : `/admin/migrate-quota-to-20gb` n'existe pas dans le backend
3. **Boucle Infinie** : Les erreurs se répètent, indiquant un script qui se réexécute en boucle

## ✅ Solution

### Option 1 : Vider le Cache du Navigateur (Solution Rapide)

1. Ouvrir les outils de développement (F12)
2. Clic droit sur le bouton de rafraîchissement
3. Sélectionner "Vider le cache et effectuer une actualisation forcée"
4. OU : Ctrl + Shift + Delete → Cocher "Images et fichiers en cache" → Effacer

### Option 2 : Rebuild le Frontend (Solution Définitive)

Si l'URL placeholder est dans le code compilé :

```powershell
cd frontend
npm run build
```

### Option 3 : Vérifier les Variables d'Environnement

Sur Render, vérifier que `VITE_API_URL` est définie correctement :
- ✅ **Correct** : `VITE_API_URL=https://kairos-0aoy.onrender.com/api`
- ❌ **Incorrect** : `VITE_API_URL=https://votre-backend-url.onrender.com/api`

## 🔒 Configuration CORS Backend

La configuration CORS du backend autorise déjà :
- ✅ `https://kairos-frontend-hjg9.onrender.com`
- ✅ `https://kairos-0aoy.onrender.com`
- ✅ Tous les domaines `*.onrender.com` en production

## 📝 Vérification

1. Vérifier dans la console du navigateur s'il y a des scripts injectés
2. Vérifier les variables d'environnement sur Render
3. Rebuild le frontend si nécessaire

---

**Note** : Si les erreurs persistent après avoir vidé le cache et rebuild, il s'agit probablement d'un script malveillant injecté dans la page. Dans ce cas, vérifier les extensions de navigateur ou les scripts tiers.
