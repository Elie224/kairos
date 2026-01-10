# 📚 Simplification des Matières - Application Kaïros

## 🎯 Objectif

Simplifier l'application pour le développement initial en ne gardant que **deux matières** :

1. **Mathématiques (Algèbre)** - `mathematics`
2. **Informatique (Machine Learning)** - `computer_science`

---

## ✅ Modifications Effectuées

### Backend

#### 1. `backend/app/models.py`
- ✅ Déjà simplifié : ne contient que `MATHEMATICS` et `COMPUTER_SCIENCE`

#### 2. `backend/app/models/user_history.py`
- ✅ Mis à jour : ne contient plus que `MATHEMATICS` et `COMPUTER_SCIENCE`
- ❌ Supprimé : `PHYSICS`, `CHEMISTRY`, `ENGLISH`, `ECONOMICS`, `OTHER`

### Frontend

#### 3. `frontend/src/constants/modules.ts`
- ✅ `SUBJECT_COLORS` : Mis à jour avec seulement les 2 matières
- ✅ `SUBJECT_ORDER` : Mis à jour avec seulement les 2 matières
- 🎨 Couleurs améliorées : `mathematics: 'blue'`, `computer_science: 'purple'`

#### 4. `frontend/src/pages/Admin.tsx`
- ✅ `SUBJECTS` : Mis à jour avec seulement les 2 matières

#### 5. `frontend/src/components/modules/SubjectCard.tsx`
- ✅ `SUBJECT_ICONS` : Mis à jour avec seulement les 2 matières
- ✅ `SUBJECT_DESCRIPTIONS` : Descriptions spécifiques pour Algèbre et Machine Learning

---

## 📝 Descriptions des Matières

### Mathématiques (Algèbre)
- **Icône** : 📐
- **Description** : "Maîtrisez l'algèbre : équations, polynômes, matrices et plus encore"
- **Couleur** : Bleu (`blue`)

### Informatique (Machine Learning)
- **Icône** : 🤖
- **Description** : "Apprenez le Machine Learning : algorithmes, réseaux de neurones, deep learning"
- **Couleur** : Violet (`purple`)

---

## 🔍 Fichiers à Vérifier (Optionnel)

Si vous voulez nettoyer complètement, vérifiez aussi :

- `backend/scripts/init_demo_content.py` - Contenu de démonstration
- `frontend/src/pages/Modules.tsx` - Filtres de matières
- `frontend/src/i18n/locales/fr.json` - Traductions
- Toute autre référence aux anciennes matières

---

## 🚀 Prochaines Étapes

1. **Redémarrer le backend** pour appliquer les changements
2. **Créer des modules de test** pour les deux matières :
   - Modules d'Algèbre (débutant, intermédiaire, avancé)
   - Modules de Machine Learning (débutant, intermédiaire, avancé)
3. **Tester l'interface** pour vérifier que seules les 2 matières apparaissent

---

## 📊 Structure Recommandée des Modules

### Mathématiques (Algèbre)
- **Débutant** : Équations linéaires, opérations de base
- **Intermédiaire** : Polynômes, factorisation, systèmes d'équations
- **Avancé** : Matrices, algèbre linéaire, espaces vectoriels

### Informatique (Machine Learning)
- **Débutant** : Introduction au ML, régression linéaire
- **Intermédiaire** : Classification, arbres de décision, SVM
- **Avancé** : Deep Learning, réseaux de neurones, CNN, RNN

---

## ✅ État Actuel

- [x] Backend simplifié
- [x] Frontend simplifié
- [x] Icônes et descriptions mises à jour
- [ ] Contenu de démonstration à créer
- [ ] Tests à effectuer

---

**Application simplifiée et prête pour le développement ! 🚀**
