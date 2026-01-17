/**
 * Constantes pour les modules d'apprentissage
 */

export const SUBJECT_COLORS: Record<string, string> = {
  mathematics: 'blue',  // Mathématiques (Fonctions, Suites, Algèbre linéaire, Analyse, Probabilités)
  computer_science: 'purple',  // Informatique, IA & Machine Learning
  physics: 'cyan',  // Physique (Mécanique, Ondes, Électricité, Quantique)
  chemistry: 'green',  // Chimie (Générale, Organique, Minérale, Solutions)
  biology: 'teal',  // Biologie (Cellules, ADN, Organes, Physiologie)
  geography: 'orange',  // Géographie (Cartes, Climats, Reliefs)
  economics: 'yellow',  // Économie (Offre/Demande, Marchés)
  history: 'red',  // Histoire (Lignes du temps, Événements)
}

export const SUBJECT_ORDER = [
  'mathematics',  // Mathématiques
  'computer_science',  // Informatique & IA
  'physics',  // Physique
  'chemistry',  // Chimie
  'biology',  // Biologie
  'geography',  // Géographie
  'economics',  // Économie
  'history',  // Histoire
] as const

export const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: 'gray',
  intermediate: 'gray',
  advanced: 'gray',
}

export const DIFFICULTY_ICONS: Record<string, string> = {
  beginner: '🌱',
  intermediate: '⚡',
  advanced: '🔥',
}


