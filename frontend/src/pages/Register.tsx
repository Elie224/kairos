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
  SimpleGrid,
} from '@chakra-ui/react'
import { FiUserPlus, FiMail, FiLock, FiUser, FiPhone, FiMapPin } from 'react-icons/fi'
import { useAuthStore } from '../store/authStore'
import { useTranslation } from 'react-i18next'

const Register = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { register, isLoading, isAuthenticated } = useAuthStore()
  
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: '',
    country: '',
  })
  const [error, setError] = useState('')

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  // Rediriger si déjà connecté
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true })
    }
  }, [isAuthenticated, navigate])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validation
    if (!formData.email || !formData.username || !formData.password) {
      setError('Veuillez remplir tous les champs obligatoires')
      return
    }

    if (formData.password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Les mots de passe ne correspondent pas')
      return
    }

    if (formData.username.length < 3) {
      setError('Le nom d\'utilisateur doit contenir au moins 3 caractères')
      return
    }

    try {
      await register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        first_name: formData.first_name || undefined,
        last_name: formData.last_name || undefined,
        phone: formData.phone || undefined,
        country: formData.country || undefined,
      })
      navigate('/login', { state: { message: 'Inscription réussie ! Connectez-vous maintenant.' } })
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        'Erreur lors de l\'inscription'
      )
    }
  }

  return (
    <Box
      minH="100vh"
      bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)"
      py={8}
    >
      <Container maxW="2xl">
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
                <Icon as={FiUserPlus} boxSize={8} color="white" />
              </Box>
              <Heading size="xl" color="gray.900" fontWeight="700">
                Créer un compte
              </Heading>
              <Text color="gray.600" textAlign="center">
                Rejoignez Kaïros et commencez votre apprentissage
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

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <FormControl isRequired>
                    <FormLabel>
                      <HStack spacing={2}>
                        <Icon as={FiMail} />
                        <Text>Email</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="votre@email.com"
                      size="lg"
                      borderRadius="md"
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>
                      <HStack spacing={2}>
                        <Icon as={FiUser} />
                        <Text>Nom d'utilisateur</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      placeholder="nom_utilisateur"
                      size="lg"
                      borderRadius="md"
                    />
                  </FormControl>
                </SimpleGrid>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <FormControl isRequired>
                    <FormLabel>
                      <HStack spacing={2}>
                        <Icon as={FiLock} />
                        <Text>Mot de passe</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="••••••••"
                      size="lg"
                      borderRadius="md"
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel>
                      <HStack spacing={2}>
                        <Icon as={FiLock} />
                        <Text>Confirmer le mot de passe</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="password"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      placeholder="••••••••"
                      size="lg"
                      borderRadius="md"
                    />
                  </FormControl>
                </SimpleGrid>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <FormControl>
                    <FormLabel>
                      <HStack spacing={2}>
                        <Icon as={FiUser} />
                        <Text>Prénom</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="text"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      placeholder="Prénom"
                      size="lg"
                      borderRadius="md"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>
                      <HStack spacing={2}>
                        <Icon as={FiUser} />
                        <Text>Nom</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="text"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      placeholder="Nom"
                      size="lg"
                      borderRadius="md"
                    />
                  </FormControl>
                </SimpleGrid>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <FormControl>
                    <FormLabel>
                      <HStack spacing={2}>
                        <Icon as={FiPhone} />
                        <Text>Téléphone</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      placeholder="+33 6 12 34 56 78"
                      size="lg"
                      borderRadius="md"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>
                      <HStack spacing={2}>
                        <Icon as={FiMapPin} />
                        <Text>Pays</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="text"
                      name="country"
                      value={formData.country}
                      onChange={handleChange}
                      placeholder="France"
                      size="lg"
                      borderRadius="md"
                    />
                  </FormControl>
                </SimpleGrid>

                <Button
                  type="submit"
                  colorScheme="blue"
                  size="lg"
                  width="full"
                  isLoading={isLoading}
                  loadingText="Inscription..."
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  _hover={{
                    bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: 'lg',
                  }}
                  transition="all 0.3s"
                  mt={4}
                >
                  S'inscrire
                </Button>
              </VStack>
            </form>

            {/* Lien vers connexion */}
            <Text textAlign="center" color="gray.600">
              Déjà un compte ?{' '}
              <Link to="/login">
                <Text as="span" color="blue.500" fontWeight="600" _hover={{ textDecoration: 'underline' }}>
                  Se connecter
                </Text>
              </Link>
            </Text>
          </VStack>
        </Box>
      </Container>
    </Box>
  )
}

export default Register
