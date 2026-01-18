# 🔧 Résolution Erreur Gradle - JvmVendorSpec IBM_SEMERU

## ⚠️ Problème

```
FAILURE: Build failed with an exception.
* What went wrong:
Class org.gradle.jvm.toolchain.JvmVendorSpec does not have member field 
'org.gradle.jvm.toolchain.JvmVendorSpec IBM_SEMERU'
```

## 🔍 Cause

Gradle 9.0.0 est trop récent et incompatible avec React Native 0.83.1. Cette version de Gradle a changé l'API JVM toolchain.

## ✅ Solution : Downgrader Gradle vers 8.7

### Étape 1 : Modifier `gradle-wrapper.properties`

Le fichier a été corrigé pour utiliser Gradle 8.7 au lieu de 9.0.0.

Vérifier que `KairosMobile/kairos/android/gradle/wrapper/gradle-wrapper.properties` contient :

```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.7-all.zip
```

### Étape 2 : Nettoyer et Réessayer

```powershell
# Aller dans le dossier android
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\KairosMobile\kairos\android

# Nettoyer le build précédent
.\gradlew.bat clean

# Réessayer le build
.\gradlew.bat assembleDebug
```

## 📋 Fichiers Modifiés

1. ✅ `android/gradle/wrapper/gradle-wrapper.properties` - Gradle 8.7 au lieu de 9.0.0
2. ✅ `android/app/build.gradle` - Ajout compileOptions Java 11
3. ✅ `android/app/src/main/AndroidManifest.xml` - Ajout permission ACCESS_NETWORK_STATE

## ⚠️ Notes

- **Gradle 8.7** est compatible avec React Native 0.83.1
- Gradle 9.0.0 nécessite React Native plus récent
- La première fois, Gradle 8.7 sera téléchargé (environ 150MB)

## 🔄 Si le Problème Persiste

### Vérifier la Version Java

Gradle 8.7 nécessite Java 11 ou supérieur :

```powershell
java -version
```

Devrait afficher `java version "11.x.x"` ou supérieur.

### Vérifier JAVA_HOME

```powershell
echo $env:JAVA_HOME
```

Si vide, configurer JAVA_HOME (voir `CONFIGURER_JAVA.md`).

---

*Après cette correction, le build devrait fonctionner !*
