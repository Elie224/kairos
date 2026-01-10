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
    (message: string, type: Notification['type'] = 'info') => {
      toast({
        title: type === 'success' ? 'Succès' : type === 'error' ? 'Erreur' : 'Information',
        description: message,
        status: type,
        duration: 5000,
        isClosable: true,
        position: 'top-right',
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





