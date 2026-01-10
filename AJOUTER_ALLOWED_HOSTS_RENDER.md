# 🔧 Ajouter ALLOWED_HOSTS sur Render - Guide Rapide

## 🎯 Important : CORS n'est PAS une variable d'environnement !

CORS est configuré dans le **code Python** (`backend/main.py`). Cependant, le code utilise certaines **variables d'environnement** pour déterminer quelles origines autoriser.

## ✅ Variables d'Environnement Nécessaires pour CORS

### Backend sur Render Dashboard

Allez sur **Render Dashboard** → Service Backend (`kairos-0aoy`) → **Environment** :

#### 1. Variable OBLIGATOIRE : `ALLOWED_HOSTS`

- **Key** : `ALLOWED_HOSTS`
- **Value** : `*`
- **Description** : Permet au code de détecter qu'il faut autoriser tous les domaines Render

#### 2. Variable OBLIGATOIRE : `ENVIRONMENT`

- **Key** : `ENVIRONMENT`
- **Value** : `production`
- **Description** : Active le mode production qui active la détection Render automatique

#### 3. Variable RECOMMANDÉE : `FRONTEND_URL`

- **Key** : `FRONTEND_URL`
- **Value** : `https://kairos-frontend-hjg9.onrender.com`
- **Description** : URL exacte du frontend (pour les liens dans les emails et priorité CORS)

## 📝 Étapes pour Ajouter les Variables

### Option 1 : Via Render Dashboard (Recommandé si services créés manuellement)

1. **Allez sur** : https://dashboard.render.com
2. **Cliquez sur votre service backend** : `kairos-0aoy` (ou le nom de votre service)
3. **Allez dans l'onglet "Environment"** (Variables d'environnement)
4. **Cliquez sur "Add Environment Variable"** pour chaque variable

#### Ajouter `ALLOWED_HOSTS` :
   - Key : `ALLOWED_HOSTS`
   - Value : `*`
   - Cliquez sur "Save Changes"

#### Ajouter `ENVIRONMENT` (si pas déjà présent) :
   - Key : `ENVIRONMENT`
   - Value : `production`
   - Cliquez sur "Save Changes"

#### Ajouter `FRONTEND_URL` :
   - Key : `FRONTEND_URL`
   - Value : `https://kairos-frontend-hjg9.onrender.com`
   - Cliquez sur "Save Changes"

5. **Le service redémarre automatiquement** après chaque sauvegarde

### Option 2 : Via `.render.yaml` (Si services créés via Blueprint)

Si vos services ont été créés via un **Render Blueprint** (en utilisant `.render.yaml`), les variables sont automatiquement configurées :

```yaml
envVars:
  - key: ALLOWED_HOSTS
    value: "*"
  - key: ENVIRONMENT
    value: production
  - key: FRONTEND_URL
    value: https://kairos-frontend-hjg9.onrender.com
```

**Mais** : Si vos services ont été créés **manuellement** avant de créer `.render.yaml`, alors `.render.yaml` n'est **pas utilisé** et vous devez configurer les variables **manuellement** dans Render Dashboard (Option 1).

## 🔍 Comment Savoir si `.render.yaml` est Utilisé ?

1. Allez sur Render Dashboard
2. Regardez la section "Infrastructure as Code" ou "Blueprint" de votre service
3. Si vous voyez une mention de `.render.yaml`, alors il est utilisé
4. Sinon, configurez les variables manuellement

## ✅ Vérification après Configuration

### 1. Vérifier dans les Logs Render

Après avoir ajouté les variables et redémarré le service, vous devriez voir dans les logs :

```
✅ FRONTEND_URL configuré: https://kairos-frontend-hjg9.onrender.com
🌐 Détection Render : Autorisation automatique des domaines *.onrender.com
🌐 ALLOWED_HOSTS=* détecté : Autorisation de tous les domaines Render
🌐 CORS autorisé pour les origines en production (4 origines): [...]
```

### 2. Tester depuis le Frontend

1. Ouvrez votre frontend : `https://kairos-frontend-hjg9.onrender.com`
2. Ouvrez la console du navigateur (F12)
3. Essayez de vous connecter
4. ✅ Si ça fonctionne sans erreur CORS, **c'est bon !**

## 🚨 Si CORS Ne Fonctionne Toujours Pas

### Vérifier que les Variables sont Bien Configurées

1. **Dans Render Dashboard → Service Backend → Environment** :
   - Vérifiez que `ALLOWED_HOSTS` = `*` est présent
   - Vérifiez que `ENVIRONMENT` = `production` est présent
   - Vérifiez que `FRONTEND_URL` est présent avec la bonne URL

2. **Redémarrez le service manuellement** :
   - Render Dashboard → Service Backend → "Manual Deploy" → "Deploy latest commit"

### Vérifier que le Frontend Utilise la Bonne URL Backend

1. **Dans Render Dashboard → Service Frontend → Environment** :
   - Vérifiez que `VITE_API_URL` = `https://kairos-0aoy.onrender.com` est présent
   - Si absente, ajoutez-la

2. **Redéployez le frontend** pour que `VITE_API_URL` soit pris en compte dans le build

## 📋 Checklist Complète

### Backend (`kairos-0aoy`) ✅
- [ ] `ALLOWED_HOSTS` = `*` (OBLIGATOIRE)
- [ ] `ENVIRONMENT` = `production` (OBLIGATOIRE)
- [ ] `FRONTEND_URL` = `https://kairos-frontend-hjg9.onrender.com` (RECOMMANDÉ)
- [ ] `MONGODB_URL` = (connection string MongoDB)
- [ ] `MONGODB_DB_NAME` = `kairos`
- [ ] `SECRET_KEY` = (clé secrète)
- [ ] `OPENAI_API_KEY` = (clé API OpenAI)

### Frontend (`kairos-frontend-hjg9`) ✅
- [ ] `VITE_API_URL` = `https://kairos-0aoy.onrender.com` (OBLIGATOIRE)

## ✅ Résumé

**CORS n'est PAS une variable** - c'est configuré dans le code. Mais le code utilise ces variables pour déterminer les origines autorisées :

1. ✅ Ajoutez `ALLOWED_HOSTS=*` sur le backend Render
2. ✅ Ajoutez `ENVIRONMENT=production` sur le backend Render (si pas déjà présent)
3. ✅ Ajoutez `FRONTEND_URL` sur le backend Render
4. ✅ Ajoutez `VITE_API_URL` sur le frontend Render
5. ✅ Redéployez les services
6. ✅ Testez la connexion

Une fois ces variables configurées, CORS fonctionnera automatiquement ! 🎉
