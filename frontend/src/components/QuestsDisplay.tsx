/**
 * Composant pour afficher les quêtes de l'utilisateur
 */
import { useQuery } from 'react-query'
import {
  Box,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  Badge,
  Icon,
  Progress,
  Button,
  SimpleGrid,
  Skeleton,
  SkeletonText,
  Flex,
  Heading,
} from '@chakra-ui/react'
import { FiTarget, FiClock, FiAward, FiCheckCircle } from 'react-icons/fi'
import api from '../services/api'
import { useAuthStore } from '../store/authStore'
import { API_TIMEOUTS } from '../constants/api'
import logger from '../utils/logger'

interface QuestRequirement {
  type: string
  target: any
  current: any
}

interface Quest {
  id: string
  title: string
  description: string
  quest_type: string
  requirements: QuestRequirement[]
  rewards: Record<string, any>
  difficulty: string
  subject?: string
  expires_at?: string
}

export const QuestsDisplay = ({ limit = 5 }: { limit?: number }) => {
  const { user } = useAuthStore()

  const { data: quests, isLoading, refetch } = useQuery<Quest[]>(
    'user-quests',
    async () => {
      try {
        const response = await api.get('/gamification/quests', {
          timeout: API_TIMEOUTS.SIMPLE, // 10 secondes pour les quêtes
          params: { limit },
        })
        return response.data || []
      } catch (error) {
        logger.error('Erreur lors de la récupération des quêtes', error, 'QuestsDisplay')
        return []
      }
    },
    {
      enabled: !!user,
      staleTime: 2 * 60 * 1000,
      cacheTime: 5 * 60 * 1000,
      retry: 1,
    }
  )

  if (isLoading) {
    return (
      <VStack spacing={4} align="stretch">
        {[...Array(limit)].map((_, i) => (
          <Card key={i}>
            <CardBody>
              <Skeleton height="20px" mb={2} />
              <SkeletonText noOfLines={2} />
            </CardBody>
          </Card>
        ))}
      </VStack>
    )
  }

  if (!quests || quests.length === 0) {
    return (
      <Box textAlign="center" py={8}>
        <Icon as={FiTarget} boxSize={12} color="gray.300" mb={4} />
        <Text color="gray.600" fontSize="lg">
          Aucune quête disponible
        </Text>
        <Text color="gray.500" fontSize="sm" mt={2}>
          De nouvelles quêtes seront disponibles bientôt !
        </Text>
      </Box>
    )
  }

  const getQuestTypeColor = (type: string) => {
    switch (type) {
      case 'daily':
        return 'blue'
      case 'weekly':
        return 'purple'
      case 'achievement':
        return 'green'
      case 'challenge':
        return 'red'
      default:
        return 'gray'
    }
  }

  const getQuestTypeLabel = (type: string) => {
    switch (type) {
      case 'daily':
        return 'Quotidienne'
      case 'weekly':
        return 'Hebdomadaire'
      case 'achievement':
        return 'Réalisation'
      case 'challenge':
        return 'Défi'
      default:
        return type
    }
  }

  const calculateProgress = (requirements: QuestRequirement[]) => {
    if (requirements.length === 0) return 0
    const totalProgress = requirements.reduce((sum, req) => {
      const progress = req.current / req.target
      return sum + Math.min(progress, 1)
    }, 0)
    return (totalProgress / requirements.length) * 100
  }

  return (
    <VStack spacing={4} align="stretch">
      {quests.map((quest) => {
        const progress = calculateProgress(quest.requirements)
        const isCompleted = progress >= 100

        return (
          <Card
            key={quest.id}
            _hover={{
              transform: 'translateY(-2px)',
              boxShadow: 'lg',
            }}
            transition="all 0.3s"
            border={isCompleted ? '2px solid' : '1px solid'}
            borderColor={isCompleted ? 'green.300' : 'gray.200'}
          >
            <CardBody>
              <VStack spacing={3} align="stretch">
                <Flex justify="space-between" align="start">
                  <VStack align="start" spacing={1} flex={1}>
                    <HStack spacing={2}>
                      <Heading size="sm">{quest.title}</Heading>
                      {isCompleted && (
                        <Icon as={FiCheckCircle} color="green.500" boxSize={5} />
                      )}
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      {quest.description}
                    </Text>
                  </VStack>
                  <Badge colorScheme={getQuestTypeColor(quest.quest_type)}>
                    {getQuestTypeLabel(quest.quest_type)}
                  </Badge>
                </Flex>

                {quest.requirements && quest.requirements.length > 0 && (
                  <Box>
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="xs" color="gray.600">
                        Progression
                      </Text>
                      <Text fontSize="xs" fontWeight="bold" color="gray.700">
                        {Math.round(progress)}%
                      </Text>
                    </HStack>
                    <Progress
                      value={progress}
                      colorScheme={isCompleted ? 'green' : getQuestTypeColor(quest.quest_type)}
                      size="sm"
                      borderRadius="full"
                      hasStripe={!isCompleted}
                      isAnimated={!isCompleted}
                    />
                    <VStack spacing={1} align="stretch" mt={2}>
                      {quest.requirements.map((req, idx) => (
                        <HStack key={idx} justify="space-between" fontSize="xs">
                          <Text color="gray.600">
                            {req.type === 'complete_modules'
                              ? 'Modules complétés'
                              : req.type === 'score_threshold'
                              ? 'Score minimum'
                              : req.type}
                          </Text>
                          <Text fontWeight="bold">
                            {req.current} / {req.target}
                          </Text>
                        </HStack>
                      ))}
                    </VStack>
                  </Box>
                )}

                {quest.rewards && Object.keys(quest.rewards).length > 0 && (
                  <HStack spacing={2}>
                    <Icon as={FiAward} color="yellow.500" />
                    <Text fontSize="xs" color="gray.600">
                      Récompenses :{' '}
                      {quest.rewards.points && `${quest.rewards.points} points`}
                      {quest.rewards.badge && ` + Badge ${quest.rewards.badge}`}
                    </Text>
                  </HStack>
                )}

                {quest.expires_at && (
                  <HStack spacing={2} fontSize="xs" color="gray.500">
                    <Icon as={FiClock} />
                    <Text>
                      Expire le{' '}
                      {new Date(quest.expires_at).toLocaleDateString('fr-FR', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                      })}
                    </Text>
                  </HStack>
                )}
              </VStack>
            </CardBody>
          </Card>
        )
      })}
    </VStack>
  )
}

export default QuestsDisplay
