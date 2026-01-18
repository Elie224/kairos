# ⚡ Commandes Rapides - Initialisation Projet React Native

## 🚀 Initialiser le Projet (Solution Rapide)

```powershell
# Aller dans le dossier parent
cd C:\Users\KOURO\OneDrive\Desktop\Kairós

# Initialiser SANS template (TypeScript est par défaut dans RN 0.71+)
npx @react-native-community/cli init KairosMobile

# ATTENDRE que l'initialisation se termine complètement (2-5 minutes)

# Ensuite, aller dans le projet
cd KairosMobile

# Installer les dépendances
npm install

# Copier votre code source
xcopy /E /I ..\mobile\src src
```

## 📋 Après Initialisation

```powershell
# Copier votre code source
xcopy /E /I mobile\src KairosMobile\src

# Aller dans le nouveau projet
cd KairosMobile

# Installer les dépendances
npm install

# Build APK Debug
npm run build:android:debug
```

## ⚠️ Note Importante

**La commande `react-native init` est dépréciée !**

Utilisez à la place :
```powershell
npx @react-native-community/cli init
```

---

*Commandes rapides pour initialiser le projet Kaïros Mobile*
