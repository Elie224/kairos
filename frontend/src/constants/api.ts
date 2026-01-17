/**
 * Constantes API - Configuration des timeouts et limites
 * Centralise les timeouts pour faciliter la maintenance
 */

/**
 * Timeouts recommandés selon le type de requête
 * Ces valeurs prennent en compte les cold starts des serveurs hébergés (Render, etc.)
 */
export const API_TIMEOUTS = {
  // Timeout par défaut (utilisé dans api.ts)
  DEFAULT: 30000, // 30 secondes - suffisant pour la plupart des requêtes

  // Authentification (peut être très lent avec cold start Render)
  AUTH: 60000, // 60 secondes pour login/register/checkAuth (cold start Render peut prendre 30-45s)

  // Requêtes simples (stats, count, etc.)
  SIMPLE: 10000, // 10 secondes pour les requêtes GET simples

  // Requêtes avec traitement (modules, progress, etc.)
  STANDARD: 15000, // 15 secondes pour les requêtes avec traitement modéré

  // Génération IA (peut prendre du temps)
  AI_GENERATION: 60000, // 60 secondes pour la génération de contenu IA

  // Upload de fichiers
  FILE_UPLOAD: 120000, // 2 minutes pour les uploads de gros fichiers

  // Streaming (chat, visualisations)
  STREAMING: 300000, // 5 minutes pour le streaming
} as const

/**
 * Configuration des retries pour React Query
 */
export const QUERY_CONFIG = {
  // Nombre de tentatives en cas d'échec
  RETRY: 2,

  // Délai entre les tentatives (backoff exponentiel)
  RETRY_DELAY: (attemptIndex: number) => Math.min(2000 * 2 ** attemptIndex, 10000),

  // Temps de cache (données considérées comme fraîches)
  STALE_TIME: {
    SHORT: 2 * 60 * 1000, // 2 minutes
    MEDIUM: 5 * 60 * 1000, // 5 minutes
    LONG: 10 * 60 * 1000, // 10 minutes
    VERY_LONG: 30 * 60 * 1000, // 30 minutes
  },

  // Temps de conservation en cache
  CACHE_TIME: {
    SHORT: 5 * 60 * 1000, // 5 minutes
    MEDIUM: 10 * 60 * 1000, // 10 minutes
    LONG: 30 * 60 * 1000, // 30 minutes
    VERY_LONG: 60 * 60 * 1000, // 1 heure
  },
} as const
