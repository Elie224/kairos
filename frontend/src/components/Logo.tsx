import { Box, HStack, Text } from '@chakra-ui/react'
import { LazyImage } from './LazyImage'
import logoKairos from '../logo_kairos.jpeg'

interface LogoProps {
  size?: { base: string; md: string } | string
  showText?: boolean
  variant?: 'default' | 'light' | 'dark'
  textSize?: { base: string; md: string } | string
}

const Logo = ({ 
  size = { base: '10', md: '12' }, 
  showText = false,
  variant = 'default',
  textSize = { base: 'xl', md: '2xl' }
}: LogoProps) => {
  const sizeValue = typeof size === 'string' 
    ? { base: size, md: size } 
    : size

  const textSizeValue = typeof textSize === 'string'
    ? { base: textSize, md: textSize }
    : textSize

  // Design moderne avec gradient bleu et ombre améliorée
  const logoBox = (
    <Box
      w={{ base: `${sizeValue.base}`, md: `${sizeValue.md}` }}
      h={{ base: `${sizeValue.base}`, md: `${sizeValue.md}` }}
      borderRadius="full"
      overflow="hidden"
      bgGradient="linear-gradient(135deg, #2563EB 0%, #1E40AF 100%)"
      p={0.5}
      boxShadow="0 4px 20px rgba(37, 99, 235, 0.3), 0 0 0 1px rgba(37, 99, 235, 0.1)"
      position="relative"
      _hover={{ 
        transform: 'scale(1.08)',
        boxShadow: '0 8px 30px rgba(37, 99, 235, 0.4), 0 0 0 2px rgba(37, 99, 235, 0.2)'
      }}
      transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
      className="gpu-accelerated"
    >
      <Box
        w="full"
        h="full"
        borderRadius="full"
        bg="white"
        p={0.5}
        overflow="hidden"
      >
        <LazyImage 
          src={logoKairos} 
          alt="Kaïros Logo" 
          w="full" 
          h="full"
          objectFit="cover"
          borderRadius="full"
          transition="all 0.3s ease"
          position="relative"
          zIndex={0}
        />
      </Box>
    </Box>
  )

  if (showText) {
    return (
      <HStack spacing={{ base: 3, md: 4 }} align="center">
        {logoBox}
        <Text 
          fontSize={textSizeValue}
          fontWeight="700" 
          bgGradient="linear-gradient(135deg, #2563EB 0%, #1E40AF 100%)"
          bgClip="text"
          color="transparent"
          letterSpacing="-0.02em"
          fontFamily="'Poppins', sans-serif"
          _hover={{
            bgGradient: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
            bgClip: 'text'
          }}
          transition="all 0.3s ease"
        >
          Kaïros
        </Text>
      </HStack>
    )
  }

  return logoBox
}

export default Logo

