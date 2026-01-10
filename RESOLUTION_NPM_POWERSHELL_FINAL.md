# 🔧 Résolution : npm bloqué par la politique PowerShell

## ❌ Problème

PowerShell bloque l'exécution de `npm` à cause de la politique d'exécution.

---

## ✅ Solution 1 : Utiliser npm.cmd (Recommandé)

**Dans PowerShell**, utilisez `npm.cmd` au lieu de `npm` :

```powershell
cd frontend
& "C:\Program Files\nodejs\npm.cmd" run dev
```

**OU avec le chemin complet** :
```powershell
cd frontend
C:\Program Files\nodejs\npm.cmd install
C:\Program Files\nodejs\npm.cmd run dev
```

---

## ✅ Solution 2 : Modifier la politique d'exécution (Temporaire)

**Pour cette session uniquement** :

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
cd frontend
npm run dev
```

**Pour l'utilisateur actuel** (persistant) :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
cd frontend
npm run dev
```

---

## ✅ Solution 3 : Utiliser le script PowerShell

J'ai créé un script qui contourne automatiquement le problème :

```powershell
.\demarrer-frontend-powershell.ps1
```

**Si vous avez une erreur**, exécutez d'abord :

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\demarrer-frontend-powershell.ps1
```

---

## ✅ Solution 4 : Utiliser CMD (Le Plus Simple)

**Ouvrez un terminal CMD** (pas PowerShell) :

```cmd
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
cd frontend
npm install
npm run dev
```

Dans CMD, npm fonctionne directement sans problème de politique.

---

## 🎯 Recommandation

**Utilisez CMD** pour le frontend, c'est le plus simple et le plus fiable !

1. Appuyez sur `Win + R`
2. Tapez `cmd` et appuyez sur Entrée
3. Exécutez :
   ```cmd
   cd "C:\Users\KOURO\OneDrive\Desktop\Kairós\frontend"
   npm run dev
   ```

---

## 📝 Note

Le problème vient de la politique d'exécution PowerShell qui bloque les scripts `.ps1`. Les fichiers `.cmd` et `.bat` ne sont pas affectés, c'est pourquoi CMD fonctionne mieux.

---

**Bon développement ! 🚀**
