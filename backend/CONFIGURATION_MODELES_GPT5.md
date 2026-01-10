# Configuration des Modèles GPT-5 pour Kaïros

## Modèles configurés

### 1. GPT-5.2 – Expert
**Clé API**: Configurée dans `.env`
**Usage**: Examens, TD avancés, TP Machine Learning, corrections détaillées

**Prompt système**:
```
Tu es un professeur universitaire expert en mathématiques et machine learning.
Ton objectif est de générer des contenus pédagogiques avancés pour les étudiants de niveau Licence 3 / Master 1.
Crée un contenu structuré comprenant :
1. Objectifs pédagogiques précis
2. Une série d'exercices progressifs (algèbre, probabilités, machine learning)
3. Des TP avec instructions pratiques et jeux de données simulés
4. Corrigés détaillés et explicatifs
5. Barème et astuces méthodologiques
```

**Format de sortie JSON**:
```json
{
  "titre": "",
  "niveau": "L3/M1",
  "exercices": [
    {
      "type": "TD/TP/Examen",
      "enonce": "",
      "solution": "",
      "points": ""
    }
  ]
}
```

**Conseil**: Utiliser GPT-5.2 uniquement pour les contenus complexes pour limiter les coûts.

---

### 2. GPT-5-mini – Usage principal / pédagogique
**Usage**: TD standards, quiz, explications de cours, exercices progressifs

**Prompt système**:
```
Tu es un professeur pédagogue en mathématiques et machine learning.
Génère un TD ou quiz pour les étudiants de Licence 3.
Le contenu doit inclure :
1. Titre du TD ou quiz
2. Liste de 5 à 10 exercices variés (probabilités, algèbre, ML)
3. Corrigés simples et clairs pour chaque exercice
4. Suggestions de difficulté pour chaque exercice (facile, moyen, difficile)
5. Formatage clair pour intégration dans une application
```

**Format de sortie JSON**:
```json
{
  "titre": "",
  "niveau": "L3",
  "exercices": [
    {
      "type": "TD/Quiz",
      "enonce": "",
      "solution": "",
      "difficulte": ""
    }
  ]
}
```

---

### 3. GPT-5-nano – Usage rapide / économique
**Usage**: QCM, flash-cards, vérification de réponses, révisions rapides

**Prompt système**:
```
Tu es un assistant pédagogique rapide.
Génère un QCM ou flash-card pour étudiants en probabilités, algèbre ou machine learning.
Chaque QCM doit inclure :
1. Question concise
2. 3 à 4 options
3. Indication de la bonne réponse
4. Explication courte si nécessaire
```

**Format de sortie JSON**:
```json
{
  "question": "",
  "options": [],
  "bonne_reponse": "",
  "explication_courte": ""
}
```

---

## Configuration dans le code

### Fichier `.env`
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Fichier `backend/app/config.py`
```python
gpt_5_2_model: str = "gpt-5.2"  # Expert - Raisonnement complexe
gpt_5_mini_model: str = "gpt-5-mini"  # Principal - Pédagogique
gpt_5_nano_model: str = "gpt-5-nano"  # Rapide - Économique
```

---

## Utilisation automatique

Le système choisit automatiquement le modèle selon le contexte :

- **GPT-5.2** : TP Machine Learning, examens, TD avancés
- **GPT-5-mini** : TD standards, quiz, chat avec l'étudiant
- **GPT-5-nano** : QCM, flash-cards, vérifications rapides

---

## Mise à jour de la clé API

Pour mettre à jour la clé API, exécutez :
```bash
cd backend
.\venv\Scripts\python.exe scripts\update_openai_key.py
```

Ou modifiez directement le fichier `backend/.env` :
```env
OPENAI_API_KEY=votre_nouvelle_cle
```

**Important**: Redémarrez le backend après modification de la clé API.
