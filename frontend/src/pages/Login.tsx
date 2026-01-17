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
  InputGroup,
  InputRightElement,
  Button,
  Alert,
  AlertIcon,
  useColorModeValue,
  Icon,
  HStack,
  FormErrorMessage,
  IconButton,
  Divider,
} from '@chakra-ui/react'
import { FiLogIn, FiMail, FiLock, FiEye, FiEyeOff, FiTarget } from 'react-icons/fi'
import { useAuthStore } from '../store/authStore'
import { useTranslation } from 'react-i18next'
import { useNotification } from '../components/NotificationProvider'
import { validateEmail } from '../utils/formValidation'
import { AnimatedBox } from '../components/AnimatedBox'
import { Onboarding } from '../components/Onboarding'
import logger from '../utils/logger'

const Login = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { login, isLoading, isAuthenticated } = useAuthStore()
  const { showNotification } = useNotification()
  
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [error, setError] = useState('')
  const [showOnboarding, setShowOnboarding] = useState(false)

  // Rediriger si déjà connecté
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true })
    }
  }, [isAuthenticated, navigate])

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  const handleBlur = (field: string) => {
    setTouched({ ...touched, [field]: true })
    
    if (field === 'email') {
      const validation = validateEmail(email)
      setErrors({ ...errors, email: validation.error || '' })
    }
  }

  const handleChange = (field: string, value: string) => {
    if (field === 'email') {
      setEmail(value)
      if (touched.email) {
        const validation = validateEmail(value)
        setErrors({ ...errors, email: validation.error || '' })
      }
    } else if (field === 'password') {
      setPassword(value)
      if (touched.password && !value) {
        setErrors({ ...errors, password: 'Le mot de passe est requis' })
      } else {
        setErrors({ ...errors, password: '' })
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    // Marquer tous les champs comme touchés
    setTouched({ email: true, password: true })

    // Validation
    const emailValidation = validateEmail(email)
    if (!emailValidation.isValid) {
      setErrors({ email: emailValidation.error || '', password: errors.password || '' })
      return
    }

    if (!password) {
      setErrors({ email: '', password: 'Le mot de passe est requis' })
      return
    }

    try {
      await login(email, password)
      showNotification('Connexion réussie ! Bienvenue sur Kaïrox.', 'success')
      navigate('/dashboard')
    } catch (err: any) {
      // Logger l'erreur de manière centralisée
      logger.error('Erreur lors de la connexion', err, 'Login')
      
      // Déterminer un message d'erreur approprié pour l'utilisateur
      let errorMessage = 'Email ou mot de passe incorrect'
      
      if (err.response) {
        // Erreur avec réponse du serveur
        if (err.response.status === 401) {
          errorMessage = 'Email ou mot de passe incorrect'
        } else if (err.response.status === 429) {
          errorMessage = 'Trop de tentatives. Veuillez réessayer plus tard.'
        } else if (err.response.status >= 500) {
          errorMessage = 'Erreur serveur. Veuillez réessayer dans quelques instants.'
        } else if (err.response.data?.detail) {
          errorMessage = err.response.data.detail
        }
      } else if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
        // Timeout - le serveur prend trop de temps à répondre
        errorMessage = 'Le serveur prend trop de temps à répondre. Veuillez réessayer.'
      } else if (err.message) {
        // Autre erreur avec message
        if (err.message.includes('Network Error') || err.message.includes('ERR_NETWORK')) {
          errorMessage = 'Erreur de connexion au serveur. Vérifiez votre connexion internet.'
        } else {
          errorMessage = err.message
        }
      }
      
      setError(errorMessage)
    }
  }

  return (
    <Box
      minH={{ base: 'auto', md: '100vh' }}
      display="flex"
      alignItems="center"
      justifyContent="center"
      py={{ base: 2, md: 8 }}
      px={4}
      position="relative"
      overflow="hidden"
      backgroundImage="url('/background.jfif')"
      backgroundSize="cover"
      backgroundPosition="center"
      backgroundRepeat="no-repeat"
    >
      {/* Overlay subtil pour améliorer la lisibilité */}
      <Box
        position="absolute"
        top={0}
        left={0}
        right={0}
        bottom={0}
        bgGradient="linear-gradient(135deg, rgba(37, 99, 235, 0.4) 0%, rgba(30, 64, 175, 0.5) 50%, rgba(37, 99, 235, 0.4) 100%)"
        zIndex={0}
      />
      
      {/* Effets de fond animés */}
      <Box
        position="absolute"
        top="-50%"
        right="-20%"
        width="500px"
        height="500px"
        bgGradient="radial(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%)"
        borderRadius="full"
        filter="blur(60px)"
        zIndex={1}
        animation="pulse 4s ease-in-out infinite"
      />
      <Box
        position="absolute"
        bottom="-30%"
        left="-20%"
        width="400px"
        height="400px"
        bgGradient="radial(circle, rgba(255, 255, 255, 0.12) 0%, transparent 70%)"
        borderRadius="full"
        filter="blur(60px)"
        zIndex={1}
        animation="pulse 5s ease-in-out infinite"
      />
      <Box
        position="absolute"
        top="20%"
        right="10%"
        width="300px"
        height="300px"
        bgGradient="radial(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%)"
        borderRadius="full"
        filter="blur(60px)"
        zIndex={1}
        animation="pulse 6s ease-in-out infinite"
      />

      <Container maxW="md" position="relative" zIndex={2}>
        <AnimatedBox animation="fadeInUp" delay={0.1}>
          <Box
            bg={bgColor}
            p={{ base: 4, md: 5 }}
            borderRadius="2xl"
            boxShadow="2xl"
            border="1px solid"
            borderColor={borderColor}
            backdropFilter="blur(10px)"
            _hover={{
              boxShadow: '2xl',
              transform: 'translateY(-4px)',
            }}
            transition="all 0.3s"
          >
            <VStack spacing={{ base: 2, md: 3 }} align="stretch">
              {/* En-tête amélioré */}
              <VStack spacing={{ base: 1, md: 2 }} align="center">
                <Box
                  p={3}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  borderRadius="lg"
                  boxShadow="md"
                  transform="rotate(-5deg)"
                  _hover={{
                    transform: 'rotate(0deg) scale(1.1)',
                  }}
                  transition="all 0.3s"
                >
                  <Icon as={FiLogIn} boxSize={6} color="white" />
                </Box>
                <VStack spacing={1}>
                  <Heading 
                    size={{ base: 'md', md: 'lg' }} 
                    color="gray.900" 
                    fontWeight="800"
                    textAlign="center"
                  >
                    Connexion
                  </Heading>
                  <Text color="gray.600" textAlign="center" fontSize={{ base: 'xs', md: 'sm' }}>
                    Connectez-vous à votre compte Kaïrox
                  </Text>
                </VStack>
              </VStack>

              <Divider borderColor="gray.200" />

              {/* Formulaire amélioré */}
              <form onSubmit={handleSubmit} noValidate>
                <VStack spacing={5} align="stretch">
                  {error && (
                    <Alert 
                      status="error" 
                      borderRadius="md"
                      variant="subtle"
                      fontSize="sm"
                    >
                      <AlertIcon />
                      {error}
                    </Alert>
                  )}

                  <FormControl isRequired isInvalid={!!errors.email && touched.email}>
                    <FormLabel fontWeight="600" color="gray.700">
                      <HStack spacing={2}>
                        <Icon as={FiMail} color="blue.500" />
                        <Text>Adresse email</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="email"
                      value={email}
                      onChange={(e) => handleChange('email', e.target.value)}
                      onBlur={() => handleBlur('email')}
                      placeholder="votre@email.com"
                      size="lg"
                      borderRadius="xl"
                      autoComplete="email"
                      border="2px solid"
                      borderColor={errors.email && touched.email ? 'red.300' : 'gray.200'}
                      _focus={{
                        borderColor: errors.email && touched.email ? 'red.500' : 'blue.500',
                        boxShadow: errors.email && touched.email 
                          ? '0 0 0 3px rgba(229, 62, 62, 0.1)' 
                          : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                      }}
                      _hover={{
                        borderColor: errors.email && touched.email ? 'red.400' : 'gray.300',
                      }}
                      transition="all 0.2s"
                      data-touch-target="true"
                    />
                    {errors.email && touched.email && (
                      <FormErrorMessage fontSize="sm">{errors.email}</FormErrorMessage>
                    )}
                  </FormControl>

                  <FormControl isRequired isInvalid={!!errors.password && touched.password}>
                    <FormLabel fontWeight="600" color="gray.700">
                      <HStack spacing={2}>
                        <Icon as={FiLock} color="blue.500" />
                        <Text>Mot de passe</Text>
                      </HStack>
                    </FormLabel>
                    <InputGroup>
                      <Input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => handleChange('password', e.target.value)}
                        onBlur={() => handleBlur('password')}
                        placeholder="••••••••"
                        size="lg"
                        borderRadius="xl"
                        autoComplete="current-password"
                        border="2px solid"
                        borderColor={errors.password && touched.password ? 'red.300' : 'gray.200'}
                        _focus={{
                          borderColor: errors.password && touched.password ? 'red.500' : 'blue.500',
                          boxShadow: errors.password && touched.password 
                            ? '0 0 0 3px rgba(229, 62, 62, 0.1)' 
                            : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                        }}
                        _hover={{
                          borderColor: errors.password && touched.password ? 'red.400' : 'gray.300',
                        }}
                        transition="all 0.2s"
                        data-touch-target="true"
                      />
                      <InputRightElement width="3rem" h="full">
                        <IconButton
                          aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                          icon={showPassword ? <FiEyeOff /> : <FiEye />}
                          variant="ghost"
                          onClick={() => setShowPassword(!showPassword)}
                          size="sm"
                          data-touch-target="true"
                        />
                      </InputRightElement>
                    </InputGroup>
                    {errors.password && touched.password && (
                      <FormErrorMessage fontSize="sm">{errors.password}</FormErrorMessage>
                    )}
                  </FormControl>

                  <Button
                    type="submit"
                    colorScheme="blue"
                    size="lg"
                    width="full"
                    isLoading={isLoading}
                    loadingText="Connexion en cours..."
                    bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                    _hover={{
                      bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)',
                      transform: 'translateY(-2px)',
                      boxShadow: 'xl',
                    }}
                    _active={{
                      transform: 'translateY(0)',
                    }}
                    transition="all 0.3s"
                    fontWeight="bold"
                    fontSize="md"
                    data-touch-target="true"
                  >
                    Se connecter
                  </Button>
                </VStack>
              </form>

              <Divider borderColor="gray.200" />

              {/* Lien vers inscription */}
              <Text textAlign="center" color="gray.600" fontSize={{ base: 'sm', md: 'md' }}>
                Pas encore de compte ?{' '}
                <Link to="/register">
                  <Text 
                    as="span" 
                    color="blue.500" 
                    fontWeight="700" 
                    _hover={{ 
                      textDecoration: 'underline',
                      color: 'blue.600',
                    }}
                    transition="color 0.2s"
                  >
                    Créer un compte
                  </Text>
                </Link>
              </Text>

              {/* Bouton pour voir l'introduction */}
              <Divider borderColor="gray.200" />
              
              <Button
                variant="outline"
                colorScheme="blue"
                size="md"
                width="full"
                onClick={() => setShowOnboarding(true)}
                leftIcon={<Icon as={FiTarget} />}
                _hover={{
                  bg: 'blue.50',
                  borderColor: 'blue.300',
                  transform: 'translateY(-2px)',
                }}
                transition="all 0.2s"
                data-touch-target="true"
              >
                Découvrir Kaïrox
              </Button>
            </VStack>
          </Box>
        </AnimatedBox>
      </Container>

      {/* Écran d'onboarding */}
      {showOnboarding && (
        <Onboarding
          onComplete={() => setShowOnboarding(false)}
          onSkip={() => setShowOnboarding(false)}
        />
      )}
    </Box>
  )
}

export default Login
