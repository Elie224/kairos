# ✅ Checklist de Vérification - Application Mobile Kaïros

## 📋 Vérifications Avant Build APK

### Configuration Générale

- [ ] **Dépendances installées**
  ```bash
  cd mobile
  npm install
  ```

- [ ] **Configuration API correcte**
  - [ ] `src/services/api.ts` pointe vers `https://kairos-0aoy.onrender.com/api` en production
  - [ ] Mode `__DEV__` détecte correctement l'environnement

- [ ] **TypeScript sans erreurs**
  ```bash
  npx tsc --noEmit
  ```

- [ ] **Linter sans erreurs critiques**
  ```bash
  npm run lint
  ```

### Configuration Android

- [ ] **Dossier `android/` existe**
  - Si absent, initialiser avec `npx react-native init` ou React Native CLI

- [ ] **`android/app/build.gradle` configuré**
  - [ ] `applicationId` défini : `com.kairosmobile`
  - [ ] `versionCode` et `versionName` définis
  - [ ] `minSdkVersion >= 21`
  - [ ] `targetSdkVersion = 33`

- [ ] **`android/app/src/main/AndroidManifest.xml` configuré**
  - [ ] Permission `<uses-permission android:name="android.permission.INTERNET" />`
  - [ ] Permission `<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />`
  - [ ] `android:usesCleartextTraffic="true"` pour HTTP (dev)

- [ ] **Variables d'environnement Android**
  - [ ] `ANDROID_HOME` ou `ANDROID_SDK_ROOT` définie
  - [ ] `JAVA_HOME` défini (JDK 11+)

- [ ] **`android/local.properties` existe**
  ```properties
  sdk.dir=/path/to/android/sdk
  ```

### Build et Test

- [ ] **Application testée en mode debug**
  ```bash
  npm run android
  ```

- [ ] **Fonctionnalités testées :**
  - [ ] Authentification (Login/Register)
  - [ ] Navigation entre écrans
  - [ ] Chargement des modules
  - [ ] Chat IA fonctionnel
  - [ ] Dashboard avec statistiques
  - [ ] Connexion API fonctionnelle

- [ ] **Pas d'erreurs console critiques**

### Build Release (Pour APK Production)

- [ ] **Keystore créé** (si première release)
  ```bash
  keytool -genkeypair -v -storetype PKCS12 \
    -keystore kairos-release-key.keystore \
    -alias kairos-key-alias \
    -keyalg RSA -keysize 2048 -validity 10000
  ```

- [ ] **`android/gradle.properties` configuré**
  - [ ] `KAIROS_RELEASE_STORE_FILE`
  - [ ] `KAIROS_RELEASE_KEY_ALIAS`
  - [ ] `KAIROS_RELEASE_STORE_PASSWORD`
  - [ ] `KAIROS_RELEASE_KEY_PASSWORD`

- [ ] **`android/app/build.gradle` avec signingConfig**
  - [ ] `signingConfigs.release` configuré
  - [ ] `buildTypes.release.signingConfig` défini

### Vérifications Post-Build

- [ ] **APK généré avec succès**
  - Debug : `android/app/build/outputs/apk/debug/app-debug.apk`
  - Release : `android/app/build/outputs/apk/release/app-release.apk`

- [ ] **Taille de l'APK acceptable** (< 50MB recommandé)

- [ ] **APK testé sur appareil réel**
  ```bash
  adb install android/app/build/outputs/apk/release/app-release.apk
  ```

- [ ] **Fonctionnalités validées sur APK release :**
  - [ ] L'application démarre correctement
  - [ ] Connexion API fonctionne
  - [ ] Toutes les fonctionnalités principales testées

### Documentation

- [ ] **README.md à jour**
- [ ] **BUILD_APK.md à jour**
- [ ] **Version et changelog documentés**

## 🐛 Problèmes Courants et Solutions

### Erreur : "SDK location not found"
**Solution** : Créer `android/local.properties` avec `sdk.dir=/path/to/sdk`

### Erreur : "Gradle build failed"
**Solution** : 
```bash
cd android
./gradlew clean
./gradlew assembleDebug
```

### Erreur : "Metro bundler not running"
**Solution** : Lancer `npm start` dans un terminal séparé

### Erreur : "Network request failed"
**Solution** : Vérifier `AndroidManifest.xml` et permissions réseau

### APK trop volumineux
**Solution** : Activer ProGuard et `shrinkResources` dans `build.gradle`

---

**Une fois tous les items cochés, l'APK est prêt pour distribution ! 🚀**
