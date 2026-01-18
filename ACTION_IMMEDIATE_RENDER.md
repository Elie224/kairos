# 🚨 ACTION IMMÉDIATE : Correction CORS sur Render

## ❌ Problème Actuel

Les erreurs CORS persistent car l'URL `votre-backend-url.onrender.com` est utilisée dans le code compilé ou les variables d'environnement sur **Render**.

## ✅ ACTION À FAIRE SUR RENDER (MAINTENANT)

### 1️⃣ Connectez-vous à Render Dashboard
👉 https://dashboard.render.com

### 2️⃣ Allez dans votre service Frontend
- Cliquez sur votre service frontend (probablement `kairos-frontend` ou similaire)

### 3️⃣ Vérifiez les Variables d'Environnement
- Onglet **"Environment"**
- Cherchez `VITE_API_URL`

**🔍 Si vous la trouvez avec `votre-backend-url` :**
- ❌ **SUPPRIMEZ** cette variable
- OU : Modifiez-la en : `https://kairos-0aoy.onrender.com/api`

**🔍 Si elle n'existe pas ou est vide :**
- ✅ **AJOUTEZ** la variable :
  - Key: `VITE_API_URL`
  - Value: `https://kairos-0aoy.onrender.com/api`

### 4️⃣ Déclenchez un Rebuild
Après avoir modifié les variables :

1. Onglet **"Manual Deploy"**
2. Cliquez sur **"Deploy latest commit"**
3. Attendez que le build se termine (2-5 minutes)

### 5️⃣ Vérifiez les Logs
Dans les logs de build, cherchez :
- ✅ `VITE_API_URL=https://kairos-0aoy.onrender.com/api`
- ❌ **NE DEVRAIT PAS** y avoir `votre-backend-url`

### 6️⃣ Videz le Cache du Navigateur
Après le rebuild sur Render :
- Ouvrez DevTools (F12)
- Clic droit sur le bouton de rafraîchissement
- **"Vider le cache et effectuer une actualisation forcée"**

---

## 📋 Checklist

- [ ] Variable `VITE_API_URL` vérifiée sur Render
- [ ] Variable définie avec `https://kairos-0aoy.onrender.com/api`
- [ ] Rebuild déclenché sur Render
- [ ] Logs vérifiés (pas de `votre-backend-url`)
- [ ] Cache du navigateur vidé
- [ ] Erreurs CORS disparues dans la console

---

**⚠️ IMPORTANT** : Le code source est **correct**. Le problème vient uniquement de la configuration sur Render ou du cache du navigateur.
