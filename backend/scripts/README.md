# Scripts d'initialisation

## Initialisation des contenus de démonstration

Le script `init_demo_content.py` permet de créer des modules de démonstration dans la base de données.

### Utilisation

```bash
# Depuis le répertoire backend
python scripts/init_demo_content.py
```

### Modules créés

Le script crée 6 modules de démonstration couvrant différentes matières :

1. **Introduction à la Mécanique Classique** (Physique - Débutant)
2. **Les Bases de l'Algèbre Linéaire** (Mathématiques - Intermédiaire)
3. **Structure Atomique et Tableau Périodique** (Chimie - Débutant)
4. **Introduction à la Programmation Python** (Informatique - Débutant)
5. **Grammaire Anglaise : Les Temps Verbaux** (Anglais - Intermédiaire)
6. **Électromagnétisme Avancé** (Physique - Avancé)

### Prérequis

- MongoDB doit être démarré et accessible
- Les variables d'environnement doivent être configurées (MONGODB_URL, etc.)
- Les dépendances Python doivent être installées

### Note

Si des modules existent déjà dans la base de données, le script vous demandera confirmation avant d'ajouter les nouveaux modules.










