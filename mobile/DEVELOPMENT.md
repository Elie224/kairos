# Guide de Développement - Application Mobile Kaïros

## 🚀 Démarrage Rapide

### Prérequis
- Node.js >= 18
- React Native CLI
- Android Studio (pour Android)
- Xcode (pour iOS - macOS uniquement)
- Backend Kaïros démarré

### Installation

1. Installer les dépendances :
```bash
cd mobile
npm install
```

2. Pour iOS (macOS uniquement) :
```bash
cd ios
pod install
cd ..
```

3. Configurer l'URL de l'API :
   - L'URL par défaut pointe vers `https://kairos-0aoy.onrender.com/api` en production
   - Pour le développement local, modifier `src/services/api.ts` :
   ```typescript
   const API_BASE_URL = __DEV__ 
     ? 'http://192.168.1.XXX:8000/api'  // Remplacer XXX par votre IP locale
     : 'https://kairos-0aoy.onrender.com/api';
   ```

### Démarrage

#### Android
```bash
npm run android
```

#### iOS (macOS uniquement)
```bash
npm run ios
```

## 📱 Structure de l'Application

```
mobile/
├── src/
│   ├── App.tsx                 # Point d'entrée principal
│   ├── navigation/             # Navigation React Navigation
│   │   ├── AuthNavigator.tsx   # Navigation authentification
│   │   └── MainNavigator.tsx    # Navigation principale (tabs + stack)
│   ├── screens/                # Écrans de l'application
│   │   ├── auth/               # Écrans d'authentification
│   │   ├── HomeScreen.tsx      # Page d'accueil
│   │   ├── ModulesScreen.tsx   # Liste des modules
│   │   ├── ModuleDetailScreen.tsx  # Détails d'un module
│   │   ├── DashboardScreen.tsx     # Tableau de bord
│   │   ├── ProfileScreen.tsx       # Profil utilisateur
│   │   ├── ExamsScreen.tsx         # Liste des examens
│   │   ├── ExamDetailScreen.tsx    # Passer un examen
│   │   └── SettingsScreen.tsx      # Paramètres
│   ├── components/             # Composants réutilisables
│   │   └── AITutorComponent.tsx    # Composant chat IA
│   ├── services/              # Services API
│   │   ├── api.ts             # Client API Axios
│   │   ├── moduleService.ts   # Gestion des modules
│   │   ├── chatService.ts     # Chat IA avec streaming
│   │   ├── quizService.ts     # Quiz interactifs
│   │   ├── examService.ts     # Examens chronométrés
│   │   └── badgeService.ts    # Badges et gamification
│   ├── store/                 # État global (Zustand)
│   │   └── authStore.ts       # Store d'authentification
│   └── types/                 # Types TypeScript
│       └── index.ts           # Types partagés
```

## 🔧 Configuration

### Variables d'environnement

Créer un fichier `.env` à la racine du projet mobile (optionnel) :
```env
API_BASE_URL=https://kairos-0aoy.onrender.com/api
```

### Google Sign-In (Optionnel)

Pour activer la connexion Google :
1. Configurer dans `android/app/build.gradle`
2. Configurer dans `ios/` selon la documentation de `@react-native-google-signin/google-signin`

## 📚 Services Disponibles

- **api.ts** : Client API Axios avec intercepteurs (gestion token, erreurs réseau, rate limiting)
- **moduleService.ts** : Gestion des modules (liste, détails, progression)
- **chatService.ts** : Chat IA avec streaming SSE
- **quizService.ts** : Quiz interactifs
- **examService.ts** : Examens chronométrés
- **badgeService.ts** : Badges et gamification

## 🎨 Navigation

L'application utilise React Navigation avec :
- **AuthNavigator** : Navigation pour les écrans d'authentification (Login, Register, ForgotPassword)
- **MainNavigator** : Navigation principale avec :
  - **Bottom Tabs** : Home, Modules, Dashboard, Profile
  - **Stack Navigator** : ModuleDetail, ExamDetail, Settings

## 🔐 Authentification

L'authentification utilise Zustand avec persistance AsyncStorage :
- Login/Register
- Token JWT stocké de manière sécurisée
- Déconnexion automatique en cas d'erreur 401
- Vérification de la connexion réseau avant les requêtes

## 📱 Écrans Principaux

1. **HomeScreen** : Page d'accueil avec accès rapide aux fonctionnalités
2. **ModulesScreen** : Liste des modules avec filtres par matière
3. **ModuleDetailScreen** : Détails d'un module avec chat IA et quiz
4. **DashboardScreen** : Statistiques et progression
5. **ProfileScreen** : Profil utilisateur
6. **ExamsScreen** : Liste des examens disponibles
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

### Erreur de navigation
- Vérifier que tous les écrans sont bien enregistrés dans les navigateurs
- Vérifier les types TypeScript dans `navigation/MainNavigator.tsx`

## 🔄 Prochaines Étapes de Développement

- [ ] Mode hors ligne avec synchronisation
- [ ] Notifications push
- [ ] Mode sombre
- [ ] Support AR/VR pour visualisations 3D
- [ ] Téléchargement de ressources hors ligne
- [ ] Amélioration des performances
- [ ] Tests unitaires et d'intégration
- [ ] CI/CD pour builds automatiques

## 📝 Notes

- L'application est optimisée pour React Native 0.73+
- Utilise TypeScript pour la sécurité des types
- Compatible Android et iOS
- Support du mode hors ligne (à implémenter)
- API backend : `https://kairos-0aoy.onrender.com/api`
