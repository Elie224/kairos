# Guide de Build APK - Application Mobile Kaïros

## 📱 Préparation de l'APK Android

### Étape 1 : Vérifier les Prérequis

Assurez-vous d'avoir installé :
- ✅ Node.js >= 18
- ✅ React Native CLI : `npm install -g react-native-cli`
- ✅ Android Studio (avec Android SDK)
- ✅ Java JDK 11 ou supérieur
- ✅ Variables d'environnement Android configurées

### Étape 2 : Initialiser le Projet React Native (si nécessaire)

Si les dossiers `android/` et `ios/` n'existent pas, initialiser le projet :

```bash
cd mobile

# Si android/ et ios/ n'existent pas, créer un nouveau projet React Native
# Note: Cette commande va créer un nouveau projet, vous devrez ensuite copier votre code src/
npx react-native init KairosMobile --template react-native-template-typescript

# Ou utiliser React Native CLI
react-native init KairosMobile --template react-native-template-typescript
```

**Important** : Si vous avez déjà le code source dans `mobile/src/`, copiez-le vers le nouveau projet après l'initialisation.

### Étape 3 : Installer les Dépendances

```bash
cd mobile
npm install
```

### Étape 4 : Configurer Android

#### 4.1 Configurer `android/app/build.gradle`

Ouvrir `android/app/build.gradle` et vérifier/modifier :

```gradle
android {
    compileSdkVersion 33
    
    defaultConfig {
        applicationId "com.kairosmobile"
        minSdkVersion 21
        targetSdkVersion 33
        versionCode 1
        versionName "1.0.0"
        // ... autres configurations
    }
    
    // ... reste de la configuration
}
```

#### 4.2 Configurer `android/app/src/main/AndroidManifest.xml`

Assurez-vous que les permissions réseau sont configurées :

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <application
        android:usesCleartextTraffic="true"
        ...>
        <!-- Configuration de l'application -->
    </application>
</manifest>
```

#### 4.3 Configurer `android/build.gradle`

Vérifier que les versions sont correctes :

```gradle
buildscript {
    ext {
        buildToolsVersion = "33.0.0"
        minSdkVersion = 21
        compileSdkVersion = 33
        targetSdkVersion = 33
        ndkVersion = "23.1.7779620"
    }
    // ... reste de la configuration
}
```

### Étape 5 : Vérifier la Configuration de l'API

Vérifier que `src/services/api.ts` pointe vers le bon backend :

```typescript
const API_BASE_URL = __DEV__ 
  ? 'http://192.168.1.XXX:8000/api'  // IP locale pour dev
  : 'https://kairos-0aoy.onrender.com/api';  // Production
```

### Étape 6 : Générer l'APK Debug (Test)

#### Option 1 : Via Gradle (Recommandé)

```bash
cd mobile/android
./gradlew assembleDebug
```

L'APK sera généré dans : `android/app/build/outputs/apk/debug/app-debug.apk`

#### Option 2 : Via React Native CLI

```bash
cd mobile
npx react-native build-android --mode=debug
```

#### Option 3 : Via Android Studio

1. Ouvrir Android Studio
2. File → Open → Sélectionner le dossier `mobile/android/`
3. Build → Build Bundle(s) / APK(s) → Build APK(s)
4. Attendre la génération
5. L'APK sera dans `app/build/outputs/apk/debug/`

### Étape 7 : Générer l'APK Release (Production)

#### 7.1 Créer un Keystore (Première fois seulement)

```bash
cd mobile/android/app
keytool -genkeypair -v -storetype PKCS12 -keystore kairos-release-key.keystore -alias kairos-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

**Important** : 
- Garder le mot de passe et l'alias en sécurité
- Ne pas commiter le fichier `.keystore` dans Git

#### 7.2 Configurer `android/gradle.properties`

Ajouter les informations du keystore :

```properties
KAIROS_RELEASE_STORE_FILE=kairos-release-key.keystore
KAIROS_RELEASE_KEY_ALIAS=kairos-key-alias
KAIROS_RELEASE_STORE_PASSWORD=votre_mot_de_passe
KAIROS_RELEASE_KEY_PASSWORD=votre_mot_de_passe
```

#### 7.3 Configurer `android/app/build.gradle`

Ajouter la configuration de signature :

```gradle
android {
    // ... configuration existante
    
    signingConfigs {
        debug {
            storeFile file('debug.keystore')
            storePassword 'android'
            keyAlias 'androiddebugkey'
            keyPassword 'android'
        }
        release {
            if (project.hasProperty('KAIROS_RELEASE_STORE_FILE')) {
                storeFile file(KAIROS_RELEASE_STORE_FILE)
                storePassword KAIROS_RELEASE_STORE_PASSWORD
                keyAlias KAIROS_RELEASE_KEY_ALIAS
                keyPassword KAIROS_RELEASE_KEY_PASSWORD
            }
        }
    }
    
    buildTypes {
        debug {
            signingConfig signingConfigs.debug
        }
        release {
            signingConfig signingConfigs.release
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

#### 7.4 Générer l'APK Release

```bash
cd mobile/android
./gradlew assembleRelease
```

L'APK sera généré dans : `android/app/build/outputs/apk/release/app-release.apk`

### Étape 8 : Vérifier l'APK

Avant de distribuer, vérifier l'APK :

```bash
# Vérifier la taille
ls -lh android/app/build/outputs/apk/release/app-release.apk

# Installer sur un appareil/émulateur pour tester
adb install android/app/build/outputs/apk/release/app-release.apk
```

### Étape 9 : Optimiser l'APK (Optionnel)

#### Créer un APK AAB (Android App Bundle) pour Google Play

```bash
cd mobile/android
./gradlew bundleRelease
```

Le fichier `.aab` sera dans : `android/app/build/outputs/bundle/release/app-release.aab`

#### Réduire la taille avec ProGuard (Production)

Activer ProGuard dans `android/app/build.gradle` :

```gradle
buildTypes {
    release {
        minifyEnabled true
        shrinkResources true
        proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
    }
}
```

### 🔍 Dépannage

#### Erreur : "SDK location not found"

```bash
# Créer local.properties dans android/
echo "sdk.dir=$HOME/Library/Android/sdk" > android/local.properties
# Ou pour Windows:
echo "sdk.dir=C\:\\Users\\USERNAME\\AppData\\Local\\Android\\Sdk" > android/local.properties
```

#### Erreur : "Gradle build failed"

```bash
cd mobile/android
./gradlew clean
./gradlew assembleDebug
```

#### Erreur : "Metro bundler not running"

```bash
# Terminal 1
cd mobile
npm start

# Terminal 2
cd mobile
npm run android
```

#### Erreur : "Network request failed"

- Vérifier que `AndroidManifest.xml` a `<uses-permission android:name="android.permission.INTERNET" />`
- Pour HTTP (non HTTPS) en dev, ajouter `android:usesCleartextTraffic="true"`

### 📝 Checklist Avant de Générer l'APK

- [ ] Toutes les dépendances installées (`npm install`)
- [ ] Configuration API correcte dans `src/services/api.ts`
- [ ] `AndroidManifest.xml` avec permissions réseau
- [ ] `build.gradle` configuré correctement
- [ ] Variables d'environnement Android configurées
- [ ] Test de l'application en mode debug
- [ ] Keystore créé pour la release (si nécessaire)
- [ ] `gradle.properties` configuré avec les infos du keystore

### 📦 Résumé des Commandes Rapides

```bash
# Installer les dépendances
cd mobile && npm install

# Nettoyer le build
cd android && ./gradlew clean

# Build APK Debug
cd android && ./gradlew assembleDebug

# Build APK Release
cd android && ./gradlew assembleRelease

# Build AAB (pour Google Play)
cd android && ./gradlew bundleRelease

# Installer l'APK sur un appareil
adb install android/app/build/outputs/apk/release/app-release.apk
```

### 🚀 Emplacement des APK Générés

- **Debug APK** : `mobile/android/app/build/outputs/apk/debug/app-debug.apk`
- **Release APK** : `mobile/android/app/build/outputs/apk/release/app-release.apk`
- **AAB** : `mobile/android/app/build/outputs/bundle/release/app-release.aab`

---

*Document créé pour faciliter la génération de l'APK Android de Kaïros Mobile*
