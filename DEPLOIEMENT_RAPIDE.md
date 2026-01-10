# 🚀 Déploiement Rapide - Résumé Exécutif

Guide ultra-rapide en 10 étapes pour pousser sur GitHub et déployer sur Render.

## ⚡ Quick Start

### 1️⃣ Créer Repository GitHub (5 min)
1. Aller sur https://github.com
2. "+" > "New repository"
3. Nom : `kairos`
4. Visibilité : `Public` ou `Private`
5. **NE PAS** cocher les options (README, .gitignore)
6. Cliquer "Create repository"
7. **COPIER** l'URL : `https://github.com/VOTRE_USERNAME/kairos.git`

### 2️⃣ Configurer Git (1 min)
```powershell
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@example.com"
```

### 3️⃣ Initialiser Git (1 min)
```powershell
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
git init
```

### 4️⃣ Vérifier les Fichiers (2 min)
```powershell
git status
# Vérifier que .env, venv/, node_modules/ ne sont PAS listés
# Si .env est listé :
git rm --cached .env
echo ".env" >> .gitignore
```

### 5️⃣ Ajouter les Fichiers (1 min)
```powershell
git add .
git status
# Vérifier que .render.yaml, env.example sont listés
```

### 6️⃣ Créer le Commit (1 min)
```powershell
git commit -m "Initial commit - Préparation déploiement Render"
```

### 7️⃣ Connecter à GitHub (1 min)
```powershell
# Remplacer VOTRE_USERNAME et kairos
git remote add origin https://github.com/VOTRE_USERNAME/kairos.git
git branch -M main
```

### 8️⃣ Pousser sur GitHub (3 min)
```powershell
git push -u origin main
# GitHub demandera authentification → Suivre les instructions
```

### 9️⃣ Vérifier sur GitHub (2 min)
1. Aller sur https://github.com/VOTRE_USERNAME/kairos
2. Vérifier que tous les fichiers sont présents
3. Vérifier que .env n'est PAS dans le repo

### 🔟 Déployer sur Render (15 min)
1. Aller sur https://dashboard.render.com
2. Se connecter avec GitHub
3. "New +" > "Blueprint"
4. Connecter votre repository GitHub
5. Render détectera `.render.yaml` automatiquement
6. Cliquer "Apply"
7. Configurer les variables d'environnement (voir `DEPLOIEMENT_RENDER.md`)
8. Déployer !

---

## 📋 Checklist Rapide

- [ ] Repository GitHub créé
- [ ] Git configuré (nom + email)
- [ ] Git initialisé dans le projet
- [ ] `.gitignore` vérifié
- [ ] `.env` exclu du repo
- [ ] Tous les fichiers ajoutés (`git add .`)
- [ ] Premier commit créé
- [ ] Remote GitHub ajouté
- [ ] Code poussé sur GitHub
- [ ] Repository vérifié sur GitHub

---

## 🔑 Variables Clés à Configurer sur Render

### Backend
```
ENVIRONMENT=production
MONGODB_URL=mongodb+srv://...
SECRET_KEY=<générer-avec-secrets.token_urlsafe(32)>
OPENAI_API_KEY=sk-...
FRONTEND_URL=https://kairos-frontend.onrender.com
```

### Frontend
```
VITE_API_URL=https://kairos-backend.onrender.com
```

---

## 📚 Guides Détaillés

- **Guide complet GitHub** : `GUIDE_COMPLET_GITHUB.md`
- **Étapes visuelles** : `ETAPES_VISUELLES_GITHUB.md`
- **Commandes exactes** : `COMMANDES_GITHUB.txt`
- **Déploiement Render** : `DEPLOIEMENT_RENDER.md`
- **Checklist complète** : `DEPLOIEMENT_CHECKLIST.md`

---

## ⏱️ Temps Total

- GitHub : ~17 minutes
- Render : ~20 minutes
- **TOTAL : ~37 minutes**

---

## 🆘 Besoin d'Aide ?

Consultez les guides détaillés ou les fichiers de résolution de problèmes.
