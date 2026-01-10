import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Box, Text, Spinner, VStack } from '@chakra-ui/react'

interface ProtectedAdminRouteProps {
  children: React.ReactElement
}

const ProtectedAdminRoute = ({ children }: ProtectedAdminRouteProps) => {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!user?.is_admin) {
    return (
      <Box minH="100vh" display="flex" alignItems="center" justifyContent="center" bg="gray.50">
        <VStack spacing={4}>
          <Text fontSize="xl" fontWeight="bold" color="gray.800">
            Accès refusé
          </Text>
          <Text color="gray.600">
            Cette page est réservée aux administrateurs.
          </Text>
        </VStack>
      </Box>
    )
  }

  return children
}

export default ProtectedAdminRoute

















