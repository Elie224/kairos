# 🚀 Démarrer le Backend dans PowerShell

## ⚠️ Important : Syntaxe PowerShell

Dans PowerShell, vous devez utiliser `.\` avant le nom du script pour l'exécuter depuis le répertoire actuel.

## ✅ Commande correcte

```powershell
.\demarrer-backend.bat
```

**Pas** :
```powershell
demarrer-backend.bat  # ❌ Ne fonctionne pas dans PowerShell
```

## 📋 Autres méthodes de démarrage

### Méthode 1 : Script Batch (Recommandé)

```powershell
.\demarrer-backend.bat
```

### Méthode 2 : Commande PowerShell directe

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Note** : Si vous obtenez une erreur d'exécution de script PowerShell, exécutez d'abord :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Méthode 3 : Invite de commandes (CMD)

Si vous préférez utiliser CMD au lieu de PowerShell :

```cmd
demarrer-backend.bat
```

Ou ouvrir directement CMD et taper :
```cmd
cd C:\Users\PC\OneDrive\Bureau\Kairós
demarrer-backend.bat
```

## 🔍 Vérification

Une fois le backend démarré, vous devriez voir :
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## 📝 Règles PowerShell

- `.\script.bat` → Exécute le script dans le répertoire actuel
- `script.bat` → PowerShell cherche dans le PATH (ne trouve pas le script local)
- `& ".\script.bat"` → Alternative avec l'opérateur d'appel

---

*Utilisez toujours `.\` devant les scripts dans PowerShell !*



