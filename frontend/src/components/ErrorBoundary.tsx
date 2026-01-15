import { Component, ErrorInfo, ReactNode } from 'react'
import { Box, Container, VStack, Heading, Text, Button, Alert, AlertIcon } from '@chakra-ui/react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Logger l'erreur avec tous les détails pour le debugging
    const errorDetails = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
    }
    
    // Utiliser le système de logging centralisé
    import('../utils/logger').then(({ logger }) => {
      logger.error('Erreur capturée par ErrorBoundary', errorDetails, 'ErrorBoundary')
    })
  }

  public render() {
    if (this.state.hasError) {
      return (
        <Container maxW="md" py={12}>
          <Box bg="white" p={8} borderRadius="lg" boxShadow="md">
            <VStack spacing={6}>
              <Alert status="error" borderRadius="md">
                <AlertIcon />
                Une erreur s'est produite
              </Alert>
              
              <Heading size="lg" color="red.600">
                Oups ! Quelque chose s'est mal passé
              </Heading>
              
              <Text color="gray.600">
                {this.state.error?.message || 'Une erreur inattendue s\'est produite'}
              </Text>
              
              <VStack spacing={3} width="full">
                <Button
                  colorScheme="brand"
                  width="full"
                  onClick={() => {
                    this.setState({ hasError: false, error: null })
                    window.location.href = '/'
                  }}
                >
                  Retour à l'accueil
                </Button>
                
                <Button
                  variant="outline"
                  width="full"
                  onClick={() => window.location.reload()}
                >
                  Recharger la page
                </Button>
              </VStack>
              
              {import.meta.env.DEV && this.state.error && (
                <Box
                  mt={4}
                  p={4}
                  bg="gray.100"
                  borderRadius="md"
                  fontSize="sm"
                  fontFamily="mono"
                  maxH="200px"
                  overflow="auto"
                >
                  <Text fontWeight="bold">Détails de l'erreur (dev):</Text>
                  <Text>{this.state.error.stack}</Text>
                </Box>
              )}
            </VStack>
          </Box>
        </Container>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary



