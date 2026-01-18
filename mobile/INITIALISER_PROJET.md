# 🚀 Initialisation du Projet React Native - Kaïros Mobile

## ⚠️ Problème Détecté

Le dossier `android/` n'existe pas dans votre projet. Il faut initialiser le projet React Native pour créer les dossiers natifs `android/` et `ios/`.

## ✅ Solution : Initialiser le Projet React Native

### Option 1 : Initialiser dans un Nouveau Dossier (Recommandé)

Si vous voulez garder votre code source actuel intact :

```powershell
# Aller dans le dossier parent
cd C:\Users\KOURO\OneDrive\Desktop\Kairós

# Créer un nouveau projet React Native avec TypeScript (Nouvelle commande)
npx @react-native-community/cli init KairosMobile --template react-native-template-typescript

# Copier votre code source vers le nouveau projet
xcopy /E /I mobile\src KairosMobile\src
xcopy /E /I mobile\node_modules KairosMobile\node_modules
copy mobile\package.json KairosMobile\package.json
copy mobile\tsconfig.json KairosMobile\tsconfig.json
copy mobile\babel.config.js KairosMobile\babel.config.js
copy mobile\metro.config.js KairosMobile\metro.config.js

# Aller dans le nouveau projet
cd KairosMobile

# Réinstaller les dépendances (si nécessaire)
npm install
```

### Option 2 : Initialiser dans le Dossier Actuel (Plus Simple)

```powershell
# Aller dans le dossier mobile
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\mobile

# Sauvegarder temporairement votre code source
move src src_backup
move package.json package.json.backup
move tsconfig.json tsconfig.json.backup

# Initialiser React Native (cela va créer android/ et ios/)
npx @react-native-community/cli init KairosMobile --template react-native-template-typescript --skip-install

# Déplacer le contenu du nouveau projet ici
move KairosMobile\* .
rmdir KairosMobile

# Restaurer votre code source
rmdir /S /Q src
move src_backup src

# Restaurer vos fichiers de configuration
del package.json
move package.json.backup package.json
del tsconfig.json
move tsconfig.json.backup tsconfig.json

# Installer les dépendances
npm install
```

### Option 3 : Utiliser React Native CLI (Alternative)

```powershell
# Installer React Native CLI globalement (si pas déjà fait)
npm install -g react-native-cli

# Initialiser le projet
cd C:\Users\KOURO\OneDrive\Desktop\Kairós
npx @react-native-community/cli init KairosMobile --template react-native-template-typescript

# Puis copier votre code src/ vers le nouveau projet
```

## 📋 Vérifications Après Initialisation

Après avoir initialisé le projet, vérifiez que ces dossiers/fichiers existent :

- [ ] `android/` (dossier complet avec build.gradle, etc.)
- [ ] `ios/` (dossier complet si vous êtes sur macOS)
- [ ] `android/gradlew.bat` (Windows) ou `android/gradlew` (macOS/Linux)
- [ ] `android/app/build.gradle`
- [ ] `android/app/src/main/AndroidManifest.xml`

## 🔧 Après Initialisation : Configurer Android

### 1. Vérifier `android/app/build.gradle`

Ouvrir `android/app/build.gradle` et vérifier :

```gradle
android {
    compileSdkVersion 33
    
    defaultConfig {
        applicationId "com.kairosmobile"  // Modifier si nécessaire
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "1.0.0"
    }
}
```

### 2. Vérifier `android/app/src/main/AndroidManifest.xml`

Assurez-vous que les permissions réseau sont présentes :

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <application
        android:usesCleartextTraffic="true"
        ...>
    </application>
</manifest>
```

### 3. Créer `android/local.properties`

Créer le fichier `android/local.properties` avec le chemin du SDK Android :

**Windows :**
```properties
sdk.dir=C\:\\Users\\KOURO\\AppData\\Local\\Android\\Sdk
```

**macOS/Linux :**
```properties
sdk.dir=/Users/USERNAME/Library/Android/sdk
```

## 🏃 Test du Build

Après avoir initialisé et configuré, tester :

```powershell
# Build APK Debug
npm run build:android:debug

# Ou directement avec Gradle
cd android
.\gradlew.bat assembleDebug  # Windows
# ou
./gradlew assembleDebug      # macOS/Linux
```

L'APK sera généré dans : `android/app/build/outputs/apk/debug/app-debug.apk`

## ⚠️ Notes Importantes

1. **Sauvegardez votre code** avant d'initialiser le projet
2. Les dossiers `android/` et `ios/` sont volumineux, ne les copiez pas manuellement
3. Si vous avez des modifications dans `android/` ou `ios/`, notez-les avant de réinitialiser
4. Le processus d'initialisation peut prendre plusieurs minutes

## 🐛 Dépannage

### Erreur : "Command failed: react-native init" ou "The init command is deprecated"

**Solution :** Utiliser la nouvelle commande CLI :
```powershell
# La nouvelle commande recommandée
npx @react-native-community/cli init KairosMobile --template react-native-template-typescript
```

### Erreur : "SDK location not found"

**Solution :** Créer `android/local.properties` avec le chemin du SDK (voir étape 3 ci-dessus)

### Erreur : "Gradle build failed"

**Solution :**
```powershell
cd android
.\gradlew.bat clean
.\gradlew.bat assembleDebug
```

---

*Une fois le projet initialisé, suivez le guide `BUILD_APK.md` pour générer l'APK.*
