/**
 * Page d'accueil - Design moderne et professionnel amélioré
 */
import { Box, Container, Heading, Text, Button, VStack, HStack, SimpleGrid, Badge, Icon, Flex, Card, CardBody, Image, Divider, Skeleton, SkeletonText } from '@chakra-ui/react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FiTarget, FiCpu, FiEye, FiZap, FiUsers, FiAward, FiArrowRight, FiPlay, FiBook, FiCheck, FiTrendingUp, FiClock } from 'react-icons/fi'
import { AnimatedBox } from '../components/AnimatedBox'
import { useQuery } from 'react-query'
import api from '../services/api'
import { useAuthStore } from '../store/authStore'
import { API_TIMEOUTS } from '../constants/api'

const Home = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()

  // Charger les statistiques dynamiques
  const { data: stats, isLoading: statsLoading } = useQuery(
    'home-stats',
    async () => {
          try {
            const response = await api.get('/auth/stats', {
              timeout: API_TIMEOUTS.SIMPLE, // 10 secondes pour les stats home
            })
            return response.data
          } catch {
        // Si l'utilisateur n'est pas admin, retourner des stats par défaut
        return null
      }
    },
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      enabled: isAuthenticated,
      retry: false,
    }
  )

  const handleExploreModules = () => {
    navigate('/modules')
  }

  return (
    <Box>
      {/* Hero Section - Design Premium Amélioré */}
      <Box
        color="white"
        py={{ base: 12, md: 32 }}
        px={{ base: 4, md: 0 }}
        position="relative"
        overflow="hidden"
        minH={{ base: '70vh', md: '90vh' }}
        display="flex"
        alignItems="center"
        backgroundImage="url('/background.jfif')"
        backgroundSize="cover"
        backgroundPosition="center"
        backgroundRepeat="no-repeat"
        data-hero="true"
      >
        {/* Overlay sombre pour améliorer la lisibilité */}
        <Box
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          bgGradient="linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0.5) 50%, rgba(0, 0, 0, 0.6) 100%)"
          zIndex={0}
        />
        
        {/* Effets de fond animés améliorés */}
        <Box
          position="absolute"
          top="-50%"
          left="-50%"
          width="200%"
          height="200%"
          bgGradient="radial(circle, rgba(255,255,255,0.05) 0%, transparent 70%)"
          zIndex={0}
        />
        <Box
          position="absolute"
          bottom="-30%"
          right="-30%"
          width="150%"
          height="150%"
          bgGradient="radial(circle, rgba(255,255,255,0.08) 0%, transparent 70%)"
          zIndex={0}
        />
        <Box
          position="absolute"
          top="20%"
          right="10%"
          width="300px"
          height="300px"
          bgGradient="radial(circle, rgba(255,255,255,0.1) 0%, transparent 70%)"
          borderRadius="full"
          filter="blur(60px)"
          zIndex={0}
        />
        
        <Container maxW="1200px" position="relative" zIndex={1}>
          <VStack spacing={8} textAlign="center">
            <AnimatedBox animation="fadeInUp" delay={0.1}>
              <Badge 
                fontSize={{ base: 'sm', md: 'md' }} 
                px={4} 
                py={2} 
                borderRadius="full"
                bg="whiteAlpha.200"
                color="white"
                fontWeight="700"
                backdropFilter="blur(10px)"
                mb={4}
              >
                🚀 Plateforme d'Apprentissage Intelligente
              </Badge>
            </AnimatedBox>

            <AnimatedBox animation="fadeInUp" delay={0.2}>
              <Heading 
                size={{ base: '2xl', md: '4xl', lg: '5xl' }} 
                fontWeight="extrabold" 
                lineHeight="shorter"
                color="white"
                textShadow="0 4px 20px rgba(0, 0, 0, 0.3)"
                letterSpacing="tight"
                maxW="900px"
              >
                Kairos – Visualisations Interactives & Gamification Pilotées par l'IA
              </Heading>
            </AnimatedBox>
            
            <AnimatedBox animation="fadeInUp" delay={0.3}>
              <Text 
                fontSize={{ base: 'md', md: 'lg', lg: 'xl' }} 
                maxW="900px" 
                lineHeight="tall" 
                color="whiteAlpha.95"
                fontWeight="medium"
                textShadow="0 2px 10px rgba(0, 0, 0, 0.2)"
              >
                Kairos repose sur un modèle OpenAI intelligent capable de générer automatiquement des contenus pédagogiques interactifs, des simulations dynamiques et une gamification adaptative, couvrant les niveaux collège, lycée et université.
              </Text>
            </AnimatedBox>
            
            <AnimatedBox animation="fadeInUp" delay={0.4}>
              <VStack 
                spacing={4} 
                w="full"
                px={{ base: 4, md: 0 }}
                mt={4}
              >
                <Link to="/register" style={{ width: '100%', maxWidth: '400px' }}>
                  <Button
                    size={{ base: 'lg', md: 'xl' }}
                    bg="white"
                    color="purple.600"
                    borderRadius="xl"
                    w="full"
                    minH="50px"
                    _hover={{
                      transform: { base: 'none', md: 'translateY(-4px) scale(1.05)' },
                      boxShadow: '0 25px 50px rgba(0, 0, 0, 0.3)',
                      bg: 'whiteAlpha.95',
                    }}
                    transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
                    fontWeight="bold"
                    px={{ base: 6, md: 8 }}
                    py={{ base: 5, md: 6 }}
                    boxShadow="0 15px 35px rgba(0, 0, 0, 0.3)"
                    rightIcon={<FiArrowRight />}
                    fontSize={{ base: 'md', md: 'lg' }}
                  >
                    Commencer gratuitement
                  </Button>
                </Link>
                <Button
                  size={{ base: 'lg', md: 'xl' }}
                  variant="outline"
                  borderRadius="xl"
                  borderColor="whiteAlpha.600"
                  borderWidth="2px"
                  color="white"
                  w="full"
                  maxW="400px"
                  minH="50px"
                  _hover={{
                    bg: 'whiteAlpha.200',
                    transform: { base: 'none', md: 'translateY(-4px) scale(1.05)' },
                    borderColor: 'white',
                    boxShadow: '0 15px 35px rgba(255, 255, 255, 0.2)',
                  }}
                  transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
                  onClick={handleExploreModules}
                  fontWeight="semibold"
                  px={{ base: 6, md: 8 }}
                  py={{ base: 5, md: 6 }}
                  leftIcon={<FiPlay />}
                  fontSize={{ base: 'md', md: 'lg' }}
                >
                  Explorer les modules
                </Button>
              </VStack>
            </AnimatedBox>

            {/* Statistiques rapides - Dynamiques si disponibles */}
            <AnimatedBox animation="fadeInUp" delay={0.5}>
              <SimpleGrid 
                columns={{ base: 3, md: 3 }} 
                spacing={6} 
                w="full"
                maxW="700px"
                mt={8}
              >
                {statsLoading ? (
                  // Skeleton pendant le chargement
                  Array.from({ length: 3 }).map((_, idx) => (
                    <Skeleton
                      key={idx}
                      height="100px"
                      borderRadius="xl"
                      startColor="whiteAlpha.200"
                      endColor="whiteAlpha.100"
                    />
                  ))
                ) : (
                  [
                    { 
                      icon: FiUsers, 
                      value: stats?.total_users ? `${stats.total_users}+` : '100%', 
                      label: stats?.total_users ? 'Utilisateurs' : 'Gratuit' 
                    },
                    { 
                      icon: FiBook, 
                      value: stats?.total_modules ? `${stats.total_modules}+` : 'IA', 
                      label: stats?.total_modules ? 'Modules' : 'Tutorat Intelligent' 
                    },
                    { 
                      icon: FiTrendingUp, 
                      value: stats?.active_users ? `${stats.active_users}+` : '24/7', 
                      label: stats?.active_users ? 'Actifs' : 'Disponible' 
                    },
                  ].map((stat, idx) => (
                    <Box
                      key={idx}
                      p={4}
                      borderRadius="xl"
                      bg="whiteAlpha.15"
                      backdropFilter="blur(20px)"
                      border="1px solid rgba(255, 255, 255, 0.2)"
                      textAlign="center"
                      _hover={{
                        bg: 'whiteAlpha.25',
                        transform: 'translateY(-4px)',
                        borderColor: 'rgba(255, 255, 255, 0.4)',
                      }}
                      transition="all 0.3s ease"
                    >
                      <Icon as={stat.icon} boxSize={6} mb={2} color="white" />
                      <Text fontSize="xl" fontWeight="bold" mb={1} color="white">{stat.value}</Text>
                      <Text fontSize="xs" color="whiteAlpha.90" fontWeight="medium">{stat.label}</Text>
                    </Box>
                  ))
                )}
              </SimpleGrid>
            </AnimatedBox>
          </VStack>
        </Container>
      </Box>

      {/* Section Matières - Design Amélioré */}
      <Box 
        bg="white"
        py={{ base: 12, md: 20 }}
        position="relative"
      >
        <Container maxW="1200px">
          <VStack spacing={6} mb={12}>
            <Badge 
              fontSize={{ base: 'sm', md: 'md' }} 
              px={4} 
              py={2} 
              borderRadius="full"
              bgGradient="linear(to-r, blue.500, purple.500)"
              color="white"
              fontWeight="700"
              boxShadow="md"
            >
              Nos Matières
            </Badge>
            <Heading 
              size={{ base: 'xl', md: '2xl', lg: '3xl' }} 
              textAlign="center" 
              color="gray.900"
              fontWeight="800"
              letterSpacing="tight"
            >
              Multiples Disciplines d'Excellence
            </Heading>
            <Text 
              fontSize={{ base: 'md', md: 'lg' }} 
              color="gray.600" 
              textAlign="center" 
              maxW="800px"
              lineHeight="1.8"
            >
              Explorez nos modules couvrant les niveaux collège, lycée et université : Mathématiques avancées, Physique classique & quantique, Chimie complète, Informatique & IA, Biologie, Géographie, Économie et Histoire
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8}>
            {[
              {
                emoji: '📐',
                title: 'Mathématiques',
                subtitle: 'Algèbre',
                description: 'Maîtrisez l\'algèbre de A à Z : équations linéaires, polynômes, factorisation, systèmes d\'équations, matrices et algèbre linéaire.',
                features: [
                  'Équations et inéquations',
                  'Polynômes et factorisation',
                  'Systèmes d\'équations',
                  'Matrices et déterminants',
                  'Espaces vectoriels'
                ],
                gradient: 'linear(to-br, blue.400, blue.600)',
                badge: 'Algèbre',
                color: 'blue',
                delay: '0s',
              },
              {
                emoji: '🤖',
                title: 'Informatique',
                subtitle: 'Machine Learning',
                description: 'Plongez dans le Machine Learning : régression, classification, réseaux de neurones, deep learning et applications pratiques.',
                features: [
                  'Régression linéaire',
                  'Classification',
                  'Réseaux de neurones',
                  'Deep Learning',
                  'Applications pratiques'
                ],
                gradient: 'linear(to-br, purple.400, purple.600)',
                badge: 'Machine Learning',
                color: 'purple',
                delay: '0.1s',
              },
            ].map((subject, idx) => (
              <AnimatedBox key={idx} animation="fadeInUp" delay={idx * 0.1}>
                <Card
                  _hover={{ 
                    transform: 'translateY(-8px)', 
                    boxShadow: '2xl',
                  }}
                  transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
                  border="2px solid"
                  borderColor="gray.100"
                  borderRadius="2xl"
                  bg="white"
                  overflow="hidden"
                  height="100%"
                  boxShadow="lg"
                >
                  {/* Header avec gradient */}
                  <Box
                    bgGradient={subject.gradient}
                    p={8}
                    color="white"
                    position="relative"
                    overflow="hidden"
                  >
                    <Box
                      position="absolute"
                      top="-50%"
                      right="-20%"
                      width="200px"
                      height="200px"
                      bg="whiteAlpha.20"
                      borderRadius="full"
                      filter="blur(40px)"
                    />
                    <VStack spacing={4} position="relative" zIndex={1}>
                      <Box
                        p={4}
                        bg="whiteAlpha.20"
                        backdropFilter="blur(10px)"
                        borderRadius="2xl"
                        fontSize="5xl"
                        boxShadow="lg"
                      >
                        {subject.emoji}
                      </Box>
                      <VStack spacing={1}>
                        <Heading size="lg" color="white" fontWeight="800">
                          {subject.title}
                        </Heading>
                        <Badge 
                          bg="whiteAlpha.30"
                          color="white"
                          px={3}
                          py={1}
                          borderRadius="full"
                          fontSize="sm"
                          fontWeight="600"
                        >
                          {subject.badge}
                        </Badge>
                      </VStack>
                    </VStack>
                  </Box>

                  <CardBody p={6}>
                    <VStack spacing={5} align="stretch">
                      <Text 
                        color="gray.700" 
                        lineHeight="1.8"
                        fontSize="md"
                      >
                        {subject.description}
                      </Text>
                      
                      <Divider borderColor="gray.200" />
                      
                      <VStack spacing={3} align="stretch">
                        <Text 
                          fontSize="sm" 
                          fontWeight="700" 
                          color="gray.900"
                          textTransform="uppercase"
                          letterSpacing="wide"
                        >
                          Concepts couverts :
                        </Text>
                        {subject.features.map((feature, fIdx) => (
                          <HStack key={fIdx} spacing={3}>
                            <Icon as={FiCheck} color={`${subject.color}.500`} boxSize={5} />
                            <Text fontSize="sm" color="gray.700">
                              {feature}
                            </Text>
                          </HStack>
                        ))}
                      </VStack>

                      <Button
                        mt={2}
                        colorScheme={subject.color}
                        variant="outline"
                        rightIcon={<FiArrowRight />}
                        onClick={handleExploreModules}
                        _hover={{
                          bg: `${subject.color}.50`,
                          borderColor: `${subject.color}.400`,
                        }}
                      >
                        Explorer les modules
                      </Button>
                    </VStack>
                  </CardBody>
                </Card>
              </AnimatedBox>
            ))}
          </SimpleGrid>
        </Container>
      </Box>

      {/* Features Section - Design amélioré */}
      <Box bgGradient="linear-gradient(180deg, gray.50 0%, white 100%)" py={{ base: 12, md: 20 }}>
        <Container maxW="1200px">
          <VStack spacing={6} mb={16}>
            <Badge 
              fontSize={{ base: 'sm', md: 'md' }} 
              px={4} 
              py={2} 
              borderRadius="full"
              bgGradient="linear(to-r, blue.500, purple.500)"
              color="white"
              fontWeight="700"
              boxShadow="md"
            >
              Fonctionnalités
            </Badge>
            <Heading 
              size={{ base: 'xl', md: '2xl', lg: '3xl' }} 
              textAlign="center" 
              color="gray.900"
              fontWeight="800"
              letterSpacing="tight"
            >
              Visualisations Interactives Avancées Pilotées par l'IA
            </Heading>
            <Text 
              fontSize={{ base: 'md', md: 'lg' }} 
              color="gray.600" 
              textAlign="center" 
              maxW="900px"
              lineHeight="1.8"
            >
              Le modèle IA analyse le niveau de l'apprenant, génère des simulations 2D/3D interactives, adapte la difficulté en temps réel et propose des expériences exploratoires guidées. Une plateforme EdTech intelligente avec assistant pédagogique autonome.
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8}>
            {[
              {
                icon: FiCpu,
                title: 'Modèle OpenAI Intelligent',
                description: 'Kairos repose sur un modèle OpenAI qui génère automatiquement des contenus pédagogiques interactifs, des simulations dynamiques et une gamification adaptative pour tous les niveaux.',
                gradient: 'linear(to-br, blue.100, blue.200)',
                iconColor: 'blue.600',
                delay: 0,
              },
              {
                icon: FiEye,
                title: 'Visualisations 2D/3D Interactives',
                description: 'Simulations avancées en Mathématiques, Physique classique & quantique, Chimie complète, Biologie, et plus. Adaptées en temps réel selon votre niveau d\'apprentissage.',
                gradient: 'linear(to-br, purple.100, purple.200)',
                iconColor: 'purple.600',
                delay: 0.1,
              },
              {
                icon: FiAward,
                title: 'Gamification Intelligente Pilotée par IA',
                description: 'Badges dynamiques, quêtes générées par IA, système de points adaptatif, classement intelligent et bienveillant. Statistiques générées par IA avec recommandations ciblées.',
                gradient: 'linear(to-br, pink.100, pink.200)',
                iconColor: 'pink.600',
                delay: 0.2,
              },
            ].map((feature, idx) => (
              <AnimatedBox key={idx} animation="fadeInUp" delay={feature.delay}>
                <Card
                  _hover={{ 
                    transform: 'translateY(-8px)', 
                    boxShadow: 'xl',
                    borderColor: `${feature.iconColor}`,
                  }}
                  transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
                  border="2px solid"
                  borderColor="gray.100"
                  borderRadius="2xl"
                  bg="white"
                  overflow="hidden"
                  height="100%"
                  boxShadow="md"
                >
                  <CardBody p={8}>
                    <VStack align="start" spacing={5}>
                      <Box
                        p={5}
                        bgGradient={feature.gradient}
                        borderRadius="2xl"
                        boxShadow="lg"
                        _hover={{
                          transform: 'scale(1.1) rotate(5deg)',
                        }}
                        transition="all 0.3s"
                      >
                        <Icon as={feature.icon} boxSize={8} color={feature.iconColor} />
                      </Box>
                      <Heading 
                        size="lg" 
                        color="gray.900" 
                        fontWeight="700"
                        letterSpacing="tight"
                      >
                        {feature.title}
                      </Heading>
                      <Text 
                        color="gray.700" 
                        lineHeight="1.8" 
                        fontSize="md"
                      >
                        {feature.description}
                      </Text>
                    </VStack>
                  </CardBody>
                </Card>
              </AnimatedBox>
            ))}
          </SimpleGrid>
        </Container>
      </Box>

      {/* Section Comment ça marche */}
      <Box bg="white" py={{ base: 12, md: 20 }}>
        <Container maxW="1200px">
          <VStack spacing={6} mb={12}>
            <Badge 
              fontSize={{ base: 'sm', md: 'md' }} 
              px={4} 
              py={2} 
              borderRadius="full"
              bgGradient="linear(to-r, blue.500, purple.500)"
              color="white"
              fontWeight="700"
            >
              Comment ça marche
            </Badge>
            <Heading 
              size={{ base: 'xl', md: '2xl', lg: '3xl' }} 
              textAlign="center" 
              color="gray.900"
              fontWeight="800"
            >
              Apprenez en 3 étapes simples
            </Heading>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8}>
            {[
              {
                step: '1',
                title: 'Choisissez un module',
                    description: 'Sélectionnez un module dans la matière de votre choix selon votre niveau et vos objectifs.',
                icon: FiBook,
                color: 'blue',
              },
              {
                step: '2',
                title: 'Apprenez avec l\'IA',
                description: 'Posez vos questions à Kaïros, notre tuteur IA qui vous guide avec des explications personnalisées.',
                icon: FiCpu,
                color: 'purple',
              },
              {
                step: '3',
                title: 'Testez vos connaissances',
                description: 'Validez votre compréhension avec des quiz interactifs et suivez votre progression en temps réel.',
                icon: FiTarget,
                color: 'pink',
              },
            ].map((step, idx) => (
              <AnimatedBox key={idx} animation="fadeInUp" delay={idx * 0.1}>
                <VStack spacing={4} textAlign="center">
                  <Box
                    w={16}
                    h={16}
                    borderRadius="full"
                    bgGradient={`linear(to-br, ${step.color}.400, ${step.color}.600)`}
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    color="white"
                    fontSize="2xl"
                    fontWeight="bold"
                    boxShadow="lg"
                    position="relative"
                    _before={{
                      content: '""',
                      position: 'absolute',
                      width: '100%',
                      height: '100%',
                      borderRadius: 'full',
                      bg: `${step.color}.200`,
                      opacity: 0.3,
                      transform: 'scale(1.5)',
                      zIndex: -1,
                    }}
                  >
                    {step.step}
                  </Box>
                  <Icon as={step.icon} boxSize={8} color={`${step.color}.500`} />
                  <Heading size="md" color="gray.900" fontWeight="700">
                    {step.title}
                  </Heading>
                  <Text color="gray.600" lineHeight="1.8" fontSize="md">
                    {step.description}
                  </Text>
                </VStack>
              </AnimatedBox>
            ))}
          </SimpleGrid>
        </Container>
      </Box>

      {/* CTA Section finale - Design premium */}
      <Box 
        bgGradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        py={{ base: 16, md: 24 }}
        position="relative"
        overflow="hidden"
      >
        <Box
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          bgGradient="radial(circle at 30% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 60%)"
        />
        <Container maxW="1200px" position="relative" zIndex={1}>
          <VStack spacing={8} textAlign="center">
            <Heading 
              size={{ base: 'xl', md: '2xl', lg: '3xl' }} 
              color="white"
              fontWeight="extrabold"
              letterSpacing="tight"
            >
              Prêt à commencer votre apprentissage ?
            </Heading>
            <Text 
              fontSize={{ base: 'lg', md: 'xl' }} 
              color="whiteAlpha.95" 
              maxW="700px"
              fontWeight="medium"
              lineHeight="1.8"
            >
                  Rejoignez Kaïros et découvrez une nouvelle façon d'apprendre diverses matières avec l'IA
            </Text>
            <HStack spacing={4} justify="center" flexWrap="wrap">
              <Link to="/register">
                <Button
                  size={{ base: 'lg', md: 'xl' }}
                  bg="white"
                  color="purple.600"
                  _hover={{ 
                    transform: 'translateY(-4px) scale(1.05)', 
                    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
                    bg: 'whiteAlpha.95',
                  }}
                  transition="all 0.4s"
                  fontWeight="bold"
                  px={8}
                  py={6}
                  boxShadow="0 10px 30px rgba(0, 0, 0, 0.2)"
                  rightIcon={<FiArrowRight />}
                  borderRadius="xl"
                >
                  Créer un compte gratuit
                </Button>
              </Link>
              <Button
                size={{ base: 'lg', md: 'xl' }}
                variant="outline"
                color="white"
                borderColor="whiteAlpha.600"
                borderWidth="2px"
                onClick={handleExploreModules}
                _hover={{ 
                  transform: 'translateY(-4px) scale(1.05)',
                  bg: 'whiteAlpha.200',
                  borderColor: 'white',
                }}
                transition="all 0.4s"
                fontWeight="semibold"
                px={8}
                py={6}
                leftIcon={<FiPlay />}
                borderRadius="xl"
              >
                Explorer les modules
              </Button>
            </HStack>
          </VStack>
        </Container>
      </Box>
    </Box>
  )
}

export default Home
