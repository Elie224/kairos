# 🔄 Réorganiser la Structure du Projet React Native

## ⚠️ Problème Détecté

Le projet a été initialisé mais la structure est incorrecte :
- ❌ `android/` est dans `KairosMobile/kairos/android/`
- ✅ Il devrait être dans `KairosMobile/android/`

## ✅ Solution : Déplacer les Fichiers

### Option 1 : Déplacer Tout le Contenu de `kairos/` vers `KairosMobile/`

```powershell
# Aller dans KairosMobile
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\KairosMobile

# Déplacer le contenu de kairos/ vers la racine
move kairos\* .

# Supprimer le dossier kairos vide
rmdir kairos

# Vérifier que android/ est maintenant à la racine
dir android
```

### Option 2 : Déplacer Manuellement les Dossiers Android/iOS

Si Option 1 ne fonctionne pas :

```powershell
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\KairosMobile

# Déplacer android/
move kairos\android .

# Déplacer ios/
move kairos\ios .

# Copier les fichiers de configuration
copy kairos\package.json .
copy kairos\tsconfig.json .
copy kairos\babel.config.js .
copy kairos\metro.config.js .
copy kairos\app.json .
copy kairos\index.js .
copy kairos\App.tsx .
```

### Option 3 : Recommencer avec la Bonne Commande (Recommandé)

Si la réorganisation est complexe, il est plus simple de recommencer :

```powershell
cd C:\Users\KOURO\OneDrive\Desktop\Kairós

# Sauvegarder votre code source
xcopy /E /I KairosMobile\src src_backup

# Supprimer le dossier mal structuré
rmdir /S /Q KairosMobile

# Réinitialiser correctement
npx @react-native-community/cli init KairosMobile

# Attendre que l'initialisation se termine

# Aller dans le nouveau projet
cd KairosMobile

# Copier votre code source
xcopy /E /I ..\src_backup src

# Installer les dépendances
npm install
```

## 📋 Structure Correcte Attendue

Après réorganisation, la structure devrait être :

```
KairosMobile/
├── android/              ✅ À la racine
│   ├── app/
│   ├── gradle/
│   └── gradlew.bat
├── ios/                  ✅ À la racine
├── src/                  ✅ Votre code
│   ├── App.tsx
│   ├── components/
│   ├── screens/
│   └── ...
├── node_modules/
├── package.json
├── tsconfig.json
├── babel.config.js
├── metro.config.js
├── app.json
└── index.js
```

## ✅ Vérification

Après réorganisation, vérifier :

```powershell
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\KairosMobile

# Vérifier que android/ est à la racine
dir android

# Vérifier que gradlew.bat existe
dir android\gradlew.bat

# Si oui, tester le build
cd android
.\gradlew.bat assembleDebug
```

## 🚀 Si Tout est Correct

Une fois la structure corrigée :

```powershell
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\KairosMobile

# Installer les dépendances (si pas déjà fait)
npm install

# Build APK Debug
npm run build:android:debug

# Ou directement avec Gradle
cd android
.\gradlew.bat assembleDebug
```

---

*Une fois la structure réorganisée, l'APK pourra être généré !*
