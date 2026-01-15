import { useState } from 'react'
import { 
  Container, 
  Box, 
  VStack, 
  Heading, 
  Card, 
  CardBody, 
  FormControl, 
  FormLabel, 
  Input, 
  Button, 
  Text, 
  Alert, 
  AlertIcon,
  FormErrorMessage,
  FormHelperText,
  Select,
  SimpleGrid,
  useColorModeValue,
  Divider,
  HStack
} from '@chakra-ui/react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import { useNotification } from '../components/NotificationProvider'
import api from '../services/api'
import { countries } from '../constants/countries'
import { useQuery, useQueryClient } from 'react-query'

const Settings = () => {
  const { t } = useTranslation()
  const { showNotification } = useNotification()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  // Récupérer les informations complètes de l'utilisateur (désactivé car auth supprimée)
  const { data: userData } = useQuery(
    'user-profile',
    async () => {
      // Retourner des données par défaut car auth supprimée
      return {
        username: 'Utilisateur',
        email: 'user@example.com',
        first_name: 'Utilisateur',
        last_name: 'Anonyme'
      }
    },
    {
      enabled: false, // Désactivé car auth supprimée
      refetchOnWindowFocus: false,
    }
  )

  const displayUser = userData || user

  const [formData, setFormData] = useState({
    email: displayUser?.email || '',
    username: displayUser?.username || '',
    first_name: displayUser?.first_name || '',
    last_name: displayUser?.last_name || '',
    date_of_birth: displayUser?.date_of_birth || '',
    country: displayUser?.country || '',
    phone: displayUser?.phone || '',
    password: '',
    confirmPassword: '',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(false)

  const validateField = (name: string, value: string): string => {
    switch (name) {
      case 'email':
        if (!value) return 'L\'email est requis'
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(value)) return 'Format d\'email invalide'
        return ''
      case 'username':
        if (!value) return 'Le nom d\'utilisateur est requis'
        if (value.length < 3) return 'Le nom d\'utilisateur doit contenir au moins 3 caractères'
        if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'Le nom d\'utilisateur ne peut contenir que des lettres, chiffres et underscores'
        return ''
      case 'first_name':
        if (!value) return 'Le prénom est requis'
        if (value.length < 2) return 'Le prénom doit contenir au moins 2 caractères'
        return ''
      case 'last_name':
        if (!value) return 'Le nom est requis'
        if (value.length < 2) return 'Le nom doit contenir au moins 2 caractères'
        return ''
      case 'date_of_birth':
        if (!value) return 'La date de naissance est requise'
        const birthDate = new Date(value)
        const today = new Date()
        const age = (today.getTime() - birthDate.getTime()) / (1000 * 60 * 60 * 24 * 365.25)
        if (age < 13) return 'Vous devez avoir au moins 13 ans'
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
        if (value && value.length < 8) return 'Le mot de passe doit contenir au moins 8 caractères'
        if (value && !/[A-Z]/.test(value)) return 'Le mot de passe doit contenir au moins une majuscule'
        if (value && !/[a-z]/.test(value)) return 'Le mot de passe doit contenir au moins une minuscule'
        if (value && !/[0-9]/.test(value)) return 'Le mot de passe doit contenir au moins un chiffre'
        if (value && !/[^A-Za-z0-9]/.test(value)) return 'Le mot de passe doit contenir au moins un caractère spécial'
        return ''
      case 'confirmPassword':
        if (formData.password && value !== formData.password) return 'Les mots de passe ne correspondent pas'
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Valider tous les champs
    const newErrors: Record<string, string> = {}
    Object.keys(formData).forEach((key) => {
      if (key !== 'confirmPassword') {
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
      // Préparer les données de mise à jour (exclure les champs vides et confirmPassword)
      const updateData: any = {}
      if (formData.email !== displayUser?.email) updateData.email = formData.email
      if (formData.username !== displayUser?.username) updateData.username = formData.username
      if (formData.first_name !== displayUser?.first_name) updateData.first_name = formData.first_name
      if (formData.last_name !== displayUser?.last_name) updateData.last_name = formData.last_name
      if (formData.date_of_birth !== displayUser?.date_of_birth) updateData.date_of_birth = formData.date_of_birth
      if (formData.country !== displayUser?.country) updateData.country = formData.country
      if (formData.phone !== displayUser?.phone) updateData.phone = formData.phone
      if (formData.password) updateData.password = formData.password

      const response = await api.put('/auth/me', updateData)
      const updatedUser = response.data

      // Mettre à jour le store
      setAuth(updatedUser, useAuthStore.getState().token || '')

      // Invalider le cache pour forcer le rafraîchissement
      queryClient.invalidateQueries(['user-profile'])

      showNotification('Informations mises à jour avec succès', 'success')
      navigate('/profile')
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Erreur lors de la mise à jour'
      showNotification(errorMessage, 'error')
      setErrors({ general: errorMessage })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box minH="calc(100vh - 80px)" py={{ base: 6, md: 8 }} px={{ base: 4, md: 0 }} bg="gray.50">
      <Container maxW="800px" px={{ base: 4, md: 6 }}>
        <VStack spacing={{ base: 4, md: 6 }} align="stretch">
          {/* En-tête */}
          <Box>
            <HStack justify="space-between" align="center" flexWrap="wrap" gap={4}>
              <Heading 
                size={{ base: 'lg', md: 'xl' }}
                bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                bgClip="text"
                className="gradient-text"
              >
                Paramètres
              </Heading>
              <Button
                variant="ghost"
                onClick={() => navigate('/profile')}
                size={{ base: 'sm', md: 'md' }}
              >
                Retour au profil
              </Button>
            </HStack>
            <Text color="gray.600" fontSize={{ base: 'sm', md: 'md' }} mt={2}>
              Modifiez vos informations personnelles
            </Text>
          </Box>

          {/* Formulaire */}
          <Card bg={bgColor} border="1px solid" borderColor={borderColor} borderRadius="2xl" boxShadow="lg">
            <CardBody p={{ base: 6, md: 8 }}>
              {errors.general && (
                <Alert status="error" borderRadius="md" variant="left-accent" fontSize="sm" mb={6}>
                  <AlertIcon />
                  {errors.general}
                </Alert>
              )}

              <form onSubmit={handleSubmit}>
                <VStack spacing={6} align="stretch">
                  {/* Informations de base */}
                  <Box>
                    <Heading size="md" mb={4} color="gray.700">
                      Informations de base
                    </Heading>
                    <VStack spacing={4}>
                      <FormControl isInvalid={!!errors.email} isRequired>
                        <FormLabel fontWeight="semibold" color="gray.700">
                          Email
                        </FormLabel>
                        <Input
                          type="email"
                          name="email"
                          value={formData.email}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          placeholder="exemple@email.com"
                          size="lg"
                          fontSize={{ base: '16px', md: '14px' }}
                          minH="48px"
                          bg="white"
                          border="2px solid"
                          borderColor={errors.email ? 'red.300' : 'gray.200'}
                          _focus={{
                            borderColor: errors.email ? 'red.500' : 'gray.500',
                            boxShadow: '0 0 0 3px rgba(128, 128, 128, 0.1)',
                          }}
                        />
                        {errors.email && (
                          <FormErrorMessage fontSize="sm">{errors.email}</FormErrorMessage>
                        )}
                      </FormControl>

                      <FormControl isInvalid={!!errors.username} isRequired>
                        <FormLabel fontWeight="semibold" color="gray.700">
                          Nom d'utilisateur
                        </FormLabel>
                        <Input
                          type="text"
                          name="username"
                          value={formData.username}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          placeholder="nom_utilisateur"
                          size="lg"
                          fontSize={{ base: '16px', md: '14px' }}
                          minH="48px"
                          bg="white"
                          border="2px solid"
                          borderColor={errors.username ? 'red.300' : 'gray.200'}
                          _focus={{
                            borderColor: errors.username ? 'red.500' : 'gray.500',
                            boxShadow: '0 0 0 3px rgba(128, 128, 128, 0.1)',
                          }}
                        />
                        {errors.username ? (
                          <FormErrorMessage fontSize="sm">{errors.username}</FormErrorMessage>
                        ) : (
                          <FormHelperText fontSize="xs" color="gray.500">
                            Lettres, chiffres et underscores uniquement (min. 3 caractères)
                          </FormHelperText>
                        )}
                      </FormControl>

                      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                        <FormControl isInvalid={!!errors.firstName} isRequired>
                          <FormLabel fontWeight="semibold" color="gray.700">
                            Prénom
                          </FormLabel>
                          <Input
                            type="text"
                            name="first_name"
                            value={formData.first_name}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            placeholder="Votre prénom"
                            size="lg"
                            bg="white"
                            border="2px solid"
                            borderColor={errors.firstName ? 'red.300' : 'gray.200'}
                            _focus={{
                              borderColor: errors.firstName ? 'red.500' : 'gray.500',
                              boxShadow: '0 0 0 3px rgba(128, 128, 128, 0.1)',
                            }}
                          />
                          {errors.firstName && (
                            <FormErrorMessage fontSize="sm">{errors.firstName}</FormErrorMessage>
                          )}
                        </FormControl>

                        <FormControl isInvalid={!!errors.lastName} isRequired>
                          <FormLabel fontWeight="semibold" color="gray.700">
                            Nom
                          </FormLabel>
                          <Input
                            type="text"
                            name="last_name"
                            value={formData.last_name}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            placeholder="Votre nom"
                            size="lg"
                            fontSize={{ base: '16px', md: '14px' }}
                            minH="48px"
                            bg="white"
                            border="2px solid"
                            borderColor={errors.lastName ? 'red.300' : 'gray.200'}
                            _focus={{
                              borderColor: errors.lastName ? 'red.500' : 'gray.500',
                              boxShadow: '0 0 0 3px rgba(128, 128, 128, 0.1)',
                            }}
                          />
                          {errors.lastName && (
                            <FormErrorMessage fontSize="sm">{errors.lastName}</FormErrorMessage>
                          )}
                        </FormControl>
                      </SimpleGrid>
                    </VStack>
                  </Box>

                  <Divider />

                  {/* Informations personnelles */}
                  <Box>
                    <Heading size="md" mb={4} color="gray.700">
                      Informations personnelles
                    </Heading>
                    <VStack spacing={4}>
                      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                        <FormControl isInvalid={!!errors.dateOfBirth} isRequired>
                          <FormLabel fontWeight="semibold" color="gray.700">
                            Date de naissance
                          </FormLabel>
                          <Input
                            type="date"
                            name="date_of_birth"
                            value={formData.date_of_birth}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            size="lg"
                            fontSize={{ base: '16px', md: '14px' }}
                            minH="48px"
                            bg="white"
                            border="2px solid"
                            borderColor={errors.dateOfBirth ? 'red.300' : 'gray.200'}
                            _focus={{
                              borderColor: errors.dateOfBirth ? 'red.500' : 'gray.500',
                              boxShadow: '0 0 0 3px rgba(128, 128, 128, 0.1)',
                            }}
                            max={new Date(new Date().setFullYear(new Date().getFullYear() - 13)).toISOString().split('T')[0]}
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
                          <FormLabel fontWeight="semibold" color="gray.700">
                            Pays
                          </FormLabel>
                          <Select
                            name="country"
                            value={formData.country}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            placeholder="Sélectionnez votre pays"
                            size="lg"
                            fontSize={{ base: '16px', md: '14px' }}
                            minH="48px"
                            bg="white"
                            border="2px solid"
                            borderColor={errors.country ? 'red.300' : 'gray.200'}
                            _focus={{
                              borderColor: errors.country ? 'red.500' : 'gray.500',
                              boxShadow: '0 0 0 3px rgba(128, 128, 128, 0.1)',
                            }}
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
                        <FormLabel fontWeight="semibold" color="gray.700">
                          Numéro de téléphone
                        </FormLabel>
                        <Input
                          type="tel"
                          name="phone"
                          value={formData.phone}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          placeholder="+33 6 12 34 56 78"
                          size="lg"
                          fontSize={{ base: '16px', md: '14px' }}
                          minH="48px"
                          bg="white"
                          border="2px solid"
                          borderColor={errors.phone ? 'red.300' : 'gray.200'}
                          _focus={{
                            borderColor: errors.phone ? 'red.500' : 'gray.500',
                            boxShadow: '0 0 0 3px rgba(128, 128, 128, 0.1)',
                          }}
                        />
                        {errors.phone ? (
                          <FormErrorMessage fontSize="sm">{errors.phone}</FormErrorMessage>
                        ) : (
                          <FormHelperText fontSize="xs" color="gray.500">
                            Format: +33 6 12 34 56 78 ou 0612345678
                          </FormHelperText>
                        )}
                      </FormControl>
                    </VStack>
                  </Box>

                  <Divider />

                  {/* Changement de mot de passe */}
                  <Box>
                    <Heading size="md" mb={4} color="gray.700">
                      Changer le mot de passe
                    </Heading>
                    <Text fontSize="sm" color="gray.600" mb={4}>
                      Laissez vide si vous ne souhaitez pas changer votre mot de passe
                    </Text>
                    <VStack spacing={4}>
                      <FormControl isInvalid={!!errors.password}>
                        <FormLabel fontWeight="semibold" color="gray.700">
                          Nouveau mot de passe
                        </FormLabel>
                        <Input
                          type="password"
                          name="password"
                          value={formData.password}
                          onChange={handleChange}
                          onBlur={handleBlur}
                          placeholder="Laissez vide pour ne pas changer"
                          size="lg"
                          bg="white"
                          border="2px solid"
                          borderColor={errors.password ? 'red.300' : 'gray.200'}
                          _focus={{
                            borderColor: errors.password ? 'red.500' : 'gray.500',
                            boxShadow: '0 0 0 3px rgba(102, 126, 0.1)',
                          }}
                        />
                        {errors.password ? (
                          <FormErrorMessage fontSize="sm">{errors.password}</FormErrorMessage>
                        ) : (
                          <FormHelperText fontSize="xs" color="gray.500">
                            Min. 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre, 1 caractère spécial
                          </FormHelperText>
                        )}
                      </FormControl>

                      {formData.password && (
                        <FormControl isInvalid={!!errors.confirmPassword}>
                          <FormLabel fontWeight="semibold" color="gray.700">
                            Confirmer le mot de passe
                          </FormLabel>
                          <Input
                            type="password"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            placeholder="Confirmez votre nouveau mot de passe"
                            size="lg"
                            fontSize={{ base: '16px', md: '14px' }}
                            minH="48px"
                            bg="white"
                            border="2px solid"
                            borderColor={errors.confirmPassword ? 'red.300' : 'gray.200'}
                            _focus={{
                              borderColor: errors.confirmPassword ? 'red.500' : 'gray.500',
                              boxShadow: '0 0 0 3px rgba(128, 128, 128, 0.1)',
                            }}
                          />
                          {errors.confirmPassword && (
                            <FormErrorMessage fontSize="sm">{errors.confirmPassword}</FormErrorMessage>
                          )}
                        </FormControl>
                      )}
                    </VStack>
                  </Box>

                  {/* Boutons */}
                  <HStack spacing={4} justify={{ base: 'stretch', md: 'flex-end' }} pt={4} flexWrap="wrap">
                    <Button
                      variant="outline"
                      onClick={() => navigate('/profile')}
                      size={{ base: 'md', md: 'lg' }}
                      minH="48px"
                      flex={{ base: 1, md: 'none' }}
                      data-touch-target="true"
                    >
                      Annuler
                    </Button>
                    <Button
                      type="submit"
                      variant="gradient"
                      size={{ base: 'md', md: 'lg' }}
                      minH="48px"
                      flex={{ base: 1, md: 'none' }}
                      data-touch-target="true"
                      isLoading={loading}
                      loadingText="Enregistrement..."
                      fontWeight="bold"
                    >
                      Enregistrer les modifications
                    </Button>
                  </HStack>
                </VStack>
              </form>
            </CardBody>
          </Card>
        </VStack>
      </Container>
    </Box>
  )
}

export default Settings

