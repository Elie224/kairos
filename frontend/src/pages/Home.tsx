/**
 * Page d'accueil de Kaïrox
 * 
 * Affiche :
 * - Section Hero avec CTA pour inscription
 * - Liste des matières disponibles avec descriptions
 * - Fonctionnalités principales (IA, visualisations 3D, gamification)
 * - Section "Comment ça marche" (3 étapes)
 * - FAQ (5 questions fréquentes)
 * - Section démonstration (6 fonctionnalités clés)
 * - CTA final pour inscription
 * 
 * La page est accessible sans authentification pour permettre la découverte
 * Les statistiques sont chargées uniquement si l'utilisateur est authentifié
 */
import { Box, Container, Heading, Text, Button, VStack, HStack, SimpleGrid, Badge, Icon, Flex, Card, CardBody, Image, Divider, Skeleton, SkeletonText } from '@chakra-ui/react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useEffect } from 'react'
import { FiTarget, FiCpu, FiEye, FiZap, FiUsers, FiAward, FiArrowRight, FiPlay, FiBook, FiCheck, FiTrendingUp, FiClock, FiChevronDown, FiStar, FiMessageCircle, FiCode, FiBarChart } from 'react-icons/fi'
import { AnimatedBox } from '../components/AnimatedBox'
import { useQuery } from 'react-query'
import api from '../services/api'
import { useAuthStore } from '../store/authStore'
import { API_TIMEOUTS } from '../constants/api'
import { useSEO } from '../hooks/useSEO'
import logger from '../utils/logger'

const Home = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()

  // Log pour déboguer le rendu
  useEffect(() => {
    const pathname = window.location.pathname
    logger.debug('Home component mounted', { pathname }, 'Home')
    console.log('🏠 Home component RENDERED', { pathname, timestamp: new Date().toISOString() })
    // Vérifier qu'on est bien sur la homepage
    if (pathname !== '/' && pathname !== '/index.html' && !pathname.startsWith('/legal')) {
      console.error('❌ ERREUR: Home component rendu sur une mauvaise route!', { pathname })
      // Si on est sur /modules, /exams, etc., ne pas rediriger (laisser React Router gérer)
      // Mais logger l'erreur pour le débogage
    }
  }, [])

  // Scroll restoration minimal - seulement après que le contenu soit rendu
  useEffect(() => {
    // Attendre que le contenu soit complètement rendu avant de scroller
    const timer = setTimeout(() => {
      try {
        // Vérifier que le contenu existe avant de scroller
        const heroSection = document.getElementById('hero-section')
        if (heroSection) {
          window.scrollTo({ top: 0, behavior: 'instant' })
          if (document.documentElement) {
            document.documentElement.scrollTop = 0
          }
          if (document.body) {
            document.body.scrollTop = 0
          }
        }
      } catch (e) {
        // Ignorer les erreurs
      }
    }, 300) // Délai plus long pour laisser le contenu se rendre
    
    return () => clearTimeout(timer)
  }, [])

  // SEO
  useSEO({
    title: 'Kaïrox - Apprentissage Immersif avec IA | Visualisations 3D & Gamification',
    description: 'Kaïrox est une plateforme d\'apprentissage intelligente avec visualisations 3D interactives, tutorat IA et gamification adaptative pour collège, lycée et université.',
    keywords: 'apprentissage, éducation, IA, visualisations 3D, gamification, tutorat intelligent, mathématiques, physique, chimie, informatique',
  })

  /**
   * Chargement des statistiques dynamiques pour la page d'accueil
   * Affiche le nombre d'utilisateurs, modules et utilisateurs actifs si disponibles
   * Ces stats ne sont chargées que si l'utilisateur est authentifié
   * IMPORTANT: Ne pas bloquer le rendu initial - les stats sont optionnelles
   */
  const { user } = useAuthStore()
  const isAdmin = user?.is_admin || false
  
  const { data: stats, isLoading: statsLoading } = useQuery(
    'home-stats',
    async () => {
      try {
        const response = await api.get('/auth/stats', {
          timeout: API_TIMEOUTS.STANDARD, // 15 secondes pour les stats (augmenté de 10s)
        })
        return response.data
      } catch (error: any) {
        // Si l'utilisateur n'est pas admin (403) ou s'il y a un timeout,
        // retourner null pour utiliser les stats par défaut affichées dans l'UI
        // Ne pas logger l'erreur si c'est juste un 403 ou un timeout (normal)
        if (error?.response?.status === 403) {
          // 403 = pas admin, c'est normal
          return null
        }
        if (error?.code === 'ECONNABORTED' || error?.message?.includes('timeout')) {
          // Timeout - c'est normal sur Render avec cold start, ne pas logger
          return null
        }
        // Pour les autres erreurs, logger uniquement en mode debug
        logger.debug('Erreur lors du chargement des stats home', { error: error?.message }, 'Home')
        return null
      }
    },
    {
      staleTime: 10 * 60 * 1000, // 10 minutes - augmenté le cache
      cacheTime: 30 * 60 * 1000, // 30 minutes - garder en cache plus longtemps
      enabled: isAuthenticated && isAdmin, // Seulement pour les admins
      retry: false, // Ne pas réessayer - les stats sont optionnelles
      refetchOnMount: false, // Ne pas refetch si déjà en cache
      refetchOnWindowFocus: false, // Ne pas refetch au focus
      // Ne pas bloquer l'affichage si non authentifié ou non admin
      // Ne pas attendre le chargement pour rendre la page
      suspense: false,
    }
  )

  /**
   * Handler pour le bouton "Explorer les modules"
   * Redirige l'utilisateur vers la page des modules
   */
  const handleExploreModules = () => {
    navigate('/modules')
  }

  // S'assurer que le contenu se rend immédiatement, même si les stats ne sont pas encore chargées
  return (
    <Box minH="100vh" position="relative" bg="gray.50" w="100%">
      {/* Hero Section - Design Premium Amélioré */}
      <Box
        color="white"
        py={{ base: 6, md: 32 }}
        px={{ base: 4, md: 0 }}
        position="relative"
        overflow="hidden"
        minH={{ base: '50vh', md: '90vh' }}
        display="flex"
        alignItems="center"
        backgroundImage="url('/background.jfif')"
        backgroundSize="cover"
        backgroundPosition="center"
        backgroundRepeat="no-repeat"
        data-hero="true"
        id="hero-section"
        w="100%"
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
                Kaïrox – Visualisations Interactives & Gamification Pilotées par l'IA
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
                Kaïrox repose sur un modèle OpenAI intelligent capable de générer automatiquement des contenus pédagogiques interactifs, des simulations dynamiques et une gamification adaptative, couvrant les niveaux collège, lycée et université.
              </Text>
            </AnimatedBox>
            
            <AnimatedBox animation="fadeInUp" delay={0.4}>
              <VStack 
                spacing={{ base: 3, md: 4 }} 
                w="full"
                px={{ base: 4, md: 0 }}
                mt={{ base: 2, md: 4 }}
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
                    aria-label="Créer un compte gratuit sur Kaïrox pour commencer l'apprentissage"
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
                  aria-label="Explorer les modules disponibles sur Kaïrox"
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
                description: 'Kaïrox repose sur un modèle OpenAI qui génère automatiquement des contenus pédagogiques interactifs, des simulations dynamiques et une gamification adaptative pour tous les niveaux.',
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
                description: 'Posez vos questions à Kaïrox, notre tuteur IA qui vous guide avec des explications personnalisées.',
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

      {/* Section FAQ - Nouvelle */}
      <Box bg="white" py={{ base: 12, md: 20 }}>
        <Container maxW="900px">
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
              Questions Fréquentes
            </Badge>
            <Heading 
              size={{ base: 'xl', md: '2xl', lg: '3xl' }} 
              textAlign="center" 
              color="gray.900"
              fontWeight="800"
            >
              Tout ce que vous devez savoir
            </Heading>
          </VStack>

          <VStack spacing={4} align="stretch">
            {[
              {
                question: 'Comment fonctionne Kaïrox ?',
                answer: 'Kaïrox utilise un modèle OpenAI intelligent pour générer automatiquement des contenus pédagogiques interactifs, des simulations 3D dynamiques et une gamification adaptative. Choisissez un module, apprenez avec notre tuteur IA, et testez vos connaissances avec des quiz interactifs.',
              },
              {
                question: 'Quelles matières sont disponibles ?',
                answer: 'Nous couvrons Mathématiques, Informatique & IA, Physique, Chimie, Biologie, Géographie, Économie et Histoire. Toutes les matières incluent des visualisations 3D interactives et un tutorat IA personnalisé.',
              },
              {
                question: 'Est-ce vraiment gratuit ?',
                answer: 'Oui ! L\'inscription et l\'accès aux modules de base sont entièrement gratuits. Créez votre compte pour commencer à apprendre dès aujourd\'hui.',
              },
              {
                question: 'Puis-je utiliser Kaïrox sur mobile ?',
                answer: 'Absolument ! Kaïrox est entièrement responsive et optimisé pour tous les appareils : smartphones, tablettes et ordinateurs.',
              },
              {
                question: 'Comment le tuteur IA s\'adapte à mon niveau ?',
                answer: 'Notre IA analyse votre progression, vos réponses et vos erreurs pour adapter automatiquement la difficulté et le style d\'explication à votre niveau d\'apprentissage.',
              },
            ].map((faq, idx) => (
              <AnimatedBox key={idx} animation="fadeInUp" delay={idx * 0.1}>
                <Card
                  border="2px solid"
                  borderColor="gray.100"
                  borderRadius="xl"
                  bg="white"
                  _hover={{
                    borderColor: 'blue.300',
                    boxShadow: 'md',
                  }}
                  transition="all 0.3s"
                >
                  <CardBody p={6}>
                    <VStack spacing={3} align="stretch">
                      <Heading size="sm" color="gray.900" fontWeight="700">
                        {faq.question}
                      </Heading>
                      <Text color="gray.700" lineHeight="1.8" fontSize="md">
                        {faq.answer}
                      </Text>
                    </VStack>
                  </CardBody>
                </Card>
              </AnimatedBox>
            ))}
          </VStack>
        </Container>
      </Box>

      {/* Section Démonstration / Exemples - Nouvelle */}
      <Box bgGradient="linear-gradient(180deg, gray.50 0%, white 100%)" py={{ base: 12, md: 20 }}>
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
              Découvrez Kaïrox
            </Badge>
            <Heading 
              size={{ base: 'xl', md: '2xl', lg: '3xl' }} 
              textAlign="center" 
              color="gray.900"
              fontWeight="800"
            >
              Une expérience d'apprentissage unique
            </Heading>
            <Text 
              fontSize={{ base: 'md', md: 'lg' }} 
              color="gray.600" 
              textAlign="center" 
              maxW="800px"
              lineHeight="1.8"
            >
              Voyez par vous-même ce qui rend Kaïrox spécial : visualisations 3D interactives, tutorat IA intelligent, et gamification motivante.
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {[
              {
                icon: FiCode,
                title: 'Visualisations 3D Réalistes',
                description: 'Explorez des concepts complexes avec des simulations 3D générées par IA, ultra-réalistes et interactives.',
                color: 'blue',
                gradient: 'linear(to-br, blue.100, blue.200)',
              },
              {
                icon: FiMessageCircle,
                title: 'Tutorat IA Personnalisé',
                description: 'Posez vos questions à notre tuteur IA qui s\'adapte à votre niveau et style d\'apprentissage.',
                color: 'purple',
                gradient: 'linear(to-br, purple.100, purple.200)',
              },
              {
                icon: FiBarChart,
                title: 'Suivi de Progression Détaillé',
                description: 'Visualisez votre progression avec des graphiques et statistiques générées par IA.',
                color: 'pink',
                gradient: 'linear(to-br, pink.100, pink.200)',
              },
              {
                icon: FiAward,
                title: 'Gamification Intelligente',
                description: 'Gagnez des badges, complétez des quêtes et montez dans les classements avec un système de gamification adaptatif.',
                color: 'orange',
                gradient: 'linear(to-br, orange.100, orange.200)',
              },
              {
                icon: FiTarget,
                title: 'Évaluations Adaptatives',
                description: 'Testez vos connaissances avec des quiz qui s\'adaptent à votre niveau et fournissent un feedback détaillé.',
                color: 'green',
                gradient: 'linear(to-br, green.100, green.200)',
              },
              {
                icon: FiTrendingUp,
                title: 'Recommandations IA',
                description: 'Recevez des recommandations personnalisées de modules et exercices basées sur votre profil d\'apprentissage.',
                color: 'cyan',
                gradient: 'linear(to-br, cyan.100, cyan.200)',
              },
            ].map((feature, idx) => (
              <AnimatedBox key={idx} animation="fadeInUp" delay={idx * 0.1}>
                <Card
                  _hover={{ 
                    transform: 'translateY(-4px)', 
                    boxShadow: 'lg',
                    borderColor: `${feature.color}.300`,
                  }}
                  transition="all 0.3s"
                  border="2px solid"
                  borderColor="gray.100"
                  borderRadius="xl"
                  bg="white"
                  height="100%"
                >
                  <CardBody p={6}>
                    <VStack spacing={4} align="start">
                      <Box
                        p={4}
                        bgGradient={feature.gradient}
                        borderRadius="xl"
                        boxShadow="md"
                      >
                        <Icon as={feature.icon} boxSize={6} color={`${feature.color}.600`} />
                      </Box>
                      <Heading size="sm" color="gray.900" fontWeight="700">
                        {feature.title}
                      </Heading>
                      <Text color="gray.700" lineHeight="1.7" fontSize="sm">
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

      {/* CTA Section finale - Design premium amélioré */}
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
                  Rejoignez Kaïrox et découvrez une nouvelle façon d'apprendre diverses matières avec l'IA
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
                  _active={{
                    transform: 'translateY(-2px) scale(1.02)',
                  }}
                  transition="all 0.4s"
                  fontWeight="bold"
                  px={10}
                  py={7}
                  boxShadow="0 10px 30px rgba(0, 0, 0, 0.2)"
                  rightIcon={<FiArrowRight />}
                  borderRadius="xl"
                  fontSize={{ base: 'lg', md: 'xl' }}
                  aria-label="Créer un compte gratuit sur Kaïrox - Inscription"
                >
                  🚀 Créer un compte gratuit
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
                  boxShadow: '0 10px 30px rgba(255, 255, 255, 0.3)',
                }}
                _active={{
                  transform: 'translateY(-2px) scale(1.02)',
                }}
                transition="all 0.4s"
                fontWeight="semibold"
                px={10}
                py={7}
                leftIcon={<FiPlay />}
                borderRadius="xl"
                fontSize={{ base: 'lg', md: 'xl' }}
                aria-label="Explorer les modules et visualisations disponibles"
              >
                👁️ Découvrir les modules
              </Button>
            </HStack>
          </VStack>
        </Container>
      </Box>
    </Box>
  )
}

export default Home
