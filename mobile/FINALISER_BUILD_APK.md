# ✅ Finaliser et Builder l'APK - Projet Initialisé avec Succès !

## 🎉 État Actuel

✅ Projet React Native initialisé avec succès dans `KairosMobile/kairos/`
✅ Tous les dossiers natifs créés (`android/`, `ios/`)
✅ Dépendances installées

## 📋 Prochaines Étapes pour Builder l'APK

### Étape 1 : Aller dans le Dossier du Projet

```powershell
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\KairosMobile\kairos
```

### Étape 2 : Vérifier la Structure

```powershell
# Vérifier que android/ existe
dir android

# Vérifier que gradlew.bat existe
dir android\gradlew.bat
```

### Étape 3 : Vérifier que votre Code Source est Copié

```powershell
# Vérifier que src/ existe avec vos fichiers
dir src
dir src\screens
dir src\services
```

Si `src/` n'existe pas ou est vide, copier votre code :

```powershell
# Depuis kairos/
xcopy /E /I ..\src src
```

### Étape 4 : Configurer Android (Important)

#### 4.1 Vérifier `android/app/build.gradle`

Ouvrir `android/app/build.gradle` et vérifier :

```gradle
android {
    compileSdkVersion 34  // ou 33
    
    defaultConfig {
        applicationId "com.kairos"  // Vérifier que c'est correct
        minSdkVersion 21
        targetSdkVersion 34  // ou 33
        versionCode 1
        versionName "1.0.0"
    }
}
```

#### 4.2 Vérifier `android/app/src/main/AndroidManifest.xml`

S'assurer que les permissions réseau sont présentes :

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

#### 4.3 Créer `android/local.properties` (si nécessaire)

Si le build échoue avec "SDK location not found" :

```powershell
# Créer le fichier local.properties
echo sdk.dir=C\:\\Users\\KOURO\\AppData\\Local\\Android\\Sdk > android\local.properties
```

**Note :** Ajuster le chemin selon votre installation Android SDK.

### Étape 5 : Vérifier la Configuration de l'API

Vérifier que `src/services/api.ts` pointe vers le bon backend :

```typescript
const API_BASE_URL = __DEV__ 
  ? 'http://192.168.1.XXX:8000/api'  // IP locale pour dev
  : 'https://kairos-0aoy.onrender.com/api';  // Production
```

### Étape 6 : Builder l'APK Debug

```powershell
# Depuis kairos/
cd android
.\gradlew.bat assembleDebug
```

L'APK sera généré dans : `android/app/build/outputs/apk/debug/app-debug.apk`

### Étape 7 : Tester l'APK (Optionnel)

```powershell
# Installer sur un appareil/émulateur connecté
adb install android\app\build\outputs\apk\debug\app-debug.apk
```

## 🚀 Commandes Rapides (Tout-en-Un)

```powershell
# 1. Aller dans le projet
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\KairosMobile\kairos

# 2. Vérifier android/
dir android

# 3. Builder l'APK Debug
cd android
.\gradlew.bat assembleDebug

# 4. L'APK sera dans :
# android/app/build/outputs/apk/debug/app-debug.apk
```

## ⚠️ Dépannage Rapide

### Erreur : "SDK location not found"

**Solution :** Créer `android/local.properties` :
```powershell
echo sdk.dir=C\:\\Users\\KOURO\\AppData\\Local\\Android\\Sdk > android\local.properties
```

### Erreur : "Gradle build failed"

**Solution :**
```powershell
cd android
.\gradlew.bat clean
.\gradlew.bat assembleDebug
```

### Erreur : "Task :app:mergeDebugResources FAILED"

**Solution :** Vérifier que les ressources Android sont correctes :
```powershell
# Nettoyer et rebuilder
cd android
.\gradlew.bat clean
.\gradlew.bat assembleDebug --info
```

## 📦 Emplacement de l'APK Généré

Une fois le build réussi :

**APK Debug :**
```
KairosMobile\kairos\android\app\build\outputs\apk\debug\app-debug.apk
```

## ✅ Checklist Finale

- [ ] Dossier `android/` existe dans `kairos/`
- [ ] `android/gradlew.bat` existe
- [ ] `android/local.properties` créé (si nécessaire)
- [ ] `src/` contient votre code source
- [ ] `AndroidManifest.xml` a les permissions réseau
- [ ] Build APK réussi
- [ ] APK trouvé dans `android/app/build/outputs/apk/debug/`

---

**🎉 Vous êtes maintenant prêt à builder l'APK ! Suivez les étapes ci-dessus.**
