import { useState } from 'react'
import { Box, Button, HStack, VStack, Text, Select, Alert, AlertIcon, Switch, FormControl, FormLabel } from '@chakra-ui/react'
import Simulation3D from './Simulation3D'
import WebARViewer from './WebARViewer'
import UnityWebGLViewer from './UnityWebGLViewer'
import PerformanceOverlay from './PerformanceOverlay'
import { useImmersiveExperience, ImmersiveMode } from '../hooks/useImmersiveExperience'

interface ImmersiveExperienceProps {
  module: {
    id: string
    content?: {
      scene?: string
    }
    subject: string
  }
}

const ImmersiveExperience = ({ module }: ImmersiveExperienceProps) => {
  const { currentMode, capabilities, switchMode, aiContext, isLoadingContext } = useImmersiveExperience({
    moduleId: module.id,
    sceneType: module.content?.scene
  })

  const [showModeSelector, setShowModeSelector] = useState(true)
  const [showPerformanceOverlay, setShowPerformanceOverlay] = useState(false)

  const handleModeChange = (mode: ImmersiveMode) => {
    if (switchMode(mode)) {
      setShowModeSelector(false)
    }
  }

  const renderExperience = () => {
    switch (currentMode) {
      case 'ar':
        return (
          <WebARViewer
            moduleId={module.id}
            sceneType={module.content?.scene}
            onARStart={() => console.log('AR démarré')}
            onAREnd={() => {
              console.log('AR terminé')
              setShowModeSelector(true)
            }}
          />
        )
      case 'unity':
        return (
          <UnityWebGLViewer
            moduleId={module.id}
            buildPath={`/unity-builds/${module.id}`}
            onUnityReady={() => console.log('Unity prêt')}
            onUnityError={(error) => console.error('Erreur Unity:', error)}
          />
        )
      case '3d':
      default:
        return <Simulation3D module={module} />
    }
  }

  return (
    <Box w="100%" h="100%" position="relative">
      {/* Sélecteur de mode */}
      {showModeSelector && (
        <VStack
          position="absolute"
          top={4}
          right={4}
          bg="white"
          p={4}
          borderRadius="lg"
          boxShadow="lg"
          zIndex={100}
          spacing={3}
          minW="250px"
        >
          <Text fontWeight="bold" fontSize="lg">
            Mode d'expérience
          </Text>
          
          <VStack spacing={2} w="100%">
            <Button
              w="100%"
              colorScheme="blue"
              onClick={() => handleModeChange('3d')}
            >
              3D Classique
            </Button>

            {capabilities.arSupported && (
              <Button
                w="100%"
                colorScheme="green"
                onClick={() => handleModeChange('ar')}
                leftIcon={<Text>📱</Text>}
              >
                Réalité Augmentée (AR)
              </Button>
            )}

            {capabilities.vrSupported && (
              <Button
                w="100%"
                colorScheme="purple"
                onClick={() => handleModeChange('vr')}
                leftIcon={<Text>🥽</Text>}
              >
                Réalité Virtuelle (VR)
              </Button>
            )}

            {capabilities.unitySupported && (
              <Button
                w="100%"
                colorScheme="orange"
                onClick={() => handleModeChange('unity')}
                leftIcon={<Text>🎮</Text>}
              >
                Unity WebGL
              </Button>
            )}
          </VStack>

          {!capabilities.arSupported && !capabilities.vrSupported && (
            <Alert status="info" fontSize="xs">
              <AlertIcon />
              <Text fontSize="xs">
                AR/VR nécessite Chrome ou Edge sur Android avec ARCore/WebXR
              </Text>
            </Alert>
          )}

          {/* Toggle performance overlay */}
          <FormControl display="flex" alignItems="center" mt={2}>
            <FormLabel htmlFor="performance-overlay" mb={0} fontSize="xs">
              Afficher performance
            </FormLabel>
            <Switch
              id="performance-overlay"
              size="sm"
              isChecked={showPerformanceOverlay}
              onChange={(e) => setShowPerformanceOverlay(e.target.checked)}
            />
          </FormControl>
        </VStack>
      )}

      {/* Performance Overlay */}
      <PerformanceOverlay enabled={showPerformanceOverlay} />

      {/* Bouton pour revenir au sélecteur */}
      {!showModeSelector && currentMode !== '3d' && (
        <Button
          position="absolute"
          top={4}
          left={4}
          zIndex={100}
          onClick={() => {
            handleModeChange('3d')
            setShowModeSelector(true)
          }}
        >
          ← Retour
        </Button>
      )}

      {/* Contexte IA pour l'expérience immersive */}
      {aiContext && !isLoadingContext && (
        <Box
          position="absolute"
          bottom={4}
          left={4}
          right={4}
          bg="blackAlpha.800"
          color="white"
          p={3}
          borderRadius="md"
          zIndex={100}
        >
          <Text fontSize="sm">{aiContext.guidance}</Text>
        </Box>
      )}

      {/* Rendu de l'expérience */}
      <Box w="100%" h="100%">
        {renderExperience()}
      </Box>
    </Box>
  )
}

export default ImmersiveExperience

