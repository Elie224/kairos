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
} from '@chakra-ui/react'
import { FiArrowRight, FiArrowLeft, FiX, FiTarget, FiCpu, FiEye, FiZap, FiUsers, FiAward } from 'react-icons/fi'
import { AnimatedBox } from './AnimatedBox'

interface OnboardingScreen {
  icon: typeof FiTarget
  title: string
  description: string
  color: string
  gradient: string
}

const onboardingScreens: OnboardingScreen[] = [
  {
    icon: FiTarget,
    title: 'Bienvenue sur Kaïros',
    description: 'Votre plateforme d\'apprentissage intelligente pour maîtriser diverses matières avec l\'IA. Explorez des cours interactifs et personnalisés adaptés à votre niveau.',
    color: 'blue',
    gradient: 'linear(to-br, blue.400, blue.600)',
  },
  {
    icon: FiCpu,
    title: 'Tutorat IA Intelligent',
    description: 'Obtenez des explications personnalisées adaptées à votre niveau. Notre IA analyse vos questions et fournit des réponses claires avec des exemples concrets.',
    color: 'purple',
    gradient: 'linear(to-br, purple.400, purple.600)',
  },
  {
    icon: FiEye,
    title: 'Visualisations Interactives',
    description: 'Visualisez des concepts complexes en 3D avec des simulations interactives. Manipulez, explorez et comprenez mieux grâce à des représentations visuelles dynamiques.',
    color: 'pink',
    gradient: 'linear(to-br, pink.400, pink.600)',
  },
  {
    icon: FiZap,
    title: 'Suivi de Progression',
    description: 'Suivez votre progression, identifiez vos forces et vos faiblesses. Obtenez des recommandations personnalisées pour optimiser votre apprentissage.',
    color: 'orange',
    gradient: 'linear(to-br, orange.400, orange.600)',
  },
  {
    icon: FiAward,
    title: 'Gamification',
    description: 'Gagnez des badges, débloquez des réalisations et montez de niveau. Transformez votre apprentissage en une expérience engageante et motivante.',
    color: 'green',
    gradient: 'linear(to-br, green.400, green.600)',
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
            border="1px solid"
            borderColor={borderColor}
            overflow="hidden"
            position="relative"
          >
            {/* Bouton de fermeture */}
            <IconButton
              aria-label="Passer l'introduction"
              icon={<FiX />}
              position="absolute"
              top={4}
              right={4}
              zIndex={10}
              variant="ghost"
              size="sm"
              onClick={handleSkip}
              _hover={{ bg: 'gray.100' }}
            />

            {/* Barre de progression */}
            <Box px={6} pt={6} pb={4}>
              <HStack spacing={2} justify="space-between" mb={2}>
                <Text fontSize="xs" color="gray.600" fontWeight="medium">
                  {currentScreen + 1} / {onboardingScreens.length}
                </Text>
                <Text fontSize="xs" color="gray.600" fontWeight="medium">
                  {Math.round(progress)}%
                </Text>
              </HStack>
              <Progress
                value={progress}
                colorScheme={current.color}
                size="sm"
                borderRadius="full"
                bg="gray.100"
              />
            </Box>

            {/* Contenu de l'écran */}
            <VStack spacing={8} px={8} pb={8} pt={4} align="stretch" minH="400px">
              <AnimatedBox animation="fadeInUp" delay={0.2}>
                <VStack spacing={6}>
                  {/* Icône */}
                  <Box
                    p={6}
                    bgGradient={current.gradient}
                    borderRadius="2xl"
                    boxShadow="lg"
                    transform="rotate(-5deg)"
                    _hover={{
                      transform: 'rotate(0deg) scale(1.1)',
                    }}
                    transition="all 0.3s"
                  >
                    <Icon as={current.icon} boxSize={12} color="white" />
                  </Box>

                  {/* Titre */}
                  <Heading
                    size={{ base: 'lg', md: 'xl' }}
                    color="gray.900"
                    fontWeight="800"
                    textAlign="center"
                  >
                    {current.title}
                  </Heading>

                  {/* Description */}
                  <Text
                    color="gray.600"
                    textAlign="center"
                    fontSize={{ base: 'md', md: 'lg' }}
                    lineHeight="tall"
                    px={2}
                  >
                    {current.description}
                  </Text>
                </VStack>
              </AnimatedBox>

              {/* Indicateurs de pages */}
              <HStack spacing={2} justify="center" mt="auto">
                {onboardingScreens.map((_, index) => (
                  <Box
                    key={index}
                    w={2}
                    h={2}
                    borderRadius="full"
                    bg={index === currentScreen ? `${current.color}.500` : 'gray.300'}
                    transition="all 0.3s"
                    _hover={{
                      bg: index === currentScreen ? `${current.color}.600` : 'gray.400',
                    }}
                  />
                ))}
              </HStack>

              {/* Boutons de navigation */}
              <HStack spacing={4} justify="space-between" mt={4}>
                <Button
                  variant="ghost"
                  leftIcon={<FiArrowLeft />}
                  onClick={handlePrevious}
                  isDisabled={isFirst}
                  _disabled={{
                    opacity: 0.4,
                    cursor: 'not-allowed',
                  }}
                >
                  Précédent
                </Button>

                <Button
                  colorScheme={current.color}
                  rightIcon={isLast ? undefined : <FiArrowRight />}
                  onClick={handleNext}
                  bgGradient={current.gradient}
                  _hover={{
                    transform: 'translateY(-2px)',
                    boxShadow: 'lg',
                  }}
                  transition="all 0.3s"
                  fontWeight="bold"
                  px={8}
                >
                  {isLast ? 'Commencer' : 'Suivant'}
                </Button>
              </HStack>
            </VStack>
          </Box>
        </AnimatedBox>
      </Container>
    </Box>
  )
}
