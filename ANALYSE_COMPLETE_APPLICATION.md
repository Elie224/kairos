# 📊 Analyse Complète de l'Application Kaïros

**Date d'analyse** : 2026-01-09  
**Version** : 1.0.0  
**Plateforme** : Apprentissage immersif avec IA

---

## 🎯 Vue d'Ensemble

**Kaïros** est une plateforme d'apprentissage immersif utilisant l'intelligence artificielle et les visualisations 3D interactives pour expliquer des concepts complexes (Mathématiques, Informatique) de manière visuelle et interactive.

---

## 🛠️ Technologies Utilisées

### Backend (Python/FastAPI)

#### Framework & Serveur
- **FastAPI** >= 0.109.0 - Framework web moderne et performant
- **Uvicorn** >= 0.27.0 - Serveur ASGI haute performance
- **Gunicorn** >= 21.2.0 - Serveur WSGI pour production

#### Bases de Données
- **MongoDB** (PyMongo 4.6.0, Motor 3.3.2) - Base de données principale (NoSQL)
- **PostgreSQL** (SQLAlchemy 2.0.0, psycopg2-binary, asyncpg) - Base relationnelle optionnelle
- **Redis** (redis[hiredis] >= 5.0.0) - Cache et rate limiting

#### Intelligence Artificielle
- **OpenAI** >= 1.54.0 - API OpenAI pour GPT-5-mini, GPT-5.2, GPT-5.2-pro
- **PyMuPDF** >= 1.23.0 - Conversion PDF en images pour analyse

#### Sécurité & Authentification
- **python-jose[cryptography]** 3.3.0 - JWT tokens
- **passlib[bcrypt]** 1.7.4 - Hachage de mots de passe
- **email-validator** >= 1.3.1 - Validation d'emails

#### Utilitaires
- **Pydantic** >= 2.9.0 - Validation de données
- **python-dotenv** 1.0.0 - Gestion des variables d'environnement
- **aiofiles** 23.2.1 - Accès asynchrone aux fichiers
- **httpx** 0.25.2 - Client HTTP asynchrone
- **requests** >= 2.32.4 - Client HTTP synchrone
- **reportlab** >= 4.0.0 - Génération de PDFs

#### Paiements
- **Stripe** >= 7.0.0 - Intégration paiements

#### Tests
- **pytest** 7.4.0 - Framework de tests
- **pytest-asyncio** 0.22.0 - Support async pour pytest
- **pytest-mock** 3.11.1 - Mocking pour tests

### Frontend (React/TypeScript)

#### Framework & Build
- **React** 18.2.0 - Bibliothèque UI
- **TypeScript** 5.2.2 - Typage statique
- **Vite** 5.0.8 - Build tool moderne et rapide

#### UI & Styling
- **Chakra UI** 2.8.2 - Composants UI modernes
- **Framer Motion** 10.16.16 - Animations fluides
- **Emotion** (react/styled) 11.11.x - CSS-in-JS

#### 3D & Immersif
- **Three.js** 0.158.0 - Bibliothèque 3D
- **React Three Fiber** 8.15.11 - React renderer pour Three.js
- **React Three Drei** 9.88.13 - Helpers pour Three.js
- **WebXR** - Support réalité augmentée/virtuelle

#### Routing & State
- **React Router DOM** 6.20.0 - Routing côté client
- **Zustand** 4.4.7 - Gestion d'état légère

#### Data Fetching
- **Axios** 1.6.2 - Client HTTP
- **React Query** 3.39.3 - Gestion de cache et requêtes

#### Internationalisation
- **i18next** 25.6.2 - Framework i18n
- **react-i18next** 16.3.1 - Intégration React

#### Authentification
- **@react-oauth/google** 0.12.2 - OAuth Google

#### Icons
- **react-icons** 4.10.1 - Bibliothèque d'icônes

---

## 🏗️ Architecture de l'Application

### Structure Backend

```
backend/
├── app/
│   ├── config.py                    # Configuration centralisée
│   ├── database.py                   # Connexion MongoDB
│   ├── database/
│   │   ├── postgres.py               # Connexion PostgreSQL
│   │   └── migrations.py            # Migrations SQLAlchemy
│   ├── models/                       # Modèles de données (6 fichiers)
│   │   ├── models.py                 # Modèles Pydantic principaux
│   │   ├── postgres_models.py       # Modèles SQLAlchemy
│   │   ├── user_history.py          # Historique utilisateur
│   │   ├── gamification.py          # Badges et progression
│   │   ├── adaptive_learning.py     # Apprentissage adaptatif
│   │   └── subscription.py          # Abonnements
│   ├── repositories/                 # Pattern Repository (18 repositories)
│   │   ├── user_repository.py
│   │   ├── module_repository.py
│   │   ├── progress_repository.py
│   │   ├── quiz_repository.py
│   │   ├── exam_repository.py
│   │   ├── td_repository.py
│   │   ├── tp_repository.py
│   │   ├── badge_repository.py
│   │   ├── resource_repository.py
│   │   └── ...
│   ├── services/                     # Logique métier (40 services)
│   │   ├── ai_service.py             # Service IA principal
│   │   ├── ai_routing_service.py     # Routing intelligent IA
│   │   ├── ai_cost_guard.py          # Contrôle des coûts IA
│   │   ├── semantic_cache.py        # Cache sémantique Redis
│   │   ├── prompt_router_service.py  # Classification requêtes IA
│   │   ├── ai_fallback.py            # Fallback gracieux IA
│   │   ├── pdf_generator_service.py  # Génération PDFs (TD, TP, Examens)
│   │   ├── quiz_service.py           # Génération quiz IA
│   │   ├── exam_service.py           # Génération examens IA
│   │   ├── module_service.py         # Gestion modules
│   │   ├── auth_service.py          # Authentification
│   │   ├── progress_service.py       # Suivi progression
│   │   ├── gamification_service.py   # Badges et points
│   │   ├── recommendation_service.py # Recommandations
│   │   ├── adaptive_learning_service.py # Apprentissage adaptatif
│   │   └── ...
│   ├── routers/                      # Endpoints API (29 routeurs)
│   │   ├── auth.py                   # Authentification
│   │   ├── ai_tutor.py               # Chat IA avec streaming
│   │   ├── modules.py                # Modules d'apprentissage
│   │   ├── quiz.py                   # Quiz interactifs
│   │   ├── exam.py                   # Examens chronométrés
│   │   ├── td.py                     # Travaux Dirigés
│   │   ├── tp.py                     # Travaux Pratiques
│   │   ├── progress.py               # Progression utilisateur
│   │   ├── badges.py                 # Gamification
│   │   ├── resources.py              # Gestion ressources (PDF, vidéos)
│   │   ├── subscriptions.py          # Abonnements Stripe
│   │   └── ...
│   ├── middleware/                   # Middlewares (7 middlewares)
│   │   ├── security.py               # Rate limiting, headers sécurité
│   │   ├── error_handler.py          # Gestion erreurs centralisée
│   │   ├── performance.py            # Monitoring performance
│   │   ├── request_size.py          # Limite taille requêtes
│   │   └── ...
│   └── utils/                        # Utilitaires
│       ├── security.py               # Hachage, validation
│       ├── cache.py                   # Cache Redis
│       ├── json_cleaner.py            # Nettoyage JSON IA
│       └── ...
└── main.py                            # Point d'entrée FastAPI
```

### Structure Frontend

```
frontend/
├── src/
│   ├── App.tsx                        # Routeur principal
│   ├── main.tsx                       # Point d'entrée React
│   ├── pages/                         # Pages (14 pages)
│   │   ├── Home.tsx                   # Page d'accueil
│   │   ├── Login.tsx                  # Connexion
│   │   ├── Register.tsx               # Inscription
│   │   ├── Dashboard.tsx              # Tableau de bord
│   │   ├── Modules.tsx                # Liste modules
│   │   ├── ModuleDetail.tsx           # Détails module + IA Tutor
│   │   ├── Exams.tsx                  # Liste examens
│   │   ├── ExamDetail.tsx             # Passer un examen
│   │   ├── Profile.tsx                # Profil utilisateur
│   │   ├── Settings.tsx               # Paramètres
│   │   ├── Support.tsx                # Support client
│   │   ├── Admin.tsx                  # Administration
│   │   └── ...
│   ├── components/                    # Composants (36+ composants)
│   │   ├── AITutor.tsx                # Chat IA avec streaming
│   │   ├── Quiz.tsx                   # Quiz interactif
│   │   ├── Exam.tsx                   # Interface examen
│   │   ├── TDList.tsx                 # Liste TD avec PDF
│   │   ├── TPList.tsx                 # Liste TP avec PDF
│   │   ├── Simulation3D.tsx          # Visualisations 3D
│   │   ├── ImmersiveExperience.tsx    # Expérience immersive
│   │   ├── Navbar.tsx                 # Navigation
│   │   ├── Footer.tsx                 # Pied de page
│   │   └── ...
│   ├── services/
│   │   ├── api.ts                     # Client Axios configuré
│   │   └── chatService.ts             # Service chat streaming
│   ├── store/
│   │   └── authStore.ts               # État auth (Zustand)
│   ├── hooks/                         # Hooks React personnalisés
│   │   ├── useModules.ts
│   │   ├── useProgressTracker.ts
│   │   └── ...
│   └── i18n/                          # Internationalisation
│       └── locales/fr.json
└── package.json
```

---

## 🚀 Fonctionnalités Complètes

### 1. 🔐 Authentification & Utilisateurs

#### Fonctionnalités
- ✅ **Inscription/Connexion** (email + mot de passe)
- ✅ **OAuth Google** (connexion sociale)
- ✅ **Réinitialisation de mot de passe** (avec tokens TTL)
- ✅ **Gestion de profil utilisateur**
- ✅ **Rôles** (utilisateur/admin)
- ✅ **JWT tokens** avec expiration
- ✅ **Middleware de sécurité** (rate limiting, CSRF, headers sécurisés)

#### Endpoints API
- `POST /api/auth/register` - Inscription
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion
- `POST /api/auth/forgot-password` - Mot de passe oublié
- `POST /api/auth/reset-password` - Réinitialisation
- `GET /api/auth/me` - Profil utilisateur actuel

#### Technologies
- JWT (python-jose)
- Bcrypt (passlib)
- OAuth 2.0 (Google)

---

### 2. 📚 Modules d'Apprentissage

#### Fonctionnalités
- ✅ **2 matières** : Mathématiques, Informatique
- ✅ **3 niveaux de difficulté** : Débutant, Intermédiaire, Avancé
- ✅ **Contenu immersif** avec visualisations 3D
- ✅ **Progression utilisateur** par module
- ✅ **Favoris** (modules favoris)
- ✅ **Recherche** dans les modules
- ✅ **Filtres** (par matière, difficulté)
- ✅ **Recommandations personnalisées**

#### Génération Automatique de Contenu
- ✅ **TD (Travaux Dirigés)** générés automatiquement par IA
- ✅ **TP (Travaux Pratiques)** générés automatiquement par IA
- ✅ **Quiz** générés automatiquement (50 questions pour Informatique)
- ✅ **Examens** générés automatiquement (15 questions)
- ✅ **PDFs** générés pour TD, TP et Examens
- ✅ **Téléchargement et visualisation** des PDFs

#### Endpoints API
- `GET /api/modules` - Liste des modules (filtres, recherche)
- `GET /api/modules/{id}` - Détails d'un module
- `POST /api/modules` - Créer un module (admin)
- `PUT /api/modules/{id}` - Modifier un module (admin)
- `DELETE /api/modules/{id}` - Supprimer un module (admin)
- `POST /api/modules/{id}/generate-content` - Régénérer contenu (admin)

#### Technologies
- OpenAI GPT pour génération contenu
- ReportLab pour génération PDFs
- PyMuPDF pour conversion PDF en images

---

### 3. 🤖 Intelligence Artificielle - Tutorat (Kaïrox)

#### Modèles IA Configurés
- ✅ **GPT-5-mini** (Principal) : Tutorat standard, réponses rapides et économiques
- ✅ **GPT-5.2** (Expert) : Raisonnement scientifique approfondi
- ✅ **GPT-5.2-pro** (Research) : Analyses académiques et recherche

#### Fonctionnalités IA
- ✅ **Chat conversationnel** avec streaming (Server-Sent Events)
- ✅ **Historique de conversation** (10 derniers messages)
- ✅ **Support multilingue** (FR/EN)
- ✅ **Modes Expert et Research** (manuel ou automatique)
- ✅ **Routing intelligent automatique** selon la complexité
- ✅ **Analyse de documents** :
  - ✅ **PDFs** : Conversion automatique en images et analyse
  - ✅ **Images** : Analyse directe avec Vision API
  - ✅ **Word/PPT** : Détection (conversion manuelle recommandée)
- ✅ **Réponses contextuelles** adaptées au message utilisateur
- ✅ **Conversations naturelles** (salutations brèves, réponses adaptées)

#### Contrôle des Coûts IA
- ✅ **AI Cost Guard** : Plafonds de tokens par utilisateur/jour selon plan
  - FREE: 50k tokens/jour
  - PREMIUM: 200k tokens/jour
  - ENTERPRISE: Illimité
- ✅ **Plafond mensuel global** configurable (10M tokens/mois, 50€/mois par défaut)
- ✅ **Fallback automatique** vers GPT-5-mini si limite atteinte
- ✅ **Statistiques détaillées** par utilisateur

#### Cache & Performance IA
- ✅ **Cache sémantique Redis** : Réduction de 60% des coûts IA
- ✅ **TTL intelligent** selon type de réponse (1h-24h)
- ✅ **Invalidation par pattern**

#### Endpoints API
- `POST /api/ai/chat` - Chat standard (sans streaming)
- `POST /api/ai/chat/stream` - Chat avec streaming SSE
- `POST /api/ai/chat/stream/with-files` - Chat avec fichiers (PDF, images)
- `GET /api/ai/cost-guard/stats` - Statistiques coûts IA
- `GET /api/prompt-router/stats` - Statistiques routing IA

#### Technologies
- OpenAI API (GPT-5-mini, GPT-5.2)
- PyMuPDF pour conversion PDF
- Redis pour cache sémantique
- Server-Sent Events (SSE) pour streaming

---

### 4. 📝 Évaluations & Contenu Pédagogique

#### Quiz
- ✅ **Génération automatique** par IA (50 questions pour Informatique)
- ✅ **Questions à choix multiples** (4 options)
- ✅ **Correction automatique**
- ✅ **Scores et statistiques**
- ✅ **Historique des tentatives**
- ✅ **Uniquement pour modules Informatique**

#### Examens
- ✅ **Génération automatique** par IA (15 questions)
- ✅ **Chronométrés** (30 minutes par défaut)
- ✅ **Score de passage** (70% par défaut)
- ✅ **Prérequis** :
  - Informatique : 90% au quiz requis
  - Mathématiques : Module complété requis
- ✅ **PDF généré** automatiquement
- ✅ **Téléchargement et visualisation** PDF

#### Travaux Dirigés (TD)
- ✅ **Génération automatique** par IA pour chaque leçon
- ✅ **Exercices progressifs** (8 exercices par TD)
- ✅ **Solutions détaillées**
- ✅ **PDF généré** automatiquement
- ✅ **Téléchargement et visualisation** PDF

#### Travaux Pratiques (TP)
- ✅ **Génération automatique** par IA pour chaque leçon
- ✅ **Exercices pratiques** avec code, algorithmes
- ✅ **Exemples de code** et tests unitaires
- ✅ **Langage de programmation** spécifié
- ✅ **PDF généré** automatiquement
- ✅ **Téléchargement et visualisation** PDF

#### Endpoints API
- `GET /api/quiz/module/{module_id}` - Récupérer quiz
- `POST /api/quiz/{quiz_id}/submit` - Soumettre quiz
- `GET /api/exams/module/{module_id}` - Récupérer examen
- `POST /api/exams/{exam_id}/start` - Démarrer examen
- `POST /api/exams/{exam_id}/submit` - Soumettre examen
- `GET /api/tds/module/{module_id}` - Liste TD
- `GET /api/tds/{td_id}/pdf` - Télécharger PDF TD
- `GET /api/tps/module/{module_id}` - Liste TP
- `GET /api/tps/{tp_id}/pdf` - Télécharger PDF TP
- `GET /api/exams/module/{module_id}/pdf` - Télécharger PDF Examen

#### Technologies
- OpenAI GPT pour génération
- ReportLab pour PDFs
- JSON cleaning pour robustesse

---

### 5. 🎮 Gamification

#### Fonctionnalités
- ✅ **Système de badges** (déblocage automatique)
- ✅ **Progression et niveaux** utilisateur
- ✅ **Points d'expérience (XP)**
- ✅ **Classements** (leaderboard)
- ✅ **Quêtes** et objectifs
- ✅ **Statistiques** de progression

#### Endpoints API
- `GET /api/badges` - Liste des badges
- `GET /api/badges/user/{user_id}` - Badges utilisateur
- `POST /api/badges/{badge_id}/unlock` - Débloquer badge
- `GET /api/gamification/stats` - Statistiques gamification

---

### 6. 🧠 Apprentissage Adaptatif

#### Fonctionnalités
- ✅ **Profils d'apprentissage** personnalisés
- ✅ **Parcours intelligents** (pathways)
- ✅ **Détection de prérequis** automatique
- ✅ **Analyse d'erreurs** (error learning)
- ✅ **Recommandations** basées sur la progression
- ✅ **Adaptation du contenu** au niveau utilisateur

#### Endpoints API
- `GET /api/learning-profiles/{user_id}` - Profil d'apprentissage
- `GET /api/pathways` - Parcours disponibles
- `GET /api/recommendations` - Recommandations personnalisées
- `POST /api/error-learning/analyze` - Analyser erreurs

---

### 7. 📁 Ressources & Contenu

#### Fonctionnalités
- ✅ **Gestion de ressources** (PDF, Word, PPT, vidéos, audio)
- ✅ **Upload de fichiers** (max 100MB)
- ✅ **Organisation par module**
- ✅ **Types de ressources** : PDF, DOCX, PPTX, Vidéo, Audio
- ✅ **Visualisation PDFs** dans l'application
- ✅ **Téléchargement** des ressources

#### Endpoints API
- `GET /api/resources/module/{module_id}` - Ressources d'un module
- `POST /api/resources` - Upload ressource
- `DELETE /api/resources/{id}` - Supprimer ressource
- `GET /api/resources/files/{filename}` - Télécharger fichier

---

### 8. 💳 Abonnements & Paiements

#### Fonctionnalités
- ✅ **Intégration Stripe** complète
- ✅ **3 plans** : FREE, PREMIUM, ENTERPRISE
- ✅ **Gestion des abonnements** (création, annulation, renouvellement)
- ✅ **Webhooks Stripe** (événements paiement)
- ✅ **Limites par plan** (tokens IA, fonctionnalités)

#### Plans
- **FREE** : 50k tokens IA/jour, fonctionnalités de base
- **PREMIUM** : 200k tokens IA/jour, fonctionnalités avancées
- **ENTERPRISE** : Illimité, toutes fonctionnalités

#### Endpoints API
- `GET /api/subscriptions` - Abonnements utilisateur
- `POST /api/subscriptions/create-checkout` - Créer session Stripe
- `POST /api/subscriptions/cancel` - Annuler abonnement
- `POST /api/subscriptions/webhook` - Webhook Stripe

---

### 9. 📊 Analytics & Monitoring

#### Fonctionnalités
- ✅ **Learning Analytics** (suivi progression)
- ✅ **Statistiques utilisateur** (modules complétés, scores)
- ✅ **Performance monitoring** (middleware)
- ✅ **Logging de sécurité** (événements suspects)
- ✅ **Métriques IA** (coûts, usage, cache hit rate)

#### Endpoints API
- `GET /api/analytics/user/{user_id}` - Analytics utilisateur
- `GET /api/progress/stats` - Statistiques progression
- `GET /api/ai/cost-guard/stats` - Statistiques coûts IA

---

### 10. 🔒 Sécurité & Conformité

#### Middlewares de Sécurité
1. **PerformanceMiddleware** - Monitoring performances
2. **GZipMiddleware** - Compression réponses (>1KB)
3. **SecurityLoggingMiddleware** - Logging sécurité
4. **RateLimitMiddleware** - Rate limiting général (60 req/min, burst 10)
5. **RegistrationRateLimitMiddleware** - Limite inscriptions (3/heure, 5/jour)
6. **AIRateLimitMiddleware** - Limite endpoints IA (10/min, 50/heure)
7. **RequestSizeLimitMiddleware** - Limite taille requêtes (10MB)
8. **SecurityHeadersMiddleware** - En-têtes sécurité (CSP, HSTS, etc.)
9. **CORSMiddleware** - CORS configuré dynamiquement
10. **ErrorHandlerMiddleware** - Gestion centralisée erreurs

#### En-têtes de Sécurité
- Content-Security-Policy (CSP) - Dynamique selon environnement
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN (pour PDFs)
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy (géolocalisation, caméra, etc.)

#### RGPD
- ✅ **Export de données** utilisateur
- ✅ **Anonymisation** des données
- ✅ **Suppression** de compte
- ✅ **Logs d'audit** (gdpr_logs)

#### Endpoints API
- `GET /api/gdpr/export` - Exporter données utilisateur
- `POST /api/gdpr/anonymize` - Anonymiser données
- `DELETE /api/gdpr/delete-account` - Supprimer compte

---

### 11. 👥 Collaboration

#### Fonctionnalités
- ✅ **Système de collaboration** entre utilisateurs
- ✅ **Partage de ressources**
- ✅ **Travaux de groupe**

#### Endpoints API
- `GET /api/collaboration/groups` - Groupes de collaboration
- `POST /api/collaboration/share` - Partager ressource

---

### 12. 🎨 Expériences Immersives

#### Fonctionnalités
- ✅ **Visualisations 3D** (Three.js, React Three Fiber)
- ✅ **Simulations interactives**
- ✅ **Support AR/VR** (WebXR)
- ✅ **Laboratoires virtuels**
- ✅ **Avatar personnalisé**

#### Technologies
- Three.js pour rendu 3D
- React Three Fiber pour intégration React
- WebXR pour réalité augmentée/virtuelle

---

### 13. 🛡️ Anti-Triche

#### Fonctionnalités
- ✅ **Détection de triche** dans les examens
- ✅ **Analyse de patterns** suspects
- ✅ **Blocage automatique** si détecté

#### Endpoints API
- `POST /api/anti-cheat/detect` - Détecter triche
- `GET /api/anti-cheat/stats` - Statistiques anti-triche

---

### 14. 📈 Progression & Suivi

#### Fonctionnalités
- ✅ **Suivi de progression** par module
- ✅ **Statistiques détaillées** (temps passé, scores)
- ✅ **Validation de modules** (après examen)
- ✅ **Historique d'apprentissage**

#### Endpoints API
- `GET /api/progress` - Progression globale
- `GET /api/progress/{module_id}` - Progression module
- `POST /api/progress` - Mettre à jour progression
- `GET /api/validations/modules` - Modules validés

---

## 📡 API Endpoints Complets

### Authentification (`/api/auth`)
- `POST /register` - Inscription
- `POST /login` - Connexion
- `POST /logout` - Déconnexion
- `POST /forgot-password` - Mot de passe oublié
- `POST /reset-password` - Réinitialisation
- `GET /me` - Profil utilisateur

### IA Tutor (`/api/ai`)
- `POST /chat` - Chat standard
- `POST /chat/stream` - Chat avec streaming
- `POST /chat/stream/with-files` - Chat avec fichiers (PDF, images)
- `GET /cost-guard/stats` - Statistiques coûts IA

### Modules (`/api/modules`)
- `GET /` - Liste modules (filtres, recherche)
- `GET /{id}` - Détails module
- `POST /` - Créer module (admin)
- `PUT /{id}` - Modifier module (admin)
- `DELETE /{id}` - Supprimer module (admin)
- `POST /{id}/generate-content` - Régénérer contenu (admin)

### Quiz (`/api/quiz`)
- `GET /module/{module_id}` - Quiz d'un module
- `POST /{quiz_id}/submit` - Soumettre quiz

### Examens (`/api/exams`)
- `GET /` - Liste examens
- `GET /module/{module_id}` - Examen d'un module
- `GET /module/{module_id}/prerequisites` - Vérifier prérequis
- `POST /{exam_id}/start` - Démarrer examen
- `POST /{exam_id}/submit` - Soumettre examen
- `GET /module/{module_id}/pdf` - Télécharger PDF examen

### TD (`/api/tds`)
- `GET /module/{module_id}` - Liste TD d'un module
- `GET /{td_id}/pdf` - Télécharger PDF TD

### TP (`/api/tps`)
- `GET /module/{module_id}` - Liste TP d'un module
- `GET /{tp_id}/pdf` - Télécharger PDF TP

### Progression (`/api/progress`)
- `GET /` - Progression globale
- `GET /{module_id}` - Progression module
- `POST /` - Mettre à jour progression
- `GET /stats` - Statistiques progression

### Badges (`/api/badges`)
- `GET /` - Liste badges
- `GET /user/{user_id}` - Badges utilisateur

### Ressources (`/api/resources`)
- `GET /module/{module_id}` - Ressources d'un module
- `POST /` - Upload ressource
- `DELETE /{id}` - Supprimer ressource
- `GET /files/{filename}` - Télécharger fichier

### Abonnements (`/api/subscriptions`)
- `GET /` - Abonnements utilisateur
- `POST /create-checkout` - Créer session Stripe
- `POST /cancel` - Annuler abonnement

### Autres
- `/api/recommendations` - Recommandations personnalisées
- `/api/pathways` - Parcours intelligents
- `/api/analytics` - Learning Analytics
- `/api/gdpr` - Conformité RGPD
- `/api/prompt-router/stats` - Statistiques routing IA

**Documentation complète** : `http://localhost:8000/docs` (Swagger UI)

---

## 🎨 Frontend - Pages & Composants

### Pages (14 pages)
1. **Home** (`/`) - Page d'accueil avec présentation
2. **Login** (`/login`) - Connexion
3. **Register** (`/register`) - Inscription
4. **Dashboard** (`/dashboard`) - Tableau de bord utilisateur
5. **Modules** (`/modules`) - Liste des modules avec filtres
6. **ModuleDetail** (`/modules/:id`) - Détails module + IA Tutor + TD/TP/Quiz
7. **Exams** (`/exams`) - Liste des examens
8. **ExamDetail** (`/modules/:moduleId/exam`) - Passer un examen
9. **Profile** (`/profile`) - Profil utilisateur
10. **Settings** (`/settings`) - Paramètres
11. **Support** (`/support`) - Support client
12. **Admin** (`/admin`) - Administration (admin uniquement)
13. **ForgotPassword** (`/forgot-password`) - Mot de passe oublié
14. **ResetPassword** (`/reset-password`) - Réinitialisation

### Composants Principaux (36+ composants)
- **AITutor** - Chat IA avec streaming, modes Expert/Research, fichiers
- **Quiz** - Quiz interactif avec correction automatique
- **Exam** - Interface d'examen chronométré
- **TDList** - Liste TD avec visualisation PDF
- **TPList** - Liste TP avec visualisation PDF
- **Simulation3D** - Visualisations 3D avec Three.js
- **ImmersiveExperience** - Expérience immersive complète
- **ModuleCard** - Carte de module avec progression
- **Navbar** - Navigation principale
- **Footer** - Pied de page
- **LoadingSpinner** - Indicateurs de chargement
- **ProtectedRoute** - Protection routes authentifiées
- **ProtectedAdminRoute** - Protection routes admin
- **ResourceManager** - Gestion ressources (admin)
- **ErrorBoundary** - Gestion erreurs React

---

## 🗄️ Bases de Données

### MongoDB (Principal)

#### Collections Principales
- `users` - Utilisateurs (email, username, password hash, role, etc.)
- `modules` - Modules d'apprentissage (title, description, subject, difficulty, content, etc.)
- `progress` - Progression utilisateur (user_id, module_id, completion, scores, etc.)
- `quizzes` - Quiz (module_id, questions, correct_answers, etc.)
- `quiz_attempts` - Tentatives de quiz (user_id, quiz_id, answers, score, etc.)
- `exams` - Examens (module_id, questions, passing_score, time_limit, pdf_url, etc.)
- `exam_attempts` - Tentatives d'examen (user_id, exam_id, answers, score, etc.)
- `tds` - Travaux Dirigés (module_id, title, exercises, pdf_url, etc.)
- `tps` - Travaux Pratiques (module_id, title, steps, programming_language, pdf_url, etc.)
- `badges` - Badges (name, description, icon, etc.)
- `user_badges` - Badges utilisateurs (user_id, badge_id, unlocked_at)
- `subscriptions` - Abonnements Stripe (user_id, plan, stripe_subscription_id, status, etc.)
- `resources` - Ressources (module_id, title, file_url, resource_type, etc.)
- `user_history` - Historique IA (user_id, module_id, question, answer, etc.)
- `learning_profiles` - Profils d'apprentissage (user_id, current_level, preferences, etc.)
- `pathways` - Parcours intelligents (subject, modules, prerequisites, etc.)
- `ai_usage` - Usage IA (user_id, model, tokens_used, cost, etc.)
- `ai_requests` - Requêtes IA (user_id, message, response, cached, etc.)
- `module_validations` - Validations modules (user_id, module_id, exam_score, validated_at, etc.)
- `favorites` - Favoris (user_id, module_id)
- `collaboration_groups` - Groupes collaboration
- `gdpr_logs` - Logs RGPD (user_id, action, timestamp)

#### Indexes MongoDB
- Index unique sur `users.email` et `users.username`
- Index sur `modules.subject`, `modules.difficulty`, `modules.created_at`
- Index de texte sur `modules(title, description)` pour recherche
- Index composé sur `progress(user_id, module_id)`
- Index TTL sur `password_resets.expires_at`
- Et plus...

### PostgreSQL (Optionnel)

#### Tables Principales
- Relations utilisateur-cours-modules
- Inscriptions (enrollments)
- Progression structurée avec relations
- Données transactionnelles

**Note** : L'application fonctionne avec MongoDB uniquement si PostgreSQL n'est pas configuré.

### Redis (Cache)

#### Utilisations
- **Cache sémantique IA** (réponses IA fréquentes)
- **Rate limiting** (compteurs par IP)
- **Cache modules** (liste modules, détails)
- **Cache quiz** (quiz générés)
- **Cache progression** (stats utilisateur)
- **Classification IA** (cache prompt router)

---

## 🔧 Configuration & Variables d'Environnement

### Variables Obligatoires
```env
# MongoDB (Obligatoire)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=kaïros

# Sécurité (Obligatoire en production)
SECRET_KEY=votre_clé_secrète_32_caractères_minimum

# OpenAI (Nécessaire pour fonctionnalités IA)
OPENAI_API_KEY=sk-proj-...
```

### Variables Optionnelles
```env
# PostgreSQL (Optionnel)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_mot_de_passe
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse

# Redis (Optionnel mais recommandé)
REDIS_URL=redis://localhost:6379/0

# Environnement
ENVIRONMENT=development  # ou production

# Contrôle des coûts IA
AI_MONTHLY_TOKEN_LIMIT=10000000  # 10M tokens/mois
AI_MONTHLY_COST_LIMIT_EUR=50.0   # 50€/mois max

# Stripe (Optionnel)
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PREMIUM_PRICE_ID=price_...
STRIPE_ENTERPRISE_PRICE_ID=price_...

# Frontend
FRONTEND_URL=http://localhost:5173
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 📊 Métriques & Performance

### Coûts IA (Estimations)
- **Avant optimisations** : ~1000€/mois (100% GPT-5.2)
- **Après optimisations** : ~200-300€/mois (80-90% GPT-5-mini)
- **Économie** : 70-80% 🎉

### Performance
- **Cache hit rate** : Objectif 60%+
- **Temps de réponse moyen** : <500ms avec cache
- **Disponibilité** : 99.9% avec fallback gracieux
- **Rate limiting** : 60 req/min général, 10/min pour IA

---

## ✅ État d'Implémentation

### Fonctionnalités Complètes ✅
- [x] Authentification complète (JWT + OAuth Google)
- [x] Modules d'apprentissage (2 matières, 3 niveaux)
- [x] IA Tutor avec 3 modèles (GPT-5-mini, GPT-5.2, GPT-5.2-pro)
- [x] AI Cost Guard (contrôle des coûts)
- [x] Cache sémantique Redis
- [x] Routing intelligent IA
- [x] Fallback gracieux IA
- [x] Streaming de réponses (SSE)
- [x] Quiz et examens avec génération IA
- [x] TD et TP avec génération IA et PDFs
- [x] Gamification (badges, progression)
- [x] Apprentissage adaptatif
- [x] Intégration Stripe
- [x] Sécurité complète (middleware, rate limiting)
- [x] RGPD (export/anonymisation)
- [x] Analytics et monitoring
- [x] Analyse de documents (PDF, images)
- [x] Conversations naturelles et contextuelles

### À Implémenter 🔄
- [ ] Mémoire pédagogique utilisateur (niveau réel, historique erreurs)
- [ ] Auto-évaluation IA (IA note ses propres réponses)
- [ ] Observabilité IA (Prometheus/Grafana)
- [ ] Détection d'abus avancée (prompt hacking, flood)
- [ ] Sandbox des prompts (versioning, rollback)
- [ ] Mode explicatif progressif (réponse courte + "Approfondir")
- [ ] Feedback utilisateur (boutons "Utile/Pas utile")
- [ ] Background tasks (Celery/RQ pour générations longues)

---

## 🎯 Points Forts du Projet

1. **Architecture solide** : Pattern Repository, séparation des responsabilités
2. **Sécurité robuste** : Multiples middlewares, rate limiting, headers sécurisés
3. **Performance optimisée** : Cache Redis, compression GZip, lazy loading frontend
4. **IA intelligente** : Routing automatique, contrôle des coûts, fallback gracieux
5. **Scalabilité** : Support MongoDB + PostgreSQL, cache distribué Redis
6. **UX moderne** : Streaming, visualisations 3D, interface réactive
7. **Production-ready** : Gestion d'erreurs, monitoring, logging, health checks
8. **Génération automatique** : TD, TP, Quiz, Examens générés par IA
9. **Support documents** : Analyse PDF, images, Word, PPT
10. **Conversations naturelles** : Réponses adaptées au contexte

---

## 📚 Documentation Disponible

- `README.md` - Vue d'ensemble
- `ANALYSE_PROJET.md` - Analyse détaillée du projet
- `ARCHITECTURE_BASES_DONNEES.md` - Architecture des BDD
- `PRODUCTION_FEATURES_GUIDE.md` - Guide des fonctionnalités production
- `CONFIGURATION_MODELES_IA_COMPLETE.md` - Configuration IA
- `CACHE_INTELLIGENT_GUIDE.md` - Guide du cache
- `PROMPT_ROUTER_GUIDE.md` - Guide du routing IA
- `STRIPE_INTEGRATION_GUIDE.md` - Intégration Stripe
- `MIGRATION_POSTGRES.md` - Migration PostgreSQL
- `VERIFICATION_PDF_COMPLETE.md` - Vérification génération PDFs

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.10+
- Node.js 18+
- MongoDB (Docker ou installation locale)
- Redis (optionnel mais recommandé)
- PostgreSQL (optionnel)

### Commandes

1. **Démarrer MongoDB** :
```bash
docker-compose up -d mongodb
# ou
.\demarrer-mongodb.bat
```

2. **Backend** :
```bash
cd backend
.\venv\Scripts\python.exe main.py
```

3. **Frontend** :
```bash
cd frontend
npm run dev
```

### Accès
- **Frontend** : http://localhost:5173
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health

---

*Analyse complète effectuée le 2026-01-09*  
*Projet: Kaïros - Plateforme d'apprentissage immersif avec IA*
