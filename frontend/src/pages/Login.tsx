import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import {
  Box,
  Container,
  VStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  Input,
  Button,
  Alert,
  AlertIcon,
  useColorModeValue,
  Icon,
  HStack,
} from '@chakra-ui/react'
import { FiLogIn, FiMail, FiLock } from 'react-icons/fi'
import { useAuthStore } from '../store/authStore'
import { useTranslation } from 'react-i18next'

const Login = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { login, isLoading, isAuthenticated } = useAuthStore()
  
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  // Rediriger si déjà connecté
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true })
    }
  }, [isAuthenticated, navigate])

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!email || !password) {
      setError('Veuillez remplir tous les champs')
      return
    }

    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        'Email ou mot de passe incorrect'
      )
    }
  }

  return (
    <Box
      minH="100vh"
      bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)"
      display="flex"
      alignItems="center"
      py={8}
    >
      <Container maxW="md">
        <Box
          bg={bgColor}
          p={8}
          borderRadius="2xl"
          boxShadow="xl"
          border="1px solid"
          borderColor={borderColor}
        >
          <VStack spacing={6} align="stretch">
            {/* En-tête */}
            <VStack spacing={3} align="center">
              <Box
                p={4}
                bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                borderRadius="xl"
                boxShadow="lg"
              >
                <Icon as={FiLogIn} boxSize={8} color="white" />
              </Box>
              <Heading size="xl" color="gray.900" fontWeight="700">
                Connexion
              </Heading>
              <Text color="gray.600" textAlign="center">
                Connectez-vous à votre compte Kaïros
              </Text>
            </VStack>

            {/* Formulaire */}
            <form onSubmit={handleSubmit}>
              <VStack spacing={4} align="stretch">
                {error && (
                  <Alert status="error" borderRadius="md">
                    <AlertIcon />
                    {error}
                  </Alert>
                )}

                <FormControl isRequired>
                  <FormLabel>
                    <HStack spacing={2}>
                      <Icon as={FiMail} />
                      <Text>Email</Text>
                    </HStack>
                  </FormLabel>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="votre@email.com"
                    size="lg"
                    borderRadius="md"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>
                    <HStack spacing={2}>
                      <Icon as={FiLock} />
                      <Text>Mot de passe</Text>
                    </HStack>
                  </FormLabel>
                  <Input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    size="lg"
                    borderRadius="md"
                  />
                </FormControl>

                <Button
                  type="submit"
                  colorScheme="blue"
                  size="lg"
                  width="full"
                  isLoading={isLoading}
                  loadingText="Connexion..."
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  _hover={{
                    bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: 'lg',
                  }}
                  transition="all 0.3s"
                >
                  Se connecter
                </Button>
              </VStack>
            </form>

            {/* Lien vers inscription */}
            <Text textAlign="center" color="gray.600">
              Pas encore de compte ?{' '}
              <Link to="/register">
                <Text as="span" color="blue.500" fontWeight="600" _hover={{ textDecoration: 'underline' }}>
                  Créer un compte
                </Text>
              </Link>
            </Text>
          </VStack>
        </Box>
      </Container>
    </Box>
  )
}

export default Login
