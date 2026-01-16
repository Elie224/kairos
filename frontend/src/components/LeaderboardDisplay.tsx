/**
 * Composant pour afficher le classement
 */
import { useState } from 'react'
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
  Avatar,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Skeleton,
  SkeletonText,
  Flex,
  Heading,
  Select,
} from '@chakra-ui/react'
import { FiAward, FiTrendingUp, FiStar } from 'react-icons/fi'
import { FaTrophy, FaMedal } from 'react-icons/fa'
import api from '../services/api'
import { useAuthStore } from '../store/authStore'

interface LeaderboardEntry {
  user_id: string
  username: string
  score: number
  rank: number
  badge?: string
}

export const LeaderboardDisplay = ({ limit = 10 }: { limit?: number }) => {
  const { user } = useAuthStore()
  const [leaderboardType, setLeaderboardType] = useState<'points' | 'modules' | 'streak'>('points')

  const { data: leaderboard, isLoading } = useQuery<LeaderboardEntry[]>(
    ['leaderboard', leaderboardType],
    async () => {
      const response = await api.get('/gamification/leaderboard', {
        params: {
          leaderboard_type: leaderboardType,
          limit,
        },
      })
      return response.data
    },
    {
      enabled: !!user,
      staleTime: 2 * 60 * 1000,
      cacheTime: 5 * 60 * 1000,
    }
  )

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Icon as={FaTrophy} color="yellow.500" boxSize={6} />
    if (rank === 2) return <Icon as={FaMedal} color="gray.400" boxSize={6} />
    if (rank === 3) return <Icon as={FaMedal} color="orange.500" boxSize={6} />
    return <Text fontWeight="bold" fontSize="lg">
      {rank}
    </Text>
  }

  const getRankColor = (rank: number) => {
    if (rank === 1) return 'yellow'
    if (rank === 2) return 'gray'
    if (rank === 3) return 'orange'
    return 'blue'
  }

  if (isLoading) {
    return (
      <VStack spacing={4} align="stretch">
        {[...Array(limit)].map((_, i) => (
          <Card key={i}>
            <CardBody>
              <HStack spacing={4}>
                <Skeleton
                  height="40px"
                  width="40px"
                  borderRadius="full"
                />
                <SkeletonText flex={1} noOfLines={2} />
              </HStack>
            </CardBody>
          </Card>
        ))}
      </VStack>
    )
  }

  if (!leaderboard || leaderboard.length === 0) {
    return (
      <Box textAlign="center" py={8}>
        <Icon as={FaTrophy} boxSize={12} color="gray.300" mb={4} />
        <Text color="gray.600" fontSize="lg">
          Aucun classement disponible
        </Text>
      </Box>
    )
  }

  const currentUserRank = leaderboard.findIndex((entry) => entry.user_id === user?.id) + 1

  return (
    <VStack spacing={4} align="stretch">
      <Flex justify="space-between" align="center">
        <HStack spacing={2}>
          <Icon as={FaTrophy} color="yellow.500" />
          <Heading size="md">Classement</Heading>
        </HStack>
        <Select
          value={leaderboardType}
          onChange={(e) => setLeaderboardType(e.target.value as any)}
          size="sm"
          width="auto"
        >
          <option value="points">Points</option>
          <option value="modules">Modules</option>
          <option value="streak">Série</option>
        </Select>
      </Flex>

      {currentUserRank > 0 && (
        <Card bgGradient="linear(to-r, blue.50, purple.50)" border="2px solid" borderColor="blue.300">
          <CardBody>
            <HStack spacing={4}>
              <Box>{getRankIcon(currentUserRank)}</Box>
              <VStack align="start" spacing={0} flex={1}>
                <HStack>
                  <Text fontWeight="bold">Vous</Text>
                  <Badge colorScheme={getRankColor(currentUserRank)}>
                    #{currentUserRank}
                  </Badge>
                </HStack>
                <Text fontSize="sm" color="gray.600">
                  {leaderboard[currentUserRank - 1]?.score.toFixed(0) || 0} points
                </Text>
              </VStack>
            </HStack>
          </CardBody>
        </Card>
      )}

      <VStack spacing={2} align="stretch">
        {leaderboard.slice(0, limit).map((entry) => {
          const isCurrentUser = entry.user_id === user?.id

          return (
            <Card
              key={entry.user_id}
              bg={isCurrentUser ? 'blue.50' : 'white'}
              border={isCurrentUser ? '2px solid' : '1px solid'}
              borderColor={isCurrentUser ? 'blue.300' : 'gray.200'}
              _hover={{
                transform: 'translateX(4px)',
                boxShadow: 'md',
              }}
              transition="all 0.2s"
            >
              <CardBody py={3}>
                <HStack spacing={4}>
                  <Box minW="40px" textAlign="center">
                    {getRankIcon(entry.rank)}
                  </Box>
                  <Avatar
                    size="sm"
                    name={entry.username}
                    src={`https://api.dicebear.com/6.x/initials/svg?seed=${entry.username}`}
                  />
                  <VStack align="start" spacing={0} flex={1}>
                    <HStack>
                      <Text fontWeight="bold" fontSize="sm">
                        {entry.username}
                      </Text>
                      {entry.badge && (
                        <Badge colorScheme="purple" fontSize="xs">
                          {entry.badge}
                        </Badge>
                      )}
                    </HStack>
                    <HStack spacing={2}>
                      <Icon as={FiTrendingUp} color="green.500" boxSize={3} />
                      <Text fontSize="xs" color="gray.600">
                        {entry.score.toFixed(0)} points
                      </Text>
                    </HStack>
                  </VStack>
                </HStack>
              </CardBody>
            </Card>
          )
        })}
      </VStack>
    </VStack>
  )
}

export default LeaderboardDisplay
