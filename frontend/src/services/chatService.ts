/**
 * Service de chat avec streaming pour GPT-5.1 et GPT-5-mini
 * Optimisé pour 100k utilisateurs
 */
import api from './api'
import logger from '../utils/logger'

// Helper pour obtenir l'URL de base de l'API pour fetch (streaming SSE)
// fetch est nécessaire pour le streaming Server-Sent Events, axios ne supporte pas bien le streaming natif
const getApiBaseURL = () => {
  // En développement, utiliser le proxy Vite qui redirige vers le backend Render
  if (import.meta.env.DEV) {
    return '/api'  // Proxy Vite
  }
  // En production, utiliser VITE_API_URL si définie, sinon le backend Render par défaut
  // Si VITE_API_URL contient déjà /api à la fin, l'utiliser tel quel
  const viteApiUrl = import.meta.env.VITE_API_URL
  if (viteApiUrl) {
    return viteApiUrl.endsWith('/api') ? viteApiUrl : `${viteApiUrl}/api`
  }
  return 'https://kairos-0aoy.onrender.com/api'
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  modelUsed?: string
  files?: Array<{ name: string; type: 'image' | 'file'; preview: string }>
}

export interface ChatStreamOptions {
  moduleId?: string
  language?: string
  expertMode?: boolean
  researchMode?: boolean
  onChunk?: (chunk: string) => void
  onComplete?: (fullResponse: string) => void
  onError?: (error: Error) => void
}

class ChatService {
  private messageHistory: ChatMessage[] = []
  private currentStreamController: AbortController | null = null

  /**
   * Récupère le token d'authentification depuis le localStorage
   */
  private getAuthToken(): string {
    const authData = localStorage.getItem('kairos-auth')
    if (authData) {
      try {
        const parsed = JSON.parse(authData)
        if (parsed.state?.token) {
          return parsed.state.token
        }
      } catch (e) {
        // Ignorer les erreurs de parsing
      }
    }
    return ''
  }

  /**
   * Envoie un message avec streaming
   */
  async sendMessageStream(
    message: string,
    options: ChatStreamOptions = {}
  ): Promise<string> {
    // Annuler le stream précédent s'il existe
    if (this.currentStreamController) {
      this.currentStreamController.abort()
    }

    this.currentStreamController = new AbortController()
    
    // Préparer l'historique de conversation AVANT d'ajouter le message actuel
    // (pour éviter d'envoyer le message actuel deux fois)
    const conversationHistory = this.messageHistory
      .slice(-10) // Limiter aux 10 derniers messages
      .map(msg => ({
        role: msg.role,
        content: msg.content
      }))
    
    // Ajouter le message utilisateur à l'historique
    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date()
    }
    this.messageHistory.push(userMessage)

    let fullResponse = ''

    try {
      // Utiliser l'URL de base correcte (proxy Vite en dev, backend Render en prod)
      const baseURL = getApiBaseURL()
      const token = this.getAuthToken()
      
      const response = await fetch(`${baseURL}/ai/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : ''
        },
        body: JSON.stringify({
          message,
          module_id: options.moduleId,
          language: options.language || 'fr',
          expert_mode: options.expertMode || false,
          research_mode: options.researchMode || false,
          conversation_history: conversationHistory.length > 0 ? conversationHistory : undefined
        }),
        signal: this.currentStreamController.signal
      })

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch (e) {
          // Si la réponse n'est pas du JSON, utiliser le message par défaut
        }
        throw new Error(errorMessage)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        // Décoder le chunk et l'ajouter au buffer
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        
        // Garder la dernière ligne incomplète dans le buffer
        buffer = lines.pop() || ''

        for (const line of lines) {
          const trimmedLine = line.trim()
          if (!trimmedLine) continue

          if (trimmedLine.startsWith('data: ')) {
            const data = trimmedLine.slice(6)
            
            if (data === '[DONE]') {
              // Stream terminé
              const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: fullResponse,
                timestamp: new Date()
              }
              this.messageHistory.push(assistantMessage)
              
              options.onComplete?.(fullResponse)
              return fullResponse
            }

            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                fullResponse += parsed.content
                options.onChunk?.(parsed.content)
              }
            } catch (e) {
              // Ignorer les erreurs de parsing pour les données malformées (logger en dev uniquement)
              logger.warn('Erreur de parsing SSE', { error: e, data }, 'ChatService')
            }
          }
        }
      }

      // Traiter le buffer restant s'il y en a
      if (buffer.trim()) {
        const trimmedBuffer = buffer.trim()
        if (trimmedBuffer.startsWith('data: ')) {
          const data = trimmedBuffer.slice(6)
          if (data !== '[DONE]') {
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                fullResponse += parsed.content
                options.onChunk?.(parsed.content)
              }
            } catch (e) {
              // Ignorer les erreurs de parsing
            }
          }
        }
      }

      return fullResponse
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        // Stream annulé par l'utilisateur
        return fullResponse
      }
      
      options.onError?.(error as Error)
      throw error
    } finally {
      this.currentStreamController = null
    }
  }

  /**
   * Envoie un message sans streaming (pour compatibilité)
   */
  async sendMessage(
    message: string,
    moduleId?: string,
    language: string = 'fr',
    expertMode: boolean = false,
    researchMode: boolean = false
  ): Promise<ChatMessage> {
    // Préparer l'historique de conversation AVANT d'ajouter le message actuel
    const conversationHistory = this.messageHistory
      .slice(-10) // Limiter aux 10 derniers messages
      .map(msg => ({
        role: msg.role,
        content: msg.content
      }))
    
    try {
      const response = await api.post('/ai/chat', {
        message,
        module_id: moduleId,
        language,
        expert_mode: expertMode,
        research_mode: researchMode,
        conversation_history: conversationHistory.length > 0 ? conversationHistory : undefined
      })

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        modelUsed: response.data.model_used
      }

      this.messageHistory.push({
        role: 'user',
        content: message,
        timestamp: new Date()
      })
      this.messageHistory.push(assistantMessage)

      return assistantMessage
    } catch (error) {
      throw error
    }
  }

  /**
   * Envoie un message avec fichiers/images et streaming
   */
  async sendMessageStreamWithFiles(
    message: string,
    files: File[],
    options: ChatStreamOptions = {}
  ): Promise<string> {
    // Annuler le stream précédent s'il existe
    if (this.currentStreamController) {
      this.currentStreamController.abort()
    }

    this.currentStreamController = new AbortController()
    
    // Préparer l'historique de conversation
    const conversationHistory = this.messageHistory
      .slice(-10)
      .map(msg => ({
        role: msg.role,
        content: msg.content
      }))
    
    // Ajouter le message utilisateur à l'historique
    const userMessage: ChatMessage = {
      role: 'user',
      content: message || '📎 Fichier(s) joint(s)',
      timestamp: new Date()
    }
    this.messageHistory.push(userMessage)

    let fullResponse = ''

    try {
      const token = this.getAuthToken()

      // Créer FormData pour l'envoi multipart
      const formData = new FormData()
      formData.append('message', message || '')
      if (options.moduleId) {
        formData.append('module_id', options.moduleId)
      }
      formData.append('language', options.language || 'fr')
      formData.append('expert_mode', String(options.expertMode || false))
      formData.append('research_mode', String(options.researchMode || false))
      
      if (conversationHistory.length > 0) {
        formData.append('conversation_history', JSON.stringify(conversationHistory))
      }

      // Ajouter les fichiers
      files.forEach((file) => {
        formData.append('files', file)
      })

      // Utiliser l'URL de base correcte (proxy Vite en dev, backend Render en prod)
      const baseURL = getApiBaseURL()
      const authToken = token || this.getAuthToken()
      
      const response = await fetch(`${baseURL}/ai/chat/stream/with-files`, {
        method: 'POST',
        headers: {
          'Authorization': authToken ? `Bearer ${authToken}` : ''
          // Ne pas définir Content-Type, le navigateur le fera automatiquement avec FormData
        },
        body: formData,
        signal: this.currentStreamController.signal
      })

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch (e) {
          // Si la réponse n'est pas du JSON
        }
        throw new Error(errorMessage)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No reader available')
      }

      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const trimmedLine = line.trim()
          if (!trimmedLine) continue

          if (trimmedLine.startsWith('data: ')) {
            const data = trimmedLine.slice(6)
            
            if (data === '[DONE]') {
              const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: fullResponse,
                timestamp: new Date()
              }
              this.messageHistory.push(assistantMessage)
              
              options.onComplete?.(fullResponse)
              return fullResponse
            }

            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                fullResponse += parsed.content
                options.onChunk?.(parsed.content)
              }
            } catch (e) {
              logger.warn('Erreur de parsing SSE', { error: e, data }, 'ChatService')
            }
          }
        }
      }

      // Traiter le buffer restant
      if (buffer.trim()) {
        const trimmedBuffer = buffer.trim()
        if (trimmedBuffer.startsWith('data: ')) {
          const data = trimmedBuffer.slice(6)
          if (data !== '[DONE]') {
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                fullResponse += parsed.content
                options.onChunk?.(parsed.content)
              }
            } catch (e) {
              // Ignorer les erreurs de parsing
            }
          }
        }
      }

      return fullResponse
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return fullResponse
      }
      
      options.onError?.(error as Error)
      throw error
    } finally {
      this.currentStreamController = null
    }
  }

  /**
   * Annule le stream en cours
   */
  cancelStream() {
    if (this.currentStreamController) {
      this.currentStreamController.abort()
      this.currentStreamController = null
    }
  }

  /**
   * Récupère l'historique des messages
   */
  getHistory(): ChatMessage[] {
    return [...this.messageHistory]
  }

  /**
   * Efface l'historique
   */
  clearHistory() {
    this.messageHistory = []
  }

  /**
   * Limite l'historique aux N derniers messages (pour économiser la mémoire)
   */
  limitHistory(maxMessages: number = 50) {
    if (this.messageHistory.length > maxMessages) {
      this.messageHistory = this.messageHistory.slice(-maxMessages)
    }
  }

  /**
   * Charge l'historique depuis le backend
   */
  async loadHistory(moduleId?: string): Promise<ChatMessage[]> {
    try {
      const response = await api.get('/user-history/history', {
        params: {
          module_id: moduleId,
          limit: 20
        }
      })
      
      if (response.data && response.data.length > 0) {
        const historyMessages: ChatMessage[] = []
        response.data.forEach((entry: any) => {
          // Ajouter le message utilisateur
          historyMessages.push({
            role: 'user',
            content: entry.question || '',
            timestamp: new Date(entry.created_at)
          })
          // Ajouter la réponse de l'assistant
          historyMessages.push({
            role: 'assistant',
            content: entry.answer || '',
            timestamp: new Date(entry.created_at),
            modelUsed: entry.model_used
          })
        })
        
        // Trier par timestamp (plus ancien en premier)
        historyMessages.sort((a, b) => 
          a.timestamp.getTime() - b.timestamp.getTime()
        )
        
        // Remplacer l'historique actuel
        this.messageHistory = historyMessages
        
        return historyMessages
      }
      
      return []
    } catch (error) {
      // Logger l'erreur de manière centralisée
      logger.error('Erreur lors du chargement de l\'historique', error, 'ChatService')
      return []
    }
  }
}

export const chatService = new ChatService()

