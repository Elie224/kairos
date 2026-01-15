import React from 'react'
import ReactDOM from 'react-dom/client'
import { ChakraProvider } from '@chakra-ui/react'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from 'react-query'
import App from './App'
import theme from './theme' // Le thème bleu sera initialisé automatiquement via initTheme.ts
import { NotificationProvider } from './components/NotificationProvider'
import ErrorBoundary from './components/ErrorBoundary'
import { LogoColorProvider } from './components/LogoColorProvider'
import './i18n/config'
import './styles/animations.css'
import './styles/mobile.css'
import './styles/mobile-enhancements.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      refetchOnMount: false, // Ne pas refetch automatiquement au montage
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes par défaut
      cacheTime: 10 * 60 * 1000, // 10 minutes de cache par défaut
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <ChakraProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <NotificationProvider>
            <LogoColorProvider>
              <BrowserRouter
                future={{
                  v7_startTransition: true,
                  v7_relativeSplatPath: true,
                }}
              >
                <App />
              </BrowserRouter>
            </LogoColorProvider>
          </NotificationProvider>
        </QueryClientProvider>
      </ChakraProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)

