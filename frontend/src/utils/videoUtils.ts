/**
 * Utilitaires pour la détection et le traitement des liens vidéo
 */

export interface VideoPlatform {
  name: string
  icon: string
  color: string
  embedUrl?: (url: string) => string
  thumbnailUrl?: (url: string) => string
}

export const VIDEO_PLATFORMS: Record<string, VideoPlatform> = {
  youtube: {
    name: 'YouTube',
    icon: '▶️',
    color: 'red',
    embedUrl: (url: string) => {
      // Extraire l'ID de la vidéo YouTube
      const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
        /youtube\.com\/watch\?.*v=([^&\n?#]+)/
      ]
      for (const pattern of patterns) {
        const match = url.match(pattern)
        if (match && match[1]) {
          return `https://www.youtube.com/embed/${match[1]}`
        }
      }
      return url
    },
    thumbnailUrl: (url: string) => {
      const patterns = [
        /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
        /youtube\.com\/watch\?.*v=([^&\n?#]+)/
      ]
      for (const pattern of patterns) {
        const match = url.match(pattern)
        if (match && match[1]) {
          return `https://img.youtube.com/vi/${match[1]}/maxresdefault.jpg`
        }
      }
      return ''
    }
  },
  openclassrooms: {
    name: 'OpenClassrooms',
    icon: '📚',
    color: 'purple',
    thumbnailUrl: (url: string) => {
      // OpenClassrooms ne fournit pas d'API publique pour les miniatures
      // On retourne une URL générique ou on peut extraire depuis l'URL si possible
      return ''
    }
  },
  udemy: {
    name: 'Udemy',
    icon: '🎓',
    color: 'blue'
  },
  coursera: {
    name: 'Coursera',
    icon: '🎯',
    color: 'orange'
  },
  edx: {
    name: 'edX',
    icon: '📖',
    color: 'green'
  },
  khanacademy: {
    name: 'Khan Academy',
    icon: '🏛️',
    color: 'teal'
  }
}

/**
 * Détecte la plateforme vidéo à partir d'une URL
 */
export function detectVideoPlatform(url: string): VideoPlatform | null {
  const lowerUrl = url.toLowerCase()
  
  if (lowerUrl.includes('youtube.com') || lowerUrl.includes('youtu.be')) {
    return VIDEO_PLATFORMS.youtube
  }
  if (lowerUrl.includes('openclassrooms.com') || lowerUrl.includes('openclassroom.org')) {
    return VIDEO_PLATFORMS.openclassrooms
  }
  if (lowerUrl.includes('udemy.com')) {
    return VIDEO_PLATFORMS.udemy
  }
  if (lowerUrl.includes('coursera.org')) {
    return VIDEO_PLATFORMS.coursera
  }
  if (lowerUrl.includes('edx.org')) {
    return VIDEO_PLATFORMS.edx
  }
  if (lowerUrl.includes('khanacademy.org') || lowerUrl.includes('khan-academy')) {
    return VIDEO_PLATFORMS.khanacademy
  }
  
  return null
}

/**
 * Extrait l'ID d'une vidéo YouTube
 */
export function extractYouTubeVideoId(url: string): string | null {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
    /youtube\.com\/watch\?.*v=([^&\n?#]+)/
  ]
  
  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match && match[1]) {
      return match[1]
    }
  }
  
  return null
}

/**
 * Vérifie si une URL est un lien vidéo valide
 */
export function isValidVideoUrl(url: string): boolean {
  return detectVideoPlatform(url) !== null
}
