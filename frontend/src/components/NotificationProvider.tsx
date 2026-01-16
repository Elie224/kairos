import { createContext, useContext, useCallback, ReactNode } from 'react'
import { useToast } from '@chakra-ui/react'

interface Notification {
  id: string
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
}

interface NotificationContextType {
  showNotification: (message: string, type?: Notification['type']) => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export const useNotification = () => {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider')
  }
  return context
}

export const NotificationProvider = ({ children }: { children: ReactNode }) => {
  const toast = useToast()

  const showNotification = useCallback(
    (message: string, type: Notification['type'] = 'info', options?: { title?: string; duration?: number; action?: { label: string; onClick: () => void } }) => {
      const titles = {
        success: '✅ Succès',
        error: '❌ Erreur',
        warning: '⚠️ Attention',
        info: 'ℹ️ Information',
      }

      toast({
        title: options?.title || titles[type],
        description: message,
        status: type,
        duration: options?.duration || (type === 'error' ? 7000 : 5000),
        isClosable: true,
        position: 'top-right',
        variant: type === 'error' ? 'solid' : 'subtle',
        // Améliorer le style selon le type
        ...(type === 'success' && {
          colorScheme: 'green',
        }),
        ...(type === 'error' && {
          colorScheme: 'red',
        }),
        ...(type === 'warning' && {
          colorScheme: 'orange',
        }),
        ...(type === 'info' && {
          colorScheme: 'blue',
        }),
      })
    },
    [toast]
  )

  return (
    <NotificationContext.Provider value={{ showNotification }}>
      {children}
    </NotificationContext.Provider>
  )
}





