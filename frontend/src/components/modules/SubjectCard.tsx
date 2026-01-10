/**
 * Carte de matière cliquable - Design amélioré
 */
import { Card, CardBody, VStack, Heading, Text, Box, Badge, HStack, Icon } from '@chakra-ui/react'
import { SUBJECT_COLORS } from '../../constants/modules'
import { FiArrowRight } from 'react-icons/fi'

interface SubjectCardProps {
  subject: string
  subjectLabel: string
  moduleCount: number
  description?: string
  icon?: string
  onClick: () => void
}

const SUBJECT_ICONS: Record<string, string> = {
  mathematics: '📐',  // Algèbre
  computer_science: '🤖',  // Machine Learning
}

const SUBJECT_DESCRIPTIONS: Record<string, string> = {
  mathematics: 'Maîtrisez l\'algèbre : équations, polynômes, matrices et plus encore',
  computer_science: 'Apprenez le Machine Learning : algorithmes, réseaux de neurones, deep learning',
}

export const SubjectCard = ({
  subject,
  subjectLabel,
  moduleCount,
  description,
  icon,
  onClick,
}: SubjectCardProps) => {
  // Utiliser le thème bleu pour toutes les matières
  const subjectColor = 'blue'
  const subjectIcon = icon || SUBJECT_ICONS[subject] || '📖'
  const subjectDescription = description || SUBJECT_DESCRIPTIONS[subject] || ''

  return (
    <Card
      role="button"
      tabIndex={0}
      _hover={{
        transform: 'translateY(-8px) scale(1.02)',
        boxShadow: 'xl',
        cursor: 'pointer',
        borderColor: 'blue.400',
        borderWidth: '2px',
      }}
      _active={{
        transform: 'translateY(-4px) scale(0.99)',
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
      overflow="hidden"
      onClick={onClick}
      position="relative"
      border="2px solid"
      borderColor="blue.100"
      boxShadow="soft"
    >
      {/* Dégradé de fond animé avec thème bleu */}
      <Box
        position="absolute"
        top={0}
        left={0}
        right={0}
        bottom={0}
        bgGradient="linear(135deg, blue.100 0%, blue.200 100%)"
        opacity={0.1}
        _groupHover={{
          opacity: 0.15,
        }}
        transition="opacity 0.3s"
        zIndex={0}
      />

      {/* Barre colorée en haut avec thème bleu */}
      <Box
        height="4px"
        bgGradient="linear(90deg, blue.400, blue.600)"
        width="100%"
        position="absolute"
        top={0}
        left={0}
        zIndex={1}
      />

      <CardBody display="flex" flexDirection="column" flex="1" p={4} position="relative" zIndex={2}>
        <VStack align="start" spacing={3} flex="1" width="full">
          {/* En-tête avec icône et badge */}
          <HStack justify="space-between" width="full" align="start">
            <Box
              p={4}
              bgGradient="linear(135deg, blue.100, blue.200)"
              borderRadius="2xl"
              fontSize="3xl"
              lineHeight={1}
              boxShadow="md"
              transform="rotate(-3deg)"
              _groupHover={{
                transform: 'rotate(0deg) scale(1.1)',
                boxShadow: 'lg',
              }}
              transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            >
              {subjectIcon}
            </Box>
            <Badge
              bg="blue.600"
              color="white"
              fontSize="xs"
              px={4}
              py={1.5}
              borderRadius="full"
              fontWeight="600"
              boxShadow="md"
            >
              {moduleCount} {moduleCount > 1 ? 'modules' : 'module'}
            </Badge>
          </HStack>

          {/* Titre */}
          <Heading
            size="lg"
            color="gray.900"
            fontWeight="700"
            lineHeight="shorter"
            fontSize="xl"
            letterSpacing="-0.02em"
            fontFamily="heading"
          >
            {subjectLabel}
          </Heading>

          {/* Description */}
          <Text
            fontSize="sm"
            color="gray.700"
            lineHeight="1.7"
            flex="1"
            noOfLines={2}
            fontFamily="body"
            fontWeight="400"
          >
            {subjectDescription}
          </Text>

          {/* Indicateur de clic avec animation */}
          <Box width="full" pt={3} borderTop="1px solid" borderColor="blue.100">
            <HStack
              spacing={2}
              color="blue.600"
              fontWeight="600"
              fontSize="xs"
              _groupHover={{
                color: 'blue.700',
                transform: 'translateX(4px)',
              }}
              transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            >
              <Text>Explorer les modules</Text>
              <Icon as={FiArrowRight} boxSize={3} />
            </HStack>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  )
}
