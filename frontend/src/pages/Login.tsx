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
  InputGroup, 
  InputRightElement, 
  IconButton,
  Divider,
  HStack,
  useColorModeValue,
  Image
} from '@chakra-ui/react'
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/authStore'
import { useNotification } from '../components/NotificationProvider'
import Logo from '../components/Logo'

const Login = () => {
  const { t } = useTranslation()
  const { showNotification } = useNotification()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const { login } = useAuthStore()

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    // Validation basique côté client
    if (!email || !password) {
      setError('Veuillez remplir tous les champs')
      return
    }

    setLoading(true)

    try {
      await login(email.trim(), password)
      showNotification('Connexion réussie ! Bienvenue sur Kaïrox', 'success')
      navigate('/dashboard')
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || t('auth.loginError')
      setError(errorMessage)
      showNotification(errorMessage, 'error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box
      minH={{ base: 'calc(100vh - 60px)', md: 'calc(100vh - 80px)' }}
      bgGradient="linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%)"
      position="relative"
      overflow="hidden"
      display="flex"
      alignItems="center"
      py={{ base: 4, md: 8 }}
      px={{ base: 4, md: 0 }}
    >
      {/* Effets de fond animés avec formes géométriques */}
      <Box
        position="absolute"
        top="-20%"
        left="-10%"
        width="400px"
        height="400px"
        borderRadius="full"
        bgGradient="radial(circle, rgba(255,255,255,0.3) 0%, transparent 70%)"
        filter="blur(60px)"
        animation="float 20s ease-in-out infinite"
        sx={{
          '@keyframes float': {
            '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
            '50%': { transform: 'translate(30px, 30px) scale(1.1)' },
          },
        }}
      />
      <Box
        position="absolute"
        bottom="-15%"
        right="-10%"
        width="500px"
        height="500px"
        borderRadius="full"
        bgGradient="radial(circle, rgba(255,255,255,0.25) 0%, transparent 70%)"
        filter="blur(80px)"
        animation="float 25s ease-in-out infinite reverse"
        sx={{
          '@keyframes float': {
            '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
            '50%': { transform: 'translate(-30px, -30px) scale(1.1)' },
          },
        }}
      />
      <Box
        position="absolute"
        top="50%"
        left="50%"
        transform="translate(-50%, -50%)"
        width="300px"
        height="300px"
        borderRadius="full"
        bgGradient="radial(circle, rgba(255,255,255,0.2) 0%, transparent 70%)"
        filter="blur(50px)"
        animation="pulse 15s ease-in-out infinite"
        sx={{
          '@keyframes pulse': {
            '0%, 100%': { opacity: 0.5, transform: 'translate(-50%, -50%) scale(1)' },
            '50%': { opacity: 0.8, transform: 'translate(-50%, -50%) scale(1.2)' },
          },
        }}
      />
      
      {/* Motif de grille subtil */}
      <Box
        position="absolute"
        top={0}
        left={0}
        right={0}
        bottom={0}
        opacity={0.1}
        backgroundImage="radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)"
        backgroundSize="50px 50px"
      />

      <Container maxW={{ base: '100%', sm: '480px' }} position="relative" zIndex={1} w="full" px={{ base: 4, sm: 6 }}>
        <Box
          bg="rgba(255, 255, 255, 0.95)"
          backdropFilter="blur(20px)"
          p={{ base: 6, sm: 6, md: 8 }}
          borderRadius={{ base: 'xl', md: '3xl' }}
          data-full-width-mobile="true"
          boxShadow="0 25px 80px -15px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.2)"
          border="1px solid"
          borderColor="rgba(255, 255, 255, 0.3)"
          overflowY="visible"
          position="relative"
          mx={{ base: 0, sm: 'auto' }}
          _before={{
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            borderRadius: { base: '2xl', md: '3xl' },
            padding: '1px',
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3), rgba(240, 147, 251, 0.3))',
            WebkitMask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
            WebkitMaskComposite: 'xor',
            maskComposite: 'exclude',
          }}
        >
          <VStack spacing={{ base: 4, md: 5 }} align="stretch">
            {/* En-tête */}
            <VStack spacing={3} align="center">
              <Box mb={2}>
                <Logo size={{ base: '20', md: '28' }} variant="default" />
              </Box>
              <Heading 
                size={{ base: 'lg', md: 'xl' }}
                id="login-heading"
                bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                bgClip="text"
                fontWeight="bold"
                letterSpacing="tight"
                className="gradient-text"
                textAlign="center"
              >
                {t('auth.loginTitle')}
              </Heading>
              <Text color="gray.600" fontSize={{ base: 'xs', md: 'sm' }} fontWeight="medium" textAlign="center">
                Connectez-vous à votre compte Kaïrox
              </Text>
            </VStack>

            {/* Message d'erreur */}
            {error && (
              <Alert 
                status="error" 
                borderRadius="md" 
                variant="left-accent"
                fontSize="sm"
                id="login-error"
                role="alert"
                aria-live="assertive"
              >
                <AlertIcon />
                {error}
              </Alert>
            )}

            {/* Formulaire */}
            <form role="form" onSubmit={handleSubmit} style={{ width: '100%' }} aria-labelledby="login-heading" aria-describedby={error ? 'login-error' : undefined}>
              <VStack spacing={{ base: 4, md: 5 }}>
                <FormControl isRequired>
                  <FormLabel htmlFor="login-email" fontWeight="semibold" color="gray.700" fontSize={{ base: 'sm', md: 'md' }}>
                    {t('auth.email')}
                  </FormLabel>
                  <Input
                    id="login-email"
                    name="email"
                    type="email"
                    aria-required={true}
                    aria-label="Email"
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="exemple@email.com"
                    size="lg"
                    bg="white"
                    border="2px solid"
                    borderColor="gray.200"
                    _hover={{
                      borderColor: '#667eea'
                    }}
                    _focus={{
                      borderColor: '#667eea',
                      boxShadow: '0 0 0 3px rgba(102, 126, 234, 0.1)',
                      transform: { base: 'none', md: 'scale(1.01)' }
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                    required
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel htmlFor="login-password" fontWeight="semibold" color="gray.700" fontSize={{ base: 'sm', md: 'md' }}>
                    {t('auth.password')}
                  </FormLabel>
                  <InputGroup size="lg">
                    <Input
                      id="login-password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      aria-required={true}
                      aria-label="Mot de passe"
                      autoComplete="current-password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Votre mot de passe"
                      bg="white"
                      border="2px solid"
                      borderColor="gray.200"
                      _hover={{
                        borderColor: '#667eea'
                      }}
                      _focus={{
                        borderColor: '#667eea',
                        boxShadow: '0 0 0 3px rgba(102, 126, 234, 0.1)',
                        transform: { base: 'none', md: 'scale(1.01)' }
                      }}
                      transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                      required
                    />
                    <InputRightElement width="4.5rem">
                      <IconButton
                        aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                        icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                        onClick={() => setShowPassword(!showPassword)}
                        variant="ghost"
                        size="sm"
                        color="gray.500"
                        _hover={{
                          color: 'gray.600',
                          bg: 'gray.50'
                        }}
                      />
                    </InputRightElement>
                  </InputGroup>
                
                </FormControl>

                <Button
                  type="submit"
                  bgGradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                  color="white"
                  width="full"
                  size="lg"
                  aria-label="Se connecter"
                  isLoading={loading}
                  loadingText="Connexion..."
                  isDisabled={loading}
                  fontWeight="bold"
                  fontSize={{ base: 'sm', md: 'md' }}
                  py={{ base: 6, md: 7 }}
                  boxShadow="0 10px 30px rgba(102, 126, 234, 0.4)"
                  _hover={{
                    bgGradient: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 15px 40px rgba(102, 126, 234, 0.5)',
                  }}
                  _active={{
                    transform: 'translateY(0)',
                  }}
                  _disabled={{
                    opacity: 0.6,
                    cursor: 'not-allowed',
                    transform: 'none',
                    bgGradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  }}
                  transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                >
                  {t('auth.signIn')}
                </Button>
              </VStack>
            </form>


            {/* Lien vers l'inscription */}
            <HStack justify="center" spacing={1} flexWrap="wrap">
              <Text color="gray.600" fontSize={{ base: 'xs', md: 'sm' }} textAlign="center">
                {t('auth.noAccount')}
              </Text>
              <Link 
                as={RouterLink} 
                to="/register" 
                color="gray.600"
                fontWeight="semibold"
                fontSize={{ base: 'xs', md: 'sm' }}
                _hover={{
                      color: 'gray.700',
                  textDecoration: 'underline'
                }}
                transition="color 0.2s"
              >
                {t('auth.signUp')}
              </Link>
            </HStack>
          </VStack>
        </Box>
      </Container>
    </Box>
  )
}

export default Login

