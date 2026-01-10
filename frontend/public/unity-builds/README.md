# Builds Unity WebGL pour Kaïros

## Structure des dossiers

Placez vos builds Unity dans la structure suivante :

```
public/
  unity-builds/
    {module_id}/
      Build/
        {module_id}.loader.js
        {module_id}.data
        {module_id}.framework.js
        {module_id}.wasm
      StreamingAssets/ (optionnel)
```

## Instructions pour exporter depuis Unity

### 1. Configuration Unity

1. Ouvrez votre projet Unity
2. Allez dans `File > Build Settings`
3. Sélectionnez `WebGL` comme plateforme
4. Cliquez sur `Switch Platform`

### 2. Paramètres Player

1. Cliquez sur `Player Settings`
2. Dans `Other Settings` :
   - **Compression Format** : `Disabled` (pour éviter les problèmes de compatibilité)
   - **Data Caching** : Activé (pour améliorer les performances)
   - **Name Files As Hashes** : Désactivé (pour garder les noms de fichiers prévisibles)

### 3. Export

1. Dans `Build Settings`, cliquez sur `Build`
2. Créez un dossier avec l'ID du module (ex: `67890abcdef1234567890123`)
3. Unity créera un dossier `Build` avec les fichiers nécessaires

### 4. Renommage des fichiers

Renommez les fichiers générés pour correspondre au format attendu :

- `Build.loader.js` → `{module_id}.loader.js`
- `Build.data` → `{module_id}.data`
- `Build.framework.js` → `{module_id}.framework.js`
- `Build.wasm` → `{module_id}.wasm`

### 5. Communication React ↔ Unity

#### Depuis React vers Unity

```typescript
import { sendMessageToUnity } from '../components/UnityWebGLViewer'

// Envoyer un message
sendMessageToUnity('GameManager', 'SetModuleId', moduleId)
sendMessageToUnity('GameManager', 'SetSceneType', 'mechanics')
```

#### Dans Unity (C#)

```csharp
using UnityEngine;

public class GameManager : MonoBehaviour
{
    private string currentModuleId;
    private string currentSceneType;
    
    // Méthode appelée depuis React
    public void SetModuleId(string moduleId)
    {
        currentModuleId = moduleId;
        Debug.Log($"Module ID reçu: {moduleId}");
        // Charger la scène appropriée
        LoadSceneForModule(moduleId);
    }
    
    // Méthode appelée depuis React
    public void SetSceneType(string sceneType)
    {
        currentSceneType = sceneType;
        Debug.Log($"Scene type reçu: {sceneType}");
        // Adapter la scène selon le type
        AdaptScene(sceneType);
    }
    
    private void LoadSceneForModule(string moduleId)
    {
        // Logique pour charger la scène appropriée
    }
    
    private void AdaptScene(string sceneType)
    {
        // Logique pour adapter la scène
    }
    
    // Méthode pour envoyer des données à React (via window.unityInstance)
    public void SendProgressToReact(float progress)
    {
        // Utiliser Application.ExternalCall si nécessaire
        Application.ExternalCall("onUnityProgress", progress);
    }
}
```

### 6. Optimisations recommandées

#### Réduire la taille du build

- Utilisez des textures compressées (DXT1, DXT5)
- Réduisez la qualité des modèles 3D
- Désactivez les fonctionnalités non utilisées
- Utilisez Asset Bundles pour les assets volumineux

#### Améliorer les performances

- Limitez le nombre de polygones (< 50k par objet)
- Utilisez LOD (Level of Detail)
- Optimisez les shaders
- Réduisez les effets visuels si nécessaire

#### Configuration recommandée

- **Target WebGL Version** : WebGL 2.0
- **Compression Format** : Disabled (pour compatibilité)
- **Exception Support** : None (pour meilleures performances)
- **Code Optimization** : Size

### 7. Tests

1. Testez le build localement avant de le déployer
2. Vérifiez la compatibilité avec différents navigateurs
3. Testez sur mobile pour vérifier les performances
4. Vérifiez que les communications React ↔ Unity fonctionnent

### 8. Exemple de structure complète

```
public/
  unity-builds/
    67890abcdef1234567890123/  (ID du module Mécanique Classique)
      Build/
        67890abcdef1234567890123.loader.js
        67890abcdef1234567890123.data
        67890abcdef1234567890123.framework.js
        67890abcdef1234567890123.wasm
      README.md (optionnel, documentation du build)
```

## Support

Pour toute question sur l'intégration Unity, consultez :
- [Documentation Unity WebGL](https://docs.unity3d.com/Manual/webgl.html)
- [Guide d'intégration React](IMMERSIVE_ARCHITECTURE.md)
















