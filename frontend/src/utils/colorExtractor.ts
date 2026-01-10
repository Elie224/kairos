/**
 * Utilitaire pour extraire les couleurs dominantes d'une image
 */

export interface ColorPalette {
  dominant: string
  secondary: string[]
  palette: Record<number, string> // 50-900
}

/**
 * Extrait les couleurs dominantes d'une image via Canvas
 */
export const extractColorsFromImage = async (imageUrl: string): Promise<ColorPalette> => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    
    img.onload = () => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      
      if (!ctx) {
        reject(new Error('Impossible de créer le contexte canvas'))
        return
      }

      canvas.width = img.width
      canvas.height = img.height
      ctx.drawImage(img, 0, 0)

      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const pixels = imageData.data
      
      // Compter les couleurs
      const colorCount: Record<string, number> = {}
      const step = 4 // Analyser tous les 4 pixels pour la performance
      
      for (let i = 0; i < pixels.length; i += step * 4) {
        const r = pixels[i]
        const g = pixels[i + 1]
        const b = pixels[i + 2]
        const a = pixels[i + 3]
        
        // Ignorer les pixels transparents
        if (a < 128) continue
        
        // Quantifier les couleurs (grouper les couleurs similaires)
        const quantizedR = Math.floor(r / 32) * 32
        const quantizedG = Math.floor(g / 32) * 32
        const quantizedB = Math.floor(b / 32) * 32
        
        const colorKey = `${quantizedR},${quantizedG},${quantizedB}`
        colorCount[colorKey] = (colorCount[colorKey] || 0) + 1
      }

      // Trier les couleurs par fréquence
      const sortedColors = Object.entries(colorCount)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 10) // Top 10 couleurs

      // Convertir en hex
      const rgbToHex = (r: number, g: number, b: number) => {
        return '#' + [r, g, b].map(x => {
          const hex = x.toString(16)
          return hex.length === 1 ? '0' + hex : hex
        }).join('')
      }

      const dominantColor = sortedColors[0]?.[0].split(',').map(Number)
      const dominantHex = dominantColor 
        ? rgbToHex(dominantColor[0], dominantColor[1], dominantColor[2])
        : '#4A90E2'

      const secondaryColors = sortedColors.slice(1, 4).map(([rgb]) => {
        const [r, g, b] = rgb.split(',').map(Number)
        return rgbToHex(r, g, b)
      })

      // Générer la palette
      const palette = generatePaletteFromColor(dominantHex)

      resolve({
        dominant: dominantHex,
        secondary: secondaryColors,
        palette
      })
    }

    img.onerror = () => {
      reject(new Error('Erreur lors du chargement de l\'image'))
    }

    img.src = imageUrl
  })
}

/**
 * Génère une palette Chakra UI (50-900) à partir d'une couleur de base
 */
const generatePaletteFromColor = (baseColor: string): Record<number, string> => {
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
  const palette: Record<number, string> = {}

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














