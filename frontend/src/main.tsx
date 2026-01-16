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
import { AccessibilityProvider } from './components/AccessibilityProvider'
import { useAuthStore } from './store/authStore'
import { cacheConfigs } from './services/cacheService'
import './i18n/config'
import './styles/animations.css'
import './styles/mobile.css'
import './styles/mobile-enhancements.css'

// Vérifier l'authentification au démarrage
useAuthStore.getState().checkAuth()

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      ...cacheConfigs.default,
      // Optimisations supplémentaires
      keepPreviousData: true, // Garder les données précédentes pendant le chargement (react-query v3)
      structuralSharing: true, // Partage structurel pour éviter les re-renders inutiles
      refetchOnMount: false, // Ne pas refetch automatiquement
      refetchOnWindowFocus: false, // Ne pas refetch au focus de la fenêtre
      refetchOnReconnect: false, // Ne pas refetch à la reconnexion
      retry: 1, // Réessayer seulement 1 fois en cas d'erreur
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 1000), // Backoff exponentiel limité à 1s
    },
    mutations: {
      retry: 1,
      // Optimiser les mutations
      onError: (error) => {
        console.error('Mutation error:', error)
      },
    },
  },
})

// Wrapper pour AccessibilityProvider qui nécessite BrowserRouter
const AppWithAccessibility = () => {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <AccessibilityProvider>
        <App />
      </AccessibilityProvider>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <ChakraProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
          <NotificationProvider>
            <LogoColorProvider>
              <AppWithAccessibility />
            </LogoColorProvider>
          </NotificationProvider>
        </QueryClientProvider>
      </ChakraProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)

