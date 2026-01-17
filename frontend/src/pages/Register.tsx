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
  SimpleGrid,
  FormErrorMessage,
  IconButton,
  Divider,
  Select,
  Progress,
  Badge,
} from '@chakra-ui/react'
import { FiUserPlus, FiMail, FiLock, FiUser, FiPhone, FiMapPin, FiEye, FiEyeOff, FiCheck, FiTarget } from 'react-icons/fi'
import { useAuthStore } from '../store/authStore'
import { useTranslation } from 'react-i18next'
import { useNotification } from '../components/NotificationProvider'
import { 
  validateEmail, 
  validateUsername, 
  validatePassword, 
  validatePasswordConfirmation,
  validatePhone,
  validateName 
} from '../utils/formValidation'
import { PasswordStrength } from '../components/PasswordStrength'
import { AnimatedBox } from '../components/AnimatedBox'
import { Onboarding } from '../components/Onboarding'
import { countries } from '../constants/countries'
import logger from '../utils/logger'

const Register = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { register, isLoading, isAuthenticated } = useAuthStore()
  const { showNotification } = useNotification()
  
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
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [touched, setTouched] = useState<Record<string, boolean>>({})
  const [error, setError] = useState('')
  const [showOnboarding, setShowOnboarding] = useState(false)
  
  // Indicateur de progression du formulaire - Amélioré pour compter tous les champs
  const formProgress = () => {
    const allFields = ['email', 'username', 'password', 'confirmPassword', 'first_name', 'last_name', 'phone', 'country']
    const requiredFields = ['email', 'username', 'password', 'confirmPassword']
    const filledRequiredFields = requiredFields.filter(field => {
      const value = formData[field as keyof typeof formData]
      return value && value.trim().length > 0
    })
    const filledOptionalFields = ['first_name', 'last_name', 'phone', 'country'].filter(field => {
      const value = formData[field as keyof typeof formData]
      return value && value.trim().length > 0
    })
    // Calcul : 60% pour les champs requis, 40% pour les champs optionnels
    const requiredProgress = (filledRequiredFields.length / requiredFields.length) * 60
    const optionalProgress = (filledOptionalFields.length / 4) * 40
    return Math.min(100, Math.round(requiredProgress + optionalProgress))
  }

  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  // Rediriger si déjà connecté
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true })
    }
  }, [isAuthenticated, navigate])

  /**
   * Handler appelé quand un champ perd le focus
   * Marque le champ comme "touché" et lance sa validation
   * @param {string} field - Nom du champ
   */
  const handleBlur = (field: string): void => {
    setTouched({ ...touched, [field]: true })
    validateField(field, formData[field as keyof typeof formData] as string)
  }

  /**
   * Valide un champ spécifique du formulaire
   * @param {string} field - Nom du champ à valider
   * @param {string} value - Valeur du champ
   * @returns {boolean} true si le champ est valide, false sinon
   */
  const validateField = (field: string, value: string): boolean => {
    let validation: { isValid: boolean; error?: string } = { isValid: true }

    switch (field) {
      case 'email':
        validation = validateEmail(value)
        break
      case 'username':
        validation = validateUsername(value)
        break
      case 'password':
        validation = validatePassword(value)
        break
      case 'confirmPassword':
        validation = validatePasswordConfirmation(formData.password, value)
        break
      case 'phone':
        validation = validatePhone(value)
        break
      case 'first_name':
        validation = validateName(value, 'prénom')
        break
      case 'last_name':
        validation = validateName(value, 'nom')
        break
    }

    setErrors({ ...errors, [field]: validation.error || '' })
    return validation.isValid
  }

  /**
   * Handler appelé à chaque modification d'un champ du formulaire
   * Met à jour la valeur du champ et valide en temps réel si nécessaire
   * @param {React.ChangeEvent<HTMLInputElement | HTMLSelectElement>} e - Événement de changement
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>): void => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })

    // Valider en temps réel immédiatement (pas besoin d'attendre que le champ soit touché)
    // Cela améliore l'expérience utilisateur avec un feedback instantané
    if (name === 'confirmPassword') {
      const validation = validatePasswordConfirmation(formData.password, value)
      setErrors({ ...errors, [name]: validation.error || '' })
    } else if (name === 'email') {
      // Validation immédiate pour email (format)
      if (value && !value.includes('@')) {
        // Donner un feedback précoce pour email invalide
        if (touched[name] || value.length > 3) {
          const validation = validateEmail(value)
          setErrors({ ...errors, [name]: validation.error || '' })
        }
      } else {
        validateField(name, value)
      }
    } else if (name === 'password' || name === 'username') {
      // Validation immédiate pour mot de passe et nom d'utilisateur (longueur minimale)
      if (touched[name] || value.length > 0) {
        validateField(name, value)
      }
    } else if (touched[name]) {
      // Pour les autres champs, valider seulement s'ils ont été touchés
      validateField(name, value)
    }
  }

  /**
   * Handler pour la soumission du formulaire d'inscription
   * Valide tous les champs, puis envoie les données au backend
   * @param {React.FormEvent} e - Événement de soumission du formulaire
   */
  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault()
    setError('')

    // Marquer tous les champs comme touchés
    const allFields = Object.keys(formData)
    setTouched(Object.fromEntries(allFields.map(field => [field, true])))

    // Valider tous les champs
    const emailValid = validateField('email', formData.email)
    const usernameValid = validateField('username', formData.username)
    const passwordValid = validateField('password', formData.password)
    const confirmPasswordValid = validateField('confirmPassword', formData.confirmPassword)
    
    if (formData.first_name) validateField('first_name', formData.first_name)
    if (formData.last_name) validateField('last_name', formData.last_name)
    if (formData.phone) validateField('phone', formData.phone)

    if (!emailValid || !usernameValid || !passwordValid || !confirmPasswordValid) {
      setError('Veuillez corriger les erreurs dans le formulaire')
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
      showNotification('Inscription réussie ! Connectez-vous maintenant.', 'success')
      navigate('/login', { state: { message: 'Inscription réussie ! Connectez-vous maintenant.' } })
    } catch (err: any) {
      logger.error('Erreur lors de l\'inscription', err, 'Register')
      const errorMessage = err.response?.data?.detail || 
        err.message || 
        'Erreur lors de l\'inscription'
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
        width="600px"
        height="600px"
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
        width="500px"
        height="500px"
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
        width="400px"
        height="400px"
        bgGradient="radial(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%)"
        borderRadius="full"
        filter="blur(60px)"
        zIndex={1}
        animation="pulse 6s ease-in-out infinite"
      />

      <Container maxW="2xl" position="relative" zIndex={2}>
        <AnimatedBox animation="fadeInUp" delay={0.1}>
          <Box
            bg={bgColor}
            p={{ base: 2, md: 6 }}
            borderRadius="2xl"
            boxShadow="2xl"
            border="1px solid"
            borderColor={borderColor}
            backdropFilter="blur(10px)"
            _hover={{
              boxShadow: '2xl',
            }}
            transition="all 0.3s"
          >
            <VStack spacing={{ base: 1.5, md: 4 }} align="stretch">
              {/* En-tête amélioré */}
              <VStack spacing={{ base: 1, md: 3 }} align="center">
                <Box
                  p={{ base: 2, md: 4 }}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  borderRadius="xl"
                  boxShadow="lg"
                  transform="rotate(-5deg)"
                  _hover={{
                    transform: 'rotate(0deg) scale(1.1)',
                  }}
                  transition="all 0.3s"
                >
                  <Icon as={FiUserPlus} boxSize={8} color="white" />
                </Box>
                <VStack spacing={2}>
                  <Heading 
                    size={{ base: 'lg', md: 'xl' }} 
                    color="gray.900" 
                    fontWeight="800"
                    textAlign="center"
                  >
                    Créer un compte
                  </Heading>
                  <Text color="gray.600" textAlign="center" fontSize={{ base: 'sm', md: 'md' }}>
                    Rejoignez Kaïrox et commencez votre apprentissage
                  </Text>
                </VStack>
                
                {/* Indicateur de progression */}
                <Box w="full" maxW="400px">
                  <HStack spacing={2} justify="space-between" mb={2}>
                    <Text fontSize="xs" color="gray.600" fontWeight="medium">
                      Progression du formulaire
                    </Text>
                    <Text fontSize="xs" color="blue.600" fontWeight="bold">
                      {Math.round(formProgress())}%
                    </Text>
                  </HStack>
                  <Progress 
                    value={formProgress()} 
                    colorScheme="blue" 
                    size="sm" 
                    borderRadius="full"
                    bg="gray.100"
                  />
                </Box>
              </VStack>

              <Divider borderColor="gray.200" />

              {/* Formulaire amélioré */}
              <form onSubmit={handleSubmit} noValidate>
                <VStack spacing={2.5} align="stretch">
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

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
                  <FormControl isRequired isInvalid={!!errors.email && touched.email}>
                    <FormLabel fontWeight="600" color="gray.700">
                      <HStack spacing={2}>
                        <Icon as={FiMail} color="blue.500" />
                        <Text>Adresse email</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
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

                  <FormControl isRequired isInvalid={!!errors.username && touched.username}>
                    <FormLabel fontWeight="600" color="gray.700">
                      <HStack spacing={2}>
                        <Icon as={FiUser} color="blue.500" />
                        <Text>Nom d'utilisateur</Text>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="text"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      onBlur={() => handleBlur('username')}
                      placeholder="nom_utilisateur"
                      size="lg"
                      borderRadius="xl"
                      autoComplete="username"
                      border="2px solid"
                      borderColor={errors.username && touched.username ? 'red.300' : 'gray.200'}
                      _focus={{
                        borderColor: errors.username && touched.username ? 'red.500' : 'blue.500',
                        boxShadow: errors.username && touched.username 
                          ? '0 0 0 3px rgba(229, 62, 62, 0.1)' 
                          : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                      }}
                      _hover={{
                        borderColor: errors.username && touched.username ? 'red.400' : 'gray.300',
                      }}
                      transition="all 0.2s"
                      data-touch-target="true"
                    />
                    {errors.username && touched.username && (
                      <FormErrorMessage fontSize="sm">{errors.username}</FormErrorMessage>
                    )}
                    {!errors.username && touched.username && formData.username && (
                      <HStack spacing={1} mt={1}>
                        <Icon as={FiCheck} color="green.500" boxSize={4} />
                        <Text fontSize="xs" color="green.600">Nom d'utilisateur valide</Text>
                      </HStack>
                    )}
                  </FormControl>
                </SimpleGrid>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
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
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        onBlur={() => handleBlur('password')}
                        placeholder="••••••••"
                        size="lg"
                        borderRadius="xl"
                        autoComplete="new-password"
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
                    {formData.password && (
                      <PasswordStrength password={formData.password} />
                    )}
                  </FormControl>

                  <FormControl isRequired isInvalid={!!errors.confirmPassword && touched.confirmPassword}>
                    <FormLabel fontWeight="600" color="gray.700">
                      <HStack spacing={2}>
                        <Icon as={FiLock} color="blue.500" />
                        <Text>Confirmer le mot de passe</Text>
                      </HStack>
                    </FormLabel>
                    <InputGroup>
                      <Input
                        type={showConfirmPassword ? 'text' : 'password'}
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        onBlur={() => handleBlur('confirmPassword')}
                        placeholder="••••••••"
                        size="lg"
                        borderRadius="xl"
                        autoComplete="new-password"
                        border="2px solid"
                        borderColor={errors.confirmPassword && touched.confirmPassword ? 'red.300' : 'gray.200'}
                        _focus={{
                          borderColor: errors.confirmPassword && touched.confirmPassword ? 'red.500' : 'blue.500',
                          boxShadow: errors.confirmPassword && touched.confirmPassword 
                            ? '0 0 0 3px rgba(229, 62, 62, 0.1)' 
                            : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                        }}
                        _hover={{
                          borderColor: errors.confirmPassword && touched.confirmPassword ? 'red.400' : 'gray.300',
                        }}
                        transition="all 0.2s"
                        data-touch-target="true"
                      />
                      <InputRightElement width="3rem" h="full">
                        <IconButton
                          aria-label={showConfirmPassword ? 'Masquer la confirmation' : 'Afficher la confirmation'}
                          icon={showConfirmPassword ? <FiEyeOff /> : <FiEye />}
                          variant="ghost"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          size="sm"
                          data-touch-target="true"
                        />
                      </InputRightElement>
                    </InputGroup>
                    {errors.confirmPassword && touched.confirmPassword && (
                      <FormErrorMessage fontSize="sm">{errors.confirmPassword}</FormErrorMessage>
                    )}
                    {!errors.confirmPassword && touched.confirmPassword && formData.confirmPassword && formData.password === formData.confirmPassword && (
                      <HStack spacing={1} mt={1}>
                        <Icon as={FiCheck} color="green.500" boxSize={4} />
                        <Text fontSize="xs" color="green.600">Les mots de passe correspondent</Text>
                      </HStack>
                    )}
                  </FormControl>
                </SimpleGrid>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
                  <FormControl isInvalid={!!errors.first_name && touched.first_name}>
                    <FormLabel fontWeight="600" color="gray.700">
                      <HStack spacing={2}>
                        <Icon as={FiUser} color="blue.500" />
                        <Text>Prénom</Text>
                        <Badge colorScheme="gray" fontSize="xs" fontWeight="normal" variant="subtle">optionnel</Badge>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="text"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleChange}
                      onBlur={() => handleBlur('first_name')}
                      placeholder="Prénom"
                      size="lg"
                      borderRadius="xl"
                      autoComplete="given-name"
                      border="2px solid"
                      borderColor={errors.first_name && touched.first_name ? 'red.300' : 'gray.200'}
                      _focus={{
                        borderColor: errors.first_name && touched.first_name ? 'red.500' : 'blue.500',
                        boxShadow: errors.first_name && touched.first_name 
                          ? '0 0 0 3px rgba(229, 62, 62, 0.1)' 
                          : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                      }}
                      _hover={{
                        borderColor: errors.first_name && touched.first_name ? 'red.400' : 'gray.300',
                      }}
                      transition="all 0.2s"
                      data-touch-target="true"
                    />
                    {errors.first_name && touched.first_name && (
                      <FormErrorMessage fontSize="sm">{errors.first_name}</FormErrorMessage>
                    )}
                  </FormControl>

                  <FormControl isInvalid={!!errors.last_name && touched.last_name}>
                    <FormLabel fontWeight="600" color="gray.700">
                      <HStack spacing={2}>
                        <Icon as={FiUser} color="blue.500" />
                        <Text>Nom</Text>
                        <Badge colorScheme="gray" fontSize="xs" fontWeight="normal" variant="subtle">optionnel</Badge>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="text"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleChange}
                      onBlur={() => handleBlur('last_name')}
                      placeholder="Nom"
                      size="lg"
                      borderRadius="xl"
                      autoComplete="family-name"
                      border="2px solid"
                      borderColor={errors.last_name && touched.last_name ? 'red.300' : 'gray.200'}
                      _focus={{
                        borderColor: errors.last_name && touched.last_name ? 'red.500' : 'blue.500',
                        boxShadow: errors.last_name && touched.last_name 
                          ? '0 0 0 3px rgba(229, 62, 62, 0.1)' 
                          : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                      }}
                      _hover={{
                        borderColor: errors.last_name && touched.last_name ? 'red.400' : 'gray.300',
                      }}
                      transition="all 0.2s"
                      data-touch-target="true"
                    />
                    {errors.last_name && touched.last_name && (
                      <FormErrorMessage fontSize="sm">{errors.last_name}</FormErrorMessage>
                    )}
                  </FormControl>
                </SimpleGrid>

                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3}>
                  <FormControl isInvalid={!!errors.phone && touched.phone}>
                    <FormLabel fontWeight="600" color="gray.700">
                      <HStack spacing={2}>
                        <Icon as={FiPhone} color="blue.500" />
                        <Text>Téléphone</Text>
                        <Badge colorScheme="gray" fontSize="xs" fontWeight="normal" variant="subtle">optionnel</Badge>
                      </HStack>
                    </FormLabel>
                    <Input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      onBlur={() => handleBlur('phone')}
                      placeholder="+33 6 12 34 56 78"
                      size="lg"
                      borderRadius="xl"
                      autoComplete="tel"
                      border="2px solid"
                      borderColor={errors.phone && touched.phone ? 'red.300' : 'gray.200'}
                      _focus={{
                        borderColor: errors.phone && touched.phone ? 'red.500' : 'blue.500',
                        boxShadow: errors.phone && touched.phone 
                          ? '0 0 0 3px rgba(229, 62, 62, 0.1)' 
                          : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                      }}
                      _hover={{
                        borderColor: errors.phone && touched.phone ? 'red.400' : 'gray.300',
                      }}
                      transition="all 0.2s"
                      data-touch-target="true"
                    />
                    {errors.phone && touched.phone && (
                      <FormErrorMessage fontSize="sm">{errors.phone}</FormErrorMessage>
                    )}
                  </FormControl>

                  <FormControl>
                    <FormLabel fontWeight="600" color="gray.700">
                      <HStack spacing={2}>
                        <Icon as={FiMapPin} color="blue.500" />
                        <Text>Pays</Text>
                        <Badge colorScheme="gray" fontSize="xs" fontWeight="normal" variant="subtle">optionnel</Badge>
                      </HStack>
                    </FormLabel>
                    <Select
                      name="country"
                      value={formData.country}
                      onChange={handleChange}
                      placeholder="Sélectionnez votre pays"
                      size="lg"
                      borderRadius="xl"
                      autoComplete="country-name"
                      border="2px solid"
                      borderColor="gray.200"
                      _focus={{
                        borderColor: 'blue.500',
                        boxShadow: '0 0 0 3px rgba(37, 99, 235, 0.1)',
                      }}
                      _hover={{
                        borderColor: 'gray.300',
                      }}
                      transition="all 0.2s"
                      data-touch-target="true"
                    >
                      {countries.map((country) => (
                        <option key={country.code} value={country.name}>
                          {country.name}
                        </option>
                      ))}
                    </Select>
                  </FormControl>
                </SimpleGrid>

                <Button
                  type="submit"
                  colorScheme="blue"
                  size="lg"
                  width="full"
                  isLoading={isLoading}
                  loadingText="Inscription en cours..."
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
                  mt={4}
                  data-touch-target="true"
                >
                  Créer mon compte
                </Button>
              </VStack>
            </form>

            <Divider borderColor="gray.200" />

            {/* Lien vers connexion */}
            <Text textAlign="center" color="gray.600" fontSize={{ base: 'sm', md: 'md' }}>
              Déjà un compte ?{' '}
              <Link to="/login">
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
                  Se connecter
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

export default Register
