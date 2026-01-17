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
import { memo, useRef } from 'react'
import { Card, CardBody, VStack, HStack, Badge, Heading, Text, Button, Box, Icon } from '@chakra-ui/react'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
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
  const navigate = useNavigate()
  // Garde pour empêcher les clics multiples et navigations simultanées
  const isNavigatingRef = useRef(false)

  const handleStartLearning = (e: React.MouseEvent) => {
    // CRITIQUE: Arrêter la propagation AVANT toute autre opération
    e.stopPropagation()
    e.preventDefault()
    e.nativeEvent.stopImmediatePropagation()
    
    // Vérifier si une navigation est déjà en cours
    if (isNavigatingRef.current) {
      console.warn('⚠️ Navigation déjà en cours, ignoré')
      return
    }
    
    if (!module.id) {
      logger.error('Module ID manquant pour la navigation', { module }, 'ModuleCard')
      console.error('❌ Module ID manquant pour la navigation', module)
      return
    }
    
    // Marquer la navigation comme en cours
    isNavigatingRef.current = true
    
    const targetPath = `/modules/${module.id}`
    console.log('🟢 Navigation vers module:', module.id, module.title)
    console.log('🟢 URL cible:', targetPath)
    logger.debug('Navigation vers module', { moduleId: module.id, moduleTitle: module.title, targetPath }, 'ModuleCard')
    
    // Navigation immédiate sans setTimeout pour éviter les problèmes
    navigate(targetPath, { replace: false })
    console.log('✅ Navigation React Router déclenchée vers:', targetPath)
    
    // Réinitialiser le garde après un court délai
    setTimeout(() => {
      isNavigatingRef.current = false
    }, 1000)
  }

  const handleCardClick = (e: React.MouseEvent) => {
    // Ne naviguer que si le clic n'est pas sur le bouton
    if ((e.target as HTMLElement).closest('button')) {
      return // Le bouton gère sa propre navigation
    }
    if (module.id) {
      const targetPath = `/modules/${module.id}`
      // Utiliser navigate() de React Router pour une navigation SPA correcte
      navigate(targetPath, { replace: false })
      console.log('✅ Navigation React Router déclenchée (clic carte) vers:', targetPath)
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
            const targetPath = `/modules/${module.id}`
            // Utiliser navigate() de React Router pour une navigation SPA correcte
            navigate(targetPath, { replace: false })
            console.log('✅ Navigation React Router déclenchée (clavier) vers:', targetPath)
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
        <Box width="full" mt={3} pt={3} borderTop="1px solid" borderColor="blue.100" onClick={(e) => e.stopPropagation()}>
          <Button
            width="full"
            size="md"
            onClick={handleStartLearning}
            onMouseDown={(e) => {
              // Empêcher le focus de la carte parent
              e.stopPropagation()
            }}
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
            type="button"
            aria-label={`Commencer l'apprentissage: ${module.title}`}
          >
            {t('modules.startLearning') || 'Commencer l\'apprentissage'}
          </Button>
        </Box>
      </CardBody>
    </Card>
  )
  })
  
ModuleCard.displayName = 'ModuleCard'
