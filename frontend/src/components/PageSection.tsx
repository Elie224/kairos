/**
 * Composant de section de page avec design professionnel
 */
import { Box, Container, BoxProps } from '@chakra-ui/react'
import { ReactNode } from 'react'

interface PageSectionProps extends BoxProps {
  children: ReactNode
  variant?: 'default' | 'dark' | 'gradient' | 'glass'
  containerMaxW?: string
  py?: number | object
}

export const PageSection = ({ 
  children, 
  variant = 'default',
  containerMaxW = '1200px',
  py = { base: 12, md: 20 },
  ...props 
}: PageSectionProps) => {
  const variantStyles = {
    default: {
      bg: 'white',
    },
    dark: {
      bg: 'gray.900',
      color: 'white',
    },
    gradient: {
      bgGradient: 'gradient.primary',
      color: 'white',
    },
    glass: {
      bg: 'whiteAlpha.100',
      backdropFilter: 'blur(10px)',
    },
  }

  return (
    <Box
      py={py}
      {...variantStyles[variant]}
      {...props}
    >
      <Container maxW={containerMaxW}>
        {children}
      </Container>
    </Box>
  )
}














