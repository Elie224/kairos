# Préparation du Déploiement - Push sur GitHub

Ce guide explique comment préparer et pousser le code sur GitHub avant le déploiement sur Render.

## 📋 Prérequis

1. Compte GitHub créé
2. Git installé sur votre machine
3. Repository GitHub créé (vide ou non)

## 🚀 Étapes pour Pousser sur GitHub

### 1. Initialiser Git (si pas déjà fait)

```bash
# Vérifier si Git est déjà initialisé
git status

# Si erreur "not a git repository", initialiser Git
git init

# Configurer Git (si pas déjà fait)
git config user.name "Votre Nom"
git config user.email "votre.email@example.com"
```

### 2. Ajouter les Fichiers de Déploiement

Les fichiers suivants doivent être ajoutés au repository :

- ✅ `.render.yaml` - Configuration Render
- ✅ `env.example` - Exemple de variables d'environnement
- ✅ `backend/build.sh` - Script de build pour Render
- ✅ `.gitignore` - Fichiers à ignorer (mise à jour)
- ✅ `DEPLOIEMENT_RENDER.md` - Documentation de déploiement

### 3. Vérifier le .gitignore

Assurez-vous que le `.gitignore` contient :

```
# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
# Garder .env.example dans le repo pour la documentation
!.env.example

# Logs
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
dist/
build/

# Node
node_modules/
dist/
.npm
.eslintcache

# Uploads (optionnel - à garder si vous voulez versionner les fichiers de test)
# uploads/

# Database
*.db
*.sqlite
```

### 4. Ajouter et Commiter les Fichiers

```bash
# Vérifier l'état
git status

# Ajouter tous les fichiers (sauf ceux dans .gitignore)
git add .

# Ou ajouter fichiers par fichiers
git add .render.yaml
git add env.example
git add backend/build.sh
git add .gitignore
git add DEPLOIEMENT_RENDER.md
git add frontend/vite.config.ts

# Vérifier ce qui sera commité
git status

# Créer un commit
git commit -m "Préparation déploiement Render

- Ajout configuration Render (.render.yaml)
- Ajout exemple variables d'environnement (env.example)
- Ajout script de build backend
- Mise à jour .gitignore
- Mise à jour vite.config.ts pour production
- Documentation déploiement Render"
```

### 5. Connecter au Repository GitHub

```bash
# Si le repository GitHub n'existe pas encore, le créer sur GitHub d'abord
# Puis connecter le repository local

# Ajouter le remote (remplacer USERNAME et REPO_NAME)
git remote add origin https://github.com/USERNAME/REPO_NAME.git

# Ou avec SSH (si configuré)
# git remote add origin git@github.com:USERNAME/REPO_NAME.git

# Vérifier le remote
git remote -v
```

### 6. Pousser sur GitHub

```bash
# Si c'est la première fois et que le repository GitHub est vide
git push -u origin main

# Si le repository GitHub contient déjà du code
git pull origin main --allow-unrelated-histories
# Résoudre les conflits si nécessaire
git push -u origin main

# Pour les prochaines fois, simplement
git push
```

### 7. Vérifier sur GitHub

1. Aller sur https://github.com/USERNAME/REPO_NAME
2. Vérifier que tous les fichiers sont présents
3. Vérifier que `.env` et `node_modules/` ne sont **PAS** dans le repository
4. Vérifier que `.render.yaml` est présent

## 🔍 Checklist avant Push

- [ ] Tous les fichiers sensibles (`.env`, clés API) sont dans `.gitignore`
- [ ] Le fichier `.render.yaml` est présent
- [ ] Le fichier `env.example` est présent (sans vraies valeurs sensibles)
- [ ] Le script `backend/build.sh` est présent et exécutable
- [ ] Le `.gitignore` est à jour
- [ ] Les fichiers `venv/` et `node_modules/` ne sont pas dans le repo
- [ ] Tous les fichiers de configuration nécessaires sont commités
- [ ] Le message de commit est clair et descriptif

## ⚠️ Important - Sécurité

**NE JAMAIS COMMITER** :
- ❌ Fichiers `.env` avec de vraies clés
- ❌ Clés API OpenAI
- ❌ Secrets JWT (SECRET_KEY)
- ❌ Mots de passe de base de données
- ❌ Clés Stripe
- ❌ Certificats SSL/TLS

**UTILISER** :
- ✅ `env.example` avec des valeurs de placeholder
- ✅ Variables d'environnement sur Render
- ✅ Secrets GitHub (pour CI/CD si nécessaire)

## 🐛 Résolution de Problèmes

### Erreur: "remote origin already exists"

```bash
# Vérifier le remote actuel
git remote -v

# Si nécessaire, supprimer et recréer
git remote remove origin
git remote add origin https://github.com/USERNAME/REPO_NAME.git
```

### Erreur: "refusing to merge unrelated histories"

```bash
git pull origin main --allow-unrelated-histories
# Résoudre les conflits si nécessaire
git push origin main
```

### Fichiers sensibles déjà commités

```bash
# Supprimer le fichier du cache Git (mais garder localement)
git rm --cached .env

# Ajouter au .gitignore si pas déjà fait
echo ".env" >> .gitignore

# Commit les changements
git add .gitignore
git commit -m "Remove sensitive files from Git"

# Pousser
git push origin main
```

**ATTENTION** : Si des fichiers sensibles ont déjà été poussés sur GitHub, les clés sont compromises. Il faut les régénérer immédiatement.

## 📚 Prochaines Étapes

Une fois le code poussé sur GitHub :

1. Aller sur [Render Dashboard](https://dashboard.render.com)
2. Suivre le guide dans `DEPLOIEMENT_RENDER.md`
3. Connecter le repository GitHub à Render
4. Configurer les variables d'environnement sur Render
5. Déployer !

## 🔗 Liens Utiles

- [GitHub Documentation](https://docs.github.com)
- [Git Documentation](https://git-scm.com/doc)
- [Render Documentation](https://render.com/docs)
