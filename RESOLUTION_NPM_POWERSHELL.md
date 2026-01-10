# 🔧 Résolution Problème npm dans PowerShell

## ❌ Erreur

```
npm : Impossible de charger le fichier C:\Program Files\nodejs\npm.ps1, 
car l'exécution de scripts est désactivée sur ce système.
```

## ✅ Solutions

### Solution 1 : Utiliser npm.cmd (Recommandé)

Au lieu de `npm`, utilisez `npm.cmd` :

```powershell
cd frontend
npm.cmd run dev
```

### Solution 2 : Utiliser le Script BAT

```cmd
cd frontend
..\demarrer-frontend.bat
```

### Solution 3 : Modifier la Politique d'Exécution PowerShell (Temporaire)

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
cd frontend
npm run dev
```

### Solution 4 : Utiliser le Script PowerShell Fourni

```powershell
cd frontend
.\demarrer-frontend-powershell.ps1
```

## 🚀 Démarrage Rapide

**Option la plus simple** :

```powershell
cd frontend
npm.cmd run dev
```

Ou utilisez le script BAT depuis la racine :

```cmd
.\demarrer-frontend.bat
```

## 📝 Note

Le script `demarrer-frontend-powershell.ps1` utilise automatiquement `npm.cmd` pour éviter les problèmes de politique d'exécution.
