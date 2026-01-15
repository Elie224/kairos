/**
 * Système de logging centralisé pour remplacer console.log/error/warn
 * Supporte différents niveaux de log et peut être intégré avec Sentry, LogRocket, etc.
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

interface LogEntry {
  level: LogLevel
  message: string
  data?: any
  timestamp: string
  context?: string
  userAgent?: string
  url?: string
}

class Logger {
  private logLevel: LogLevel
  private logs: LogEntry[] = []
  private maxLogs = 100 // Garder seulement les 100 derniers logs en mémoire

  constructor() {
    // En production, ne logger que WARN et ERROR
    // En développement, logger tout
    this.logLevel = import.meta.env.PROD ? LogLevel.WARN : LogLevel.DEBUG
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= this.logLevel
  }

  private formatMessage(level: LogLevel, message: string, data?: any, context?: string): string {
    const prefix = {
      [LogLevel.DEBUG]: '🔍 [DEBUG]',
      [LogLevel.INFO]: 'ℹ️ [INFO]',
      [LogLevel.WARN]: '⚠️ [WARN]',
      [LogLevel.ERROR]: '❌ [ERROR]',
    }[level]

    const contextStr = context ? `[${context}]` : ''
    return `${prefix} ${contextStr} ${message}`
  }

  private addLog(level: LogLevel, message: string, data?: any, context?: string): void {
    if (!this.shouldLog(level)) return

    const logEntry: LogEntry = {
      level,
      message,
      data,
      timestamp: new Date().toISOString(),
      context,
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
      url: typeof window !== 'undefined' ? window.location.href : undefined,
    }

    // Ajouter au tableau de logs (limité à maxLogs)
    this.logs.push(logEntry)
    if (this.logs.length > this.maxLogs) {
      this.logs.shift()
    }

    // Logger dans la console selon le niveau
    const formattedMessage = this.formatMessage(level, message, data, context)
    
    switch (level) {
      case LogLevel.DEBUG:
        if (import.meta.env.DEV) {
          console.debug(formattedMessage, data || '')
        }
        break
      case LogLevel.INFO:
        if (import.meta.env.DEV) {
          console.info(formattedMessage, data || '')
        }
        break
      case LogLevel.WARN:
        console.warn(formattedMessage, data || '')
        break
      case LogLevel.ERROR:
        console.error(formattedMessage, data || '')
        // En production, envoyer à un service de logging externe
        if (import.meta.env.PROD) {
          this.sendToExternalService(logEntry)
        }
        break
    }
  }

  private sendToExternalService(logEntry: LogEntry): void {
    // TODO: Intégrer avec Sentry, LogRocket, etc.
    // Pour l'instant, juste stocker en mémoire
    // En production, vous pouvez envoyer à un endpoint backend
    try {
      // Exemple d'intégration future :
      // if (window.Sentry) {
      //   window.Sentry.captureException(new Error(logEntry.message), {
      //     extra: logEntry.data,
      //     tags: { context: logEntry.context },
      //   })
      // }
    } catch (e) {
      // Ignorer les erreurs de logging externe
    }
  }

  debug(message: string, data?: any, context?: string): void {
    this.addLog(LogLevel.DEBUG, message, data, context)
  }

  info(message: string, data?: any, context?: string): void {
    this.addLog(LogLevel.INFO, message, data, context)
  }

  warn(message: string, data?: any, context?: string): void {
    this.addLog(LogLevel.WARN, message, data, context)
  }

  error(message: string, error?: any, context?: string): void {
    const errorData = error instanceof Error 
      ? { message: error.message, stack: error.stack, ...error }
      : error
    this.addLog(LogLevel.ERROR, message, errorData, context)
  }

  // Méthode pour récupérer les logs (utile pour le debugging)
  getLogs(level?: LogLevel): LogEntry[] {
    if (level !== undefined) {
      return this.logs.filter(log => log.level === level)
    }
    return [...this.logs]
  }

  // Méthode pour vider les logs
  clearLogs(): void {
    this.logs = []
  }
}

// Instance singleton
export const logger = new Logger()

// Export par défaut pour faciliter l'utilisation
export default logger
