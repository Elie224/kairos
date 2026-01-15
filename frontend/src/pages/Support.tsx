import { useState } from 'react'
import { 
  Container, 
  Box, 
  VStack, 
  Heading, 
  Text, 
  Card, 
  CardBody, 
  FormControl, 
  FormLabel, 
  Input, 
  Textarea,
  Button, 
  Alert, 
  AlertIcon,
  FormErrorMessage,
  SimpleGrid,
  useColorModeValue,
  HStack,
  Icon,
  Badge,
  Divider
} from '@chakra-ui/react'
import { FiMail, FiPhone, FiMessageSquare, FiHeart, FiCode, FiDollarSign, FiUsers, FiArrowRight } from 'react-icons/fi'
import { useTranslation } from 'react-i18next'
import { useNotification } from '../components/NotificationProvider'
import api from '../services/api'

const Support = () => {
  const { t } = useTranslation()
  const { showNotification } = useNotification()
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: '',
    supportType: 'general', // general, financial, technical, partnership
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  const validateField = (name: string, value: string): string => {
    switch (name) {
      case 'name':
        if (!value) return 'Le nom est requis'
        if (value.length < 2) return 'Le nom doit contenir au moins 2 caractères'
        return ''
      case 'email':
        if (!value) return 'L\'email est requis'
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(value)) return 'Format d\'email invalide'
        return ''
      case 'phone':
        if (value) {
          const cleanedPhone = value.replace(/[\s\-\(\)]/g, '')
          const internationalFormat = /^\+[1-9]\d{9,14}$/.test(cleanedPhone)
          const frenchFormat = /^0[1-9]\d{8}$/.test(cleanedPhone)
          if (!internationalFormat && !frenchFormat) {
            return 'Format invalide. Utilisez +33 6 12 34 56 78 ou 0612345678'
          }
        }
        return ''
      case 'subject':
        if (!value) return 'Le sujet est requis'
        if (value.length < 5) return 'Le sujet doit contenir au moins 5 caractères'
        return ''
      case 'message':
        if (!value) return 'Le message est requis'
        if (value.length < 20) return 'Le message doit contenir au moins 20 caractères'
        return ''
      default:
        return ''
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value,
    })
    
    if (errors[name]) {
      const error = validateField(name, value)
      setErrors({
        ...errors,
        [name]: error,
      })
    }
  }

  const handleBlur = (e: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    const error = validateField(name, value)
    setErrors({
      ...errors,
      [name]: error,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Valider tous les champs
    const newErrors: Record<string, string> = {}
    Object.keys(formData).forEach((key) => {
      if (key !== 'phone' || formData.phone) { // Le téléphone est optionnel
        const error = validateField(key, formData[key as keyof typeof formData])
        if (error) newErrors[key] = error
      }
    })
    
    setErrors(newErrors)
    
    if (Object.keys(newErrors).length > 0) {
      showNotification('Veuillez corriger les erreurs dans le formulaire', 'error')
      return
    }
    
    setLoading(true)

    try {
      // Envoyer le message de soutien
      // Note: Vous devrez créer un endpoint backend pour recevoir ces messages
      // Pour l'instant, on simule l'envoi
      await api.post('/support/contact', formData)
      
      showNotification('Merci pour votre soutien ! Nous vous contacterons bientôt.', 'success')
      
      // Réinitialiser le formulaire
      setFormData({
        name: '',
        email: '',
        phone: '',
        subject: '',
        message: '',
        supportType: 'general',
      })
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Erreur lors de l\'envoi du message'
      showNotification(errorMessage, 'error')
      setErrors({ general: errorMessage })
    } finally {
      setLoading(false)
    }
  }

  const supportTypes = [
    {
      value: 'general',
      label: 'Soutien Général',
      icon: FiHeart,
      description: 'Soutien général au projet',
      color: 'blue',
    },
    {
      value: 'financial',
      label: 'Soutien Financier',
      icon: FiDollarSign,
      description: 'Contribuer financièrement',
      color: 'blue',
    },
    {
      value: 'technical',
      label: 'Soutien Technique',
      icon: FiCode,
      description: 'Aide au développement',
      color: 'blue',
    },
    {
      value: 'partnership',
      label: 'Partenariat',
      icon: FiUsers,
      description: 'Créer un partenariat',
      color: 'blue',
    },
  ]

  return (
    <Box minH="calc(100vh - 80px)" py={{ base: 6, md: 12 }} bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)">
      <Container maxW="1200px">
        <VStack spacing={{ base: 8, md: 10 }} align="stretch">
          {/* En-tête amélioré avec thème bleu */}
          <VStack spacing={6} textAlign="center">
            <Badge 
              fontSize={{ base: 'sm', md: 'md' }} 
              px={4} 
              py={2} 
              borderRadius="full"
              bg="blue.600"
              color="white"
              fontWeight="600"
              boxShadow="md"
            >
              Soutenez Kaïrox
            </Badge>
            <Heading 
              size={{ base: 'xl', md: '2xl' }}
              color="gray.900"
              fontWeight="700"
              letterSpacing="-0.02em"
              fontFamily="heading"
            >
              Aidez-nous à améliorer l'éducation
            </Heading>
            <Text 
              fontSize={{ base: 'md', md: 'lg' }} 
              color="gray.700" 
              maxW="700px"
              lineHeight="1.7"
              letterSpacing="0.01em"
              fontFamily="body"
            >
              Votre soutien nous permet de développer de nouvelles fonctionnalités, améliorer l'expérience utilisateur et rendre l'apprentissage accessible à tous.
            </Text>
          </VStack>

          {/* Types de soutien améliorés avec thème bleu */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            {supportTypes.map((type) => (
              <Card
                key={type.value}
                bg="white"
                border="2px solid"
                borderColor={formData.supportType === type.value ? 'blue.500' : 'blue.100'}
                borderRadius="2xl"
                boxShadow={formData.supportType === type.value ? 'lg' : 'soft'}
                _hover={{
                  transform: 'translateY(-8px) scale(1.02)',
                  boxShadow: 'xl',
                  borderColor: 'blue.400',
                }}
                transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                cursor="pointer"
                onClick={() => setFormData({ ...formData, supportType: type.value })}
                position="relative"
                overflow="hidden"
              >
                {formData.supportType === type.value && (
                  <Box
                    position="absolute"
                    top={0}
                    left={0}
                    right={0}
                    height="4px"
                    bgGradient="linear-gradient(90deg, blue.400, blue.600)"
                  />
                )}
                <CardBody p={6} textAlign="center">
                  <Box
                    p={4}
                    bgGradient={formData.supportType === type.value 
                      ? "linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                      : "linear-gradient(135deg, blue.100 0%, blue.200 100%)"
                    }
                    borderRadius="xl"
                    display="inline-flex"
                    mb={4}
                    boxShadow={formData.supportType === type.value ? 'md' : 'sm'}
                  >
                    <Icon 
                      as={type.icon} 
                      boxSize={6} 
                      color={formData.supportType === type.value ? 'white' : 'blue.600'}
                    />
                  </Box>
                  <Heading 
                    size="sm" 
                    mb={2} 
                    color="gray.900"
                    fontWeight="700"
                    letterSpacing="-0.02em"
                    fontFamily="heading"
                  >
                    {type.label}
                  </Heading>
                  <Text 
                    fontSize="xs" 
                    color="gray.700"
                    fontFamily="body"
                    lineHeight="1.6"
                  >
                    {type.description}
                  </Text>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>

          {/* Formulaire de contact amélioré */}
          <Card 
            bg="white" 
            border="2px solid" 
            borderColor="blue.100" 
            borderRadius="2xl" 
            boxShadow="soft-lg"
          >
            <CardBody p={{ base: 6, md: 8 }}>
              <VStack spacing={3} mb={6}>
                <HStack spacing={3} align="center">
                  <Box
                    p={2}
                    bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                    borderRadius="lg"
                    boxShadow="md"
                  >
                    <Icon as={FiMessageSquare} boxSize={5} color="white" />
                  </Box>
                  <Heading 
                    size="lg" 
                    color="gray.900"
                    fontWeight="700"
                    letterSpacing="-0.02em"
                    fontFamily="heading"
                  >
                    Contactez-nous
                  </Heading>
                </HStack>
              </VStack>

              {errors.general && (
                <Alert 
                  status="error" 
                  borderRadius="xl" 
                  variant="left-accent" 
                  fontSize="sm" 
                  mb={6}
                  bg="red.50"
                  border="1px solid"
                  borderColor="red.200"
                >
                  <AlertIcon color="red.500" />
                  <Text color="gray.800" fontFamily="body" fontWeight="500">{errors.general}</Text>
                </Alert>
              )}

              <form onSubmit={handleSubmit}>
                <VStack spacing={6} align="stretch">
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                    <FormControl isInvalid={!!errors.name} isRequired>
                      <FormLabel 
                        fontWeight="600" 
                        color="gray.800"
                        fontFamily="body"
                      >
                        Nom complet
                      </FormLabel>
                      <Input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        placeholder="Votre nom"
                        size="lg"
                        bg="white"
                        border="2px solid"
                        borderColor={errors.name ? 'red.300' : 'blue.100'}
                        borderRadius="xl"
                        _focus={{
                          borderColor: errors.name ? 'red.500' : 'blue.400',
                          boxShadow: errors.name ? '0 0 0 3px rgba(229, 62, 62, 0.1)' : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                        }}
                        _hover={{
                          borderColor: errors.name ? 'red.400' : 'blue.200',
                        }}
                        transition="all 0.3s"
                        fontFamily="body"
                      />
                      {errors.name && (
                        <FormErrorMessage fontSize="sm" fontFamily="body">{errors.name}</FormErrorMessage>
                      )}
                    </FormControl>

                    <FormControl isInvalid={!!errors.email} isRequired>
                      <FormLabel 
                        fontWeight="600" 
                        color="gray.800"
                        fontFamily="body"
                      >
                        Email
                      </FormLabel>
                      <Input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        onBlur={handleBlur}
                        placeholder="votre@email.com"
                        size="lg"
                        fontSize={{ base: '16px', md: '14px' }}
                        minH="48px"
                        bg="white"
                        border="2px solid"
                        borderColor={errors.email ? 'red.300' : 'blue.100'}
                        borderRadius="xl"
                        _focus={{
                          borderColor: errors.email ? 'red.500' : 'blue.400',
                          boxShadow: errors.email ? '0 0 0 3px rgba(229, 62, 62, 0.1)' : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                        }}
                        _hover={{
                          borderColor: errors.email ? 'red.400' : 'blue.200',
                        }}
                        transition="all 0.3s"
                        fontFamily="body"
                      />
                      {errors.email && (
                        <FormErrorMessage fontSize="sm" fontFamily="body">{errors.email}</FormErrorMessage>
                      )}
                    </FormControl>
                  </SimpleGrid>

                  <FormControl isInvalid={!!errors.phone}>
                    <FormLabel 
                      fontWeight="600" 
                      color="gray.800"
                      fontFamily="body"
                    >
                      Téléphone <Text as="span" color="gray.500" fontSize="sm" fontWeight="400">(optionnel)</Text>
                    </FormLabel>
                    <Input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      placeholder="+33 6 12 34 56 78 ou 0612345678"
                      size="lg"
                      fontSize={{ base: '16px', md: '14px' }}
                      minH="48px"
                      bg="white"
                      border="2px solid"
                      borderColor={errors.phone ? 'red.300' : 'blue.100'}
                      borderRadius="xl"
                      _focus={{
                        borderColor: errors.phone ? 'red.500' : 'blue.400',
                        boxShadow: errors.phone ? '0 0 0 3px rgba(229, 62, 62, 0.1)' : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                      }}
                      _hover={{
                        borderColor: errors.phone ? 'red.400' : 'blue.200',
                      }}
                      transition="all 0.3s"
                      fontFamily="body"
                    />
                    {errors.phone && (
                      <FormErrorMessage fontSize="sm" fontFamily="body">{errors.phone}</FormErrorMessage>
                    )}
                  </FormControl>

                  <FormControl isInvalid={!!errors.subject} isRequired>
                    <FormLabel 
                      fontWeight="600" 
                      color="gray.800"
                      fontFamily="body"
                    >
                      Sujet
                    </FormLabel>
                    <Input
                      type="text"
                      name="subject"
                      value={formData.subject}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      placeholder="Sujet de votre message"
                      size="lg"
                      fontSize={{ base: '16px', md: '14px' }}
                      minH="48px"
                      bg="white"
                      border="2px solid"
                      borderColor={errors.subject ? 'red.300' : 'blue.100'}
                      borderRadius="xl"
                      _focus={{
                        borderColor: errors.subject ? 'red.500' : 'blue.400',
                        boxShadow: errors.subject ? '0 0 0 3px rgba(229, 62, 62, 0.1)' : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                      }}
                      _hover={{
                        borderColor: errors.subject ? 'red.400' : 'blue.200',
                      }}
                      transition="all 0.3s"
                      fontFamily="body"
                    />
                    {errors.subject && (
                      <FormErrorMessage fontSize="sm" fontFamily="body">{errors.subject}</FormErrorMessage>
                    )}
                  </FormControl>

                  <FormControl isInvalid={!!errors.message} isRequired>
                    <FormLabel 
                      fontWeight="600" 
                      color="gray.800"
                      fontFamily="body"
                    >
                      Message
                    </FormLabel>
                    <Textarea
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      onBlur={handleBlur}
                      placeholder="Décrivez comment vous souhaitez soutenir le projet Kaïrox..."
                      size="lg"
                      fontSize={{ base: '16px', md: '14px' }}
                      minH="120px"
                      bg="white"
                      border="2px solid"
                      borderColor={errors.message ? 'red.300' : 'blue.100'}
                      borderRadius="xl"
                      _focus={{
                        borderColor: errors.message ? 'red.500' : 'blue.400',
                        boxShadow: errors.message ? '0 0 0 3px rgba(229, 62, 62, 0.1)' : '0 0 0 3px rgba(37, 99, 235, 0.1)',
                      }}
                      _hover={{
                        borderColor: errors.message ? 'red.400' : 'blue.200',
                      }}
                      transition="all 0.3s"
                      rows={6}
                      resize="vertical"
                      fontFamily="body"
                    />
                    {errors.message ? (
                      <FormErrorMessage fontSize="sm" fontFamily="body">{errors.message}</FormErrorMessage>
                    ) : (
                      <Text fontSize="xs" color="gray.500" mt={1} fontFamily="body">
                        Minimum 20 caractères
                      </Text>
                    )}
                  </FormControl>

                  <Button
                    type="submit"
                    bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                    color="white"
                    size={{ base: 'md', md: 'lg' }}
                    minH="48px"
                    w={{ base: 'full', md: 'auto' }}
                    isLoading={loading}
                    loadingText="Envoi en cours..."
                    fontWeight="600"
                    rightIcon={<FiArrowRight />}
                    py={{ base: 6, md: 7 }}
                    borderRadius="xl"
                    boxShadow="md"
                    _hover={{
                      bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)',
                      transform: { base: 'none', md: 'translateY(-2px)' },
                      boxShadow: 'lg',
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                    fontFamily="body"
                    data-touch-target="true"
                  >
                    Envoyer le message
                  </Button>
                </VStack>
              </form>
            </CardBody>
          </Card>

          {/* Informations supplémentaires améliorées avec thème bleu */}
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
            <Card 
              bg="white" 
              border="2px solid" 
              borderColor="blue.100" 
              borderRadius="2xl"
              boxShadow="soft"
              _hover={{
                transform: 'translateY(-4px)',
                boxShadow: 'lg',
                borderColor: 'blue.300',
              }}
              transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            >
              <CardBody p={6} textAlign="center">
                <Box
                  p={3}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  borderRadius="xl"
                  display="inline-flex"
                  mb={4}
                  boxShadow="md"
                >
                  <Icon as={FiMail} boxSize={5} color="white" />
                </Box>
                <Heading 
                  size="sm" 
                  mb={2}
                  color="gray.900"
                  fontWeight="700"
                  fontFamily="heading"
                >
                  Email
                </Heading>
                <Text 
                  fontSize="sm" 
                  color="gray.700"
                  fontFamily="body"
                  as="a"
                  href="mailto:kouroumaelisee@gmail.com"
                  _hover={{ color: 'blue.600', textDecoration: 'underline' }}
                >
                  kouroumaelisee@gmail.com
                </Text>
              </CardBody>
            </Card>

            <Card 
              bg="white" 
              border="2px solid" 
              borderColor="blue.100" 
              borderRadius="2xl"
              boxShadow="soft"
              _hover={{
                transform: 'translateY(-4px)',
                boxShadow: 'lg',
                borderColor: 'blue.300',
              }}
              transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            >
              <CardBody p={6} textAlign="center">
                <Box
                  p={3}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  borderRadius="xl"
                  display="inline-flex"
                  mb={4}
                  boxShadow="md"
                >
                  <Icon as={FiPhone} boxSize={5} color="white" />
                </Box>
                <Heading 
                  size="sm" 
                  mb={2}
                  color="gray.900"
                  fontWeight="700"
                  fontFamily="heading"
                >
                  Téléphone
                </Heading>
                <Text 
                  fontSize="sm" 
                  color="gray.700"
                  fontFamily="body"
                  as="a"
                  href="tel:+33689306432"
                  _hover={{ color: 'blue.600', textDecoration: 'underline' }}
                >
                  +33 6 89 30 64 32
                </Text>
              </CardBody>
            </Card>

            <Card 
              bg="white" 
              border="2px solid" 
              borderColor="blue.100" 
              borderRadius="2xl"
              boxShadow="soft"
              _hover={{
                transform: 'translateY(-4px)',
                boxShadow: 'lg',
                borderColor: 'blue.300',
              }}
              transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            >
              <CardBody p={6} textAlign="center">
                <Box
                  p={3}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  borderRadius="xl"
                  display="inline-flex"
                  mb={4}
                  boxShadow="md"
                >
                  <Icon as={FiMessageSquare} boxSize={5} color="white" />
                </Box>
                <Heading 
                  size="sm" 
                  mb={2}
                  color="gray.900"
                  fontWeight="700"
                  fontFamily="heading"
                >
                  Réseaux sociaux
                </Heading>
                <Text 
                  fontSize="sm" 
                  color="gray.700"
                  fontFamily="body"
                >
                  @kairos_education
                </Text>
              </CardBody>
            </Card>
          </SimpleGrid>
        </VStack>
      </Container>
    </Box>
  )
}

export default Support

