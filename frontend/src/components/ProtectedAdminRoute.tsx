import React, { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Box, Spinner, Container, VStack, Text, Alert, AlertIcon } from '@chakra-ui/react'

interface ProtectedAdminRouteProps {
  children: React.ReactNode
}

const ProtectedAdminRoute = ({ children }: ProtectedAdminRouteProps) => {
  const { isAuthenticated, isLoading, user, checkAuth } = useAuthStore()

  // Vérifier l'authentification au montage
  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      checkAuth()
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

  // Vérifier si l'utilisateur est admin
  if (!user?.is_admin) {
    return (
      <Box minH="100vh" display="flex" alignItems="center" justifyContent="center" bg="gray.50">
        <Container maxW="md">
          <Alert status="error" borderRadius="md">
            <AlertIcon />
            <VStack align="stretch" spacing={2}>
              <Text fontWeight="bold">Accès refusé</Text>
              <Text>Vous devez être administrateur pour accéder à cette page.</Text>
            </VStack>
          </Alert>
        </Container>
      </Box>
    )
  }

  return <>{children}</>
}

export default ProtectedAdminRoute
