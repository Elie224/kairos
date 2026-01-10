# Guide Complet - Création Repository GitHub et Push du Code

Ce guide vous accompagne étape par étape pour créer un repository GitHub et pousser votre code Kaïros.

## 📋 Prérequis

1. Compte GitHub créé (si pas encore fait : https://github.com/signup)
2. Git installé sur votre machine
   - Vérifier : `git --version`
   - Télécharger : https://git-scm.com/downloads
3. Code du projet Kaïros prêt

## 🚀 Étape 1 : Créer le Repository sur GitHub

### 1.1 Se connecter à GitHub

1. Aller sur https://github.com
2. Se connecter avec vos identifiants
3. Cliquer sur le **"+"** en haut à droite > **"New repository"**

### 1.2 Configurer le Repository

**Paramètres à configurer :**

- **Repository name** : `kairos` (ou `kairos-platform`, `kairos-learning`, etc.)
- **Description** (optionnel) : `Plateforme d'apprentissage immersif avec IA - Kaïros`
- **Visibility** :
  - ✅ **Public** : Visible par tout le monde (gratuit, illimité)
  - 🔒 **Private** : Visible uniquement par vous (gratuit, 3 collaborateurs max)
- **Ne PAS cocher** :
  - ❌ Add a README file (on va le créer nous-mêmes)
  - ❌ Add .gitignore (on a déjà un .gitignore)
  - ❌ Choose a license (optionnel, peut être ajouté plus tard)

### 1.3 Créer le Repository

1. Cliquer sur **"Create repository"** (bouton vert)
2. **NE PAS** suivre les instructions qui s'affichent sur GitHub
3. Noter l'URL du repository :
   - HTTPS : `https://github.com/VOTRE_USERNAME/kairos.git`
   - SSH : `git@github.com:VOTRE_USERNAME/kairos.git`

## 🚀 Étape 2 : Configurer Git Localement (si pas déjà fait)

### 2.1 Vérifier la Configuration Git

Ouvrir PowerShell ou Terminal dans le dossier du projet :

```powershell
# Vérifier si Git est installé
git --version

# Si erreur, installer Git : https://git-scm.com/downloads
```

### 2.2 Configurer Git (si pas déjà fait)

```powershell
# Configurer votre nom (remplacer par votre nom)
git config --global user.name "Votre Nom"

# Configurer votre email (remplacer par votre email GitHub)
git config --global user.email "votre.email@example.com"

# Vérifier la configuration
git config --global --list
```

**Important** : Utilisez l'email associé à votre compte GitHub !

## 🚀 Étape 3 : Initialiser Git dans le Projet

### 3.1 Vérifier si Git est déjà initialisé

```powershell
# Se placer dans le dossier du projet
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"

# Vérifier si Git est déjà initialisé
git status
```

**Si erreur "not a git repository"** : Git n'est pas encore initialisé, passer à l'étape 3.2  
**Si aucun erreur** : Git est déjà initialisé, passer à l'étape 4

### 3.2 Initialiser Git (si nécessaire)

```powershell
# Initialiser Git
git init

# Vérifier que c'est bien initialisé
git status
```

## 🚀 Étape 4 : Vérifier et Préparer les Fichiers

### 4.1 Vérifier le .gitignore

Assurez-vous que le fichier `.gitignore` existe et contient :

```powershell
# Vérifier que .gitignore existe
cat .gitignore

# Ou l'ouvrir dans un éditeur
code .gitignore
```

**Le .gitignore doit contenir au minimum :**
```
# Environment
.env
.env.local

# Logs
*.log

# Python
__pycache__/
*.py[cod]
venv/
env/

# Node
node_modules/
dist/
```

### 4.2 Vérifier les Fichiers à Ajouter

```powershell
# Voir les fichiers qui seront ajoutés
git status

# Vérifier que les fichiers sensibles ne sont PAS listés :
# ❌ .env (ne doit PAS apparaître)
# ❌ venv/ (ne doit PAS apparaître)
# ❌ node_modules/ (ne doit PAS apparaître)
# ✅ .render.yaml (DOIT apparaître)
# ✅ env.example (DOIT apparaître)
# ✅ backend/build.sh (DOIT apparaître)
```

### 4.3 Si .env est listé (ERREUR - à corriger)

```powershell
# Supprimer .env du cache Git (mais garder le fichier localement)
git rm --cached .env

# S'assurer que .env est dans .gitignore
echo ".env" >> .gitignore

# Vérifier
git status
```

## 🚀 Étape 5 : Ajouter les Fichiers au Repository Git

### 5.1 Ajouter Tous les Fichiers (sauf ceux dans .gitignore)

```powershell
# Ajouter tous les fichiers qui ne sont pas dans .gitignore
git add .

# Vérifier ce qui a été ajouté
git status
```

### 5.2 Vérifier que les Fichiers Importants sont Présents

```powershell
# Vérifier que les fichiers suivants sont bien ajoutés :
git ls-files | Select-String -Pattern "\.render\.yaml|env\.example|build\.sh|\.gitignore"
```

**Fichiers qui DOIVENT être présents :**
- ✅ `.render.yaml`
- ✅ `env.example`
- ✅ `backend/build.sh`
- ✅ `.gitignore`
- ✅ `DEPLOIEMENT_RENDER.md`
- ✅ `README_DEPLOIEMENT_GITHUB.md`
- ✅ `backend/requirements.txt`
- ✅ `frontend/package.json`
- ✅ Et tous les fichiers source du projet

**Fichiers qui NE DOIVENT PAS être présents :**
- ❌ `.env` (avec de vraies clés)
- ❌ `venv/`
- ❌ `node_modules/`
- ❌ `*.log`

## 🚀 Étape 6 : Créer le Premier Commit

### 6.1 Créer le Commit

```powershell
# Créer un commit avec un message descriptif
git commit -m "Initial commit - Préparation déploiement Render

- Configuration Render (.render.yaml)
- Variables d'environnement (env.example)
- Script de build backend
- Documentation déploiement complète
- Mise à jour configuration pour production"
```

**Si c'est le premier commit, Git peut demander de configurer l'identité :**
```powershell
# Si erreur, configurer Git (voir étape 2.2)
git config user.name "Votre Nom"
git config user.email "votre.email@example.com"
```

### 6.2 Vérifier le Commit

```powershell
# Voir l'historique des commits
git log --oneline

# Doit afficher quelque chose comme :
# abc1234 Initial commit - Préparation déploiement Render
```

## 🚀 Étape 7 : Connecter au Repository GitHub

### 7.1 Ajouter le Remote

```powershell
# Remplacer VOTRE_USERNAME et kairos par vos valeurs réelles
git remote add origin https://github.com/VOTRE_USERNAME/kairos.git

# Exemple concret :
# git remote add origin https://github.com/johndoe/kairos.git
```

**Si erreur "remote origin already exists"** :

```powershell
# Vérifier le remote actuel
git remote -v

# Si nécessaire, supprimer et recréer
git remote remove origin
git remote add origin https://github.com/VOTRE_USERNAME/kairos.git
```

### 7.2 Vérifier le Remote

```powershell
# Vérifier que le remote est bien configuré
git remote -v

# Doit afficher :
# origin  https://github.com/VOTRE_USERNAME/kairos.git (fetch)
# origin  https://github.com/VOTRE_USERNAME/kairos.git (push)
```

## 🚀 Étape 8 : Pousser le Code sur GitHub

### 8.1 Renommer la Branche en "main" (si nécessaire)

Git utilise maintenant "main" au lieu de "master" :

```powershell
# Vérifier la branche actuelle
git branch

# Si la branche est "master", la renommer en "main"
git branch -M main

# Vérifier
git branch
```

### 8.2 Pousser sur GitHub

```powershell
# Pousser le code sur GitHub (première fois)
git push -u origin main
```

**GitHub va demander vos identifiants :**

**Option 1 : Authentification par Navigateur (Recommandé)**
- Git ouvrira automatiquement votre navigateur
- Se connecter à GitHub dans le navigateur
- Autoriser l'accès
- Revenir au terminal

**Option 2 : Token Personnel (Si l'option 1 ne fonctionne pas)**

1. Aller sur GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Générer un nouveau token :
   - Note : `Git CLI`
   - Expiration : `90 days` (ou plus)
   - Scopes : Cocher `repo` (tous les sous-éléments)
3. Cliquer sur "Generate token"
4. **COPIER le token** (il ne sera affiché qu'une fois !)
5. Dans PowerShell, quand demandé :
   - Username : Votre nom d'utilisateur GitHub
   - Password : Coller le token (pas votre mot de passe)

### 8.3 Vérifier que le Push a Réussi

```powershell
# Vérifier le statut
git status

# Doit afficher :
# On branch main
# Your branch is up to date with 'origin/main'.
```

### 8.4 Vérifier sur GitHub

1. Aller sur https://github.com/VOTRE_USERNAME/kairos
2. Vérifier que tous les fichiers sont présents
3. Vérifier que `.env` et `node_modules/` ne sont **PAS** dans le repository
4. Vérifier que `.render.yaml` et `env.example` sont présents

## 🚀 Étape 9 : Vérifications Finales

### 9.1 Checklist sur GitHub

Aller sur votre repository GitHub et vérifier :

- [ ] ✅ Tous les fichiers source sont présents
- [ ] ✅ `.render.yaml` est présent
- [ ] ✅ `env.example` est présent
- [ ] ✅ `README.md` est présent (ou sera ajouté)
- [ ] ❌ `.env` n'est **PAS** dans le repository
- [ ] ❌ `venv/` n'est **PAS** dans le repository
- [ ] ❌ `node_modules/` n'est **PAS** dans le repository
- [ ] ❌ `*.log` ne sont **PAS** dans le repository

### 9.2 Si des Fichiers Sensibles sont Présents (URGENT)

**Si vous voyez `.env` ou des fichiers avec des clés API sur GitHub :**

1. **SUPPRIMER immédiatement le fichier** sur GitHub
2. **Régénérer toutes les clés** :
   - SECRET_KEY
   - OPENAI_API_KEY
   - Mots de passe MongoDB
   - Clés Stripe
3. **Nettoyer l'historique Git** :

```powershell
# Supprimer le fichier de l'historique Git
git rm --cached .env
git commit -m "Remove sensitive files from Git history"
git push origin main

# OU utiliser git filter-branch (plus complexe mais plus efficace)
```

**Note** : Même après suppression, l'historique Git contient encore les fichiers. Considérez changer les clés exposées.

## 🔄 Pour les Prochains Pushes

Une fois le repository configuré, pour pousser des modifications :

```powershell
# 1. Vérifier les modifications
git status

# 2. Ajouter les fichiers modifiés
git add .

# 3. Créer un commit
git commit -m "Description des modifications"

# 4. Pousser sur GitHub
git push
```

## 🐛 Résolution de Problèmes

### Erreur : "remote origin already exists"

```powershell
# Vérifier le remote
git remote -v

# Supprimer et recréer
git remote remove origin
git remote add origin https://github.com/VOTRE_USERNAME/kairos.git
```

### Erreur : "refusing to merge unrelated histories"

```powershell
# Si le repository GitHub contient déjà du code (README, .gitignore, etc.)
git pull origin main --allow-unrelated-histories

# Résoudre les conflits si nécessaire dans les fichiers
# Puis :
git add .
git commit -m "Merge with GitHub repository"
git push origin main
```

### Erreur : "authentication failed"

1. Vérifier que vous utilisez le bon nom d'utilisateur
2. Utiliser un token personnel GitHub (voir étape 8.2)
3. Vérifier que le token a les permissions `repo`

### Erreur : "not a git repository"

```powershell
# Réinitialiser Git
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/VOTRE_USERNAME/kairos.git
git push -u origin main
```

### Erreur : "filename too long"

```powershell
# Activer le support des longs noms de fichiers (Windows)
git config --global core.longpaths true

# Réessayer
git add .
git commit -m "Initial commit"
git push -u origin main
```

### Erreur : "Permission denied (publickey)"

Si vous utilisez SSH :

```powershell
# Utiliser HTTPS à la place
git remote set-url origin https://github.com/VOTRE_USERNAME/kairos.git

# Réessayer
git push -u origin main
```

## 📚 Commandes Git Utiles

```powershell
# Voir l'état du repository
git status

# Voir l'historique des commits
git log --oneline

# Voir les différences
git diff

# Voir les fichiers trackés
git ls-files

# Voir les remotes
git remote -v

# Changer l'URL du remote
git remote set-url origin https://github.com/VOTRE_USERNAME/kairos.git

# Supprimer un fichier de Git (mais garder localement)
git rm --cached fichier.txt

# Annuler des modifications non commitées
git checkout -- fichier.txt

# Annuler le dernier commit (garder les modifications)
git reset --soft HEAD~1
```

## ✅ Checklist Finale

- [ ] Repository GitHub créé
- [ ] Git configuré localement (nom + email)
- [ ] Repository Git initialisé
- [ ] .gitignore vérifié et à jour
- [ ] Fichiers sensibles exclus (.env, venv, node_modules)
- [ ] Tous les fichiers ajoutés (`git add .`)
- [ ] Premier commit créé
- [ ] Remote GitHub ajouté
- [ ] Code poussé sur GitHub (`git push`)
- [ ] Repository vérifié sur GitHub
- [ ] Aucun fichier sensible exposé

## 🎉 Félicitations !

Votre code est maintenant sur GitHub ! 

**Prochaine étape** : Suivre le guide `DEPLOIEMENT_RENDER.md` pour déployer sur Render.

## 📞 Besoin d'Aide ?

- [Documentation GitHub](https://docs.github.com)
- [Documentation Git](https://git-scm.com/doc)
- [GitHub Support](https://support.github.com)
