/**
 * Carte de fonctionnalité avec design professionnel
 */
import { 
  Card, 
  CardBody, 
  VStack, 
  Heading, 
  Text, 
  Icon, 
  Box,
  CardProps 
} from '@chakra-ui/react'
import { IconType } from 'react-icons'
import { AnimatedBox } from './AnimatedBox'

interface FeatureCardProps extends CardProps {
  icon: IconType
  title: string
  description: string
  delay?: number
  iconColor?: string
}

export const FeatureCard = ({ 
  icon, 
  title, 
  description, 
  delay = 0,
  iconColor = 'blue.500',
  ...props 
}: FeatureCardProps) => {
  return (
    <AnimatedBox animation="fadeInUp" delay={delay}>
      <Card
        variant="elevated"
        h="full"
        border="2px solid"
        borderColor="blue.100"
        _hover={{
          transform: 'translateY(-8px) scale(1.02)',
          borderColor: 'blue.400',
          boxShadow: 'xl',
        }}
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
        boxShadow="soft"
        {...props}
      >
        <CardBody>
          <VStack spacing={4} align="stretch">
            <Box
              w={12}
              h={12}
              borderRadius="xl"
              bgGradient="linear-gradient(135deg, #2563EB 0%, #1E40AF 100%)"
              display="flex"
              alignItems="center"
              justifyContent="center"
              boxShadow="lg"
              _hover={{
                transform: 'scale(1.1) rotate(5deg)',
                boxShadow: 'xl',
              }}
              transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            >
              <Icon as={icon} boxSize={6} color="white" />
            </Box>
            <Heading 
              size="md" 
              fontWeight="700"
              letterSpacing="-0.02em"
              fontFamily="heading"
              color="gray.900"
            >
              {title}
            </Heading>
            <Text 
              color="gray.700" 
              lineHeight="1.7"
              letterSpacing="0.01em"
              fontFamily="body"
              fontWeight="400"
            >
              {description}
            </Text>
          </VStack>
        </CardBody>
      </Card>
    </AnimatedBox>
  )
}







