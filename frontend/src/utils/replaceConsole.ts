/**
 * Script utilitaire pour remplacer console.log/error/warn par logger
 * À exécuter manuellement ou via un script de migration
 */

// Ce fichier sert de référence pour le remplacement manuel
// Les remplacements ont été faits dans les fichiers critiques

// Pattern de remplacement :
// console.log(...) -> logger.debug(...) ou logger.info(...)
// console.error(...) -> logger.error(...)
// console.warn(...) -> logger.warn(...)

// Import du logger :
// import logger from '../utils/logger'
// ou
// import { logger } from '../utils/logger'

// Exemples :
// console.log('Message', data) -> logger.debug('Message', data, 'Context')
// console.error('Error', error) -> logger.error('Error', error, 'Context')
// console.warn('Warning', data) -> logger.warn('Warning', data, 'Context')
