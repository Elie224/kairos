/**
 * Composant pour afficher les badges de l'utilisateur
 */
import { useQuery } from 'react-query'
import {
  Box,
  VStack,
  HStack,
  Text,
  SimpleGrid,
  Card,
  CardBody,
  Badge,
  Icon,
  Tooltip,
  Skeleton,
  Flex,
  Heading,
} from '@chakra-ui/react'
import { FiAward, FiStar, FiTarget, FiZap, FiBook, FiTrendingUp } from 'react-icons/fi'
import api from '../services/api'
import { useAuthStore } from '../store/authStore'

interface BadgeData {
  id: string
  badge_type: string
  earned_at: string
  metadata?: Record<string, any>
}

const badgeConfig: Record<string, { icon: typeof FiAward; color: string; label: string; description: string }> = {
  first_module: {
    icon: FiStar,
    color: 'yellow',
    label: 'Premier Pas',
    description: 'A complété votre premier module',
  },
  perfect_score: {
    icon: FiTarget,
    color: 'green',
    label: 'Score Parfait',
    description: 'A obtenu 100% sur un module',
  },
  streak_days: {
    icon: FiZap,
    color: 'orange',
    label: 'Série',
    description: 'Connexions consécutives',
  },
  subject_master: {
    icon: FiBook,
    color: 'purple',
    label: 'Maître',
    description: 'A maîtrisé une matière',
  },
  speed_learner: {
    icon: FiZap,
    color: 'blue',
    label: 'Apprenant Rapide',
    description: 'A complété rapidement',
  },
  dedicated_learner: {
    icon: FiTrendingUp,
    color: 'pink',
    label: 'Dévoué',
    description: '10+ modules complétés',
  },
  quiz_master: {
    icon: FiTarget,
    color: 'red',
    label: 'Maître Quiz',
    description: 'Excellent aux quiz',
  },
}

export const BadgesDisplay = ({ limit = 8 }: { limit?: number }) => {
  const { user } = useAuthStore()

  const { data: badges, isLoading } = useQuery<BadgeData[]>(
    'user-badges',
    async () => {
      const response = await api.get('/badges/')
      return response.data
    },
    {
      enabled: !!user,
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
    }
  )

  if (isLoading) {
    return (
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
        {[...Array(limit)].map((_, i) => (
          <Card key={i}>
            <CardBody>
              <VStack spacing={2}>
                <Skeleton
                  height="64px"
                  width="64px"
                  borderRadius="full"
                />
                <Skeleton height="20px" width="80%" />
              </VStack>
            </CardBody>
          </Card>
        ))}
      </SimpleGrid>
    )
  }

  const displayedBadges = badges?.slice(0, limit) || []

  if (displayedBadges.length === 0) {
    return (
      <Box textAlign="center" py={8}>
        <Icon as={FiAward} boxSize={12} color="gray.300" mb={4} />
        <Text color="gray.600" fontSize="lg">
          Aucun badge obtenu pour le moment
        </Text>
        <Text color="gray.500" fontSize="sm" mt={2}>
          Complétez des modules pour débloquer vos premiers badges !
        </Text>
      </Box>
    )
  }

  return (
    <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
      {displayedBadges.map((badge) => {
        const config = badgeConfig[badge.badge_type] || {
          icon: FiAward,
          color: 'gray',
          label: badge.badge_type,
          description: 'Badge obtenu',
        }

        return (
          <Tooltip
            key={badge.id}
            label={
              <VStack spacing={1} align="start">
                <Text fontWeight="bold">{config.label}</Text>
                <Text fontSize="xs">{config.description}</Text>
                {badge.metadata && Object.keys(badge.metadata).length > 0 && (
                  <Text fontSize="xs" color="gray.300">
                    {JSON.stringify(badge.metadata)}
                  </Text>
                )}
              </VStack>
            }
            hasArrow
          >
            <Card
              _hover={{
                transform: 'translateY(-4px)',
                boxShadow: 'lg',
              }}
              transition="all 0.3s"
              cursor="pointer"
            >
              <CardBody>
                <VStack spacing={2}>
                  <Box
                    p={4}
                    bgGradient={`linear(to-br, ${config.color}.400, ${config.color}.600)`}
                    borderRadius="full"
                    boxShadow="md"
                  >
                    <Icon as={config.icon} boxSize={8} color="white" />
                  </Box>
                  <Text fontSize="sm" fontWeight="bold" textAlign="center" noOfLines={2}>
                    {config.label}
                  </Text>
                  <Badge colorScheme={config.color} fontSize="xs">
                    {new Date(badge.earned_at).toLocaleDateString('fr-FR', {
                      day: 'numeric',
                      month: 'short',
                    })}
                  </Badge>
                </VStack>
              </CardBody>
            </Card>
          </Tooltip>
        )
      })}
    </SimpleGrid>
  )
}

export default BadgesDisplay
