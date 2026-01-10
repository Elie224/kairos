# Kaïros Mobile - Application React Native

Application mobile React Native pour la plateforme d'apprentissage Kaïros avec toutes les fonctionnalités de l'application web.

## 🚀 Fonctionnalités

- ✅ Authentification complète (Login, Register, OAuth Google)
- ✅ Modules d'apprentissage (Mathématiques et Informatique)
- ✅ Chat IA avec streaming (GPT-5-mini, GPT-5.2, GPT-5.2-pro)
- ✅ Quiz interactifs
- ✅ Examens chronométrés
- ✅ Tableau de bord avec statistiques
- ✅ Gamification (badges, progression)
- ✅ Profil utilisateur
- ✅ Paramètres

## 📋 Prérequis

- Node.js >= 18
- React Native CLI
- Android Studio (pour Android)
- Xcode (pour iOS - macOS uniquement)
- Backend Kaïros démarré sur `http://localhost:8000`

## 🛠️ Installation

1. Installer les dépendances :
```bash
cd mobile
npm install
```

2. Installer les pods iOS (macOS uniquement) :
```bash
cd ios
pod install
cd ..
```

3. Configurer l'URL de l'API dans `src/services/api.ts` :
```typescript
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api'  // Android: utiliser l'IP de votre machine
  : 'https://votre-domaine.com/api';
```

**Note pour Android** : Utiliser l'IP de votre machine au lieu de `localhost` :
```typescript
const API_BASE_URL = __DEV__ 
  ? 'http://192.168.1.XXX:8000/api'  // Remplacer XXX par votre IP
  : 'https://votre-domaine.com/api';
```

## 🏃 Démarrage

### Android
```bash
npm run android
```

### iOS (macOS uniquement)
```bash
npm run ios
```

## 📱 Structure du Projet

```
mobile/
├── src/
│   ├── App.tsx                 # Point d'entrée
│   ├── navigation/             # Navigation React Navigation
│   │   ├── AuthNavigator.tsx
│   │   └── MainNavigator.tsx
│   ├── screens/                 # Écrans de l'application
│   │   ├── auth/
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── RegisterScreen.tsx
│   │   │   └── ForgotPasswordScreen.tsx
│   │   ├── HomeScreen.tsx
│   │   ├── ModulesScreen.tsx
│   │   ├── ModuleDetailScreen.tsx
│   │   ├── DashboardScreen.tsx
│   │   ├── ProfileScreen.tsx
│   │   ├── ExamsScreen.tsx
│   │   ├── ExamDetailScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── components/              # Composants réutilisables
│   │   └── AITutorComponent.tsx
│   ├── services/                # Services API
│   │   ├── api.ts
│   │   ├── moduleService.ts
│   │   ├── chatService.ts
│   │   ├── quizService.ts
│   │   ├── examService.ts
│   │   └── badgeService.ts
│   ├── store/                   # État global (Zustand)
│   │   └── authStore.ts
│   └── types/                    # Types TypeScript
│       └── index.ts
├── package.json
├── tsconfig.json
└── README.md
```

## 🔧 Configuration

### Variables d'environnement

Créer un fichier `.env` à la racine du projet mobile :

```env
API_BASE_URL=http://localhost:8000/api
```

### Google Sign-In (Optionnel)

Pour activer la connexion Google, configurer dans `android/app/build.gradle` et `ios/` selon la documentation de `@react-native-google-signin/google-signin`.

## 📚 Services Disponibles

- **api.ts** : Client API Axios avec intercepteurs
- **moduleService.ts** : Gestion des modules
- **chatService.ts** : Chat IA avec streaming SSE
- **quizService.ts** : Quiz interactifs
- **examService.ts** : Examens chronométrés
- **badgeService.ts** : Badges et gamification

## 🎨 Navigation

L'application utilise React Navigation avec :
- **AuthNavigator** : Navigation pour les écrans d'authentification
- **MainNavigator** : Navigation principale avec tabs et stack

## 🔐 Authentification

L'authentification utilise Zustand avec persistance AsyncStorage :
- Login/Register
- Token JWT stocké de manière sécurisée
- Déconnexion automatique en cas d'erreur 401

## 📱 Écrans Principaux

1. **HomeScreen** : Page d'accueil avec accès rapide
2. **ModulesScreen** : Liste des modules avec filtres
3. **ModuleDetailScreen** : Détails d'un module avec chat IA
4. **DashboardScreen** : Statistiques et progression
5. **ProfileScreen** : Profil utilisateur
6. **ExamsScreen** : Liste des examens
7. **ExamDetailScreen** : Passer un examen chronométré

## 🐛 Dépannage

### Erreur de connexion API
- Vérifier que le backend est démarré
- Pour Android, utiliser l'IP de votre machine au lieu de `localhost`
- Vérifier les permissions réseau dans `AndroidManifest.xml`

### Erreur de build
- Nettoyer le cache : `npm start -- --reset-cache`
- Réinstaller les dépendances : `rm -rf node_modules && npm install`
- Pour iOS : `cd ios && pod install && cd ..`

## 📝 Notes

- L'application est optimisée pour React Native 0.73+
- Utilise TypeScript pour la sécurité des types
- Compatible Android et iOS
- Support du mode hors ligne (à implémenter)

## 🔄 Prochaines Étapes

- [ ] Mode hors ligne avec synchronisation
- [ ] Notifications push
- [ ] Mode sombre
- [ ] Support AR/VR pour visualisations 3D
- [ ] Téléchargement de ressources hors ligne
- [ ] Amélioration des performances

---

*Application mobile Kaïros - Toutes les fonctionnalités de la plateforme web disponibles sur mobile !*



