import { useState, useEffect } from 'react'
import { extractColorsFromImage } from '../utils/colorExtractor'
import logoKairos from '../logo_kairos.jpeg'

export interface LogoColors {
  dominant: string
  secondary: string[]
  palette: Record<number, string>
  isLoading: boolean
  error: Error | null
}

/**
 * Hook pour extraire les couleurs du logo et les utiliser dans l'application
 */
export const useLogoColors = (): LogoColors => {
  const [colors, setColors] = useState<Omit<LogoColors, 'isLoading' | 'error'>>({
    dominant: '#4A90E2',
    secondary: [],
    palette: {}
  })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const loadColors = async () => {
      try {
        setIsLoading(true)
        const extracted = await extractColorsFromImage(logoKairos)
        setColors(extracted)
        setError(null)
      } catch (err) {
        console.error('Erreur lors de l\'extraction des couleurs:', err)
        setError(err instanceof Error ? err : new Error('Erreur inconnue'))
        // Utiliser des couleurs par défaut en cas d'erreur
        setColors({
          dominant: '#4A90E2',
          secondary: ['#7B68EE', '#50C878'],
          palette: {}
        })
      } finally {
        setIsLoading(false)
      }
    }

    loadColors()
  }, [])

  return {
    ...colors,
    isLoading,
    error
  }
}














