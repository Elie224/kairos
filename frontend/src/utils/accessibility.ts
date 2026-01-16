/**
 * Utilitaires pour l'accessibilité
 */

/**
 * Gère la navigation au clavier dans une liste
 */
export function handleKeyboardNavigation(
  event: React.KeyboardEvent,
  currentIndex: number,
  totalItems: number,
  onSelect: (index: number) => void
) {
  let newIndex = currentIndex

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      newIndex = currentIndex < totalItems - 1 ? currentIndex + 1 : 0
      break
    case 'ArrowUp':
      event.preventDefault()
      newIndex = currentIndex > 0 ? currentIndex - 1 : totalItems - 1
      break
    case 'Home':
      event.preventDefault()
      newIndex = 0
      break
    case 'End':
      event.preventDefault()
      newIndex = totalItems - 1
      break
    case 'Enter':
    case ' ':
      event.preventDefault()
      onSelect(currentIndex)
      return
    default:
      return
  }

  onSelect(newIndex)
}

/**
 * Génère des attributs ARIA pour un composant interactif
 */
export function getAriaAttributes(options: {
  label?: string
  describedBy?: string
  expanded?: boolean
  controls?: string
  live?: 'polite' | 'assertive' | 'off'
  atomic?: boolean
}) {
  const attrs: Record<string, string | boolean> = {}

  if (options.label) {
    attrs['aria-label'] = options.label
  }

  if (options.describedBy) {
    attrs['aria-describedby'] = options.describedBy
  }

  if (options.expanded !== undefined) {
    attrs['aria-expanded'] = options.expanded
  }

  if (options.controls) {
    attrs['aria-controls'] = options.controls
  }

  if (options.live) {
    attrs['aria-live'] = options.live
    if (options.atomic !== undefined) {
      attrs['aria-atomic'] = options.atomic
    }
  }

  return attrs
}

/**
 * Gère le focus trap dans un modal/drawer
 */
export function trapFocus(element: HTMLElement | null) {
  if (!element) return

  const focusableElements = element.querySelectorAll(
    'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
  )

  const firstElement = focusableElements[0] as HTMLElement
  const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

  const handleTabKey = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return

    if (e.shiftKey) {
      if (document.activeElement === firstElement) {
        e.preventDefault()
        lastElement?.focus()
      }
    } else {
      if (document.activeElement === lastElement) {
        e.preventDefault()
        firstElement?.focus()
      }
    }
  }

  element.addEventListener('keydown', handleTabKey)
  firstElement?.focus()

  return () => {
    element.removeEventListener('keydown', handleTabKey)
  }
}

/**
 * Annonce une modification à un lecteur d'écran
 */
export function announceToScreenReader(message: string, priority: 'polite' | 'assertive' = 'polite') {
  // Vérifier que nous sommes dans un environnement navigateur
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return
  }

  // Attendre que document.body soit disponible
  if (!document.body) {
    // Si document.body n'est pas encore disponible, attendre un peu
    setTimeout(() => announceToScreenReader(message, priority), 100)
    return
  }

  try {
    const announcement = document.createElement('div')
    announcement.setAttribute('role', 'status')
    announcement.setAttribute('aria-live', priority)
    announcement.setAttribute('aria-atomic', 'true')
    announcement.className = 'sr-only'
    announcement.style.cssText = `
      position: absolute;
      left: -10000px;
      width: 1px;
      height: 1px;
      overflow: hidden;
    `
    announcement.textContent = message

    document.body.appendChild(announcement)

    setTimeout(() => {
      try {
        if (document.body && document.body.contains(announcement)) {
          document.body.removeChild(announcement)
        }
      } catch (error) {
        // Ignorer les erreurs de nettoyage
      }
    }, 1000)
  } catch (error) {
    // Ignorer les erreurs silencieusement en production
    if (import.meta.env.DEV) {
      console.warn('Erreur lors de l\'annonce au lecteur d\'écran:', error)
    }
  }
}

/**
 * Vérifie si l'utilisateur préfère les animations réduites
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Vérifie si l'utilisateur préfère le contraste élevé
 */
export function prefersHighContrast(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-contrast: high)').matches
}
