import axios, { AxiosError } from 'axios'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // Timeout de 30 secondes par défaut (augmenté pour les requêtes longues comme la génération de contenu)
})

// Timeout pour les uploads de fichiers (5 minutes pour supporter jusqu'à 100MB)
const FILE_UPLOAD_TIMEOUT = 5 * 60 * 1000 // 5 minutes

// Récupérer le token depuis le localStorage si disponible
const initializeAuth = () => {
  const authData = localStorage.getItem('kairos-auth')
  if (authData) {
    try {
      const parsed = JSON.parse(authData)
      if (parsed.state?.token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${parsed.state.token}`
      }
    } catch (e) {
      // Ignorer les erreurs de parsing
    }
  }
}

// Initialiser l'auth au chargement
initializeAuth()

// Intercepteur pour gérer les requêtes et supprimer Content-Type pour FormData
api.interceptors.request.use(
  (config) => {
    // Si la donnée est une instance FormData, supprimer le Content-Type
    // pour laisser le navigateur définir automatiquement multipart/form-data avec boundary
    if (config.data instanceof FormData) {
      // Supprimer le Content-Type de toutes les façons possibles
      if (config.headers) {
        delete config.headers['Content-Type']
        delete config.headers['content-type']
        // S'assurer que les headers sont bien configurés
        if (config.headers.common) {
          delete config.headers.common['Content-Type']
        }
      }
      // Augmenter le timeout pour les uploads de fichiers
      if (!config.timeout || config.timeout < FILE_UPLOAD_TIMEOUT) {
        config.timeout = FILE_UPLOAD_TIMEOUT
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any
    
    // Gérer les erreurs 401 (non autorisé)
    if (error.response?.status === 401) {
      // Déconnexion automatique si le token est invalide
      const { logout } = useAuthStore.getState()
      logout()
      // Rediriger vers la page de connexion (utiliser navigate si disponible)
      if (window.location.pathname !== '/login') {
        // Éviter de recharger toute la page si possible
        if (typeof window !== 'undefined' && window.history) {
          window.location.href = '/login'
        }
      }
      return Promise.reject(error)
    }
    
    // Gérer les erreurs réseau (pas de réponse du serveur)
    if (!error.response) {
      if (error.request) {
        // Vérifier si c'est une erreur d'annulation (requête annulée)
        if (axios.isCancel && axios.isCancel(error)) {
          // Requête annulée, ne pas logger d'erreur
          return Promise.reject(error)
        }
        
        // Vérifier si c'est une erreur de timeout
        if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
          // Timeout - ne pas logger pour les requêtes GET qui ont un retry automatique
          // Le retry va gérer silencieusement
          if (originalRequest && originalRequest.method?.toLowerCase() === 'get') {
            // Pour les GET, le retry va gérer, ne pas logger
            return Promise.reject(error)
          }
          // Pour les autres méthodes, logger seulement en développement
          if (process.env.NODE_ENV === 'development') {
            console.warn('Timeout de requête (peut être normal pour les opérations longues)')
          }
        } else {
          // Autre erreur réseau
          if (process.env.NODE_ENV === 'development') {
            console.error('Erreur réseau: Pas de réponse du serveur', error.message)
          }
        }
        
        // Optionnel: Retry pour les erreurs réseau temporaires (seulement pour les requêtes GET)
        if (originalRequest && !originalRequest._retry && originalRequest.method?.toLowerCase() === 'get') {
          originalRequest._retry = true
          // Retry une seule fois après 500ms (plus rapide)
          await new Promise(resolve => setTimeout(resolve, 500))
          return api(originalRequest)
        }
      }
      return Promise.reject(error)
    }
    
    // Gérer les erreurs 429 (rate limiting)
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after']
      const delay = retryAfter ? parseInt(retryAfter) * 1000 : 5000
      if (process.env.NODE_ENV === 'development') {
        console.warn(`Rate limit atteint. Nouvelle tentative dans ${delay}ms`)
      }
      
      if (originalRequest && !originalRequest._retry) {
        originalRequest._retry = true
        await new Promise(resolve => setTimeout(resolve, delay))
        return api(originalRequest)
      }
    }
    
    // Gérer les erreurs 503 (service indisponible)
    if (error.response?.status === 503) {
      if (originalRequest && !originalRequest._retry) {
        originalRequest._retry = true
        // Retry après 3 secondes pour les erreurs 503
        await new Promise(resolve => setTimeout(resolve, 3000))
        return api(originalRequest)
      }
    }
    
    return Promise.reject(error)
  }
)

export default api

