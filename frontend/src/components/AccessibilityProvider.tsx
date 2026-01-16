/**
 * Provider pour améliorer l'accessibilité globale de l'application
 */
import { useEffect, ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { announceToScreenReader, prefersReducedMotion } from '../utils/accessibility'

interface AccessibilityProviderProps {
  children: ReactNode
}

export const AccessibilityProvider = ({ children }: AccessibilityProviderProps) => {
  const location = useLocation()

  // Annoncer les changements de page aux lecteurs d'écran
  useEffect(() => {
    // Attendre que le DOM soit prêt
    const timeout = setTimeout(() => {
      const pageTitle = document.title || 'Kaïros'
      announceToScreenReader(`Page chargée: ${pageTitle}`, 'polite')
    }, 100)
    return () => clearTimeout(timeout)
  }, [location.pathname])

  // Appliquer les préférences de mouvement réduit
  useEffect(() => {
    if (prefersReducedMotion()) {
      document.documentElement.style.setProperty('--animation-duration', '0.01ms')
      document.documentElement.style.setProperty('--transition-duration', '0.01ms')
    } else {
      document.documentElement.style.removeProperty('--animation-duration')
      document.documentElement.style.removeProperty('--transition-duration')
    }
  }, [])

  // Gérer le focus lors de la navigation
  useEffect(() => {
    // Focus sur le contenu principal après navigation
    const mainContent = document.querySelector('main') || document.querySelector('[role="main"]')
    if (mainContent) {
      // Ne pas forcer le focus si l'utilisateur est en train de naviguer au clavier
      const handleFocus = () => {
        if (document.activeElement === document.body) {
          ;(mainContent as HTMLElement).focus()
        }
      }
      // Petit délai pour permettre au navigateur de terminer la navigation
      const timeout = setTimeout(handleFocus, 100)
      return () => clearTimeout(timeout)
    }
  }, [location.pathname])

  // Ajouter un attribut lang si nécessaire
  useEffect(() => {
    document.documentElement.lang = 'fr'
  }, [])

  return <>{children}</>
}
