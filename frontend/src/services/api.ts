/**
 * Configuration et instance Axios pour les appels API
 * 
 * Gère :
 * - Configuration de base URL (dev/prod)
 * - Authentification automatique via tokens
 * - Intercepteurs pour erreurs et retry
 * - Gestion des timeouts adaptatifs
 * 
 * @module services/api
 */
import axios, { AxiosError } from 'axios'

/**
 * Détermine l'URL de base de l'API selon l'environnement
 * 
 * - En développement : utilise le proxy Vite (/api) pour éviter CORS
 * - En production : utilise VITE_API_URL ou le backend Render par défaut
 * 
 * @returns {string} URL de base de l'API
 */
const getBaseURL = (): string => {
  // En développement local (npm run dev), utiliser le proxy Vite qui contourne CORS
  // Le proxy Vite redirige /api vers le backend Render configuré dans vite.config.ts
  if (import.meta.env.DEV) {
    return '/api'  // Proxy Vite redirige vers backend Render via vite.config.ts
  }
  
  // En production (build), utiliser VITE_API_URL si définie
  // Si VITE_API_URL n'est pas définie, utiliser le backend Render par défaut
  if (import.meta.env.PROD) {
    return import.meta.env.VITE_API_URL || 'https://kairos-0aoy.onrender.com/api'
  }
  
  // Fallback
  return '/api'
}

import { API_TIMEOUTS } from '../constants/api'

/**
 * Instance Axios configurée pour l'application Kaïrox
 * 
 * Configuration :
 * - baseURL : Déterminé automatiquement selon l'environnement
 * - timeout : 30 secondes par défaut (configurable par requête)
 * - headers : Content-Type application/json par défaut
 */
const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: API_TIMEOUTS.STANDARD, // 15 secondes par défaut (timeout standard)
})

/**
 * Timeout spécifique pour les uploads de fichiers (2 minutes)
 * Les fichiers peuvent être volumineux et nécessiter plus de temps
 */
const FILE_UPLOAD_TIMEOUT = API_TIMEOUTS.FILE_UPLOAD // 120 secondes pour les uploads

/**
 * Initialise l'authentification depuis le localStorage
 * 
 * Récupère le token stocké et l'ajoute aux headers par défaut de Axios
 * Appelé une seule fois au chargement du module
 */
const initializeAuth = (): void => {
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

initializeAuth()

/**
 * Intercepteur de requête Axios
 * 
 * Gère :
 * - Suppression automatique de Content-Type pour FormData (laisser le navigateur le définir)
 * - Application du timeout FILE_UPLOAD_TIMEOUT pour les uploads
 * - Préservation de Content-Type pour URLSearchParams
 */
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
    // Pour les requêtes avec URLSearchParams (comme login), préserver le Content-Type
    if (config.data instanceof URLSearchParams) {
      // Le Content-Type application/x-www-form-urlencoded sera défini dans les headers
      // Ne pas le supprimer
      if (config.headers && !config.headers['Content-Type']) {
        config.headers['Content-Type'] = 'application/x-www-form-urlencoded'
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

/**
 * Intercepteur de réponse Axios pour la gestion des erreurs
 * 
 * Gère :
 * - Erreurs 401 (non autorisé) : déconnexion et redirection vers login
 * - Erreurs réseau/timeout : retry automatique pour les requêtes GET
 * - Erreurs 429 (rate limiting) : retry après délai défini dans Retry-After
 * - Erreurs 503 (service indisponible) : retry après 3 secondes
 * 
 * @param {any} response - Réponse réussie (passée telle quelle)
 * @param {AxiosError} error - Erreur à traiter
 * @returns {Promise} Réponse ou rejet avec erreur gérée
 */
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any
    
    // Gérer les erreurs 401 (non autorisé)
    if (error.response?.status === 401) {
      // Supprimer le token invalide
      delete api.defaults.headers.common['Authorization']
      localStorage.removeItem('kairos-auth')
      
      // Rediriger vers login si on n'y est pas déjà
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
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
          if (import.meta.env.DEV) {
            // Timeout géré silencieusement (retry automatique)
          }
        } else {
          // Autre erreur réseau
          if (import.meta.env.DEV) {
            // Erreur réseau gérée par retry automatique
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
      if (import.meta.env.DEV) {
        // Rate limit géré automatiquement avec retry
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

