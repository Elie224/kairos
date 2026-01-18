# 🔧 Résolution Problème PowerShell - Execution Policy

## ❌ Problème

Erreur rencontrée :
```
npm : Impossible de charger le fichier C:\Program Files\nodejs\npm.ps1, car 
l'exécution de scripts est désactivée sur ce système.
```

## ✅ Solution 1 : Modifier la Policy d'Exécution (Recommandé)

### Étape 1 : Ouvrir PowerShell en Administrateur

1. Rechercher "PowerShell" dans le menu Démarrer
2. **Clic droit** sur "Windows PowerShell"
3. Sélectionner **"Exécuter en tant qu'administrateur"**

### Étape 2 : Vérifier la Policy Actuelle

```powershell
Get-ExecutionPolicy
```

### Étape 3 : Changer la Policy (Choisir UNE option)

#### Option A : RemoteSigned (Recommandé pour la plupart des cas)

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Option B : Bypass (Pour cette session seulement)

```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

#### Option C : Unrestricted (Moins sécurisé, mais fonctionne)

```powershell
Set-ExecutionPolicy Unrestricted -Scope CurrentUser
```

### Étape 4 : Confirmer

Tapez `Y` et appuyez sur Entrée pour confirmer.

### Étape 5 : Vérifier

```powershell
Get-ExecutionPolicy
```

Vous devriez voir `RemoteSigned`, `Bypass`, ou `Unrestricted`.

## ✅ Solution 2 : Utiliser cmd.exe au lieu de PowerShell

Si vous préférez ne pas modifier la policy PowerShell :

### Ouvrir cmd.exe (Invite de commandes)

1. Appuyer sur `Windows + R`
2. Taper `cmd` et appuyer sur Entrée
3. Naviguer vers le projet :

```cmd
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\mobile
npm install
```

## ✅ Solution 3 : Utiliser npm.cmd explicitement

Dans PowerShell, utiliser `.cmd` à la fin :

```powershell
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\mobile
npm.cmd install
npm.cmd run build:android:debug
```

## 📋 Commandes Après Résolution

Une fois le problème résolu, vous pourrez exécuter :

```powershell
# Aller dans le dossier mobile
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\mobile

# Installer les dépendances
npm install

# Build APK Debug
npm run build:android:debug

# Build APK Release
npm run build:android:release

# Build AAB pour Google Play
npm run build:android:bundle
```

## 🔒 Explications des Policies

| Policy | Description | Sécurité |
|--------|-------------|----------|
| **Restricted** | Aucun script ne peut s'exécuter (défaut) | Très sécurisé mais bloque tout |
| **RemoteSigned** | Scripts locaux OK, scripts téléchargés doivent être signés | Bon équilibre |
| **AllSigned** | Tous les scripts doivent être signés | Très sécurisé |
| **Unrestricted** | Tous les scripts peuvent s'exécuter | Moins sécurisé |
| **Bypass** | Aucune restriction (session seulement) | Pour tests rapides |

## ⚠️ Important

- **RemoteSigned** est généralement la meilleure option pour le développement
- Cela permet l'exécution de scripts locaux (npm, npx, etc.)
- Les scripts téléchargés devront être signés (sécurité)

## 🚀 Vérification Rapide

Après avoir changé la policy, tester avec :

```powershell
npm --version
npx --version
```

Si ces commandes fonctionnent, le problème est résolu ! ✅

---

*Guide créé pour résoudre les problèmes d'exécution de scripts PowerShell dans le projet Kaïros Mobile*
