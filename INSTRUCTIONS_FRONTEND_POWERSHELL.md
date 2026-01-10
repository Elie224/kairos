# 🎨 Démarrer le Frontend dans PowerShell

## ⚠️ Problème

Vous êtes dans **PowerShell** et `npm` n'est pas reconnu car Node.js n'est pas dans le PATH de PowerShell.

---

## ✅ Solution 1 : Utiliser le Script PowerShell (Recommandé)

**Dans PowerShell**, exécutez :

```powershell
.\demarrer-frontend.ps1
```

**Si vous avez une erreur de politique d'exécution**, exécutez d'abord :

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\demarrer-frontend.ps1
```

---

## ✅ Solution 2 : Ajouter Node.js au PATH Manuellement

**Dans PowerShell**, exécutez ces commandes :

```powershell
# Ajouter Node.js au PATH pour cette session
$env:PATH += ";C:\Program Files\nodejs"

# Vérifier que ça fonctionne
npm --version

# Maintenant vous pouvez démarrer le frontend
cd frontend
npm install
npm run dev
```

---

## ✅ Solution 3 : Utiliser CMD (Le Plus Simple)

**Ouvrez un terminal CMD** (pas PowerShell) et exécutez :

```cmd
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
cd frontend
npm install
npm run dev
```

**OU utilisez le script batch** :
```cmd
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
demarrer-frontend-cmd.bat
```

---

## 🎯 Recommandation

**Utilisez CMD** pour le frontend, c'est plus simple et ça fonctionne directement ! 

Dans CMD, Node.js est déjà dans le PATH, donc `npm` fonctionne sans configuration supplémentaire.

---

## 📝 Note

Les fichiers `.bat` ne peuvent pas être exécutés directement dans PowerShell comme des commandes. Utilisez :
- `.\nom-du-fichier.bat` dans PowerShell
- OU ouvrez directement un terminal CMD

---

**Bon développement ! 🚀**


