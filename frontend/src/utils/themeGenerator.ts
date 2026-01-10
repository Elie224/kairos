/**
 * Génère un thème Chakra UI basé sur les couleurs du logo
 */

import { extendTheme, ThemeConfig } from '@chakra-ui/react'

/**
 * Récupère les couleurs du logo depuis localStorage ou utilise des valeurs par défaut
 */
const getLogoColors = () => {
  try {
    const stored = localStorage.getItem('kairos-logo-colors')
    if (stored) {
      const parsed = JSON.parse(stored)
      return {
        dominant: parsed.dominant || '#4A90E2',
        secondary: parsed.secondary || ['#7B68EE', '#50C878'],
        palette: parsed.palette || {}
      }
    }
  } catch (e) {
    console.error('Erreur lors de la récupération des couleurs:', e)
  }
  
  // Couleurs par défaut (seront remplacées une fois le logo analysé)
  return {
    dominant: '#4A90E2',
    secondary: ['#7B68EE', '#50C878'],
    palette: {}
  }
}

/**
 * Génère une palette de couleurs Chakra UI à partir d'une couleur de base
 */
const generateColorPalette = (baseColor: string): Record<string, string> => {
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

/**
 * Génère le thème avec les couleurs du logo
 */
export const generateTheme = () => {
  const logoColors = getLogoColors()
  
  // Générer les palettes de couleurs
  const primaryPalette = logoColors.palette && Object.keys(logoColors.palette).length > 0
    ? logoColors.palette
    : generateColorPalette(logoColors.dominant)
  
  const secondaryPalette = logoColors.secondary.length > 0
    ? generateColorPalette(logoColors.secondary[0])
    : generateColorPalette('#7B68EE')

  return extendTheme({
    colors: {
      brand: primaryPalette,
      secondary: secondaryPalette,
      logo: {
        primary: logoColors.dominant,
        secondary: logoColors.secondary[0] || '#7B68EE',
        accent: logoColors.secondary[1] || '#50C878',
      },
      // Garder les couleurs existantes pour compatibilité
      dark: {
        50: '#1a1a1a',
        100: '#0f0f0f',
        200: '#0A0A0A',
        300: '#000000',
        400: '#000000',
        500: '#000000',
        600: '#000000',
        700: '#000000',
        800: '#000000',
        900: '#000000',
      },
      gradient: {
        primary: `linear-gradient(135deg, ${logoColors.dominant} 0%, ${primaryPalette[700] || logoColors.dominant} 100%)`,
        secondary: logoColors.secondary.length > 0
          ? `linear-gradient(135deg, ${logoColors.secondary[0]} 0%, ${secondaryPalette[700] || logoColors.secondary[0]} 100%)`
          : 'linear-gradient(135deg, #7B68EE 0%, #5A4FCF 100%)',
        accent: logoColors.secondary.length > 1
          ? `linear-gradient(135deg, ${logoColors.secondary[1]} 0%, ${generateColorPalette(logoColors.secondary[1])[700] || logoColors.secondary[1]} 100%)`
          : 'linear-gradient(135deg, #50C878 0%, #3FA05A 100%)',
      },
    },
    // ... reste du thème existant
  })
}














