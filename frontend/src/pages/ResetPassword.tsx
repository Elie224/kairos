import { useState, useEffect } from 'react'
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
  FormErrorMessage,
  Progress,
  useColorModeValue,
  Flex,
  HStack
} from '@chakra-ui/react'
import { ViewIcon, ViewOffIcon, CheckIcon } from '@chakra-ui/icons'
import { Link as RouterLink, useNavigate, useSearchParams } from 'react-router-dom'
import { useNotification } from '../components/NotificationProvider'
import api from '../services/api'

// Fonction pour calculer la force du mot de passe
const calculatePasswordStrength = (password: string): { strength: number; label: string; color: string } => {
  if (!password) return { strength: 0, label: '', color: 'gray' }
  
  let strength = 0
  const checks = {
    length: password.length >= 8,
    lowercase: /[a-z]/.test(password),
    uppercase: /[A-Z]/.test(password),
    number: /[0-9]/.test(password),
    special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password),
  }
  
  strength = Object.values(checks).filter(Boolean).length
  
  if (strength <= 2) return { strength: 25, label: 'Faible', color: 'red' }
  if (strength === 3) return { strength: 50, label: 'Moyen', color: 'gray' }
  if (strength === 4) return { strength: 75, label: 'Fort', color: 'gray' }
  return { strength: 100, label: 'Très fort', color: 'gray' }
}

const ResetPassword = () => {
  const { showNotification } = useNotification()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const token = searchParams.get('token')

  const passwordStrength = calculatePasswordStrength(password)

  useEffect(() => {
    if (!token) {
      setError('Token de réinitialisation manquant ou invalide')
    }
  }, [token])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!password) {
      setError('Le mot de passe est requis')
      return
    }

    if (password.length < 8) {
      setError('Le mot de passe doit contenir au moins 8 caractères')
      return
    }

    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      return
    }

    if (!token) {
      setError('Token de réinitialisation manquant')
      return
    }

    setLoading(true)

    try {
      await api.post('/auth/reset-password', {
        token,
        new_password: password
      })
      setSuccess(true)
      showNotification('Mot de passe réinitialisé avec succès', 'success')
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Erreur lors de la réinitialisation du mot de passe'
      setError(errorMessage)
      showNotification(errorMessage, 'error')
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
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
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              <VStack align="start" spacing={2}>
                <Text fontWeight="semibold">Token invalide</Text>
                <Text fontSize="sm">Le lien de réinitialisation est invalide ou a expiré.</Text>
                <Button
                  as={RouterLink}
                  to="/forgot-password"
                  colorScheme="brand"
                  size="sm"
                  mt={2}
                >
                  Demander un nouveau lien
                </Button>
              </VStack>
            </Alert>
          </Box>
        </Container>
      </Box>
    )
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
                Réinitialiser votre mot de passe
              </Heading>
              <Text color="gray.600" fontSize="sm" textAlign="center">
                Entrez votre nouveau mot de passe
              </Text>
            </VStack>

            {success ? (
              <Alert status="success" borderRadius="md" variant="left-accent">
                <AlertIcon />
                <VStack align="start" spacing={2}>
                  <Text fontWeight="semibold">Mot de passe réinitialisé !</Text>
                  <Text fontSize="sm">
                    Votre mot de passe a été réinitialisé avec succès. Vous allez être redirigé vers la page de connexion...
                  </Text>
                </VStack>
              </Alert>
            ) : (
              <form onSubmit={handleSubmit} style={{ width: '100%' }}>
                <VStack spacing={5}>
                  {error && (
                    <Alert status="error" borderRadius="md" variant="left-accent" fontSize="sm" width="full">
                      <AlertIcon />
                      {error}
                    </Alert>
                  )}

                  <FormControl isRequired>
                    <FormLabel fontWeight="semibold" color="gray.700">
                      Nouveau mot de passe
                    </FormLabel>
                    <InputGroup size="lg">
                      <Input
                        type={showPassword ? 'text' : 'password'}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Créez un mot de passe sécurisé"
                        size="lg"
                        bg="white"
                        border="2px solid"
                        borderColor={error ? 'red.300' : 'gray.200'}
                        _hover={{
                          borderColor: error ? 'red.400' : 'gray.300'
                      }}
                      _focus={{
                        borderColor: error ? 'red.500' : 'gray.500',
                          boxShadow: error 
                            ? '0 0 0 1px var(--chakra-colors-red-500)' 
                            : '0 0 0 1px var(--chakra-colors-brand-500)'
                        }}
                        required
                        minLength={8}
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
                    
                    {password && (
                      <VStack align="stretch" spacing={2} mt={2}>
                        <Progress 
                          value={passwordStrength.strength} 
                          colorScheme={passwordStrength.color}
                          size="sm"
                          borderRadius="full"
                        />
                        <Flex justify="space-between" align="center">
                          <Text fontSize="xs" color={`${passwordStrength.color}.600`} fontWeight="medium">
                            Force : {passwordStrength.label}
                          </Text>
                          <HStack spacing={1} fontSize="xs">
                            {[
                              { check: password.length >= 8, label: '8+ caractères' },
                              { check: /[a-z]/.test(password), label: 'Minuscule' },
                              { check: /[A-Z]/.test(password), label: 'Majuscule' },
                              { check: /[0-9]/.test(password), label: 'Chiffre' },
                              { check: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password), label: 'Spécial' }
                            ].map((item, idx) => (
                              <HStack key={idx} spacing={0.5}>
                                {item.check && <CheckIcon color="green.500" boxSize={2.5} />}
                                <Text 
                                  color={item.check ? 'green.600' : 'gray.400'}
                                  fontSize="xs"
                                >
                                  {item.label}
                                </Text>
                              </HStack>
                            ))}
                          </HStack>
                        </Flex>
                      </VStack>
                    )}
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel fontWeight="semibold" color="gray.700">
                      Confirmer le mot de passe
                    </FormLabel>
                    <InputGroup size="lg">
                      <Input
                        type={showConfirmPassword ? 'text' : 'password'}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        placeholder="Confirmez votre mot de passe"
                        size="lg"
                        bg="white"
                        border="2px solid"
                        borderColor={error && password !== confirmPassword ? 'red.300' : 'gray.200'}
                        _hover={{
                          borderColor: error && password !== confirmPassword ? 'red.400' : 'gray.300'
                      }}
                      _focus={{
                        borderColor: error && password !== confirmPassword ? 'red.500' : 'gray.500',
                          boxShadow: error && password !== confirmPassword
                            ? '0 0 0 1px var(--chakra-colors-red-500)' 
                            : '0 0 0 1px var(--chakra-colors-brand-500)'
                        }}
                        required
                      />
                      <InputRightElement width="4.5rem">
                        <IconButton
                          aria-label={showConfirmPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                          icon={showConfirmPassword ? <ViewOffIcon /> : <ViewIcon />}
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
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
                    {confirmPassword && password !== confirmPassword && (
                      <FormErrorMessage fontSize="sm">Les mots de passe ne correspondent pas</FormErrorMessage>
                    )}
                  </FormControl>

                  <Button
                    type="submit"
                    colorScheme="brand"
                    width="full"
                    size="lg"
                    isLoading={loading}
                    loadingText="Réinitialisation..."
                    isDisabled={loading || !password || password !== confirmPassword}
                    fontWeight="semibold"
                    fontSize="md"
                    py={6}
                    _hover={{
                      transform: 'translateY(-2px)',
                      boxShadow: 'lg'
                    }}
                    transition="all 0.2s"
                  >
                    Réinitialiser le mot de passe
                  </Button>
                </VStack>
              </form>
            )}

            <Text textAlign="center" fontSize="sm" color="gray.600">
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
                Retour à la connexion
              </Link>
            </Text>
          </VStack>
        </Box>
      </Container>
    </Box>
  )
}

export default ResetPassword

