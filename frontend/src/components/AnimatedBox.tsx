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
  // Mapper les noms d'animations aux keyframes CSS
  const animationMap: Record<string, string> = {
    fadeIn: 'fadeIn',
    fadeInUp: 'slideInTop',
    fadeInDown: 'slideInBottom',
    slideInRight: 'slideInRight',
    slideInLeft: 'slideInLeft',
    scaleIn: 'scaleIn',
    scaleUp: 'scaleIn',
  }
  
  const animationName = animationMap[animation] || 'fadeIn'
  
  // Utiliser les propriétés d'animation CSS séparées pour une meilleure compatibilité
  const animationStyle: CSSProperties = {
    animationName: animationName,
    animationDuration: `${duration}s`,
    animationDelay: `${delay}s`,
    animationFillMode: 'both',
    animationTimingFunction: 'ease-out',
  }
  
  return (
    <Box
      style={animationStyle}
      {...props}
    >
      {children}
    </Box>
  )
}














