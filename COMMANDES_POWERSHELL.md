# 💻 Commandes PowerShell - Guide Rapide

## ⚠️ Important : Syntaxe PowerShell

Dans PowerShell, pour exécuter un script dans le répertoire actuel, vous devez utiliser `.\` avant le nom du fichier.

---

## 🚀 Démarrer les Services

### Backend

```powershell
.\demarrer-backend.bat
```

**OU manuellement** :
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python main.py
```

### Frontend

```powershell
cd frontend
npm run dev
```

**OU si npm n'est pas reconnu** :
```powershell
$env:PATH += ";C:\Program Files\nodejs"
cd frontend
npm run dev
```

### Tout en une fois

```powershell
.\demarrer-tout.bat
```

---

## 📝 Commandes Utiles

### Vérifier les fichiers disponibles

```powershell
Get-ChildItem *.bat
```

### Exécuter un script batch

```powershell
.\nom-du-script.bat
```

### Changer de répertoire

```powershell
cd "C:\Users\KOURO\OneDrive\Desktop\Kairós"
```

### Lister les fichiers

```powershell
ls
# OU
Get-ChildItem
```

---

## 🔧 Résolution de Problèmes

### "Le terme n'est pas reconnu"

**Solution** : Utilisez `.\` avant le nom du fichier
```powershell
# ❌ Incorrect
demarrer-backend.bat

# ✅ Correct
.\demarrer-backend.bat
```

### npm non reconnu

**Solution** : Ajoutez Node.js au PATH
```powershell
$env:PATH += ";C:\Program Files\nodejs"
npm --version
```

### Politique d'exécution

**Solution** : Autoriser l'exécution pour cette session
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

---

## 💡 Astuce

**Utilisez CMD au lieu de PowerShell** si vous préférez :
- Les scripts `.bat` fonctionnent directement
- Pas besoin de `.\`
- Node.js est déjà dans le PATH

---

**Bon développement ! 🚀**
