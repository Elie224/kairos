import React, { useEffect, useState } from 'react'
import ReactDOM from 'react-dom/client'
import { ChakraProvider, Box, VStack, Spinner, Text } from '@chakra-ui/react'
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
import { handleMutationError } from './utils/errorHandler'
import { prefetchMainRoutes } from './utils/navigation'
import './i18n/config'
import './styles/animations.css'
import './styles/mobile-unified.css'

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
      // Optimiser les mutations - Utiliser le gestionnaire d'erreurs centralisé
      onError: handleMutationError,
    },
  },
})

// Scroll restoration simplifié - ne pas bloquer le rendu initial
if (typeof window !== 'undefined') {
  // Attendre que React soit monté avant de scroller
  window.addEventListener('load', () => {
    setTimeout(() => {
      try {
        window.scrollTo(0, 0)
        if (document.documentElement) {
          document.documentElement.scrollTop = 0
        }
        if (document.body) {
          document.body.scrollTop = 0
        }
      } catch (e) {
        // Ignorer les erreurs
      }
    }, 150)
  })
}

// Loader global pour le chargement initial
const GlobalLoader = () => {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Masquer le loader après que React soit monté ET que le DOM soit prêt
    // Utiliser plusieurs vérifications pour s'assurer que tout est chargé
    const checkReady = () => {
      // Vérifier que le DOM est prêt
      if (document.readyState === 'complete' || document.readyState === 'interactive') {
        // Attendre un peu plus pour que React soit complètement monté
        const timer = setTimeout(() => {
          setIsLoading(false)
        }, 300) // Augmenté à 300ms pour éviter la page blanche
        return () => clearTimeout(timer)
      }
    }
    
    // Vérifier immédiatement
    const immediateCheck = checkReady()
    
    // Écouter aussi l'événement load
    window.addEventListener('load', () => {
      setTimeout(() => {
        setIsLoading(false)
      }, 200)
    })
    
    // Fallback: masquer après 1 seconde maximum
    const fallbackTimer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)
    
    return () => {
      if (immediateCheck) immediateCheck()
      clearTimeout(fallbackTimer)
      window.removeEventListener('load', () => {})
    }
  }, [])

  if (!isLoading) return null

  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      right={0}
      bottom={0}
      bg="white"
      zIndex={9999}
      display="flex"
      alignItems="center"
      justifyContent="center"
    >
      <VStack spacing={4}>
        <Spinner size="xl" color="blue.500" thickness="4px" />
        <Text color="gray.600" fontSize="lg">Chargement de Kaïrox...</Text>
      </VStack>
    </Box>
  )
}

// Wrapper pour AccessibilityProvider qui nécessite BrowserRouter
const AppWithAccessibility = () => {
  // Précharger les routes principales après le montage
  useEffect(() => {
    prefetchMainRoutes()
    // S'assurer que le scroll est en haut au montage
    window.scrollTo({ top: 0, behavior: 'instant' })
    document.documentElement.scrollTop = 0
    document.body.scrollTop = 0
  }, [])

  return (
    <>
      <GlobalLoader />
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
    </>
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

