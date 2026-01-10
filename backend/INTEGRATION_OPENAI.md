# 🤖 Intégration OpenAI - Application Kaïros

## 📋 Vue d'ensemble

L'application Kaïros intègre OpenAI pour créer une expérience d'apprentissage immersive avec génération automatique de contenu pédagogique.

## ✨ Fonctionnalités

### 1. Génération de TD (Travaux Dirigés)
- Génère automatiquement des exercices progressifs
- 5 à 8 exercices par TD
- Chaque exercice avec indices et solutions détaillées
- Adapté au niveau de difficulté du module

### 2. Génération de TP (Travaux Pratiques)
- Crée des travaux pratiques avec étapes claires
- 4 à 6 étapes progressives
- Objectifs, matériel nécessaire, critères d'évaluation
- Adapté à la matière (Mathématiques ou Informatique)

### 3. Génération de Quiz
- Questions variées (QCM, vrai/faux, calculs)
- 4 options par question
- Explications détaillées pour chaque réponse
- Adapté au niveau de difficulté

### 4. Chat avec l'Assistant IA
- Échange conversationnel avec l'étudiant
- Contexte du module intégré
- Historique de conversation
- Suggestions de questions

## 🚀 Utilisation

### Configuration

1. **Ajouter la clé API OpenAI dans `.env`** :
```env
OPENAI_API_KEY=sk-...
```

2. **Redémarrer le backend** :
```powershell
.\demarrer-backend.bat
```

### Endpoints API

#### 1. Chat avec l'Assistant IA

```http
POST /api/openai/chat
Content-Type: application/json

{
  "message": "Explique-moi les matrices",
  "module_id": "module_id_optional",
  "conversation_history": [
    {"role": "user", "content": "Bonjour"},
    {"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider ?"}
  ]
}
```

**Réponse** :
```json
{
  "response": "Les matrices sont...",
  "suggestions": [
    "Peux-tu expliquer plus en détail ?",
    "Donne-moi un exemple pratique",
    "Quelle est la prochaine étape ?"
  ]
}
```

#### 2. Générer un TD

```http
POST /api/openai/generate/td?module_id=MODULE_ID&lesson_index=0
Authorization: Bearer TOKEN
```

**Réponse** :
```json
{
  "type": "td",
  "data": {
    "title": "TD - Matrices",
    "introduction": "...",
    "exercises": [
      {
        "number": 1,
        "title": "Exercice 1",
        "question": "...",
        "hints": ["Indice 1", "Indice 2"],
        "solution": "...",
        "difficulty": "facile"
      }
    ]
  }
}
```

#### 3. Générer un TP

```http
POST /api/openai/generate/tp?module_id=MODULE_ID&lesson_index=0
Authorization: Bearer TOKEN
```

#### 4. Générer un Quiz

```http
POST /api/openai/generate/quiz?module_id=MODULE_ID&num_questions=10
Authorization: Bearer TOKEN
```

**Réponse** :
```json
{
  "type": "quiz",
  "count": 10,
  "data": [
    {
      "question": "Qu'est-ce qu'une matrice ?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "...",
      "difficulty": "facile",
      "points": 1
    }
  ]
}
```

#### 5. Générer tout le contenu (Admin)

```http
POST /api/openai/generate-all/MODULE_ID
Authorization: Bearer ADMIN_TOKEN
```

Génère automatiquement TD, TP et Quiz pour toutes les leçons d'un module.

## 📝 Structure du Code

### Service OpenAI
- **Fichier** : `backend/app/services/openai_content_generator.py`
- **Classe** : `OpenAIContentGenerator`
- **Méthodes** :
  - `generate_td()` - Génère un TD
  - `generate_tp()` - Génère un TP
  - `generate_quiz_questions()` - Génère des questions de quiz
  - `chat_with_student()` - Chat avec l'étudiant

### Routes API
- **Fichier** : `backend/app/routers/openai_content.py`
- **Préfixe** : `/api/openai`
- **Endpoints** :
  - `POST /chat` - Chat avec l'IA
  - `POST /generate/{content_type}` - Générer du contenu
  - `POST /generate-all/{module_id}` - Générer tout (Admin)

## 🔧 Modèles OpenAI Utilisés

- **GPT-4o-mini** : Modèle principal pour génération de contenu
  - Efficace et économique
  - Bonne qualité de génération
  - Temps de réponse rapide

## 🎯 Matières Supportées

1. **Mathématiques (Algèbre)**
   - TD avec exercices progressifs
   - TP pratiques
   - Quiz adaptés

2. **Informatique (Machine Learning)**
   - TD avec cas pratiques
   - TP avec code et implémentation
   - Quiz techniques

## 🔒 Sécurité

- Authentification requise pour tous les endpoints
- Rate limiting appliqué (via `AIRateLimitMiddleware`)
- Validation des entrées
- Sanitization des données

## 📊 Monitoring

Les erreurs sont loggées avec :
- Détails de l'erreur
- Contexte du module
- Type de contenu généré

## 🚨 Gestion d'Erreurs

Si OpenAI n'est pas configuré :
- Retour de contenu exemple
- Message d'avertissement dans les logs
- L'application continue de fonctionner

## 📚 Documentation API

Accédez à la documentation interactive :
```
http://localhost:8000/docs
```

Cherchez les endpoints sous le tag **"OpenAI Content Generation"**.

## ✅ Checklist d'Intégration

- [x] Service OpenAI créé
- [x] Routes API créées
- [x] Intégration dans main.py
- [x] Gestion d'erreurs
- [x] Documentation
- [ ] Tests unitaires
- [ ] Tests d'intégration
- [ ] Interface frontend

## 🎉 Prochaines Étapes

1. **Frontend** : Créer l'interface pour utiliser ces endpoints
2. **Tests** : Ajouter des tests unitaires et d'intégration
3. **Optimisation** : Cache des réponses OpenAI
4. **Analytics** : Suivre l'utilisation de l'IA
