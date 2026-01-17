/**
 * Couleurs de thème par domaine d'application
 * Basé sur la psychologie des couleurs et les associations sectorielles
 */

export interface ThemeColorConfig {
  primary: string
  secondary: string
  accent: string
  name: string
  description: string
}

/**
 * Génère une palette de couleurs Chakra UI à partir d'une couleur de base
 */
export const generateColorPalette = (baseColor: string): Record<string, string> => {
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 74, g: 144, b: 226 }
  }

  const rgbToHex = (r: number, g: number, b: number) => {
    return '#' + [r, g, b].map(x => {
      const hex = Math.round(x).toString(16)
      return hex.length === 1 ? '0' + hex : hex
    }).join('')
  }

  const rgb = hexToRgb(baseColor)
  const palette: Record<string, string> = {}

  // Nuances claires (50-400)
  for (let i = 50; i <= 400; i += 50) {
    const factor = (500 - i) / 500
    const r = Math.min(255, rgb.r + (255 - rgb.r) * factor)
    const g = Math.min(255, rgb.g + (255 - rgb.g) * factor)
    const b = Math.min(255, rgb.b + (255 - rgb.b) * factor)
    palette[i] = rgbToHex(r, g, b)
  }

  // Couleur principale (500)
  palette[500] = baseColor

  // Nuances foncées (600-900)
  for (let i = 600; i <= 900; i += 100) {
    const factor = (i - 500) / 500
    const r = Math.max(0, rgb.r * (1 - factor * 0.8))
    const g = Math.max(0, rgb.g * (1 - factor * 0.8))
    const b = Math.max(0, rgb.b * (1 - factor * 0.8))
    palette[i] = rgbToHex(r, g, b)
  }

  return palette
}

export const THEME_COLORS: Record<string, ThemeColorConfig> = {
  red: {
    primary: '#DC2626', // Rouge vif
    secondary: '#EF4444',
    accent: '#F87171',
    name: 'Rouge',
    description: 'Nourriture, technologies, transport, achat compulsif, mode, loisirs, sport, marketing, publicité, services d\'urgence, santé'
  },
  green: {
    primary: '#16A34A', // Vert nature
    secondary: '#22C55E',
    accent: '#4ADE80',
    name: 'Vert',
    description: 'Bien-être, santé, plein air, environnement, agriculture, produits biologiques'
  },
  yellow: {
    primary: '#EAB308', // Jaune soleil
    secondary: '#FACC15',
    accent: '#FDE047',
    name: 'Jaune',
    description: 'Enfance, alimentaire, maison, décoration, tourisme, énergie solaire, électricité'
  },
  purple: {
    primary: '#9333EA', // Violet luxe
    secondary: '#A855F7',
    accent: '#C084FC',
    name: 'Violet',
    description: 'Luxe, beauté, astrologie, massages, yoga, spiritualité'
  },
  orange: {
    primary: '#EA580C', // Orange énergique
    secondary: '#F97316',
    accent: '#FB923C',
    name: 'Orange',
    description: 'Technologiques, gadgets, divertissement, jeunesse, sport, création'
  },
  pink: {
    primary: '#DB2777', // Rose tendre
    secondary: '#EC4899',
    accent: '#F472B6',
    name: 'Rose',
    description: 'Public féminin, enfance, culture'
  },
  brown: {
    primary: '#92400E', // Marron naturel
    secondary: '#A16207',
    accent: '#CA8A04',
    name: 'Marron',
    description: 'Entreprises artisanales, produits naturels ou rustiques, culture, luxe, secteur du chocolat'
  },
  black: {
    primary: '#0A0A0A', // Noir élégant
    secondary: '#1A1A1A',
    accent: '#2B2B2B',
    name: 'Noir',
    description: 'Luxe, technologie, automobile, haut de gamme, cinéma, art, photo'
  },
  white: {
    primary: '#2563EB', // Bleu technologie vif et professionnel
    secondary: '#1E40AF', // Bleu foncé pour le contraste
    accent: '#3B82F6', // Bleu moyen pour les accents
    name: 'Blanc',
    description: 'Entreprises sanitaires, santé, charité, mode, actualités, technologies, informatique'
  },
  blue: {
    primary: '#2563EB', // Bleu high-tech professionnel
    secondary: '#1E40AF', // Bleu foncé pour le contraste
    accent: '#3B82F6', // Bleu moyen pour les accents
    name: 'Bleu',
    description: 'Santé, transactions monétaires, high-tech, transport, voyage, juridique et réseaux sociaux'
  }
}

/**
 * Détermine la couleur de thème recommandée pour un type d'application
 */
export const getThemeForAppType = (appType: 'education' | 'technology' | 'health' | 'luxury' | 'entertainment' | 'sports' | 'culture' | 'business'): ThemeColorConfig => {
  const themeMap: Record<string, keyof typeof THEME_COLORS> = {
    education: 'blue',       // Éducation = Bleu (high-tech, technologies)
    technology: 'blue',      // Technologie = Bleu (high-tech, réseaux sociaux)
    health: 'green',         // Santé = Vert (bien-être, santé)
    luxury: 'black',         // Luxe = Noir (luxe, haut de gamme)
    entertainment: 'orange',  // Divertissement = Orange (divertissement, jeunesse)
    sports: 'red',           // Sport = Rouge (sport, loisirs)
    culture: 'pink',         // Culture = Rose (culture)
    business: 'blue'         // Business = Bleu (high-tech, transactions monétaires)
  }
  
  const colorKey = themeMap[appType] || 'blue'
  return THEME_COLORS[colorKey]
}

/**
 * Récupère la configuration de couleur depuis localStorage ou utilise la valeur par défaut
 * Par défaut, utilise le thème bleu pour Kaïrox (plateforme éducative high-tech)
 */
export const getThemeConfig = (): ThemeColorConfig => {
  try {
    const stored = localStorage.getItem('kairos-theme-color')
    if (stored) {
      const parsed = JSON.parse(stored)
      // Si l'ancien thème "white" est utilisé, le remplacer par "blue"
      if (parsed && parsed.color === 'white') {
        setThemeColor('blue')
        return THEME_COLORS.blue
      }
      if (parsed && THEME_COLORS[parsed.color]) {
        return THEME_COLORS[parsed.color]
      }
    }
  } catch (e) {
    console.error('Erreur lors de la récupération du thème:', e)
  }
  
  // Par défaut, utiliser Bleu pour Kaïrox (plateforme éducative high-tech)
  // Bleu = high-tech, technologies, réseaux sociaux (parfait pour une plateforme d'apprentissage immersive avec IA)
  const defaultTheme = THEME_COLORS.blue
  // Toujours sauvegarder le thème bleu par défaut
  setThemeColor('blue')
  return defaultTheme
}

/**
 * Définit la couleur de thème
 */
export const setThemeColor = (colorKey: keyof typeof THEME_COLORS): void => {
  try {
    localStorage.setItem('kairos-theme-color', JSON.stringify({
      color: colorKey,
      appliedAt: new Date().toISOString()
    }))
  } catch (e) {
    console.error('Erreur lors de la sauvegarde du thème:', e)
  }
}

