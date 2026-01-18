# ☕ Configuration Java JDK pour Build Android

## ⚠️ Problème

```
ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
```

Gradle a besoin de Java JDK pour builder l'APK Android.

## ✅ Solution : Configurer Java JDK

### Étape 1 : Vérifier si Java est Installé

```powershell
java -version
```

Si cela affiche une version (ex: `java version "11.0.x"`), Java est installé, mais JAVA_HOME n'est pas configuré.

Si cela affiche une erreur, Java n'est pas installé → Voir **Installation Java** ci-dessous.

### Étape 2 : Trouver le Chemin d'Installation de Java

#### Si Java est Installé via Android Studio

Java est généralement inclus avec Android Studio dans :
```
C:\Program Files\Android\Android Studio\jbr
```

#### Si Java est Installé Séparément

Chercher dans :
```
C:\Program Files\Java\jdk-11
C:\Program Files\Java\jdk-17
C:\Program Files (x86)\Java\jdk-11
```

#### Méthode Automatique pour Trouver Java

```powershell
# Chercher java.exe sur le système
where.exe java
```

Cela donnera le chemin, par exemple : `C:\Program Files\Java\jdk-11\bin\java.exe`

Le JAVA_HOME sera alors : `C:\Program Files\Java\jdk-11` (sans `\bin`)

### Étape 3 : Configurer JAVA_HOME (Session Actuelle)

Pour la session PowerShell actuelle :

```powershell
# Remplacer le chemin par votre chemin réel
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
# ou
$env:JAVA_HOME = "C:\Program Files\Java\jdk-11"

# Vérifier
$env:JAVA_HOME
echo $env:JAVA_HOME
```

### Étape 4 : Configurer JAVA_HOME (Permanent)

#### Option A : Via l'Interface Windows (Recommandé)

1. Rechercher "Variables d'environnement" dans le menu Démarrer
2. Cliquer sur "Modifier les variables d'environnement système"
3. Cliquer sur "Variables d'environnement"
4. Sous "Variables système", cliquer sur "Nouveau"
5. Nom de la variable : `JAVA_HOME`
6. Valeur de la variable : `C:\Program Files\Android\Android Studio\jbr` (ou votre chemin Java)
7. Cliquer sur "OK"
8. Dans "Variables système", trouver `Path` et cliquer sur "Modifier"
9. Cliquer sur "Nouveau" et ajouter : `%JAVA_HOME%\bin`
10. Cliquer sur "OK" partout
11. **Redémarrer PowerShell** pour que les changements prennent effet

#### Option B : Via PowerShell (Permanent pour l'Utilisateur)

```powershell
# Remplacer le chemin par votre chemin réel
[System.Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Android\Android Studio\jbr', 'User')

# Ajouter au PATH
$currentPath = [System.Environment]::GetEnvironmentVariable('Path', 'User')
$newPath = "$currentPath;%JAVA_HOME%\bin"
[System.Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
```

**Important :** Fermer et rouvrir PowerShell après cette commande.

### Étape 5 : Vérifier la Configuration

Dans une **nouvelle session PowerShell** :

```powershell
# Vérifier JAVA_HOME
echo $env:JAVA_HOME

# Vérifier Java
java -version

# Vérifier javac (compilateur)
javac -version
```

Tous devraient fonctionner sans erreur.

### Étape 6 : Tester le Build Android

```powershell
# Aller dans le projet
cd C:\Users\KOURO\OneDrive\Desktop\Kairós\KairosMobile\kairos\android

# Tester Gradle
.\gradlew.bat --version

# Builder l'APK
.\gradlew.bat assembleDebug
```

## 📥 Installation Java (Si Non Installé)

### Option 1 : Utiliser Java d'Android Studio (Recommandé)

Si Android Studio est installé, Java est inclus :

1. Ouvrir Android Studio
2. Aller dans `File` → `Settings` → `Build, Execution, Deployment` → `Build Tools` → `Gradle`
3. Le chemin JDK devrait être affiché
4. Ou chercher dans : `C:\Program Files\Android\Android Studio\jbr`

### Option 2 : Télécharger Java JDK 11 ou 17

1. Aller sur : https://adoptium.net/ (OpenJDK)
2. Télécharger **JDK 11** ou **JDK 17** pour Windows x64
3. Installer (par défaut dans `C:\Program Files\Eclipse Adoptium\jdk-11.x.x-hotspot\`)
4. Configurer JAVA_HOME avec ce chemin (voir Étape 3 ou 4)

### Option 3 : Via Chocolatey (Si Installé)

```powershell
choco install openjdk11
```

## 🔍 Vérifications Utiles

### Trouver Tous les Java Installés

```powershell
# Chercher tous les java.exe
Get-ChildItem -Path "C:\Program Files" -Filter "java.exe" -Recurse -ErrorAction SilentlyContinue
Get-ChildItem -Path "C:\Program Files (x86)" -Filter "java.exe" -Recurse -ErrorAction SilentlyContinue
```

### Vérifier la Version Java

```powershell
java -version
```

React Native requiert généralement **JDK 11 ou supérieur**.

## ⚠️ Notes Importantes

- **JDK 11 ou 17** est recommandé pour React Native
- **Ne pas utiliser** JRE (Java Runtime Environment) - Gradle a besoin du **JDK** (Java Development Kit)
- Après avoir configuré JAVA_HOME, **redémarrer PowerShell** est essentiel
- Android Studio inclut généralement JDK 11, utilisez-le si disponible

## 🐛 Dépannage

### Erreur : "JAVA_HOME is set to an invalid directory"

**Solution :** Vérifier que le chemin est correct et ne contient pas d'espaces mal échappés.

### Erreur : "java command not found"

**Solution :** Ajouter `%JAVA_HOME%\bin` au PATH (voir Étape 4).

### Erreur : "Unsupported major.minor version"

**Solution :** Utiliser JDK 11 ou supérieur (pas JDK 8 ou inférieur).

---

*Une fois Java configuré, le build Android pourra être effectué !*
