/**
 * Composant de carte de module réutilisable
 * 
 * Affiche une carte pour un module avec :
 * - Titre et description du module
 * - Badge de difficulté avec couleur adaptée
 * - Bouton "Commencer l'apprentissage" pour naviguer vers le module
 * - Affichage du sujet (matière) avec couleur associée
 * 
 * Le composant est mémorisé (memo) pour éviter les re-renders inutiles
 * 
 * @module components/modules/ModuleCard
 */
import { memo } from 'react'
import { Card, CardBody, VStack, HStack, Badge, Heading, Text, Button, Box, Icon } from '@chakra-ui/react'
import { useTranslation } from 'react-i18next'
import { FiClock, FiBookOpen } from 'react-icons/fi'
import { Module } from '../../types/module'
import { DIFFICULTY_COLORS } from '../../constants/modules'
import logger from '../../utils/logger'

interface ModuleCardProps {
  module: Module
  subjectColor: string
  subjectLabel: string
}

export const ModuleCard = memo(({ module, subjectColor, subjectLabel }: ModuleCardProps) => {
  const { t } = useTranslation()

  const handleStartLearning = (e: React.MouseEvent) => {
    e.stopPropagation() // Empêcher le déclenchement du onClick du Card parent
    e.preventDefault() // Empêcher tout comportement par défaut
    if (module.id) {
      const targetPath = `/modules/${module.id}`
      console.log('🟢 Navigation vers module:', module.id, module.title)
      console.log('🟢 URL cible:', targetPath)
      logger.debug('Navigation vers module', { moduleId: module.id, moduleTitle: module.title, targetPath }, 'ModuleCard')
      
      // SOLUTION DÉFINITIVE: Utiliser window.location.href directement
      // React Router a des problèmes de matching avec les routes paramétrées dans certains cas
      // window.location.href garantit un rechargement complet et le bon matching de la route
      window.location.href = targetPath
    } else {
      // Logger l'erreur si module.id n'existe pas
      logger.error('Module ID manquant pour la navigation', { module }, 'ModuleCard')
      console.error('❌ Module ID manquant pour la navigation', module)
    }
  }

  const handleCardClick = (e: React.MouseEvent) => {
    // Ne naviguer que si le clic n'est pas sur le bouton
    if ((e.target as HTMLElement).closest('button')) {
      return // Le bouton gère sa propre navigation
    }
    if (module.id) {
      // Utiliser window.location.href pour garantir la navigation
      window.location.href = `/modules/${module.id}`
    }
  }

  // Utiliser le thème bleu pour toutes les cartes
  const cardColor = 'blue'

  return (
    <Card
      role="button"
      tabIndex={0}
      _hover={{
        transform: 'translateY(-8px) scale(1.02)',
        boxShadow: 'xl',
        borderColor: 'blue.400',
        borderWidth: '2px',
      }}
      _active={{
        transform: 'translateY(-4px)',
      }}
      _focus={{
        outline: '2px solid',
        outlineColor: 'blue.500',
        outlineOffset: '2px',
      }}
      transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
      height="100%"
      display="flex"
      flexDirection="column"
      bg="white"
      borderRadius="2xl"
      border="2px solid"
      borderColor="blue.100"
      cursor="pointer"
      onClick={handleCardClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          if (module.id) {
            // Utiliser window.location.href pour garantir la navigation
            window.location.href = `/modules/${module.id}`
          }
        }
      }}
      position="relative"
      overflow="hidden"
      boxShadow="soft"
    >
      {/* Barre colorée à gauche avec thème bleu */}
      <Box
        position="absolute"
        left={0}
        top={0}
        bottom={0}
        width="6px"
        bgGradient="linear(180deg, blue.400, blue.600)"
        zIndex={1}
      />

      {/* Dégradé subtil avec thème bleu */}
      <Box
        position="absolute"
        top={0}
        right={0}
        width="200px"
        height="200px"
        bgGradient="radial(circle, blue.100, transparent)"
        opacity={0.2}
        borderRadius="full"
        transform="translate(50%, -50%)"
        zIndex={0}
      />

      <CardBody display="flex" flexDirection="column" flex="1" p={4} position="relative" zIndex={2}>
        <VStack align="start" spacing={3} flex="1" width="full">
          {/* En-tête avec badges */}
          <HStack justify="space-between" width="full" flexWrap="wrap" gap={2}>
            <Badge
              bg="blue.600"
              color="white"
              fontSize="xs"
              px={3}
              py={1.5}
              borderRadius="full"
              fontWeight="600"
              textTransform="uppercase"
              letterSpacing="wide"
              boxShadow="md"
            >
              {subjectLabel}
            </Badge>
          </HStack>

          {/* Titre */}
          <Heading
            size="md"
            color="gray.900"
            fontWeight="700"
            noOfLines={2}
            width="full"
            lineHeight="1.3"
            fontSize="lg"
            letterSpacing="-0.02em"
            fontFamily="heading"
            _groupHover={{
              color: 'blue.700',
            }}
            transition="color 0.2s"
          >
            {module.title}
          </Heading>

          {/* Description */}
          <Text
            fontSize="sm"
            color="gray.700"
            lineHeight="1.7"
            noOfLines={2}
            flex="1"
            width="full"
            fontFamily="body"
            fontWeight="400"
          >
            {module.description}
          </Text>

          {/* Temps estimé avec icône */}
          <HStack
            width="full"
            pt={2}
            borderTop="1px solid"
            borderColor="blue.100"
            spacing={2}
          >
            <Icon as={FiClock} boxSize={3} color="blue.400" />
            <Text fontSize="xs" color="gray.600" fontWeight="500" fontFamily="body">
              {t('modules.estimatedTime', { time: module.estimated_time })}
            </Text>
          </HStack>
        </VStack>

        {/* Bouton d'action amélioré avec thème bleu */}
        <Box width="full" mt={3} pt={3} borderTop="1px solid" borderColor="blue.100">
          <Button
            width="full"
            size="md"
            onClick={handleStartLearning}
            leftIcon={<Icon as={FiBookOpen} boxSize={4} />}
            bgGradient="linear(to-r, blue.500, blue.600)"
            color="white"
            _hover={{
              transform: 'translateY(-2px)',
              boxShadow: 'lg',
              bgGradient: 'linear(to-r, blue.600, blue.700)',
            }}
            _active={{
              transform: 'translateY(0px)',
            }}
            transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            fontWeight="600"
            fontSize="sm"
            py={4}
            borderRadius="xl"
            boxShadow="md"
          >
            {t('modules.startLearning') || 'Commencer l\'apprentissage'}
          </Button>
        </Box>
      </CardBody>
    </Card>
  )
  })
  
ModuleCard.displayName = 'ModuleCard'
