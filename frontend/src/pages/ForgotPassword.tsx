import { useState } from 'react'
import { 
  Container, 
  Box, 
  VStack, 
  Heading, 
  FormControl, 
  FormLabel, 
  Input, 
  Button, 
  Text, 
  Link, 
  Alert, 
  AlertIcon,
  useColorModeValue
} from '@chakra-ui/react'
import { Link as RouterLink } from 'react-router-dom'
import { useNotification } from '../components/NotificationProvider'
import api from '../services/api'

const ForgotPassword = () => {
  const { showNotification } = useNotification()
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [resetLink, setResetLink] = useState<string | null>(null)

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email) {
      showNotification('Veuillez entrer votre adresse email', 'error')
      return
    }

    setLoading(true)

    try {
      const response = await api.post('/auth/forgot-password', { email })
      setSuccess(true)
      // En développement, le lien peut être dans la réponse
      if (response.data?.reset_link) {
        setResetLink(response.data.reset_link)
        showNotification('Lien de réinitialisation généré (mode développement)', 'success')
      } else {
        showNotification('Un lien de réinitialisation a été envoyé à votre email', 'success')
      }
    } catch (err: any) {
      // Ne pas révéler si l'email existe ou non (sécurité)
      setSuccess(true)
      if (err.response?.data?.reset_link) {
        setResetLink(err.response.data.reset_link)
      }
      showNotification('Si cet email existe, un lien de réinitialisation a été envoyé', 'info')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box
      minH="calc(100vh - 80px)"
      bgGradient="linear(to-br, gray.50, gray.100)"
      display="flex"
      alignItems="center"
      py={12}
    >
      <Container maxW="md">
        <Box
          bg={bgColor}
          p={8}
          borderRadius="xl"
          boxShadow="xl"
          border="1px solid"
          borderColor={borderColor}
        >
          <VStack spacing={6} align="stretch">
            <VStack spacing={2} align="center">
              <Heading 
                size="xl" 
                color="gray.600"
                fontWeight="bold"
                letterSpacing="tight"
              >
                Mot de passe oublié ?
              </Heading>
              <Text color="gray.600" fontSize="sm" textAlign="center">
                Entrez votre adresse email et nous vous enverrons un lien pour réinitialiser votre mot de passe
              </Text>
            </VStack>

            {success ? (
              <VStack spacing={4} align="stretch">
                <Alert status="success" borderRadius="md" variant="left-accent">
                  <AlertIcon />
                  <VStack align="start" spacing={2}>
                    <Text fontWeight="semibold">Lien de réinitialisation généré !</Text>
                    <Text fontSize="sm">
                      {resetLink 
                        ? "En mode développement, utilisez le lien ci-dessous pour réinitialiser votre mot de passe."
                        : "Si cet email existe dans notre système, vous recevrez un lien de réinitialisation. Vérifiez votre boîte de réception et vos spams."}
                    </Text>
                  </VStack>
                </Alert>
                
                {resetLink && (
                  <Box
                    p={4}
                    bg="blue.50"
                    borderRadius="md"
                    border="1px solid"
                    borderColor="blue.200"
                  >
                    <Text fontSize="xs" fontWeight="semibold" color="blue.800" mb={2}>
                      Lien de réinitialisation (Mode développement) :
                    </Text>
                    <Link
                      href={resetLink}
                      color="blue.600"
                      fontWeight="medium"
                      fontSize="sm"
                      wordBreak="break-all"
                      _hover={{ textDecoration: 'underline' }}
                    >
                      {resetLink}
                    </Link>
                    <Button
                      as={RouterLink}
                      to={resetLink}
                      colorScheme="blue"
                      size="sm"
                      width="full"
                      mt={3}
                    >
                      Réinitialiser mon mot de passe
                    </Button>
                  </Box>
                )}
                
                <Button
                  as={RouterLink}
                  to="/login"
                  colorScheme="brand"
                  size="sm"
                  variant="outline"
                >
                  Retour à la connexion
                </Button>
              </VStack>
            ) : (
              <form onSubmit={handleSubmit} style={{ width: '100%' }}>
                <VStack spacing={5}>
                  <FormControl isRequired>
                    <FormLabel fontWeight="semibold" color="gray.700">
                      Adresse email
                    </FormLabel>
                    <Input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="exemple@email.com"
                      size="lg"
                      bg="white"
                      border="2px solid"
                      borderColor="gray.200"
                      _hover={{
                        borderColor: 'gray.300'
                      }}
                      _focus={{
                        borderColor: 'gray.500',
                        boxShadow: '0 0 0 1px var(--chakra-colors-brand-500)'
                      }}
                      required
                    />
                  </FormControl>

                  <Button
                    type="submit"
                    colorScheme="brand"
                    width="full"
                    size="lg"
                    isLoading={loading}
                    loadingText="Envoi en cours..."
                    isDisabled={loading || !email}
                    fontWeight="semibold"
                    fontSize="md"
                    py={6}
                    _hover={{
                      transform: 'translateY(-2px)',
                      boxShadow: 'lg'
                    }}
                    transition="all 0.2s"
                  >
                    Envoyer le lien de réinitialisation
                  </Button>
                </VStack>
              </form>
            )}

            <Text textAlign="center" fontSize="sm" color="gray.600">
              Vous vous souvenez de votre mot de passe ?{' '}
              <Link 
                as={RouterLink} 
                to="/login" 
                color="gray.600"
                fontWeight="semibold"
                _hover={{
                  color: 'gray.700',
                  textDecoration: 'underline'
                }}
              >
                Se connecter
              </Link>
            </Text>
          </VStack>
        </Box>
      </Container>
    </Box>
  )
}

export default ForgotPassword

