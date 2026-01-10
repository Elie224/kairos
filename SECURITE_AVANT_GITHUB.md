# ⚠️ SÉCURITÉ - Vérifications Avant Push sur GitHub

## ✅ Vérifications Effectuées

### 1. Fichiers Sensibles
- ✅ `.env` n'existe pas (ou est dans .gitignore)
- ✅ Clé API OpenAI supprimée de `CONFIGURATION_MODELES_GPT5.md`
- ✅ `.gitignore` configuré correctement pour exclure :
  - `.env`, `.env.local`, `.env.production`
  - `venv/`, `node_modules/`
  - `*.log`, fichiers temporaires

### 2. Fichiers à Vérifier

**Avant chaque push, vérifier que :**
- ❌ Aucun fichier `.env` n'est dans le repository
- ❌ Aucune clé API réelle dans le code source
- ❌ Aucun mot de passe ou secret hardcodé
- ❌ Aucun token personnel GitHub dans le code

**Fichiers sûrs à pousser :**
- ✅ `env.example` (avec valeurs placeholder)
- ✅ `.render.yaml` (sans secrets)
- ✅ `backend/build.sh`
- ✅ Tous les fichiers source (`.py`, `.tsx`, etc.)

### 3. Clés et Secrets à Configurer sur Render

Ces valeurs doivent être configurées comme **variables d'environnement sur Render**, pas dans le code :

```bash
# À configurer sur Render (NE PAS dans le code)
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/kairos
SECRET_KEY=<générer-une-nouvelle-clé>
OPENAI_API_KEY=sk-proj-...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
POSTGRES_PASSWORD=...
```

### 4. Génération de SECRET_KEY

**AVANT de pousser sur GitHub, générer une nouvelle SECRET_KEY :**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**IMPORTANT :**
- ❌ Ne jamais utiliser la même SECRET_KEY en développement et production
- ❌ Ne jamais commiter la SECRET_KEY
- ✅ Générer une nouvelle clé pour chaque environnement

## 🔒 Checklist de Sécurité

Avant de pousser sur GitHub :

- [ ] ✅ Aucun fichier `.env` dans le repository
- [ ] ✅ Aucune clé API réelle dans le code source
- [ ] ✅ `env.example` utilise des placeholders (`your-...-here`)
- [ ] ✅ `.gitignore` exclut tous les fichiers sensibles
- [ ] ✅ Tous les secrets sont dans les variables d'environnement (pas dans le code)
- [ ] ✅ Aucun mot de passe hardcodé
- [ ] ✅ Aucun token personnel GitHub dans le code
- [ ] ✅ Fichiers de documentation vérifiés (pas de vraies clés)

## 🚨 Si vous avez Accidentellement Poussé des Secrets

**URGENT - À faire immédiatement :**

1. **Supprimer les secrets de GitHub :**
   - Aller sur GitHub > Repository > Fichier concerné
   - Supprimer le fichier avec les secrets
   - Faire un nouveau commit

2. **Régénérer TOUS les secrets exposés :**
   - SECRET_KEY : Générer une nouvelle clé
   - OPENAI_API_KEY : Générer une nouvelle clé sur OpenAI
   - MongoDB : Changer le mot de passe
   - Stripe : Régénérer les clés API
   - PostgreSQL : Changer le mot de passe

3. **Nettoyer l'historique Git (si nécessaire) :**
   ```bash
   # Utiliser git filter-branch ou BFG Repo-Cleaner
   # Attention : Cela réécrit l'historique Git
   ```

4. **Informer tous les collaborateurs :**
   - Tous les secrets ont été compromis
   - Ne plus utiliser les anciennes clés

## 📚 Ressources

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Render Environment Variables](https://render.com/docs/environment-variables)
