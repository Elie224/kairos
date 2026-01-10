import api from './api';
import { ChatMessage, ChatStreamOptions } from '../types';
import { useAuthStore } from '../store/authStore';

class ChatService {
  private messageHistory: ChatMessage[] = [];
  private currentStreamController: AbortController | null = null;

  private getAuthToken(): string {
    const { token } = useAuthStore.getState();
    return token || '';
  }

  async sendMessageStream(
    message: string,
    options: ChatStreamOptions = {}
  ): Promise<string> {
    // Annuler le stream précédent s'il existe
    if (this.currentStreamController) {
      this.currentStreamController.abort();
    }

    this.currentStreamController = new AbortController();

    // Préparer l'historique de conversation
    const conversationHistory = this.messageHistory
      .slice(-10)
      .map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

    // Ajouter le message utilisateur à l'historique
    const userMessage: ChatMessage = {
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    this.messageHistory.push(userMessage);

    let fullResponse = '';

    try {
      const token = this.getAuthToken();

      const response = await fetch(`${api.defaults.baseURL}/ai/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({
          message,
          module_id: options.moduleId,
          language: options.language || 'fr',
          expert_mode: options.expertMode || false,
          research_mode: options.researchMode || false,
          conversation_history: conversationHistory.length > 0 ? conversationHistory : undefined,
        }),
        signal: this.currentStreamController.signal,
      });

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          // Si la réponse n'est pas du JSON
        }
        throw new Error(errorMessage);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');

        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (!trimmedLine) continue;

          if (trimmedLine.startsWith('data: ')) {
            const data = trimmedLine.slice(6);

            if (data === '[DONE]') {
              const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: fullResponse,
                timestamp: new Date(),
              };
              this.messageHistory.push(assistantMessage);

              options.onComplete?.(fullResponse);
              return fullResponse;
            }

            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                fullResponse += parsed.content;
                options.onChunk?.(parsed.content);
              }
            } catch (e) {
              // Ignorer les erreurs de parsing
            }
          }
        }
      }

      // Traiter le buffer restant
      if (buffer.trim()) {
        const trimmedBuffer = buffer.trim();
        if (trimmedBuffer.startsWith('data: ')) {
          const data = trimmedBuffer.slice(6);
          if (data !== '[DONE]') {
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                fullResponse += parsed.content;
                options.onChunk?.(parsed.content);
              }
            } catch (e) {
              // Ignorer les erreurs de parsing
            }
          }
        }
      }

      return fullResponse;
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return fullResponse;
      }

      options.onError?.(error as Error);
      throw error;
    } finally {
      this.currentStreamController = null;
    }
  }

  async sendMessage(
    message: string,
    moduleId?: string,
    language: string = 'fr',
    expertMode: boolean = false,
    researchMode: boolean = false
  ): Promise<ChatMessage> {
    const conversationHistory = this.messageHistory
      .slice(-10)
      .map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

    try {
      const response = await api.post('/ai/chat', {
        message,
        module_id: moduleId,
        language,
        expert_mode: expertMode,
        research_mode: researchMode,
        conversation_history: conversationHistory.length > 0 ? conversationHistory : undefined,
      });

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date(),
        modelUsed: response.data.model_used,
      };

      this.messageHistory.push({
        role: 'user',
        content: message,
        timestamp: new Date(),
      });
      this.messageHistory.push(assistantMessage);

      return assistantMessage;
    } catch (error) {
      throw error;
    }
  }

  cancelStream() {
    if (this.currentStreamController) {
      this.currentStreamController.abort();
      this.currentStreamController = null;
    }
  }

  getHistory(): ChatMessage[] {
    return [...this.messageHistory];
  }

  clearHistory() {
    this.messageHistory = [];
  }

  limitHistory(maxMessages: number = 50) {
    if (this.messageHistory.length > maxMessages) {
      this.messageHistory = this.messageHistory.slice(-maxMessages);
    }
  }
}

export const chatService = new ChatService();



