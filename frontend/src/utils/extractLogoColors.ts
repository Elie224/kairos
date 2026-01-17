/**
 * Utilitaire pour extraire les couleurs dominantes du logo
 * et créer une palette de couleurs pour l'application
 */

// Couleurs extraites du logo Kaïrox (à ajuster selon le logo réel)
// Ces couleurs seront utilisées comme base pour la palette de l'application
// Thème bleu high-tech pour plateforme éducative immersive avec IA
export const LOGO_COLORS = {
  // Couleurs principales extraites du logo - Thème bleu high-tech
  primary: '#2563EB',      // Bleu high-tech professionnel (couleur principale)
  secondary: '#1E40AF',    // Bleu foncé pour le contraste
  accent: '#3B82F6',       // Bleu moyen pour les accents
  dark: '#1E3A8A',         // Bleu très foncé
  light: '#DBEAFE',        // Bleu très clair
}

/**
 * Génère une palette de couleurs Chakra UI basée sur les couleurs du logo
 */
export const generateColorPalette = (baseColor: string) => {
  // Convertir hex en RGB
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  }

  // Convertir RGB en hex
  const rgbToHex = (r: number, g: number, b: number) => {
    return '#' + [r, g, b].map(x => {
      const hex = x.toString(16)
      return hex.length === 1 ? '0' + hex : hex
    }).join('')
  }

  // Générer les nuances de couleur (50-900)
  const rgb = hexToRgb(baseColor)
  if (!rgb) return {}

  const palette: Record<string, string> = {}
  
  // Générer les nuances plus claires (50-400)
  for (let i = 50; i <= 400; i += 50) {
    const factor = (500 - i) / 500
    const r = Math.min(255, Math.round(rgb.r + (255 - rgb.r) * factor))
    const g = Math.min(255, Math.round(rgb.g + (255 - rgb.g) * factor))
    const b = Math.min(255, Math.round(rgb.b + (255 - rgb.b) * factor))
    palette[i] = rgbToHex(r, g, b)
  }

  // Couleur principale (500)
  palette[500] = baseColor

  // Générer les nuances plus foncées (600-900)
  for (let i = 600; i <= 900; i += 100) {
    const factor = (i - 500) / 500
    const r = Math.max(0, Math.round(rgb.r * (1 - factor * 0.7)))
    const g = Math.max(0, Math.round(rgb.g * (1 - factor * 0.7)))
    const b = Math.max(0, Math.round(rgb.b * (1 - factor * 0.7)))
    palette[i] = rgbToHex(r, g, b)
  }

  return palette
}

/**
 * Palette de couleurs basée sur le logo Kaïrox
 * Thème bleu high-tech pour plateforme éducative immersive avec IA
 */
export const KAIROS_COLORS = {
  // Palette principale basée sur les couleurs du logo - Thème bleu high-tech
  primary: generateColorPalette('#2563EB'), // Bleu high-tech professionnel
  secondary: generateColorPalette('#1E40AF'), // Bleu foncé pour le contraste
  accent: generateColorPalette('#3B82F6'),   // Bleu moyen pour les accents
}

