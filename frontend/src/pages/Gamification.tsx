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
      const response = await api.get('/badges/count')
      return response.data
    },
    {
      enabled: !!user,
      staleTime: 5 * 60 * 1000,
    }
  )

  const { data: badges } = useQuery(
    'all-badges',
    async () => {
      const response = await api.get('/badges/')
      return response.data
    },
    {
      enabled: !!user,
      staleTime: 5 * 60 * 1000,
    }
  )

  return (
    <Box minH="calc(100vh - 80px)" py={{ base: 6, md: 8 }} px={{ base: 4, md: 0 }} bg="gray.50">
      <Container maxW="1200px" px={{ base: 4, md: 6 }}>
        <VStack spacing={6} align="stretch">
          {/* En-tête */}
          <Box>
            <HStack spacing={3} mb={2}>
              <Icon as={FiAward} boxSize={8} color="purple.500" />
              <Heading size={{ base: 'lg', md: 'xl' }} bgGradient="linear-gradient(135deg, purple.500 0%, pink.500 100%)" bgClip="text">
                Gamification & Récompenses
              </Heading>
            </HStack>
            <Text color="gray.600" fontSize={{ base: 'sm', md: 'md' }}>
              Gagnez des badges, complétez des quêtes et montez dans le classement
            </Text>
          </Box>

          {/* Statistiques rapides */}
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
            <Card bgGradient="linear(to-br, yellow.400, yellow.600)" color="white">
              <CardBody>
                <Stat>
                  <StatLabel color="whiteAlpha.900">Badges</StatLabel>
                  <StatNumber>
                    {badgeCountLoading ? (
                      <StatCardSkeleton />
                    ) : (
                      badgeCount || 0
                    )}
                  </StatNumber>
                  <StatHelpText color="whiteAlpha.800">
                    <Icon as={FiStar} mr={1} />
                    Obtenus
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bgGradient="linear(to-br, blue.400, blue.600)" color="white">
              <CardBody>
                <Stat>
                  <StatLabel color="whiteAlpha.900">Quêtes</StatLabel>
                  <StatNumber>5</StatNumber>
                  <StatHelpText color="whiteAlpha.800">
                    <Icon as={FiTarget} mr={1} />
                    Actives
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bgGradient="linear(to-br, green.400, green.600)" color="white">
              <CardBody>
                <Stat>
                  <StatLabel color="whiteAlpha.900">Points</StatLabel>
                  <StatNumber>
                    {badges
                      ? badges.reduce((sum: number, badge: any) => {
                          // Calculer les points basés sur les badges
                          return sum + (badge.rewards?.points || 10)
                        }, 0)
                      : 0}
                  </StatNumber>
                  <StatHelpText color="whiteAlpha.800">
                    <Icon as={FiTrendingUp} mr={1} />
                    Totaux
                  </StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card bgGradient="linear(to-br, purple.400, purple.600)" color="white">
              <CardBody>
                <Stat>
                  <StatLabel color="whiteAlpha.900">Classement</StatLabel>
                  <StatNumber>#--</StatNumber>
                  <StatHelpText color="whiteAlpha.800">
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
                  <Heading size="md">Vos Badges</Heading>
                  <BadgesDisplay limit={12} />
                </VStack>
              </TabPanel>

              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <Heading size="md">Vos Quêtes</Heading>
                  <QuestsDisplay limit={10} />
                </VStack>
              </TabPanel>

              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <Heading size="md">Classement Général</Heading>
                  <LeaderboardDisplay limit={20} />
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
