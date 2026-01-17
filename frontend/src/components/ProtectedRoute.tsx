/**
 * Composant pour protéger les routes nécessitant une authentification
 * 
 * Vérifie si l'utilisateur est authentifié avant de rendre les enfants.
 * Si non authentifié, redirige vers la page de connexion.
 * 
 * @module components/ProtectedRoute
 */
import React, { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Box, Spinner, Container, VStack, Text } from '@chakra-ui/react'

/**
 * Props du composant ProtectedRoute
 */
interface ProtectedRouteProps {
  /** Composants enfants à afficher si l'utilisateur est authentifié */
  children: React.ReactNode
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore()
  const location = useLocation()

  // Vérifier l'authentification au montage (seulement si nécessaire)
  useEffect(() => {
    // Vérifier seulement si on n'est pas authentifié et pas déjà en train de charger
    if (!isAuthenticated && !isLoading) {
      // Vérifier d'abord le token dans localStorage avant d'appeler l'API
      const authData = localStorage.getItem('kairos-auth')
      if (authData) {
        try {
          const parsed = JSON.parse(authData)
          if (parsed.state?.token) {
            // Il y a un token, vérifier avec l'API
            checkAuth()
          }
        } catch {
          // Pas de token valide, rediriger directement
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, isLoading]) // Retirer checkAuth des dépendances pour éviter les boucles infinies

  // IMPORTANT: Ne pas bloquer le rendu si on est en train de charger
  // Cela permet à React Router de matcher correctement la route même pendant le chargement
  if (isLoading) {
    return (
      <Box minH="100vh" display="flex" alignItems="center" justifyContent="center">
        <Container>
          <VStack spacing={4}>
            <Spinner size="xl" color="blue.500" thickness="4px" />
            <Text color="gray.600">Chargement...</Text>
          </VStack>
        </Container>
      </Box>
    )
  }

  // CRITIQUE: Ne rediriger vers /login que si on est vraiment non authentifié
  // et sauvegarder la route demandée pour redirection après login
  if (!isAuthenticated) {
    console.log('🔒 ProtectedRoute: Utilisateur non authentifié, redirection vers /login', { 
      requestedPath: location.pathname 
    })
    // Sauvegarder la route demandée pour redirection après login
    const returnPath = location.pathname + location.search
    return <Navigate to={`/login?returnTo=${encodeURIComponent(returnPath)}`} replace />
  }

  // S'assurer que les enfants sont rendus avec une clé unique pour forcer le re-render
  // Utiliser une clé basée sur le pathname complet pour forcer le remount complet lors de la navigation
  // IMPORTANT: Utiliser location.key (unique pour chaque navigation) au lieu de pathname pour garantir le remount
  return (
    <Box key={`protected-route-${location.key || location.pathname}`} w="100%" minH="100%">
      {children}
    </Box>
  )
}

export default ProtectedRoute
