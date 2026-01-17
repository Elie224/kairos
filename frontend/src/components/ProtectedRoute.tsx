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

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // S'assurer que les enfants sont rendus avec une clé unique pour forcer le re-render
  // Utiliser une clé basée sur le pathname pour forcer le re-render lors de la navigation
  // Utiliser React.Fragment avec une clé unique pour forcer le remount complet
  return <React.Fragment key={`route-${location.pathname}`}>{children}</React.Fragment>
}

export default ProtectedRoute
