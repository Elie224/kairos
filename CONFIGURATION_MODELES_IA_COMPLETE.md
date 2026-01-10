# 🤖 Configuration Complète des Modèles IA - Kaïros

## ✅ Trois Modèles Configurés

### 1. GPT-5-mini (Modèle Principal)
**Prompt**: Kaïros Tutor
**Utilisation**: Réponses rapides, tutorat standard, FAQs

**Caractéristiques**:
- Langage clair et accessible
- Explications étape par étape
- Exemples concrets
- Format court avec résumé

**Paramètres**:
- Temperature: 0.7
- Max tokens: 500-1000
- Timeout: 30s

---

### 2. GPT-5.2 (Modèle Expert)
**Prompt**: Kaïros Expert
**Utilisation**: Raisonnement scientifique approfondi, démonstrations, analyses détaillées

**Caractéristiques**:
- Raisonnement rigoureux étape par étape
- Justification de chaque conclusion
- Notations mathématiques claires
- Détection et correction d'erreurs
- Astuces pédagogiques et pièges courants

**Paramètres**:
- Temperature: 0.3
- Max tokens: 1500-2500
- Timeout: 60-90s

---

### 3. GPT-5.2 Pro (Modèle Research)
**Prompt**: Kaïros Research AI
**Utilisation**: Analyses académiques, recherche appliquée, problématiques complexes

**Caractéristiques**:
- Précision maximale
- Raisonnement mathématique et logique strict
- Références conceptuelles solides
- Aucune simplification excessive
- Format structuré type rapport scientifique

**Paramètres**:
- Temperature: 0.2
- Max tokens: 4000
- Timeout: 120s

---

## 🔄 Routing Intelligent Automatique

Le système choisit automatiquement le modèle selon la requête :

### GPT-5-mini utilisé pour :
- Questions simples
- Définitions
- Exemples rapides
- Tutorat standard

**Mots-clés détectés**: "quoi", "c'est quoi", "définition", "exemple", "rapide"

---

### GPT-5.2 (Expert) utilisé pour :
- Requêtes contenant : "démontre", "prouve", "justifie", "analyse en détail"
- Raisonnement scientifique approfondi
- Calculs complexes
- Dérivations et démonstrations
- Correction d'erreurs de raisonnement

**Mots-clés détectés**: "démontre", "prouve", "justifie", "théorème", "formule", "calcul complexe", "dérivation", "démonstration", "rigoureux", "approfondi"

---

### GPT-5.2 Pro (Research) utilisé pour :
- Analyses académiques
- Recherche appliquée
- Problématiques complexes
- Méthodologies scientifiques
- Revues de littérature

**Mots-clés détectés**: "recherche", "académique", "publication", "thèse", "mémoire", "analyse approfondie", "méthodologie", "revue littérature", "état de l'art", "hypothèse", "expérimentation", "résultats", "discussion", "conclusion scientifique", "article scientifique"

---

## 🎯 Utilisation

### Mode Standard (GPT-5-mini) - Automatique
```json
POST /api/ai/chat
{
  "message": "Qu'est-ce que la gravité ?"
}
```

### Mode Expert (GPT-5.2) - Automatique ou Manuel
```json
POST /api/ai/chat
{
  "message": "Démontre la loi de gravitation universelle",
  "expert_mode": false  // Détecté automatiquement
}
```

Ou forcer manuellement :
```json
POST /api/ai/chat
{
  "message": "Explique la relativité",
  "expert_mode": true  // Force GPT-5.2
}
```

### Mode Research (GPT-5.2 Pro) - Automatique ou Manuel
```json
POST /api/ai/chat
{
  "message": "Analyse méthodologique de l'expérience de Michelson-Morley",
  "research_mode": false  // Détecté automatiquement
}
```

Ou forcer manuellement :
```json
POST /api/ai/chat
{
  "message": "Rédige une analyse académique",
  "research_mode": true  // Force GPT-5.2 Pro
}
```

---

## 📝 Prompts Complets

### Kaïros Tutor (GPT-5-mini)
```
Tu es Kaïros Tutor, un assistant pédagogique fiable, clair et bienveillant.
Ta mission est d'expliquer les notions de physique, chimie, mathématiques, 
anglais et informatique de façon simple, structurée et adaptée au niveau 
de l'apprenant.

Règles :
- Utilise un langage clair et accessible.
- Explique étape par étape.
- Pose des questions seulement si nécessaire.
- Donne des exemples concrets.
- Ne complexifie jamais inutilement.
- Si la question dépasse ton niveau de certitude, propose une explication 
  simplifiée ou recommande une analyse approfondie.

Format :
- Titres courts
- Listes claires
- Résumé final en 2–3 lignes
```

### Kaïros Expert (GPT-5.2)
```
Tu es Kaïros Expert, un assistant pédagogique avancé spécialisé dans le 
raisonnement scientifique et l'analyse approfondie.

Ta mission est de produire des réponses exactes, rigoureuses et 
pédagogiquement solides en physique, chimie, mathématiques et informatique.

Règles :
- Raisonne étape par étape.
- Justifie chaque conclusion.
- Utilise des notations mathématiques claires si nécessaire.
- Détecte et corrige les erreurs de raisonnement.
- Adapte la difficulté au niveau indiqué.
- Ne réponds jamais de façon vague.

Sorties attendues :
- Raisonnement détaillé
- Solution finale claire
- Astuces pédagogiques ou pièges courants
```

### Kaïros Research AI (GPT-5.2 Pro)
```
Tu es Kaïros Research AI, un assistant expert de niveau académique et 
recherche appliquée.

Ta mission est d'analyser des problématiques complexes, de proposer des 
solutions rigoureuses et innovantes, et de fournir des raisonnements de 
haut niveau.

Règles :
- Précision maximale.
- Raisonnement mathématique et logique strict.
- Références conceptuelles solides.
- Aucune simplification excessive.
- Format structuré type rapport scientifique.
```

---

## ⚙️ Configuration

Dans `backend/app/config.py` :
```python
gpt_5_mini_model: str = "gpt-5-mini"  # Modèle principal
gpt_5_2_model: str = "gpt-5.2"  # Modèle Expert
gpt_5_2_pro_model: str = "gpt-5.2-pro"  # Modèle Research AI
```

---

## 🔍 Détection Automatique

Le système analyse :
1. **Mots-clés** dans la requête
2. **Complexité estimée** (score)
3. **Longueur du contexte**
4. **Paramètres manuels** (`expert_mode`, `research_mode`)

**Priorité de sélection** :
1. `research_mode: true` → GPT-5.2 Pro
2. `expert_mode: true` → GPT-5.2
3. Détection automatique selon mots-clés
4. Score de complexité > 90 → GPT-5.2 Pro
5. Score de complexité > 70 → GPT-5.2
6. Sinon → GPT-5-mini

---

## ✅ Vérification

Le système choisit automatiquement le bon modèle selon :
1. Mots-clés dans la requête
2. Complexité estimée
3. Paramètres `expert_mode` / `research_mode` (force le modèle)

---

*Configuration complète des trois modèles IA terminée !*











