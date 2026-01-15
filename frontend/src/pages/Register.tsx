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
  FormErrorMessage, 
  FormHelperText, 
  Divider,
  HStack,
  Flex,
  Select,
  SimpleGrid,
  InputGroup,
  InputRightElement,
  IconButton
} from '@chakra-ui/react'
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/authStore'
import { useNotification } from '../components/NotificationProvider'
import Logo from '../components/Logo'
import { countries } from '../constants/countries'

const Register = () => {
  const { t } = useTranslation()
  const { showNotification } = useNotification()
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    firstName: '',
    lastName: '',
    dateOfBirth: '',
    country: '',
    phone: '',
    password: '',
    confirmPassword: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [currentStep, setCurrentStep] = useState(1)
  const navigate = useNavigate()
  const { register } = useAuthStore()

  const validateField = (name: string, value: string): string => {
    switch (name) {
      case 'email':
        if (!value) return t('auth.emailRequired') || 'L\'email est requis'
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(value)) return t('auth.invalidEmail') || 'Format d\'email invalide'
        return ''
      case 'username':
        if (!value) return t('auth.usernameRequired') || 'Le nom d\'utilisateur est requis'
        if (value.length < 3) return 'Le nom d\'utilisateur doit contenir au moins 3 caractères'
        if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres et underscores'
        return ''
      case 'firstName':
        if (!value) return 'Le prénom est requis'
        if (value.length < 2) return 'Le prénom doit contenir au moins 2 caractères'
        return ''
      case 'lastName':
        if (!value) return 'Le nom est requis'
        if (value.length < 2) return 'Le nom doit contenir au moins 2 caractères'
        return ''
      case 'dateOfBirth':
        if (!value) return 'La date de naissance est requise'
        const birthDate = new Date(value)
        const today = new Date()
        const age = (today.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25)
        if (age < 13) return 'Vous devez avoir au moins 13 ans pour vous inscrire'
        if (age > 120) return 'Date de naissance invalide'
        return ''
      case 'country':
        if (!value) return 'Le pays est requis'
        return ''
      case 'phone':
        if (!value) return 'Le numéro de téléphone est requis'
        // Nettoyer le numéro (supprimer espaces, tirets, parenthèses)
        const cleanedPhone = value.replace(/[\s\-\(\)]/g, '')
        // Accepter deux formats :
        // 1. Format international : +33 6 12 34 56 78 → +33612345678
        // 2. Format français : 0612345678
        const internationalFormat = /^\+[1-9]\d{9,14}$/.test(cleanedPhone) // + suivi de 1-9 puis 9-14 chiffres
        const frenchFormat = /^0[1-9]\d{8}$/.test(cleanedPhone) // 0 suivi de 1-9 puis 8 chiffres
        if (!internationalFormat && !frenchFormat) {
          return 'Format invalide. Utilisez +33 6 12 34 56 78 ou 0612345678'
        }
        return ''
      case 'password':
        if (!value) return 'Le mot de passe est requis'
        if (value.length < 8) return 'Le mot de passe doit contenir au moins 8 caractères'
        if (!/[A-Z]/.test(value)) return 'Le mot de passe doit contenir au moins une majuscule'
        if (!/[a-z]/.test(value)) return 'Le mot de passe doit contenir au moins une minuscule'
        if (!/[0-9]/.test(value)) return 'Le mot de passe doit contenir au moins un chiffre'
        if (!/[^A-Za-z0-9]/.test(value)) return 'Le mot de passe doit contenir au moins un caractère spécial'
        return ''
      case 'confirmPassword':
        if (!value) return 'La confirmation du mot de passe est requise'
        if (value !== formData.password) return 'Les mots de passe ne correspondent pas'
        return ''
      default:
        return ''
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
    
    // Validation en temps réel
    if (errors[name]) {
      const error = validateField(name, value)
      setErrors({
        ...errors,
        [name]: error,
      })
    }
  }

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    const error = validateField(name, value)
    setErrors({
      ...errors,
      [name]: error,
    })
  }

  // Validation des champs d'une étape spécifique
  const validateStep = (step: number): boolean => {
    const stepFields: Record<number, string[]> = {
      1: ['email', 'username', 'firstName', 'lastName'],
      2: ['dateOfBirth', 'country', 'phone'],
      3: ['password', 'confirmPassword'],
    }

    const fieldsToValidate = stepFields[step] || []
    const newErrors: Record<string, string> = {}

    fieldsToValidate.forEach((field) => {
      const error = validateField(field, formData[field as keyof typeof formData])
      if (error) {
        newErrors[field] = error
      }
    })

    setErrors((prev) => ({ ...prev, ...newErrors }))
    return Object.keys(newErrors).length === 0
  }

  // Navigation vers l'étape suivante
  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, 3))
      // Scroll vers le haut sur mobile
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      showNotification('Veuillez remplir correctement tous les champs', 'error')
    }
  }

  // Navigation vers l'étape précédente
  const handlePrevious = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Valider tous les champs
    const newErrors: Record<string, string> = {}
    Object.keys(formData).forEach((key) => {
        const error = validateField(key, formData[key as keyof typeof formData])
        if (error) newErrors[key] = error
    })
    
    setErrors(newErrors)
    
    if (Object.keys(newErrors).length > 0) {
      showNotification('Veuillez corriger les erreurs dans le formulaire', 'error')
      return
    }
    
    setLoading(true)

    try {

      // Inscription
      await register(
        formData.email.trim(),
        formData.username.trim(),
        formData.firstName.trim(),
        formData.lastName.trim(),
        formData.dateOfBirth,
        formData.country.trim(),
        formData.phone.trim(),
        formData.password
      )
      
      showNotification('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success')
      navigate('/login')
    } catch (err: any) {
      console.error('Registration error:', err)
      console.error('Error response:', err.response)
      
      // Extraire le message d'erreur avec plus de détails
      let errorMessage = t('auth.registerError') || 'Erreur lors de l\'inscription'
      
      if (err.response) {
        // Erreur HTTP avec réponse
        const responseData = err.response.data
        const status = err.response.status
        
        // Afficher le message d'erreur détaillé du serveur
        if (responseData?.detail) {
          // Si detail est un tableau (erreurs de validation Pydantic)
          if (Array.isArray(responseData.detail)) {
            const errors = responseData.detail.map((err: any) => {
              const field = err.loc ? err.loc.join('.') : 'champ'
              return `${field}: ${err.msg}`
            }).join(', ')
            errorMessage = `Erreurs de validation: ${errors}`
          } else {
            errorMessage = responseData.detail
          }
        } else if (responseData?.message) {
          errorMessage = responseData.message
        } else if (typeof responseData === 'string') {
          errorMessage = responseData
        } else if (responseData) {
          errorMessage = JSON.stringify(responseData)
        } else {
          errorMessage = err.response.statusText || errorMessage
        }
        
        // Messages spécifiques selon le code d'erreur
        if (status === 503) {
          errorMessage = responseData?.detail || "Service de base de données indisponible. Vérifiez que MongoDB est démarré."
        } else if (status === 400) {
          // Pour les erreurs 400, utiliser le message détaillé déjà extrait ci-dessus
          if (!responseData?.detail && !responseData?.message) {
            errorMessage = "Données invalides. Vérifiez vos informations."
          }
        } else if (status === 500) {
          errorMessage = responseData?.detail || responseData?.message || "Erreur serveur. Vérifiez les logs du backend."
        }
        
        // Afficher aussi dans la console pour le débogage
        console.error('Erreur serveur complète:', {
          status,
          data: responseData,
          headers: err.response.headers
        })
        console.error('Détails de l\'erreur:', JSON.stringify(responseData, null, 2))
      } else if (err.request) {
        // Requête envoyée mais pas de réponse
        errorMessage = "Pas de réponse du serveur. Vérifiez que le backend est démarré."
        console.error('Pas de réponse du serveur:', err.request)
      } else if (err.message) {
        errorMessage = err.message
      }
      
      showNotification(errorMessage, 'error')
      setErrors({ general: errorMessage })
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
      alignItems={{ base: 'flex-start', md: 'center' }}
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

      <Container maxW={{ base: '100%', sm: '560px' }} position="relative" zIndex={1} w="full" px={{ base: 4, sm: 6 }}>
        <Box
          bg="rgba(255, 255, 255, 0.95)"
          backdropFilter="blur(20px)"
          p={{ base: 5, sm: 6, md: 8 }}
          borderRadius={{ base: '2xl', md: '3xl' }}
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
              <Heading id="register-heading"
                size={{ base: 'lg', md: 'xl' }}
                bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                bgClip="text"
                fontWeight="bold"
                letterSpacing="tight"
                className="gradient-text"
                textAlign="center"
              >
                {t('auth.registerTitle')}
              </Heading>
              <Text color="gray.600" fontSize={{ base: 'xs', md: 'sm' }} textAlign="center" fontWeight="medium">
                Créez votre compte Kaïrox et commencez votre apprentissage
              </Text>
            </VStack>

            {/* Indicateur de progression */}
            <Box role="region" aria-label="Progression de l'inscription">
              <Flex justify="space-between" mb={2} role="progressbar" aria-valuemin={1} aria-valuemax={3} aria-valuenow={currentStep}>
                {[1, 2, 3].map((step) => (
                  <Box
                    key={step}
                    flex={1}
                    mx={1}
                    h="2"
                    borderRadius="full"
                    bg={currentStep >= step ? 'gray.600' : 'gray.200'}
                    transition="all 0.3s ease"
                    aria-current={currentStep === step ? 'step' : undefined}
                    role="listitem"
                  />
                ))}
              </Flex>
              <Text fontSize="xs" color="gray.500" textAlign="center" mt={2}>
                Étape {currentStep} sur 3
              </Text>
            </Box>
          
          {errors.general && (
              <Alert 
                status="error" 
                borderRadius="md"
                variant="left-accent"
                fontSize="sm"
                id="register-error"
                role="alert"
                aria-live="assertive"
              >
              <AlertIcon />
              {errors.general}
            </Alert>
          )}

          <form role="form" onSubmit={async (e) => { 
            e.preventDefault(); 
            if (currentStep === 3) {
              await handleSubmit(e);
            } else {
              handleNext();
            }
          }} style={{ width: '100%' }} aria-labelledby="register-heading" aria-describedby={errors.general ? 'register-error' : undefined}>
            <VStack spacing={5}>
              {/* Étape 1 : Informations de base */}
              {currentStep === 1 && (
                <>
                <FormControl isInvalid={!!errors.email} isRequired>
                  <FormLabel htmlFor="register-email" fontWeight="semibold" color="gray.700">
                    {t('auth.email')}
                  </FormLabel>
                <Input
                  id="register-email"
                  type="email"
                  name="email"
                  aria-required={true}
                  value={formData.email}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  placeholder="exemple@email.com"
                  size="lg"
                    bg="white"
                    border="2px solid"
                    borderColor={errors.email ? 'red.300' : 'gray.200'}
                    _hover={{
                      borderColor: errors.email ? 'red.400' : '#667eea'
                    }}
                    _focus={{
                      borderColor: errors.email ? 'red.500' : '#667eea',
                      boxShadow: errors.email 
                        ? '0 0 0 3px rgba(229, 62, 62, 0.1)' 
                        : '0 0 0 3px rgba(102, 126, 234, 0.1)'
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                  required
                />
                  {errors.email && (
                    <FormErrorMessage fontSize="sm">{errors.email}</FormErrorMessage>
                  )}
              </FormControl>

                <FormControl isInvalid={!!errors.username} isRequired>
                  <FormLabel htmlFor="register-username" fontWeight="semibold" color="gray.700">
                    {t('auth.username')}
                  </FormLabel>
                <Input
                  id="register-username"
                  name="username"
                  type="text"
                  aria-required={true}
                  value={formData.username}
                  onChange={handleChange}
                  onBlur={handleBlur}
                  placeholder="nom_utilisateur"
                  size="lg"
                    bg="white"
                    border="2px solid"
                    borderColor={errors.username ? 'red.300' : 'gray.200'}
                    _hover={{
                      borderColor: errors.username ? 'red.400' : '#667eea'
                    }}
                    _focus={{
                      borderColor: errors.username ? 'red.500' : '#667eea',
                      boxShadow: errors.username 
                        ? '0 0 0 3px rgba(229, 62, 62, 0.1)'
                        : '0 0 0 3px rgba(102, 126, 234, 0.1)',
                      transform: 'scale(1.01)'
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                  required
                />
                {errors.username ? (
                    <FormErrorMessage fontSize="sm">{errors.username}</FormErrorMessage>
                ) : (
                    <FormHelperText fontSize="xs" color="gray.500">
                      Lettres, chiffres et underscores uniquement (min. 3 caractères)
                    </FormHelperText>
                )}
              </FormControl>

              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={5}>
                <FormControl isInvalid={!!errors.firstName} isRequired>
                  <FormLabel htmlFor="register-firstName" fontWeight="semibold" color="gray.700">
                    Prénom
                  </FormLabel>
                  <Input
                    id="register-firstName"
                    name="firstName"
                    type="text"
                    aria-required={true}
                    value={formData.firstName}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="Votre prénom"
                    size="lg"
                    bg="white"
                    border="2px solid"
                    borderColor={errors.firstName ? 'red.300' : 'gray.200'}
                    _hover={{
                      borderColor: errors.firstName ? 'red.400' : '#667eea'
                    }}
                    _focus={{
                      borderColor: errors.firstName ? 'red.500' : '#667eea',
                      boxShadow: errors.firstName 
                        ? '0 0 0 3px rgba(229, 62, 62, 0.1)'
                        : '0 0 0 3px rgba(102, 126, 234, 0.1)',
                      transform: 'scale(1.01)'
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                    required
                  />
                  {errors.firstName && (
                    <FormErrorMessage fontSize="sm">{errors.firstName}</FormErrorMessage>
                  )}
                </FormControl>

                <FormControl isInvalid={!!errors.lastName} isRequired>
                  <FormLabel htmlFor="register-lastName" fontWeight="semibold" color="gray.700">
                    Nom
                  </FormLabel>
                <Input
                  aria-required={true}
                  id="register-lastName"
                  name="lastName"
                  type="text"
                    value={formData.lastName}
                  onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="Votre nom"
                  size="lg"
                    bg="white"
                    border="2px solid"
                    borderColor={errors.lastName ? 'red.300' : 'gray.200'}
                    _hover={{
                      borderColor: errors.lastName ? 'red.400' : '#667eea'
                    }}
                    _focus={{
                      borderColor: errors.lastName ? 'red.500' : '#667eea',
                      boxShadow: errors.lastName 
                        ? '0 0 0 3px rgba(229, 62, 62, 0.1)'
                        : '0 0 0 3px rgba(102, 126, 234, 0.1)',
                      transform: 'scale(1.01)'
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                    required
                  />
                  {errors.lastName && (
                    <FormErrorMessage fontSize="sm">{errors.lastName}</FormErrorMessage>
                  )}
              </FormControl>
              </SimpleGrid>
                </>
              )}

              {/* Étape 2 : Informations personnelles */}
              {currentStep === 2 && (
                <>
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={5}>
                <FormControl isInvalid={!!errors.dateOfBirth} isRequired>
                  <FormLabel htmlFor="register-dateOfBirth" fontWeight="semibold" color="gray.700">
                    Date de naissance
                  </FormLabel>
                  <Input
                    aria-required={true}
                    id="register-dateOfBirth"
                    name="dateOfBirth"
                    type="date"
                    value={formData.dateOfBirth}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    size="lg"
                    bg="white"
                    border="2px solid"
                    borderColor={errors.dateOfBirth ? 'red.300' : 'gray.200'}
                    _hover={{
                      borderColor: errors.dateOfBirth ? 'red.400' : '#667eea'
                    }}
                    _focus={{
                      borderColor: errors.dateOfBirth ? 'red.500' : '#667eea',
                      boxShadow: errors.dateOfBirth 
                        ? '0 0 0 3px rgba(229, 62, 62, 0.1)' 
                        : '0 0 0 3px rgba(102, 126, 234, 0.1)',
                      transform: 'scale(1.01)'
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                    max={new Date(new Date().setFullYear(new Date().getFullYear() - 13)).toISOString().split('T')[0]}
                    required
                  />
                  {errors.dateOfBirth ? (
                    <FormErrorMessage fontSize="sm">{errors.dateOfBirth}</FormErrorMessage>
                  ) : (
                    <FormHelperText fontSize="xs" color="gray.500">
                      Vous devez avoir au moins 13 ans
                    </FormHelperText>
                  )}
                </FormControl>

                <FormControl isInvalid={!!errors.country} isRequired>
                  <FormLabel htmlFor="register-country" fontWeight="semibold" color="gray.700">
                    Pays
                  </FormLabel>
                  <Select
                    id="register-country"
                    name="country"
                    aria-required={true}
                    value={formData.country}
                    onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="Sélectionnez votre pays"
                    size="lg"
                    bg="white"
                    border="2px solid"
                    borderColor={errors.country ? 'red.300' : 'gray.200'}
                    _hover={{
                      borderColor: errors.country ? 'red.400' : '#667eea'
                    }}
                    _focus={{
                      borderColor: errors.country ? 'red.500' : '#667eea',
                      boxShadow: errors.country 
                        ? '0 0 0 3px rgba(229, 62, 62, 0.1)'
                        : '0 0 0 3px rgba(102, 126, 234, 0.1)',
                      transform: 'scale(1.01)'
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                    required
                  >
                    {countries.map((country) => (
                      <option key={country.code} value={country.code}>
                        {country.name}
                      </option>
                    ))}
                  </Select>
                  {errors.country && (
                    <FormErrorMessage fontSize="sm">{errors.country}</FormErrorMessage>
                  )}
                </FormControl>
              </SimpleGrid>

                <FormControl isInvalid={!!errors.phone} isRequired>
                  <FormLabel htmlFor="register-phone" fontWeight="semibold" color="gray.700">
                    Numéro de téléphone
                  </FormLabel>
                  <Input
                    aria-required={true}
                    id="register-phone"
                    name="phone"
                    type="tel"
                    value={formData.phone}
                  onChange={handleChange}
                    onBlur={handleBlur}
                    placeholder="+33 6 12 34 56 78"
                  size="lg"
                    bg="white"
                    border="2px solid"
                    borderColor={errors.phone ? 'red.300' : 'gray.200'}
                    _hover={{
                      borderColor: errors.phone ? 'red.400' : '#667eea'
                    }}
                    _focus={{
                      borderColor: errors.phone ? 'red.500' : '#667eea',
                      boxShadow: errors.phone 
                        ? '0 0 0 3px rgba(229, 62, 62, 0.1)'
                        : '0 0 0 3px rgba(102, 126, 234, 0.1)',
                      transform: 'scale(1.01)'
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                    required
                  />
                  {errors.phone ? (
                    <FormErrorMessage fontSize="sm">{errors.phone}</FormErrorMessage>
                  ) : (
                    <FormHelperText fontSize="xs" color="gray.500">
                      Format: +33 6 12 34 56 78 ou 0612345678
                    </FormHelperText>
                )}
              </FormControl>
                </>
              )}

              {/* Étape 3 : Mot de passe */}
              {currentStep === 3 && (
                <>
                <FormControl isInvalid={!!errors.password} isRequired>
                  <FormLabel htmlFor="register-password" fontWeight="semibold" color="gray.700">
                    Mot de passe
                  </FormLabel>
                  <InputGroup size="lg">
                    <Input
                      aria-required={true}
                      id="register-password"
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      placeholder="Votre mot de passe"
                      bg="white"
                      border="2px solid"
                      borderColor={errors.password ? 'red.300' : 'gray.200'}
                      _hover={{
                        borderColor: errors.password ? 'red.400' : '#667eea'
                      }}
                      _focus={{
                        borderColor: errors.password ? 'red.500' : '#667eea',
                        boxShadow: errors.password 
                          ? '0 0 0 3px rgba(229, 62, 62, 0.1)'
                          : '0 0 0 3px rgba(102, 126, 234, 0.1)',
                        transform: 'scale(1.01)'
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
                {errors.password ? (
                    <FormErrorMessage fontSize="sm">{errors.password}</FormErrorMessage>
                ) : (
                    <FormHelperText fontSize="xs" color="gray.500">
                      Au moins 8 caractères avec majuscule, minuscule, chiffre et caractère spécial
                    </FormHelperText>
                )}
              </FormControl>

                <FormControl isInvalid={!!errors.confirmPassword} isRequired>
                  <FormLabel htmlFor="register-confirmPassword" fontWeight="semibold" color="gray.700">
                    Confirmer le mot de passe
                  </FormLabel>
                  <InputGroup size="lg">
                    <Input
                      aria-required={true}
                      id="register-confirmPassword"
                      name="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      placeholder="Confirmez votre mot de passe"
                      bg="white"
                      border="2px solid"
                      borderColor={errors.confirmPassword ? 'red.300' : 'gray.200'}
                      _hover={{
                        borderColor: errors.confirmPassword ? 'red.400' : '#667eea'
                      }}
                      _focus={{
                        borderColor: errors.confirmPassword ? 'red.500' : '#667eea',
                        boxShadow: errors.confirmPassword 
                          ? '0 0 0 3px rgba(229, 62, 62, 0.1)' 
                          : '0 0 0 3px rgba(102, 126, 234, 0.1)',
                        transform: 'scale(1.01)'
                      }}
                      transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                      required
                    />
                    <InputRightElement width="4.5rem">
                      <IconButton
                        aria-label={showConfirmPassword ? 'Masquer la confirmation' : 'Afficher la confirmation'}
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
                  {errors.confirmPassword ? (
                    <FormErrorMessage fontSize="sm">{errors.confirmPassword}</FormErrorMessage>
                  ) : (
                    <FormHelperText fontSize="xs" color="gray.500">
                      Saisissez à nouveau votre mot de passe pour confirmer
                    </FormHelperText>
                  )}
                </FormControl>
                </>
              )}

              {/* Boutons de navigation */}
              <HStack spacing={4} width="full" mt={4}>
                {currentStep > 1 && (
                  <Button
                    type="button"
                    variant="outline"
                    borderColor="#667eea"
                    color="#667eea"
                    width={{ base: 'full', md: 'auto' }}
                    flex={{ base: 1, md: 'none' }}
                    onClick={handlePrevious}
                    size="lg"
                    fontWeight="semibold"
                    _hover={{
                      bg: 'rgba(102, 126, 234, 0.1)',
                      borderColor: '#764ba2',
                      color: '#764ba2',
                      transform: 'translateY(-2px)',
                    }}
                    _active={{
                      transform: 'translateY(0)',
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                  >
                    Précédent
                  </Button>
                )}
              <Button
                type="submit"
                bgGradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                color="white"
                width={{ base: 'full', md: currentStep > 1 ? 'auto' : 'full' }}
                flex={{ base: 1, md: currentStep > 1 ? 'none' : 'none' }}
                size="lg"
                isLoading={loading && currentStep === 3}
                aria-label={currentStep === 3 ? t('auth.signUp') : 'Suivant'}
                loadingText="Inscription en cours..."
                isDisabled={loading && currentStep === 3}
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
                {currentStep === 3 ? t('auth.signUp') : 'Suivant'}
              </Button>
              </HStack>
            </VStack>
          </form>

            <Divider />


            {/* Lien vers la connexion */}
            <HStack justify="center" spacing={1}>
              <Text color="gray.600" fontSize="sm">
                {t('auth.hasAccount')}
              </Text>
              <Link 
                as={RouterLink} 
                to="/login" 
                color="gray.600"
                fontWeight="semibold"
                _hover={{
                  color: 'gray.700',
                  textDecoration: 'underline'
                }}
                transition="color 0.2s"
              >
              {t('auth.signIn')}
            </Link>
            </HStack>
        </VStack>
      </Box>
    </Container>
    </Box>
  )
}

export default Register

