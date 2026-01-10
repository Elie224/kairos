import { Button, HStack, IconButton, VStack, Text, Box } from '@chakra-ui/react'
import { FiRotateCw, FiZoomIn, FiZoomOut, FiRefreshCw, FiX } from 'react-icons/fi'

interface ARControlsProps {
  onRotate?: () => void
  onZoomIn?: () => void
  onZoomOut?: () => void
  onReset?: () => void
  onClose?: () => void
  isARActive: boolean
}

const ARControls = ({ 
  onRotate, 
  onZoomIn, 
  onZoomOut, 
  onReset, 
  onClose,
  isARActive 
}: ARControlsProps) => {
  if (!isARActive) return null

  return (
    <VStack
      position="absolute"
      bottom={4}
      left="50%"
      transform="translateX(-50%)"
      bg="blackAlpha.800"
      p={3}
      borderRadius="lg"
      spacing={2}
      zIndex={100}
    >
      <HStack spacing={2}>
        <IconButton
          aria-label="Rotation"
          icon={<FiRotateCw />}
          onClick={onRotate}
          colorScheme="blue"
          size="sm"
        />
        <IconButton
          aria-label="Zoom avant"
          icon={<FiZoomIn />}
          onClick={onZoomIn}
          colorScheme="green"
          size="sm"
        />
        <IconButton
          aria-label="Zoom arrière"
          icon={<FiZoomOut />}
          onClick={onZoomOut}
          colorScheme="orange"
          size="sm"
        />
        <IconButton
          aria-label="Réinitialiser"
          icon={<FiRefreshCw />}
          onClick={onReset}
          colorScheme="purple"
          size="sm"
        />
        <IconButton
          aria-label="Fermer AR"
          icon={<FiX />}
          onClick={onClose}
          colorScheme="red"
          size="sm"
        />
      </HStack>
      <Text fontSize="xs" color="white" textAlign="center">
        Déplacez votre appareil pour explorer
      </Text>
    </VStack>
  )
}

export default ARControls
















