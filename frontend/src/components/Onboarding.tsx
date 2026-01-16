/**
 * Composant d'onboarding pour présenter l'application aux nouveaux utilisateurs
 */
import { useState } from 'react'
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Icon,
  Progress,
  IconButton,
  useColorModeValue,
  BoxProps,
  Badge,
  SimpleGrid,
} from '@chakra-ui/react'
import { FiArrowRight, FiArrowLeft, FiX, FiTarget, FiCpu, FiEye, FiZap, FiUsers, FiAward, FiBook, FiTrendingUp, FiCheck } from 'react-icons/fi'
import { AnimatedBox } from './AnimatedBox'


interface OnboardingScreen {
  icon: typeof FiTarget
  title: string
  description: string
  color: string
  gradient: string
  features?: string[]
  emoji?: string
}

const onboardingScreens: OnboardingScreen[] = [
  {
    icon: FiTarget,
    title: 'Bienvenue sur Kaïros',
    description: 'Votre plateforme d\'apprentissage intelligente pour maîtriser diverses matières avec l\'IA. Explorez des cours interactifs et personnalisés adaptés à votre niveau.',
    color: 'blue',
    gradient: 'linear(to-br, blue.400, blue.600)',
    emoji: '🎓',
    features: [
      'Cours personnalisés par IA',
      'Plusieurs matières disponibles',
      'Adapté à tous les niveaux',
    ],
  },
  {
    icon: FiCpu,
    title: 'Tutorat IA Intelligent',
    description: 'Obtenez des explications personnalisées adaptées à votre niveau. Notre IA analyse vos questions et fournit des réponses claires avec des exemples concrets.',
    color: 'purple',
    gradient: 'linear(to-br, purple.400, purple.600)',
    emoji: '🤖',
    features: [
      'Réponses instantanées',
      'Explications détaillées',
      'Exemples pratiques',
    ],
  },
  {
    icon: FiEye,
    title: 'Visualisations Interactives',
    description: 'Visualisez des concepts complexes en 3D avec des simulations interactives. Manipulez, explorez et comprenez mieux grâce à des représentations visuelles dynamiques.',
    color: 'pink',
    gradient: 'linear(to-br, pink.400, pink.600)',
    emoji: '👁️',
    features: [
      'Simulations 3D',
      'Manipulation interactive',
      'Compréhension visuelle',
    ],
  },
  {
    icon: FiTrendingUp,
    title: 'Suivi de Progression',
    description: 'Suivez votre progression, identifiez vos forces et vos faiblesses. Obtenez des recommandations personnalisées pour optimiser votre apprentissage.',
    color: 'orange',
    gradient: 'linear(to-br, orange.400, orange.600)',
    emoji: '📈',
    features: [
      'Statistiques détaillées',
      'Recommandations personnalisées',
      'Objectifs adaptatifs',
    ],
  },
  {
    icon: FiAward,
    title: 'Gamification & Récompenses',
    description: 'Gagnez des badges, débloquez des réalisations et montez de niveau. Transformez votre apprentissage en une expérience engageante et motivante.',
    color: 'green',
    gradient: 'linear(to-br, green.400, green.600)',
    emoji: '🏆',
    features: [
      'Badges et réalisations',
      'Système de niveaux',
      'Défis quotidiens',
    ],
  },
]

interface OnboardingProps {
  onComplete: () => void
  onSkip: () => void
}

export const Onboarding = ({ onComplete, onSkip }: OnboardingProps) => {
  const [currentScreen, setCurrentScreen] = useState(0)
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')

  const current = onboardingScreens[currentScreen]
  const isFirst = currentScreen === 0
  const isLast = currentScreen === onboardingScreens.length - 1
  const progress = ((currentScreen + 1) / onboardingScreens.length) * 100

  const handleNext = () => {
    if (isLast) {
      onComplete()
    } else {
      setCurrentScreen(currentScreen + 1)
    }
  }

  const handlePrevious = () => {
    if (!isFirst) {
      setCurrentScreen(currentScreen - 1)
    }
  }

  const handleSkip = () => {
    onSkip()
  }

  return (
    <Box
      position="fixed"
      top={0}
      left={0}
      right={0}
      bottom={0}
      bg="blackAlpha.800"
      zIndex={9999}
      display="flex"
      alignItems="center"
      justifyContent="center"
      backdropFilter="blur(10px)"
    >
      <Container maxW="md" px={4}>
        <AnimatedBox animation="scaleIn" delay={0.1}>
          <Box
            bg={bgColor}
            borderRadius="2xl"
            boxShadow="2xl"
            border="2px solid"
            borderColor={borderColor}
            overflow="hidden"
            position="relative"
            _hover={{
              boxShadow: '2xl',
              borderColor: `${current.color}.300`,
            }}
            transition="all 0.3s"
          >
            {/* Bouton de fermeture amélioré */}
            <IconButton
              aria-label="Passer l'introduction"
              icon={<FiX />}
              position="absolute"
              top={4}
              right={4}
              zIndex={10}
              variant="ghost"
              size="md"
              onClick={handleSkip}
              borderRadius="full"
              _hover={{
                bg: 'red.50',
                color: 'red.500',
                transform: 'rotate(90deg)',
              }}
              transition="all 0.3s"
              data-touch-target="true"
            />

            {/* Barre de progression améliorée */}
            <Box px={4} pt={3} pb={2} bgGradient={`linear(to-r, ${current.color}.50, white, ${current.color}.50)`}>
              <HStack spacing={2} justify="space-between" mb={2}>
                <Badge
                  colorScheme={current.color}
                  px={2}
                  py={0.5}
                  borderRadius="full"
                  fontSize="2xs"
                  fontWeight="bold"
                >
                  Étape {currentScreen + 1}/{onboardingScreens.length}
                </Badge>
                <Text fontSize="2xs" color="gray.600" fontWeight="bold">
                  {Math.round(progress)}%
                </Text>
              </HStack>
              <Progress
                value={progress}
                colorScheme={current.color}
                size="sm"
                borderRadius="full"
                bg="gray.100"
                boxShadow="sm"
                hasStripe
                isAnimated
              />
            </Box>

            {/* Contenu de l'écran */}
            <VStack spacing={3} px={5} pb={5} pt={2} align="stretch" minH="320px">
              <AnimatedBox animation="fadeInUp" delay={0.2}>
                <VStack spacing={3}>
                  {/* Icône avec emoji */}
                  <VStack spacing={1}>
                    {current.emoji && (
                      <Text fontSize="4xl" lineHeight={1} mb={0}>
                        {current.emoji}
                      </Text>
                    )}
                    <Box
                      p={3}
                      bgGradient={current.gradient}
                      borderRadius="lg"
                      boxShadow="md"
                      transform="rotate(-5deg)"
                      _hover={{
                        transform: 'rotate(0deg) scale(1.1)',
                      }}
                      transition="all 0.3s"
                      position="relative"
                    >
                      <Icon as={current.icon} boxSize={6} color="white" />
                      {/* Effet de brillance */}
                      <Box
                        position="absolute"
                        top="-50%"
                        left="-50%"
                        width="200%"
                        height="200%"
                        bgGradient="radial(circle, rgba(255,255,255,0.3) 0%, transparent 70%)"
                        borderRadius="full"
                        opacity={0}
                        _hover={{ opacity: 1 }}
                        transition="opacity 0.3s"
                      />
                    </Box>
                  </VStack>

                  {/* Titre */}
                  <Heading
                    size={{ base: 'md', md: 'lg' }}
                    color="gray.900"
                    fontWeight="800"
                    textAlign="center"
                    bgGradient={current.gradient}
                    bgClip="text"
                    letterSpacing="tight"
                  >
                    {current.title}
                  </Heading>

                  {/* Description */}
                  <Text
                    color="gray.600"
                    textAlign="center"
                    fontSize={{ base: 'sm', md: 'md' }}
                    lineHeight="1.6"
                    px={2}
                    fontWeight="500"
                  >
                    {current.description}
                  </Text>

                  {/* Liste de fonctionnalités */}
                  {current.features && current.features.length > 0 && (
                    <SimpleGrid columns={1} spacing={2} w="full" mt={1}>
                      {current.features.map((feature, idx) => (
                        <HStack
                          key={idx}
                          spacing={2}
                          p={2}
                          bg={`${current.color}.50`}
                          borderRadius="md"
                          border="1px solid"
                          borderColor={`${current.color}.200`}
                          _hover={{
                            bg: `${current.color}.100`,
                            transform: 'translateX(4px)',
                          }}
                          transition="all 0.2s"
                        >
                          <Icon
                            as={FiCheck}
                            color={`${current.color}.600`}
                            boxSize={4}
                            flexShrink={0}
                          />
                          <Text
                            fontSize="xs"
                            color="gray.700"
                            fontWeight="medium"
                            flex={1}
                          >
                            {feature}
                          </Text>
                        </HStack>
                      ))}
                    </SimpleGrid>
                  )}
                </VStack>
              </AnimatedBox>

              {/* Indicateurs de pages améliorés */}
              <HStack spacing={3} justify="center" mt="auto" mb={2}>
                {onboardingScreens.map((_, index) => (
                  <Box
                    key={index}
                    as="button"
                    onClick={() => setCurrentScreen(index)}
                    w={index === currentScreen ? 8 : 2}
                    h={2}
                    borderRadius="full"
                    bg={index === currentScreen ? `${current.color}.500` : 'gray.300'}
                    transition="all 0.3s"
                    _hover={{
                      bg: index === currentScreen ? `${current.color}.600` : 'gray.400',
                      w: index === currentScreen ? 8 : 3,
                    }}
                    cursor="pointer"
                    aria-label={`Aller à l'écran ${index + 1}`}
                  />
                ))}
              </HStack>

              {/* Boutons de navigation */}
              <HStack spacing={3} justify="space-between" mt={2}>
                <Button
                  variant="ghost"
                  leftIcon={<FiArrowLeft />}
                  onClick={handlePrevious}
                  isDisabled={isFirst}
                  _disabled={{
                    opacity: 0.4,
                    cursor: 'not-allowed',
                  }}
                  _hover={{
                    bg: 'gray.100',
                    transform: 'translateX(-2px)',
                  }}
                  transition="all 0.2s"
                  size="sm"
                  fontSize="sm"
                >
                  Précédent
                </Button>

                <Button
                  colorScheme={current.color}
                  rightIcon={isLast ? undefined : <FiArrowRight />}
                  onClick={handleNext}
                  bgGradient={current.gradient}
                  color="white"
                  _hover={{
                    transform: 'translateY(-2px)',
                    boxShadow: 'xl',
                    bgGradient: current.gradient,
                  }}
                  _active={{
                    transform: 'translateY(0)',
                  }}
                  transition="all 0.3s"
                  fontWeight="bold"
                  px={6}
                  size="md"
                  boxShadow="md"
                  fontSize="sm"
                >
                  {isLast ? '🚀 Commencer' : 'Suivant'}
                </Button>
              </HStack>
            </VStack>
          </Box>
        </AnimatedBox>
      </Container>
    </Box>
  )
}
