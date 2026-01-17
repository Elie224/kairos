/**
 * Hook pour gérer le SEO des pages
 */
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { updateSEO, resetSEO } from '../utils/seo'

interface UseSEOOptions {
  title: string
  description: string
  keywords?: string
  image?: string
}

export function useSEO(options: UseSEOOptions) {
  const location = useLocation()

  useEffect(() => {
    const baseUrl = 'https://kairos-frontend-hjg9.onrender.com'
    updateSEO({
      title: options.title,
      description: options.description,
      keywords: options.keywords,
      image: options.image || `${baseUrl}/background.jfif`,
      url: `${baseUrl}${location.pathname}`,
    })

    // Réinitialiser au démontage
    return () => {
      resetSEO()
    }
  }, [location.pathname, options.title, options.description, options.keywords, options.image])
}
