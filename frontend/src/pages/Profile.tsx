import { useQuery } from 'react-query'
import { 
  Container, 
  Box, 
  VStack, 
  Heading, 
  Card, 
  CardBody, 
  Text, 
  HStack, 
  Badge,
  Avatar,
  SimpleGrid,
  Divider,
  Icon,
  useColorModeValue
} from '@chakra-ui/react'
import { FiUser, FiMail, FiPhone, FiCalendar, FiMapPin, FiEdit } from 'react-icons/fi'
import { useTranslation } from 'react-i18next'
// Auth supprimée - useAuthStore n'existe plus
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { Button } from '@chakra-ui/react'
import { LazyImage } from '../components/LazyImage'
import logoKairos from '../logo_kairos.jpeg'
import { countries } from '../constants/countries'

const Profile = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  // Récupérer les informations complètes de l'utilisateur (désactivé car auth supprimée)
  const { data: userData, isLoading } = useQuery(
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
      refetchOnMount: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    }
  )

  const displayUser = userData || {
    username: 'Utilisateur',
    email: 'user@example.com',
    first_name: 'Utilisateur',
    last_name: 'Anonyme'
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Non renseigné'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('fr-FR', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })
    } catch {
      return dateString
    }
  }

  const getCountryName = (code?: string) => {
    if (!code) return 'Non renseigné'
    try {
      const country = countries.find((c: { code: string }) => c.code === code)
      return country ? country.name : code
    } catch {
      return code
    }
  }

  if (isLoading) {
    return (
      <Box minH="calc(100vh - 80px)" py={8} bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)">
        <Container maxW="1200px">
          <Text color="gray.700" fontFamily="body">Chargement...</Text>
        </Container>
      </Box>
    )
  }

  return (
    <Box minH="calc(100vh - 80px)" py={{ base: 6, md: 8 }} bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)">
      <Container maxW="1200px">
        <VStack spacing={{ base: 6, md: 8 }} align="stretch">
          {/* En-tête amélioré avec thème bleu */}
          <Box>
            <HStack justify="space-between" align="center" flexWrap="wrap" gap={4}>
              <HStack spacing={4} align="center">
                <Box
                  p={3}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  borderRadius="xl"
                  boxShadow="lg"
                >
                  <Icon as={FiUser} boxSize={5} color="white" />
                </Box>
                <Heading 
                  size={{ base: 'lg', md: 'xl' }}
                  color="gray.900"
                  fontWeight="700"
                  letterSpacing="-0.02em"
                  fontFamily="heading"
                >
                  Mon Profil
                </Heading>
              </HStack>
              <Button
                leftIcon={<FiEdit />}
                bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                color="white"
                onClick={() => navigate('/settings')}
                size={{ base: 'sm', md: 'md' }}
                fontWeight="600"
                boxShadow="md"
                _hover={{
                  bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)',
                  transform: 'translateY(-2px)',
                  boxShadow: 'lg',
                }}
                transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
              >
                Modifier
              </Button>
            </HStack>
          </Box>

          {/* Carte principale du profil améliorée */}
          <Card 
            bg="white"
            border="2px solid"
            borderColor="blue.100"
            borderRadius="2xl"
            boxShadow="soft-lg"
          >
            <CardBody p={{ base: 6, md: 8 }}>
              <VStack spacing={6} align="stretch">
                {/* Avatar et nom améliorés */}
                <HStack spacing={6} align="center" flexWrap="wrap">
                  <Box position="relative">
                    <Avatar
                      size={{ base: 'xl', md: '2xl' }}
                      src={logoKairos}
                      name={displayUser?.first_name && displayUser?.last_name 
                        ? `${displayUser.first_name} ${displayUser.last_name}`
                        : displayUser?.username || displayUser?.email}
                      loading="lazy"
                      bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                      border="4px solid"
                      borderColor="blue.100"
                      boxShadow="lg"
                    />
                    <Box
                      position="absolute"
                      bottom={0}
                      right={0}
                      w={6}
                      h={6}
                      bg="blue.500"
                      borderRadius="full"
                      border="3px solid"
                      borderColor="white"
                      boxShadow="md"
                    />
                  </Box>
                  <VStack align="start" spacing={2}>
                    <Heading 
                      size={{ base: 'md', md: 'lg' }}
                      color="gray.900"
                      fontWeight="700"
                      letterSpacing="-0.02em"
                      fontFamily="heading"
                    >
                      {displayUser?.first_name && displayUser?.last_name
                        ? `${displayUser.first_name} ${displayUser.last_name}`
                        : displayUser?.username || 'Utilisateur'}
                    </Heading>
                    <Text 
                      color="gray.600" 
                      fontSize={{ base: 'sm', md: 'md' }}
                      fontFamily="body"
                    >
                      @{displayUser?.username || 'username'}
                    </Text>
                    {displayUser?.is_admin && (
                      <Badge 
                        bg="blue.600"
                        color="white"
                        mt={1}
                        px={3}
                        py={1}
                        borderRadius="full"
                        fontWeight="600"
                        boxShadow="md"
                      >
                        Administrateur
                      </Badge>
                    )}
                  </VStack>
                </HStack>

                <Divider borderColor="blue.100" />

                {/* Informations détaillées avec thème bleu unifié */}
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                  <HStack 
                    spacing={4}
                    p={4}
                    bg="blue.50"
                    borderRadius="xl"
                    border="1px solid"
                    borderColor="blue.100"
                    _hover={{
                      bg: 'blue.100',
                      borderColor: 'blue.200',
                      transform: 'translateX(4px)',
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                  >
                    <Box
                      p={3}
                      borderRadius="xl"
                      bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                      color="white"
                      boxShadow="md"
                    >
                      <Icon as={FiMail} boxSize={5} />
                    </Box>
                    <VStack align="start" spacing={0} flex="1">
                      <Text 
                        fontSize="xs" 
                        color="gray.600" 
                        textTransform="uppercase"
                        fontWeight="600"
                        letterSpacing="wide"
                        fontFamily="body"
                      >
                        Email
                      </Text>
                      <Text 
                        fontWeight="600" 
                        fontSize={{ base: 'sm', md: 'md' }}
                        color="gray.900"
                        fontFamily="body"
                      >
                        {displayUser?.email || 'Non renseigné'}
                      </Text>
                    </VStack>
                  </HStack>

                  <HStack 
                    spacing={4}
                    p={4}
                    bg="blue.50"
                    borderRadius="xl"
                    border="1px solid"
                    borderColor="blue.100"
                    _hover={{
                      bg: 'blue.100',
                      borderColor: 'blue.200',
                      transform: 'translateX(4px)',
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                  >
                    <Box
                      p={3}
                      borderRadius="xl"
                      bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                      color="white"
                      boxShadow="md"
                    >
                      <Icon as={FiPhone} boxSize={5} />
                    </Box>
                    <VStack align="start" spacing={0} flex="1">
                      <Text 
                        fontSize="xs" 
                        color="gray.600" 
                        textTransform="uppercase"
                        fontWeight="600"
                        letterSpacing="wide"
                        fontFamily="body"
                      >
                        Téléphone
                      </Text>
                      <Text 
                        fontWeight="600" 
                        fontSize={{ base: 'sm', md: 'md' }}
                        color="gray.900"
                        fontFamily="body"
                      >
                        {displayUser?.phone || 'Non renseigné'}
                      </Text>
                    </VStack>
                  </HStack>

                  <HStack 
                    spacing={4}
                    p={4}
                    bg="blue.50"
                    borderRadius="xl"
                    border="1px solid"
                    borderColor="blue.100"
                    _hover={{
                      bg: 'blue.100',
                      borderColor: 'blue.200',
                      transform: 'translateX(4px)',
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                  >
                    <Box
                      p={3}
                      borderRadius="xl"
                      bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                      color="white"
                      boxShadow="md"
                    >
                      <Icon as={FiCalendar} boxSize={5} />
                    </Box>
                    <VStack align="start" spacing={0} flex="1">
                      <Text 
                        fontSize="xs" 
                        color="gray.600" 
                        textTransform="uppercase"
                        fontWeight="600"
                        letterSpacing="wide"
                        fontFamily="body"
                      >
                        Date de naissance
                      </Text>
                      <Text 
                        fontWeight="600" 
                        fontSize={{ base: 'sm', md: 'md' }}
                        color="gray.900"
                        fontFamily="body"
                      >
                        {formatDate(displayUser?.date_of_birth)}
                      </Text>
                    </VStack>
                  </HStack>

                  <HStack 
                    spacing={4}
                    p={4}
                    bg="blue.50"
                    borderRadius="xl"
                    border="1px solid"
                    borderColor="blue.100"
                    _hover={{
                      bg: 'blue.100',
                      borderColor: 'blue.200',
                      transform: 'translateX(4px)',
                    }}
                    transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                  >
                    <Box
                      p={3}
                      borderRadius="xl"
                      bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                      color="white"
                      boxShadow="md"
                    >
                      <Icon as={FiMapPin} boxSize={5} />
                    </Box>
                    <VStack align="start" spacing={0} flex="1">
                      <Text 
                        fontSize="xs" 
                        color="gray.600" 
                        textTransform="uppercase"
                        fontWeight="600"
                        letterSpacing="wide"
                        fontFamily="body"
                      >
                        Pays
                      </Text>
                      <Text 
                        fontWeight="600" 
                        fontSize={{ base: 'sm', md: 'md' }}
                        color="gray.900"
                        fontFamily="body"
                      >
                        {getCountryName(displayUser?.country)}
                      </Text>
                    </VStack>
                  </HStack>
                </SimpleGrid>

                {/* Date d'inscription améliorée */}
                <Divider borderColor="blue.100" />
                <HStack 
                  justify="space-between"
                  p={4}
                  bg="blue.50"
                  borderRadius="xl"
                  border="1px solid"
                  borderColor="blue.100"
                >
                  <Text 
                    fontSize="sm" 
                    color="gray.600"
                    fontWeight="600"
                    fontFamily="body"
                  >
                    Membre depuis
                  </Text>
                  <Text 
                    fontSize="sm" 
                    fontWeight="600"
                    color="gray.900"
                    fontFamily="body"
                  >
                    {displayUser?.created_at 
                      ? formatDate(displayUser.created_at)
                      : 'Date inconnue'}
                  </Text>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        </VStack>
      </Container>
    </Box>
  )
}

export default Profile

