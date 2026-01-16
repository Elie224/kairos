/**
 * Composant d'affichage d'erreur amélioré avec suggestions
 */
import {
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Box,
  Button,
  VStack,
  HStack,
  Text,
  Icon,
  Collapse,
} from '@chakra-ui/react'
import { FiRefreshCw, FiHome, FiHelpCircle, FiChevronDown, FiChevronUp } from 'react-icons/fi'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

interface ErrorDisplayProps {
  error: any
  title?: string
  onRetry?: () => void
  showDetails?: boolean
  compact?: boolean
}

export const ErrorDisplay = ({
  error,
  title,
  onRetry,
  showDetails = false,
  compact = false,
}: ErrorDisplayProps) => {
  const navigate = useNavigate()
  const [showFullDetails, setShowFullDetails] = useState(showDetails)

  // Extraire le message d'erreur et la suggestion
  const errorMessage = error?.userMessage || error?.message || error?.response?.data?.detail || 'Une erreur est survenue'
  const suggestion = error?.suggestion || 'Veuillez réessayer ou contacter le support si le problème persiste.'
  const status = error?.response?.status

  // Messages personnalisés selon le code d'erreur
  const getStatusMessage = (statusCode?: number) => {
    switch (statusCode) {
      case 400:
        return 'Requête invalide'
      case 401:
        return 'Authentification requise'
      case 403:
        return 'Accès refusé'
      case 404:
        return 'Ressource introuvable'
      case 429:
        return 'Trop de requêtes'
      case 500:
        return 'Erreur serveur'
      case 503:
        return 'Service indisponible'
      default:
        return 'Erreur'
    }
  }

  if (compact) {
    return (
      <Alert status="error" borderRadius="md" variant="subtle">
        <AlertIcon />
        <Box flex="1">
          <AlertTitle fontSize="sm">{title || getStatusMessage(status)}</AlertTitle>
          <AlertDescription fontSize="xs">{errorMessage}</AlertDescription>
        </Box>
        {onRetry && (
          <Button size="xs" colorScheme="red" variant="ghost" onClick={onRetry}>
            <Icon as={FiRefreshCw} />
          </Button>
        )}
      </Alert>
    )
  }

  return (
    <Box
      bg="white"
      borderRadius="xl"
      boxShadow="lg"
      border="2px solid"
      borderColor="red.200"
      p={6}
    >
      <VStack spacing={4} align="stretch">
        <Alert status="error" borderRadius="md">
          <AlertIcon boxSize="6" />
          <Box flex="1">
            <AlertTitle fontSize="lg" fontWeight="bold">
              {title || getStatusMessage(status)}
            </AlertTitle>
            <AlertDescription fontSize="md" mt={2}>
              {errorMessage}
            </AlertDescription>
          </Box>
        </Alert>

        {/* Suggestion */}
        <Box
          bg="blue.50"
          border="1px solid"
          borderColor="blue.200"
          borderRadius="md"
          p={4}
        >
          <HStack spacing={2} mb={2}>
            <Icon as={FiHelpCircle} color="blue.600" />
            <Text fontWeight="semibold" color="blue.900" fontSize="sm">
              Suggestion
            </Text>
          </HStack>
          <Text color="blue.800" fontSize="sm">
            {suggestion}
          </Text>
        </Box>

        {/* Actions */}
        <HStack spacing={3} flexWrap="wrap">
          {onRetry && (
            <Button
              leftIcon={<Icon as={FiRefreshCw} />}
              colorScheme="blue"
              onClick={onRetry}
              size="md"
            >
              Réessayer
            </Button>
          )}
          <Button
            leftIcon={<Icon as={FiHome} />}
            variant="outline"
            onClick={() => navigate('/')}
            size="md"
          >
            Retour à l'accueil
          </Button>
        </HStack>

        {/* Détails techniques (développement) */}
        {import.meta.env.DEV && error && (
          <Box>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFullDetails(!showFullDetails)}
              rightIcon={<Icon as={showFullDetails ? FiChevronUp : FiChevronDown} />}
            >
              {showFullDetails ? 'Masquer' : 'Afficher'} les détails techniques
            </Button>
            <Collapse in={showFullDetails} animateOpacity>
              <Box
                mt={2}
                p={4}
                bg="gray.50"
                borderRadius="md"
                border="1px solid"
                borderColor="gray.200"
                fontSize="xs"
                fontFamily="mono"
                maxH="300px"
                overflow="auto"
              >
                <Text fontWeight="bold" mb={2}>Détails de l'erreur :</Text>
                <pre>{JSON.stringify(error, null, 2)}</pre>
              </Box>
            </Collapse>
          </Box>
        )}
      </VStack>
    </Box>
  )
}
