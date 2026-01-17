/**
 * Page dédiée à la gamification et récompenses
 */
import { useState } from 'react'
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  SimpleGrid,
  Card,
  CardBody,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Icon,
  Badge,
  Divider,
  Skeleton,
  SkeletonText,
} from '@chakra-ui/react'
import { FiAward, FiTarget, FiTrendingUp, FiStar } from 'react-icons/fi'
import { FaTrophy } from 'react-icons/fa'
import { BadgesDisplay } from '../components/BadgesDisplay'
import { QuestsDisplay } from '../components/QuestsDisplay'
import { LeaderboardDisplay } from '../components/LeaderboardDisplay'
import { useQuery } from 'react-query'
import api from '../services/api'
import { useAuthStore } from '../store/authStore'
import { StatCardSkeleton } from '../components/SkeletonLoader'

const Gamification = () => {
  const { user } = useAuthStore()

  const { data: badgeCount, isLoading: badgeCountLoading } = useQuery(
    'badge-count',
    async () => {
      const response = await api.get('/badges/count', {
        timeout: 1000, // Timeout de 1 seconde
      })
      return response.data?.count || 0
    },
    {
      enabled: !!user,
      staleTime: 5 * 60 * 1000,
      retry: 1,
    }
  )

  const { data: badges, isLoading: badgesLoading } = useQuery(
    'all-badges',
    async () => {
      const response = await api.get('/badges/', {
        timeout: 1000, // Timeout de 1 seconde
      })
      return response.data || []
    },
    {
      enabled: !!user,
      staleTime: 5 * 60 * 1000,
      retry: 1,
    }
  )

  const { data: quests, isLoading: questsLoading } = useQuery(
    'user-quests',
    async () => {
      const response = await api.get('/gamification/quests', {
        timeout: 1000, // Timeout de 1 seconde
        params: { limit: 10 },
      })
      return response.data || []
    },
    {
      enabled: !!user,
      staleTime: 2 * 60 * 1000,
      retry: 1,
    }
  )

  const { data: leaderboard, isLoading: leaderboardLoading } = useQuery(
    ['leaderboard', 'points'],
    async () => {
      const response = await api.get('/gamification/leaderboard', {
        timeout: 1000, // Timeout de 1 seconde
        params: {
          leaderboard_type: 'points',
          limit: 100,
        },
      })
      return response.data || []
    },
    {
      enabled: !!user,
      staleTime: 2 * 60 * 1000,
      retry: 1,
    }
  )

  // Calculer les points totaux basés sur les badges
  const totalPoints = badges
    ? badges.reduce((sum: number, badge: any) => {
        // Points par type de badge
        const pointsMap: Record<string, number> = {
          first_module: 10,
          perfect_score: 25,
          streak_days: 15,
          subject_master: 50,
          speed_learner: 20,
          dedicated_learner: 100,
          quiz_master: 30,
        }
        return sum + (pointsMap[badge.badge_type] || 10)
      }, 0)
    : 0

  // Trouver le rang de l'utilisateur
  const userRank = leaderboard
    ? leaderboard.findIndex((entry: any) => entry.user_id === user?.id) + 1
    : null

  // Compter les quêtes actives
  const activeQuests = quests
    ? quests.filter((quest: any) => {
        const progress = quest.requirements
          ? quest.requirements.reduce((sum: number, req: any) => {
              const progress = req.current / req.target
              return sum + Math.min(progress, 1)
            }, 0) / quest.requirements.length
          : 0
        return progress < 1
      }).length
    : 0

  return (
    <Box minH="calc(100vh - 80px)" py={{ base: 6, md: 8 }} px={{ base: 4, md: 0 }} bg="gray.50">
      <Container maxW="1200px" px={{ base: 4, md: 6 }}>
        <VStack spacing={6} align="stretch">
          {/* En-tête */}
          <Box>
            <HStack spacing={3} mb={2}>
              <Icon as={FiAward} boxSize={8} color="purple.500" />
              <Heading size={{ base: 'lg', md: 'xl' }} bgGradient="linear-gradient(135deg, purple.500 0%, pink.500 100%)" bgClip="text">
                Gamification Intelligente Pilotée par l'IA
              </Heading>
            </HStack>
            <Text color="gray.600" fontSize={{ base: 'sm', md: 'md' }}>
              Badges dynamiques, quêtes générées par IA, système de points adaptatif, classement intelligent et bienveillant. Statistiques générées par IA avec recommandations ciblées.
            </Text>
          </Box>

          {/* Statistiques rapides */}
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
            <Card 
              bgGradient="linear(to-br, yellow.400, yellow.600)" 
              color="white"
              _hover={{ transform: 'translateY(-4px)', boxShadow: 'xl' }}
              transition="all 0.3s"
            >
              <CardBody>
                <Stat>
                  <StatLabel color="whiteAlpha.900" fontSize="sm" fontWeight="600">
                    Badges
                  </StatLabel>
                  <StatNumber fontSize="3xl" fontWeight="bold">
                    {badgeCountLoading ? (
                      <Skeleton height="40px" width="60px" />
                    ) : (
                      badgeCount || 0
                    )}
                  </StatNumber>
                  <StatHelpText color="whiteAlpha.800" fontSize="xs">
                    <Icon as={FiStar} mr={1} />
                    Obtenus
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card 
              bgGradient="linear(to-br, blue.400, blue.600)" 
              color="white"
              _hover={{ transform: 'translateY(-4px)', boxShadow: 'xl' }}
              transition="all 0.3s"
            >
              <CardBody>
                <Stat>
                  <StatLabel color="whiteAlpha.900" fontSize="sm" fontWeight="600">
                    Quêtes
                  </StatLabel>
                  <StatNumber fontSize="3xl" fontWeight="bold">
                    {questsLoading ? (
                      <Skeleton height="40px" width="60px" />
                    ) : (
                      activeQuests
                    )}
                  </StatNumber>
                  <StatHelpText color="whiteAlpha.800" fontSize="xs">
                    <Icon as={FiTarget} mr={1} />
                    Actives
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card 
              bgGradient="linear(to-br, green.400, green.600)" 
              color="white"
              _hover={{ transform: 'translateY(-4px)', boxShadow: 'xl' }}
              transition="all 0.3s"
            >
              <CardBody>
                <Stat>
                  <StatLabel color="whiteAlpha.900" fontSize="sm" fontWeight="600">
                    Points
                  </StatLabel>
                  <StatNumber fontSize="3xl" fontWeight="bold">
                    {badgesLoading ? (
                      <Skeleton height="40px" width="80px" />
                    ) : (
                      totalPoints.toLocaleString('fr-FR')
                    )}
                  </StatNumber>
                  <StatHelpText color="whiteAlpha.800" fontSize="xs">
                    <Icon as={FiTrendingUp} mr={1} />
                    Totaux
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card 
              bgGradient="linear(to-br, purple.400, purple.600)" 
              color="white"
              _hover={{ transform: 'translateY(-4px)', boxShadow: 'xl' }}
              transition="all 0.3s"
            >
              <CardBody>
                <Stat>
                  <StatLabel color="whiteAlpha.900" fontSize="sm" fontWeight="600">
                    Classement
                  </StatLabel>
                  <StatNumber fontSize="3xl" fontWeight="bold">
                    {leaderboardLoading ? (
                      <Skeleton height="40px" width="60px" />
                    ) : userRank ? (
                      `#${userRank}`
                    ) : (
                      '--'
                    )}
                  </StatNumber>
                  <StatHelpText color="whiteAlpha.800" fontSize="xs">
                    <Icon as={FaTrophy} mr={1} />
                    Position
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>

          <Divider />

          {/* Onglets */}
          <Tabs colorScheme="purple" variant="enclosed">
            <TabList>
              <Tab>
                <HStack spacing={2}>
                  <Icon as={FiAward} />
                  <Text>Badges</Text>
                </HStack>
              </Tab>
              <Tab>
                <HStack spacing={2}>
                  <Icon as={FiTarget} />
                  <Text>Quêtes</Text>
                </HStack>
              </Tab>
              <Tab>
                <HStack spacing={2}>
                  <Icon as={FaTrophy} />
                  <Text>Classement</Text>
                </HStack>
              </Tab>
            </TabList>

            <TabPanels>
              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between" align="center">
                    <Heading size="md">Vos Badges</Heading>
                    {badges && badges.length > 0 && (
                      <Badge colorScheme="yellow" fontSize="sm" px={3} py={1}>
                        {badges.length} badge{badges.length > 1 ? 's' : ''}
                      </Badge>
                    )}
                  </HStack>
                  {badgesLoading ? (
                    <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                      {[...Array(8)].map((_, i) => (
                        <Card key={i}>
                          <CardBody>
                            <VStack spacing={2}>
                              <Skeleton height="64px" width="64px" borderRadius="full" />
                              <Skeleton height="20px" width="80%" />
                            </VStack>
                          </CardBody>
                        </Card>
                      ))}
                    </SimpleGrid>
                  ) : (
                    <BadgesDisplay limit={12} />
                  )}
                </VStack>
              </TabPanel>

              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between" align="center">
                    <Heading size="md">Vos Quêtes</Heading>
                    {quests && quests.length > 0 && (
                      <Badge colorScheme="blue" fontSize="sm" px={3} py={1}>
                        {activeQuests} active{activeQuests > 1 ? 's' : ''}
                      </Badge>
                    )}
                  </HStack>
                  {questsLoading ? (
                    <VStack spacing={4} align="stretch">
                      {[...Array(5)].map((_, i) => (
                        <Card key={i}>
                          <CardBody>
                            <Skeleton height="100px" />
                          </CardBody>
                        </Card>
                      ))}
                    </VStack>
                  ) : (
                    <QuestsDisplay limit={10} />
                  )}
                </VStack>
              </TabPanel>

              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between" align="center">
                    <Heading size="md">Classement Général</Heading>
                    {leaderboard && leaderboard.length > 0 && (
                      <Badge colorScheme="purple" fontSize="sm" px={3} py={1}>
                        {leaderboard.length} participant{leaderboard.length > 1 ? 's' : ''}
                      </Badge>
                    )}
                  </HStack>
                  {leaderboardLoading ? (
                    <VStack spacing={2} align="stretch">
                      {[...Array(10)].map((_, i) => (
                        <Card key={i}>
                          <CardBody>
                            <HStack spacing={4}>
                              <Skeleton height="40px" width="40px" borderRadius="full" />
                              <SkeletonText flex={1} noOfLines={2} />
                            </HStack>
                          </CardBody>
                        </Card>
                      ))}
                    </VStack>
                  ) : (
                    <LeaderboardDisplay limit={20} />
                  )}
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </VStack>
      </Container>
    </Box>
  )
}

export default Gamification
