/**
 * Initialisation du thème - Doit être importé AVANT le fichier theme.ts
 * Force l'application du thème bleu pour Kaïros
 */
import { setThemeColor } from './themeColors'

// Forcer l'application du thème bleu au démarrage
// Migration automatique de l'ancien thème "white" vers "blue"
try {
  const stored = localStorage.getItem('kairos-theme-color')
  if (stored) {
    const parsed = JSON.parse(stored)
    // Migrer automatiquement de "white" vers "blue" si nécessaire
    if (!parsed || parsed.color === 'white' || parsed.color !== 'blue') {
      setThemeColor('blue')
    }
  } else {
    // Aucun thème défini, utiliser bleu par défaut
    setThemeColor('blue')
  }
} catch (e) {
  // En cas d'erreur, forcer le thème bleu
  setThemeColor('blue')
}








