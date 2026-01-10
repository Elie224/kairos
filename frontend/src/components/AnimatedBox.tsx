/**
 * Composant Box avec animations professionnelles
 */
import { Box, BoxProps } from '@chakra-ui/react'
import { ReactNode } from 'react'

interface AnimatedBoxProps extends BoxProps {
  animation?: 'fadeIn' | 'fadeInUp' | 'fadeInDown' | 'slideInRight' | 'slideInLeft' | 'scaleIn' | 'scaleUp'
  delay?: number
  duration?: number
  children: ReactNode
}

export const AnimatedBox = ({ 
  animation = 'fadeIn', 
  delay = 0, 
  duration = 0.5,
  children, 
  ...props 
}: AnimatedBoxProps) => {
  const animationClass = `animate-${animation.replace(/([A-Z])/g, '-$1').toLowerCase()}`
  
  return (
    <Box
      className={animationClass}
      style={{
        animationDelay: `${delay}s`,
        animationDuration: `${duration}s`,
        animationFillMode: 'both',
      }}
      {...props}
    >
      {children}
    </Box>
  )
}














