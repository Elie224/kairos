import React, { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Box, Spinner, Container, VStack, Text } from '@chakra-ui/react'

interface ProtectedRouteProps {
  children: React.ReactNode
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore()

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
  }, [isAuthenticated, isLoading, checkAuth])

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

  return <>{children}</>
}

export default ProtectedRoute
