# Kaïrox - Plateforme d'apprentissage immersif avec IA

Application web utilisant l'intelligence artificielle et les visualisations 3D interactives pour expliquer des concepts complexes (physique, chimie, mathématiques, anglais et informatique) de manière visuelle et interactive.

## 🚀 Technologies

- **Frontend**: React + TypeScript + Three.js/WebXR
- **Backend**: Python + FastAPI
- **Base de données**: MongoDB
- **IA**: OpenAI API / LLM pour tutorat intelligent

## 📁 Structure du projet

```
Kaïrox/
├── backend/          # API FastAPI
├── frontend/         # Application React
├── shared/           # Types et utilitaires partagés
└── docs/             # Documentation
```

## 🚀 Démarrage Rapide

### ⚠️ IMPORTANT : Démarrer MongoDB d'abord !

**Avant de démarrer l'application, vous devez démarrer MongoDB :**

**Option 1 : Avec Docker (Recommandé)**
1. Démarrez Docker Desktop
2. Exécutez : `demarrer-mongodb.bat` (Windows) ou `docker-compose up -d mongodb`
3. Initialisez la base : `initialiser-bdd.bat` (Windows) ou `cd backend && python scripts/init_db.py`

**Option 2 : Installer MongoDB directement**
- Suivez le guide : `GUIDE_MONGODB.md`

### Liens d'accès (après démarrage)
- **Application** : http://localhost:3000
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs

### Commandes de démarrage

**1. Backend (Terminal 1)**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python main.py
```

**2. Frontend (Terminal 2)**
```bash
cd frontend
npm install
npm run dev
```

📖 **Guide complet** : Voir `DEMARRAGE_RAPIDE.md` pour plus de détails  
📘 **Guide MongoDB** : Voir `GUIDE_MONGODB.md` pour configurer MongoDB

## 📚 Modules disponibles

- **Physique**: Gravitation, Électricité, Magnétisme
- **Chimie**: Réactions chimiques, Structure atomique
- **Maths**: Géométrie 3D, Calcul différentiel
- **Anglais**: Grammaire, Vocabulaire, Conversation et Compréhension

## 🤖 Fonctionnalités IA

- Tutorat intelligent avec explications adaptées
- Génération de quiz personnalisés
- Feedback automatique sur les exercices

