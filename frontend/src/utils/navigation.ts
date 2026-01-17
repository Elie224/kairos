/**
 * Utilitaires pour améliorer la navigation
 * Prefetch et optimisations pour une navigation plus fluide
 */

/**
 * Prefetch une route pour accélérer la navigation
 */
export function prefetchRoute(path: string): void {
  // Précharger le chunk JavaScript de la route
  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    requestIdleCallback(() => {
      // Les routes lazy-loaded seront préchargées automatiquement par React Router
      // On peut aussi précharger manuellement si nécessaire
      const link = document.createElement('link')
      link.rel = 'prefetch'
      link.href = path
      document.head.appendChild(link)
    })
  }
}

/**
 * Navigation optimisée avec transition
 */
export function navigateWithTransition(
  navigate: (path: string) => void,
  path: string,
  startTransition?: (callback: () => void) => void
): void {
  if (startTransition) {
    startTransition(() => {
      navigate(path)
    })
  } else {
    navigate(path)
  }
}

/**
 * Précharger les routes principales au démarrage
 */
export function prefetchMainRoutes(): void {
  if (typeof window === 'undefined') return

  const mainRoutes = [
    '/modules',
    '/dashboard',
    '/exams',
    '/gamification',
    '/visualizations',
    '/profile',
  ]

  // Précharger après un délai pour ne pas bloquer le chargement initial
  setTimeout(() => {
    mainRoutes.forEach(route => {
      prefetchRoute(route)
    })
  }, 2000)
}
