/**
 * Carte de statistique avec design professionnel
 */
import { 
  Box, 
  VStack, 
  Text, 
  Icon, 
  Heading,
  BoxProps 
} from '@chakra-ui/react'
import { IconType } from 'react-icons'
import { AnimatedBox } from './AnimatedBox'

interface StatCardProps extends BoxProps {
  icon: IconType
  value: string | number
  label: string
  description?: string
  delay?: number
  iconColor?: string
  trend?: 'up' | 'down' | 'neutral'
}

export const StatCard = ({ 
  icon, 
  value, 
  label, 
  description,
  delay = 0,
  iconColor = 'brand.500',
  trend = 'neutral',
  ...props 
}: StatCardProps) => {
  return (
    <AnimatedBox animation="fadeInUp" delay={delay}>
      <Box
        p={6}
        borderRadius="2xl"
        bg="white"
        border="1px solid"
        borderColor="gray.100"
        boxShadow="md"
        _hover={{
          transform: 'translateY(-8px) scale(1.02)',
          boxShadow: 'xl',
          borderColor: `${iconColor}40`,
        }}
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
        {...props}
      >
        <VStack spacing={4} align="stretch">
          <Box
            w={12}
            h={12}
            borderRadius="xl"
            bgGradient={`linear-gradient(135deg, ${iconColor} 0%, ${iconColor}80 100%)`}
            display="flex"
            alignItems="center"
            justifyContent="center"
            boxShadow="lg"
          >
            <Icon as={icon} boxSize={6} color="white" />
          </Box>
          <VStack spacing={1} align="stretch">
            <Heading size="lg" fontWeight="bold" color="gray.800">
              {value}
            </Heading>
            <Text fontSize="sm" fontWeight="semibold" color="gray.600">
              {label}
            </Text>
            {description && (
              <Text fontSize="xs" color="gray.500" fontStyle="italic">
                {description}
              </Text>
            )}
          </VStack>
        </VStack>
      </Box>
    </AnimatedBox>
  )
}














