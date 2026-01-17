# 🚀 Documentation API Kairos - Prompts Officiels

## Vue d'ensemble

Kairos dispose d'une architecture IA pédagogique complète avec 10 priorités stratégiques implémentées.

**Base URL**: `/api/kairos`

---

## 📐 PRIORITÉ 1 - Curriculum Intelligent

### `POST /api/kairos/curriculum/generate`

Génère un curriculum complet et structuré pour une matière.

**Request Body:**
```json
{
  "subject": "mathematics",
  "level": "lycée",
  "objective": "exam"
}
```

**Response:**
```json
{
  "success": true,
  "curriculum": {
    "modules": [...],
    "progression_path": {...},
    "adaptation_strategy": {...}
  }
}
```

---

## 🧠 PRIORITÉ 2 - Profil Cognitif

### `POST /api/kairos/learner/profile/update`

Met à jour le profil cognitif de l'apprenant.

**Request Body:**
```json
{
  "learning_data": {
    "completed_modules": 5,
    "average_score": 75,
    "errors": ["erreur1"]
  }
}
```

### `GET /api/kairos/learner/profile?user_id=xxx`

Récupère le profil cognitif.

---

## 📊 PRIORITÉ 3 - Évaluation Intelligente

### `POST /api/kairos/evaluation/generate`

Génère une évaluation complète.

**Request Body:**
```json
{
  "subject": "physics",
  "level": "lycée",
  "evaluation_type": "formative|summative|adaptive|oral"
}
```

### `POST /api/kairos/evaluation/correct`

Corrige une évaluation avec feedback détaillé.

---

## 🔍 PRIORITÉ 4 - Explainability

### `POST /api/kairos/explainability/analyze`

Analyse une erreur et explique pourquoi l'apprenant s'est trompé.

**Request Body:**
```json
{
  "error_analysis": {
    "user_answer": "réponse",
    "correct_answer": "bonne réponse",
    "question": "question"
  }
}
```

---

## 🧪 PRIORITÉ 5 - Mode Laboratoire

### `POST /api/kairos/lab/simulate`

Génère une simulation de laboratoire interactive.

**Request Body:**
```json
{
  "simulation_request": "Simule un circuit RC avec résistance variable"
}
```

---

## 🎮 PRIORITÉ 6 - Gamification Avancée

### `POST /api/kairos/gamification/season/generate`

Génère une saison pédagogique avec progression.

**Request Body:**
```json
{
  "subject": "mathematics",
  "theme": "Algèbre avancée"
}
```

### `POST /api/kairos/gamification/badge/evolve`

Évalue si un badge peut évoluer (Bronze → Argent → Or).

---

## 🤖 PRIORITÉ 7 - Multi-Agents IA

### `POST /api/kairos/agents/{agent_type}`

Appelle un agent IA spécifique.

**Agents disponibles:**
- `theorist_prof` - Prof Théoricien
- `motivation_coach` - Coach Motivation
- `examiner` - Examinateur
- `scientific_researcher` - Chercheur Scientifique

**Request Body:**
```json
{
  "agent_type": "theorist_prof",
  "context": {
    "concept": "dérivée",
    "level": "lycée"
  }
}
```

---

## 📈 PRIORITÉ 8 - Analytics & Dashboard

### `POST /api/kairos/analytics/predict`

Prédit le taux de réussite et détecte les risques de décrochage.

### `POST /api/kairos/analytics/dashboard`

Génère des insights intelligents pour le dashboard.

---

## 📚 PRIORITÉ 9 - Contenu Académique

### `POST /api/kairos/academic/pdf-notes`

Génère des notes de cours au format PDF.

### `POST /api/kairos/academic/learning-report`

Génère un rapport d'apprentissage complet.

---

## 🎯 Endpoints Existants

### Visualisations
- `POST /api/kairos/visualization/generate`

### Quêtes
- `POST /api/kairos/quest/generate`

### Badges
- `POST /api/kairos/badge/attribute`

### Feedback
- `POST /api/kairos/feedback/generate`

### Recommandations
- `POST /api/kairos/recommendation/generate`

### Topics
- `GET /api/kairos/topics/{subject}`

---

## 🧪 Tests

Exécuter les tests :
```bash
pytest backend/tests/test_kairos_prompts.py -v
```

---

## 📝 Notes

- Tous les endpoints retournent du JSON
- Les réponses OpenAI sont parsées automatiquement
- En cas d'erreur de parsing, `raw_response` contient la réponse brute
- Les endpoints sont publics (authentification optionnelle à ajouter)
