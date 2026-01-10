/**
 * Composant de chargement professionnel
 */
import { Box, Spinner, Text, VStack } from '@chakra-ui/react'
import { keyframes } from '@emotion/react'

const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  text?: string
  fullScreen?: boolean
}

export const LoadingSpinner = ({ 
  size = 'lg', 
  text, 
  fullScreen = false 
}: LoadingSpinnerProps) => {
  const sizeMap = {
    sm: '20px',
    md: '40px',
    lg: '60px',
    xl: '80px',
  }

  const spinnerSize = sizeMap[size]

  const content = (
    <VStack spacing={4}>
      <Box position="relative" w={spinnerSize} h={spinnerSize}>
        <Spinner
          thickness="4px"
          speed="0.65s"
          color="brand.500"
          size={size}
          position="absolute"
          top="50%"
          left="50%"
          transform="translate(-50%, -50%)"
        />
        <Box
          position="absolute"
          top="50%"
          left="50%"
          transform="translate(-50%, -50%)"
          w={`calc(${spinnerSize} - 8px)`}
          h={`calc(${spinnerSize} - 8px)`}
          borderRadius="full"
          border="2px solid"
          borderColor="brand.100"
          animation={`${pulse} 2s ease-in-out infinite`}
        />
      </Box>
      {text && (
        <Text
          fontSize="sm"
          color="gray.600"
          fontWeight="medium"
          animation={`${pulse} 2s ease-in-out infinite`}
        >
          {text}
        </Text>
      )}
    </VStack>
  )

  if (fullScreen) {
    return (
      <Box
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        display="flex"
        alignItems="center"
        justifyContent="center"
        bg="whiteAlpha.800"
        backdropFilter="blur(4px)"
        zIndex={9999}
      >
        {content}
      </Box>
    )
  }

  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      minH="200px"
      w="full"
    >
      {content}
    </Box>
  )
}

