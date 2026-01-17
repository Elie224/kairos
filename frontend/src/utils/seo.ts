/**
 * Utilitaires SEO pour gérer les méta descriptions dynamiques
 */
interface SEOData {
  title: string
  description: string
  keywords?: string
  image?: string
  url?: string
}

/**
 * Met à jour les balises meta SEO de la page
 */
export function updateSEO(data: SEOData): void {
  if (typeof document === 'undefined') return

  // Mettre à jour le titre
  document.title = data.title

  // Mettre à jour la meta description
  let metaDescription = document.querySelector('meta[name="description"]')
  if (!metaDescription) {
    metaDescription = document.createElement('meta')
    metaDescription.setAttribute('name', 'description')
    document.head.appendChild(metaDescription)
  }
  metaDescription.setAttribute('content', data.description)

  // Mettre à jour les keywords si fournis
  if (data.keywords) {
    let metaKeywords = document.querySelector('meta[name="keywords"]')
    if (!metaKeywords) {
      metaKeywords = document.createElement('meta')
      metaKeywords.setAttribute('name', 'keywords')
      document.head.appendChild(metaKeywords)
    }
    metaKeywords.setAttribute('content', data.keywords)
  }

  // Mettre à jour Open Graph
  const ogTitle = document.querySelector('meta[property="og:title"]')
  if (ogTitle) ogTitle.setAttribute('content', data.title)

  const ogDescription = document.querySelector('meta[property="og:description"]')
  if (ogDescription) ogDescription.setAttribute('content', data.description)

  if (data.url) {
    const ogUrl = document.querySelector('meta[property="og:url"]')
    if (ogUrl) ogUrl.setAttribute('content', data.url)
  }

  if (data.image) {
    const ogImage = document.querySelector('meta[property="og:image"]')
    if (ogImage) ogImage.setAttribute('content', data.image)
  }

  // Mettre à jour Twitter Card
  const twitterTitle = document.querySelector('meta[property="twitter:title"]')
  if (twitterTitle) twitterTitle.setAttribute('content', data.title)

  const twitterDescription = document.querySelector('meta[property="twitter:description"]')
  if (twitterDescription) twitterDescription.setAttribute('content', data.description)

  if (data.image) {
    const twitterImage = document.querySelector('meta[property="twitter:image"]')
    if (twitterImage) twitterImage.setAttribute('content', data.image)
  }
}

/**
 * Réinitialise les balises SEO aux valeurs par défaut
 */
export function resetSEO(): void {
  updateSEO({
    title: 'Kaïrox - Apprentissage Immersif avec IA | Visualisations 3D & Gamification',
    description: 'Kaïrox est une plateforme d\'apprentissage intelligente avec visualisations 3D interactives, tutorat IA et gamification adaptative pour collège, lycée et université.',
    keywords: 'apprentissage, éducation, IA, visualisations 3D, gamification, tutorat intelligent',
    url: 'https://kairos-frontend-hjg9.onrender.com/',
    image: 'https://kairos-frontend-hjg9.onrender.com/background.jfif',
  })
}
