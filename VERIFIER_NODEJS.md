# 🔍 Vérification de Node.js

## ❌ Problème Détecté

`npm` n'est pas reconnu, ce qui signifie que **Node.js n'est pas installé** ou **n'est pas dans le PATH**.

---

## ✅ Solution : Installer Node.js

### Étape 1 : Télécharger Node.js

1. Allez sur : **https://nodejs.org/**
2. Téléchargez la version **LTS** (Long Term Support)
3. Version minimale requise : **Node.js 18+**

### Étape 2 : Installer Node.js

1. Exécutez le fichier d'installation téléchargé
2. **IMPORTANT** : Cochez l'option **"Add to PATH"** pendant l'installation
3. Suivez les instructions de l'installateur
4. Redémarrez votre terminal après l'installation

### Étape 3 : Vérifier l'Installation

Ouvrez un **nouveau terminal** et exécutez :

```cmd
node --version
npm --version
```

Vous devriez voir les versions de Node.js et npm.

---

## 🚀 Après l'Installation

Une fois Node.js installé :

1. **Fermez tous les terminaux** ouverts
2. **Ouvrez un nouveau terminal**
3. Naviguez vers le dossier du projet :
   ```cmd
   cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
   ```
4. Démarrez le frontend :
   ```cmd
   cd frontend
   npm install
   npm run dev
   ```

**OU utilisez le script batch** :
```cmd
demarrer-frontend.bat
```

---

## 📝 Note Importante

- Le dossier `frontend` est au **même niveau** que `backend`, pas à l'intérieur
- Vous devez être dans le dossier racine du projet pour accéder à `frontend`
- Si vous êtes dans `backend`, faites `cd ..` pour revenir au dossier racine

---

## 🎯 Structure des Dossiers

```
Kairós/
├── backend/
│   ├── venv/
│   └── main.py
├── frontend/
│   ├── node_modules/  (sera créé après npm install)
│   └── package.json
└── demarrer-frontend.bat
```

---

**Après avoir installé Node.js, vous pourrez démarrer le frontend ! 🚀**


