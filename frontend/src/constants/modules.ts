/**
 * Constantes pour les modules d'apprentissage
 */

export const SUBJECT_COLORS: Record<string, string> = {
  mathematics: 'blue',  // Algèbre
  computer_science: 'purple',  // Machine Learning
}

export const SUBJECT_ORDER = [
  'mathematics',  // Algèbre
  'computer_science',  // Machine Learning
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


