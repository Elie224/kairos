/**
 * Gestionnaire d'erreurs centralisé
 * Fournit des fonctions utilitaires pour gérer et logger les erreurs de manière cohérente
 */

import logger from './logger'

/**
 * Interface pour les erreurs typées
 */
export interface AppError extends Error {
  code?: string
  statusCode?: number
  context?: string
  userMessage?: string
}

/**
 * Crée une erreur typée avec contexte
 */
export function createAppError(
  message: string,
  code?: string,
  statusCode?: number,
  context?: string
): AppError {
  const error = new Error(message) as AppError
  error.code = code
  error.statusCode = statusCode
  error.context = context
  error.name = 'AppError'
  return error
}

/**
 * Gère une erreur en la loggant et en retournant un message utilisateur
 */
export function handleError(
  error: unknown,
  context?: string,
  userMessage?: string
): string {
  const errorMessage = error instanceof Error 
    ? error.message 
    : String(error)
  
  const finalContext = context || 'App'
  const finalUserMessage = userMessage || 'Une erreur est survenue. Veuillez réessayer.'

  // Logger l'erreur
  logger.error(
    `Erreur dans ${finalContext}: ${errorMessage}`,
    error,
    finalContext
  )

  return finalUserMessage
}

/**
 * Wrapper pour les fonctions async qui gère automatiquement les erreurs
 */
export function withErrorHandling<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  context?: string,
  userMessage?: string
): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await fn(...args)
    } catch (error) {
      const message = handleError(error, context, userMessage)
      throw new Error(message)
    }
  }) as T
}

/**
 * Gère les erreurs de mutation React Query
 */
export function handleMutationError(error: unknown): void {
  handleError(error, 'ReactQuery', 'Une erreur est survenue lors de l\'opération.')
}

/**
 * Gère les erreurs de requête API
 */
export function handleApiError(error: unknown, endpoint?: string): string {
  const context = endpoint ? `API:${endpoint}` : 'API'
  return handleError(
    error,
    context,
    'Une erreur est survenue lors de la communication avec le serveur.'
  )
}

/**
 * Gère les erreurs de parsing/validation
 */
export function handleValidationError(error: unknown, field?: string): string {
  const context = field ? `Validation:${field}` : 'Validation'
  return handleError(
    error,
    context,
    'Les données saisies sont invalides. Veuillez vérifier et réessayer.'
  )
}
