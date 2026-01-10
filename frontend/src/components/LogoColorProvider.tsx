import { useEffect, useState } from 'react'
import { useLogoColors } from '../hooks/useLogoColors'

/**
 * Composant qui extrait les couleurs du logo et les applique au thème
 * Les couleurs sont stockées dans localStorage pour être réutilisées
 */
export const LogoColorProvider = ({ children }: { children: React.ReactNode }) => {
  const { dominant, secondary, palette, isLoading } = useLogoColors()
  const [colorsApplied, setColorsApplied] = useState(false)

  useEffect(() => {
    if (!isLoading && dominant && !colorsApplied) {
      // Stocker les couleurs dans localStorage
      const logoColors = {
        dominant,
        secondary,
        palette,
        extractedAt: new Date().toISOString()
      }
      
      localStorage.setItem('kairos-logo-colors', JSON.stringify(logoColors))
      
      // Appliquer les couleurs via CSS variables pour utilisation dynamique
      const root = document.documentElement
      if (palette && Object.keys(palette).length > 0) {
        Object.entries(palette).forEach(([shade, color]) => {
          root.style.setProperty(`--logo-color-${shade}`, color)
        })
      }
      
      root.style.setProperty('--logo-primary', dominant || '#2563EB')
      root.style.setProperty('--logo-secondary', secondary[0] || '#1E40AF')
      root.style.setProperty('--logo-accent', secondary[1] || '#3B82F6')
      
      // Forcer le rechargement de la page pour appliquer le nouveau thème
      // (le thème est généré au chargement, donc on doit recharger)
      if (!localStorage.getItem('kairos-theme-applied')) {
        localStorage.setItem('kairos-theme-applied', 'true')
        // Ne pas recharger automatiquement - laisser l'utilisateur voir le changement
        // window.location.reload()
      }
      
      setColorsApplied(true)
    }
  }, [dominant, secondary, palette, isLoading, colorsApplied])

  return <>{children}</>
}

/**
 * Récupère les couleurs du logo depuis localStorage
 */
export const getLogoColors = () => {
  try {
    const stored = localStorage.getItem('kairos-logo-colors')
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (e) {
    console.error('Erreur lors de la récupération des couleurs:', e)
  }
  return null
}

