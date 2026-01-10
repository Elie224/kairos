# 📸 Guide Visuel - Création Repository GitHub

Guide étape par étape avec captures d'écran (description textuelle).

## 🎯 Vue d'Ensemble

```
1. Créer Repository sur GitHub          [5 minutes]
2. Configurer Git Local                 [2 minutes]
3. Initialiser Git dans le Projet       [1 minute]
4. Préparer les Fichiers                [3 minutes]
5. Créer le Premier Commit              [2 minutes]
6. Connecter au Repository GitHub       [1 minute]
7. Pousser le Code                      [3 minutes]
──────────────────────────────────────────────────
TOTAL : ~17 minutes
```

## 📝 ÉTAPE 1 : Créer le Repository sur GitHub

### 1.1 Ouvrir GitHub

1. Aller sur **https://github.com**
2. Se connecter avec vos identifiants

### 1.2 Créer un Nouveau Repository

1. Cliquer sur le **"+"** en haut à droite
2. Sélectionner **"New repository"**

### 1.3 Configurer le Repository

**Sur la page de création :**

```
┌─────────────────────────────────────────────┐
│ Repository name *                           │
│ ┌─────────────────────────────────────────┐ │
│ │ kairos                                   │ │
│ └─────────────────────────────────────────┘ │
│                                              │
│ Description (optional)                       │
│ ┌─────────────────────────────────────────┐ │
│ │ Plateforme d'apprentissage immersif...  │ │
│ └─────────────────────────────────────────┘ │
│                                              │
│ ○ Public   ◉ Private                         │
│   Anyone can see this repository             │
│   You choose who can see and commit          │
│                                              │
│ ☐ Add a README file    [NE PAS COCHER]      │
│ ☐ Add .gitignore       [NE PAS COCHER]      │
│ ☐ Choose a license     [NE PAS COCHER]      │
│                                              │
│              [Create repository]             │
└─────────────────────────────────────────────┘
```

**Configuration recommandée :**
- ✅ **Repository name** : `kairos` (ou un autre nom)
- ✅ **Description** : `Plateforme d'apprentissage immersif avec IA`
- ✅ **Visibility** : `Public` (gratuit, illimité) ou `Private` (gratuit, 3 collaborateurs)
- ❌ **NE PAS cocher** les options (README, .gitignore, license)

### 1.4 Créer le Repository

1. Cliquer sur **"Create repository"** (bouton vert)
2. **IGNORER** les instructions qui s'affichent après
3. **COPIER** l'URL du repository :
   - HTTPS : `https://github.com/VOTRE_USERNAME/kairos.git`
   - Notez cette URL, vous en aurez besoin plus tard

---

## 💻 ÉTAPE 2 : Ouvrir PowerShell dans le Dossier du Projet

### 2.1 Ouvrir PowerShell

**Option 1 : Depuis l'Explorateur Windows**
1. Ouvrir l'Explorateur de fichiers
2. Naviguer vers `C:\Users\KOURO\OneDrive\Desktop\Kairós`
3. Cliquer avec le bouton droit dans le dossier
4. Sélectionner **"Ouvrir dans le terminal"** ou **"Ouvrir dans PowerShell"**

**Option 2 : Depuis PowerShell**
1. Ouvrir PowerShell
2. Taper :
```powershell
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
```

### 2.2 Vérifier que vous êtes au bon endroit

```powershell
pwd
# Doit afficher : C:\Users\KOURO\OneDrive\Desktop\Kairós

ls
# Doit afficher les dossiers : backend, frontend, etc.
```

---

## ⚙️ ÉTAPE 3 : Configurer Git (si pas déjà fait)

### 3.1 Vérifier que Git est Installé

```powershell
git --version
# Doit afficher : git version 2.x.x
```

**Si erreur** : Installer Git depuis https://git-scm.com/downloads

### 3.2 Configurer Git

```powershell
# Remplacer "Votre Nom" par votre vrai nom
git config --global user.name "Votre Nom"

# Remplacer "votre.email@example.com" par votre email GitHub
git config --global user.email "votre.email@example.com"

# Vérifier la configuration
git config --global --list
```

**Important** : Utilisez l'email associé à votre compte GitHub !

---

## 📦 ÉTAPE 4 : Initialiser Git dans le Projet

### 4.1 Vérifier si Git est Déjà Initialisé

```powershell
git status
```

**Résultat possible 1** : Affiche des fichiers
```
On branch main
...
```
✅ Git est déjà initialisé → Passer à l'ÉTAPE 5

**Résultat possible 2** : Erreur "not a git repository"
```
fatal: not a git repository (or any of the parent directories): .git
```
→ Initialiser Git maintenant :

### 4.2 Initialiser Git (si nécessaire)

```powershell
git init
# Doit afficher : Initialized empty Git repository in C:/Users/KOURO/OneDrive/Desktop/Kairós/.git/

# Vérifier
git status
# Doit maintenant afficher des fichiers
```

---

## ✅ ÉTAPE 5 : Vérifier les Fichiers à Ajouter

### 5.1 Vérifier l'État Actuel

```powershell
git status
```

**Résultat attendu :**
```
On branch main

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        .gitignore
        .render.yaml
        DEPLOIEMENT_RENDER.md
        backend/
        env.example
        frontend/
        ...
```

### 5.2 Vérifier que les Fichiers Sensibles ne sont PAS Listés

**Fichiers qui NE DOIVENT PAS apparaître :**
- ❌ `.env` (ne doit PAS être là)
- ❌ `venv/` (ne doit PAS être là)
- ❌ `node_modules/` (ne doit PAS être là)

**Fichiers qui DOIVENT apparaître :**
- ✅ `.gitignore`
- ✅ `.render.yaml`
- ✅ `env.example`
- ✅ `backend/build.sh`
- ✅ `backend/requirements.txt`
- ✅ `frontend/package.json`
- ✅ Et tous les autres fichiers source

### 5.3 Si .env est Listé (PROBLÈME à Corriger)

```powershell
# Supprimer .env du cache Git (mais garder le fichier localement)
git rm --cached .env

# S'assurer que .env est dans .gitignore
echo ".env" >> .gitignore

# Vérifier
git status
# .env ne doit plus apparaître
```

---

## ➕ ÉTAPE 6 : Ajouter les Fichiers au Repository

### 6.1 Ajouter Tous les Fichiers

```powershell
git add .
```

**Aucune sortie = Succès !**

### 6.2 Vérifier ce qui a été Ajouté

```powershell
git status
```

**Résultat attendu :**
```
On branch main

Changes to be committed:
  (use "git reset HEAD <file>..." to unstage)
        new file:   .gitignore
        new file:   .render.yaml
        new file:   DEPLOIEMENT_RENDER.md
        new file:   backend/build.sh
        ...
```

**Vérifier que :**
- ✅ `.render.yaml` est listé
- ✅ `env.example` est listé
- ✅ `backend/build.sh` est listé
- ❌ `.env` n'est PAS listé
- ❌ `venv/` n'est PAS listé
- ❌ `node_modules/` n'est PAS listé

---

## 💾 ÉTAPE 7 : Créer le Premier Commit

### 7.1 Créer le Commit

```powershell
git commit -m "Initial commit - Préparation déploiement Render"
```

**Résultat attendu :**
```
[main (root-commit) abc1234] Initial commit - Préparation déploiement Render
 150 files changed, 12345 insertions(+)
```

**Si erreur** : "Please tell me who you are"
→ Retourner à l'ÉTAPE 3 pour configurer Git

### 7.2 Vérifier le Commit

```powershell
git log --oneline
```

**Résultat attendu :**
```
abc1234 (HEAD -> main) Initial commit - Préparation déploiement Render
```

---

## 🔗 ÉTAPE 8 : Connecter au Repository GitHub

### 8.1 Ajouter le Remote

**Important** : Remplacer `VOTRE_USERNAME` et `kairos` par vos valeurs réelles !

```powershell
# Général (à adapter)
git remote add origin https://github.com/VOTRE_USERNAME/kairos.git

# Exemple concret :
# git remote add origin https://github.com/johndoe/kairos.git
```

**Si erreur** : "remote origin already exists"
```powershell
# Vérifier le remote actuel
git remote -v

# Supprimer et recréer
git remote remove origin
git remote add origin https://github.com/VOTRE_USERNAME/kairos.git
```

### 8.2 Vérifier le Remote

```powershell
git remote -v
```

**Résultat attendu :**
```
origin  https://github.com/VOTRE_USERNAME/kairos.git (fetch)
origin  https://github.com/VOTRE_USERNAME/kairos.git (push)
```

### 8.3 Renommer la Branche en "main" (si nécessaire)

```powershell
# Vérifier la branche actuelle
git branch

# Si la branche s'appelle "master", la renommer
git branch -M main

# Vérifier
git branch
# Doit afficher : * main
```

---

## 🚀 ÉTAPE 9 : Pousser le Code sur GitHub

### 9.1 Pousser le Code

```powershell
git push -u origin main
```

### 9.2 Authentification GitHub

**GitHub va demander vos identifiants :**

**Option 1 : Authentification par Navigateur (Recommandé)**
1. PowerShell va afficher :
   ```
   info: please complete authentication in your browser...
   ```
2. Votre navigateur s'ouvrira automatiquement
3. Se connecter à GitHub dans le navigateur
4. Autoriser l'accès Git
5. Revenir au terminal PowerShell
6. Le push continuera automatiquement

**Option 2 : Token Personnel (Si l'option 1 ne fonctionne pas)**

1. Aller sur GitHub :
   - Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Cliquer sur "Generate new token (classic)"
3. Configurer :
   - Note : `Git CLI`
   - Expiration : `90 days`
   - Scopes : Cocher `repo` (et tous les sous-éléments)
4. Cliquer sur "Generate token"
5. **COPIER le token** (il ne sera affiché qu'une fois ! Exemple : `ghp_xxxxxxxxxxxxx`)
6. Dans PowerShell, quand demandé :
   - Username : Votre nom d'utilisateur GitHub
   - Password : Coller le token (pas votre mot de passe GitHub)

### 9.3 Résultat du Push

**Résultat attendu :**
```
Enumerating objects: 150, done.
Counting objects: 100% (150/150), done.
Delta compression using up to 8 threads
Compressing objects: 100% (120/120), done.
Writing objects: 100% (150/150), 2.5 MiB | 1.2 MiB/s, done.
Total 150 (delta 30), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (30/30), done.
To https://github.com/VOTRE_USERNAME/kairos.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

✅ **Succès !**

---

## ✅ ÉTAPE 10 : Vérifier sur GitHub

### 10.1 Aller sur le Repository GitHub

1. Ouvrir votre navigateur
2. Aller sur : `https://github.com/VOTRE_USERNAME/kairos`
3. Vous devriez voir tous vos fichiers !

### 10.2 Checklist sur GitHub

Vérifier que :

- [ ] ✅ Tous les fichiers source sont présents
- [ ] ✅ `.render.yaml` est présent (cliquer pour voir)
- [ ] ✅ `env.example` est présent
- [ ] ✅ `README.md` est présent
- [ ] ✅ `backend/` dossier est présent
- [ ] ✅ `frontend/` dossier est présent
- [ ] ❌ `.env` n'est **PAS** dans le repository
- [ ] ❌ `venv/` n'est **PAS** dans le repository
- [ ] ❌ `node_modules/` n'est **PAS** dans le repository

### 10.3 Vérifier les Fichiers Importants

1. Cliquer sur `.render.yaml` → Doit afficher le contenu
2. Cliquer sur `env.example` → Doit afficher les variables d'environnement
3. Cliquer sur `backend/build.sh` → Doit afficher le script de build

---

## 🎉 Félicitations !

Votre code est maintenant sur GitHub !

**Prochaine étape** : Suivre le guide `DEPLOIEMENT_RENDER.md` pour déployer sur Render.

---

## 🐛 Problèmes Courants

### Erreur : "authentication failed"

**Solution :**
1. Utiliser un token personnel GitHub (voir ÉTAPE 9.2 - Option 2)
2. Vérifier que le token a les permissions `repo`

### Erreur : "remote origin already exists"

**Solution :**
```powershell
git remote remove origin
git remote add origin https://github.com/VOTRE_USERNAME/kairos.git
```

### Erreur : "refusing to merge unrelated histories"

**Solution :**
```powershell
git pull origin main --allow-unrelated-histories
# Résoudre les conflits si nécessaire
git add .
git commit -m "Merge with GitHub repository"
git push origin main
```

### Erreur : "filename too long"

**Solution :**
```powershell
git config --global core.longpaths true
git add .
git commit -m "Initial commit"
git push -u origin main
```

---

## 📚 Ressources

- Guide complet : `GUIDE_COMPLET_GITHUB.md`
- Commandes exactes : `COMMANDES_GITHUB.txt`
- Documentation GitHub : https://docs.github.com
- Documentation Git : https://git-scm.com/doc
