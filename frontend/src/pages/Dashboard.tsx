import { useQuery } from 'react-query'
import { Container, VStack, Heading, SimpleGrid, Card, CardBody, Text, Stat, StatLabel, StatNumber, StatHelpText, Progress, Box, Button, HStack, Icon, Badge, Divider, Flex, Wrap, WrapItem } from '@chakra-ui/react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FiBook, FiClock, FiTrendingUp, FiAward, FiArrowRight, FiFileText, FiMessageCircle, FiCheckCircle, FiBarChart2, FiUsers, FiCpu } from 'react-icons/fi'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import { StatCardSkeleton } from '../components/SkeletonLoader'

interface ProgressStats {
  total_modules: number
  completed_modules: number
  completion_rate: number
  total_time_spent: number
  average_score: number | null
}

interface HistoryStats {
  total_questions: number
  total_tokens: number
  total_cost: number
  by_subject: Record<string, number>
  by_model: Record<string, number>
}

const Dashboard = () => {
  const { t } = useTranslation()
  const { user } = useAuthStore()
  // Chargement prioritaire : Stats d'abord (affichage immédiat)
  const { data: stats, isLoading: statsLoading } = useQuery<ProgressStats>(
    'progress-stats',
    async () => {
      const response = await api.get('/progress/stats', {
        timeout: 30000, // Timeout de 30 secondes
      })
      return response.data
    },
    {
      staleTime: 5 * 60 * 1000, // 5 minutes - cache plus long
      cacheTime: 10 * 60 * 1000,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      retry: 1, // Réessayer une seule fois
      retryDelay: 1000,
    }
  )

  // Chargement secondaire : Modules (peut attendre)
  const { data: modules } = useQuery(
    'modules',
    async () => {
      const response = await api.get('/modules/', {
        timeout: 30000, // Timeout de 30 secondes
        params: { limit: 50 }, // Limiter à 50 modules pour la performance
      })
      return response.data
    },
    {
      staleTime: 10 * 60 * 1000, // 10 minutes - cache très long
      cacheTime: 30 * 60 * 1000,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      retry: 1,
      enabled: !statsLoading, // Charger seulement après les stats
    }
  )

  // Chargement secondaire : Progression (peut attendre)
  const { data: progress, isError: progressError, error: progressErrorObj } = useQuery(
    'progress',
    async () => {
      const response = await api.get('/progress/', {
        timeout: 30000, // Timeout de 30 secondes
        params: { limit: 10 }, // Limiter à 10 pour la performance
      })
      return response.data
    },
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      retry: 1,
      enabled: !statsLoading, // Charger seulement après les stats
    }
  )

  // Chargement secondaire : Validations (peut attendre)
  const { data: validatedModules } = useQuery(
    'validated-modules',
    async () => {
      const response = await api.get('/validations/modules', {
        timeout: 30000, // Timeout de 30 secondes
      })
      return response.data as string[]
    },
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      retry: 1,
      enabled: !statsLoading, // Charger seulement après les stats
    }
  )

  // Chargement des statistiques de l'historique Kaïros
  const { data: historyStats } = useQuery<HistoryStats>(
    'history-stats',
    async () => {
      const response = await api.get('/user-history/stats', {
        timeout: 30000, // Timeout de 30 secondes
      })
      return response.data
    },
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      retry: 1,
      enabled: !statsLoading,
    }
  )

  const isLoading = statsLoading

  // Trouver les modules récents avec progression
  const recentProgress = (progress && Array.isArray(progress)) ? progress.slice(0, 3) : []
  const recentModules = recentProgress.map((p: any) => {
    const module = (modules && Array.isArray(modules)) ? modules.find((m: any) => m.id === p.module_id) : null
    return { ...p, module }
  }).filter((item: any) => item.module)

  const subjectColors: Record<string, string> = {
    mathematics: 'blue',
    computer_science: 'purple',
  }

  return (
    <Box
      minH="100vh"
      bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)"
      py={{ base: 6, md: 8 }}
    >
      <Container maxW="1200px">
        <VStack spacing={{ base: 6, md: 8 }} align="stretch">
          {/* En-tête amélioré avec thème bleu */}
          <Box>
            <VStack spacing={3} align="start">
              <HStack spacing={4} align="center">
                <Box
                  p={3}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  borderRadius="xl"
                  boxShadow="lg"
                >
                  <Icon as={FiTrendingUp} boxSize={5} color="white" />
                </Box>
                <Heading 
                  size={{ base: 'lg', md: 'xl' }} 
                  color="gray.900"
                  fontWeight="700"
                  letterSpacing="-0.02em"
                  fontFamily="heading"
                >
                  {t('dashboard.title')}
                </Heading>
              </HStack>
              <Text 
                color="gray.700" 
                fontSize={{ base: 'md', md: 'lg' }} 
                fontWeight="500"
                fontFamily="body"
                lineHeight="1.7"
              >
                {t('dashboard.welcome', { username: user?.username || user?.email || 'Utilisateur' })}
              </Text>
            </VStack>
          </Box>

        {isLoading ? (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </SimpleGrid>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            <Card 
              bg="white"
              _hover={{ 
                transform: { base: 'none', md: 'translateY(-8px) scale(1.02)' }, 
                boxShadow: { base: 'soft-lg', md: 'xl' },
                borderColor: 'blue.400',
                borderWidth: '2px'
              }} 
              transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
              border="2px solid"
              borderColor="blue.100"
              borderRadius="2xl"
              className="hover-lift"
              boxShadow="soft-lg"
            >
              <CardBody p={{ base: 4, md: 6 }}>
                <HStack spacing={{ base: 3, md: 4 }}>
                  <Box 
                    p={{ base: 3, md: 4 }} 
                    bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                    borderRadius="xl"
                    boxShadow="md"
                  >
                    <Icon as={FiBook} boxSize={{ base: 5, md: 6 }} color="white" />
                  </Box>
                  <Stat>
                    <StatLabel 
                      color="gray.700" 
                      fontWeight="600" 
                      fontSize={{ base: 'xs', md: 'sm' }}
                      fontFamily="body"
                    >
                      {t('dashboard.completedModules')}
                    </StatLabel>
                    <StatNumber 
                      fontSize={{ base: '2xl', md: '3xl' }} 
                      fontWeight="700" 
                      color="gray.900"
                      fontFamily="heading"
                    >
                      {stats?.completed_modules || 0}
                    </StatNumber>
                    <StatHelpText 
                      color="gray.600" 
                      fontSize={{ base: '2xs', md: 'xs' }}
                      fontFamily="body"
                    >
                      {t('dashboard.onModules', { total: stats?.total_modules || 0 })}
                    </StatHelpText>
                  </Stat>
                </HStack>
              </CardBody>
            </Card>

            <Card 
              bg="white"
              _hover={{ 
                transform: { base: 'none', md: 'translateY(-8px) scale(1.02)' }, 
                boxShadow: { base: 'soft-lg', md: 'xl' },
                borderColor: 'blue.400',
                borderWidth: '2px'
              }} 
              transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
              border="2px solid"
              borderColor="blue.100"
              borderRadius="2xl"
              className="hover-lift"
              boxShadow="soft-lg"
            >
              <CardBody p={{ base: 4, md: 6 }}>
                <HStack spacing={{ base: 3, md: 4 }}>
                  <Box 
                    p={{ base: 3, md: 4 }} 
                    bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                    borderRadius="xl"
                    boxShadow="md"
                  >
                    <Icon as={FiTrendingUp} boxSize={{ base: 5, md: 6 }} color="white" />
                  </Box>
                  <Stat>
                    <StatLabel 
                      color="gray.700" 
                      fontWeight="600" 
                      fontSize={{ base: 'xs', md: 'sm' }}
                      fontFamily="body"
                    >
                      {t('dashboard.completionRate')}
                    </StatLabel>
                    <StatNumber 
                      fontSize={{ base: '2xl', md: '3xl' }} 
                      fontWeight="700" 
                      color="gray.900"
                      fontFamily="heading"
                    >
                      {(stats?.completion_rate ?? 0).toFixed(1)}%
                    </StatNumber>
                    <StatHelpText mt={2}>
                      <Progress 
                        value={stats?.completion_rate || 0} 
                        colorScheme="blue" 
                        size="sm" 
                        borderRadius="full"
                        bg="blue.50"
                      />
                    </StatHelpText>
                  </Stat>
                </HStack>
              </CardBody>
            </Card>

            <Card 
              bg="white"
              _hover={{ 
                transform: { base: 'none', md: 'translateY(-8px) scale(1.02)' }, 
                boxShadow: { base: 'soft-lg', md: 'xl' },
                borderColor: 'blue.400',
                borderWidth: '2px'
              }} 
              transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
              border="2px solid"
              borderColor="blue.100"
              borderRadius="2xl"
              className="hover-lift"
              boxShadow="soft-lg"
            >
              <CardBody p={{ base: 4, md: 6 }}>
                <HStack spacing={{ base: 3, md: 4 }}>
                  <Box 
                    p={{ base: 3, md: 4 }} 
                    bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                    borderRadius="xl"
                    boxShadow="md"
                  >
                    <Icon as={FiClock} boxSize={{ base: 5, md: 6 }} color="white" />
                  </Box>
                  <Stat>
                    <StatLabel 
                      color="gray.700" 
                      fontWeight="600" 
                      fontSize={{ base: 'xs', md: 'sm' }}
                      fontFamily="body"
                    >
                      {t('dashboard.totalTime')}
                    </StatLabel>
                    <StatNumber 
                      fontSize={{ base: '2xl', md: '3xl' }} 
                      fontWeight="700" 
                      color="gray.900"
                      fontFamily="heading"
                    >
                      {Math.floor((stats?.total_time_spent || 0) / 60)}
                    </StatNumber>
                    <StatHelpText 
                      color="gray.600" 
                      fontSize={{ base: '2xs', md: 'xs' }}
                      fontFamily="body"
                    >
                      {t('dashboard.minutes')} {t('dashboard.timeSpent')}
                    </StatHelpText>
                  </Stat>
                </HStack>
              </CardBody>
            </Card>

            {/* Statistiques Kaïros */}
            {historyStats && historyStats.total_questions > 0 && (
              <Card 
                bg="white"
                _hover={{ 
                  transform: { base: 'none', md: 'translateY(-8px) scale(1.02)' }, 
                  boxShadow: { base: 'soft-lg', md: 'xl' },
                  borderColor: 'purple.400',
                  borderWidth: '2px'
                }} 
                transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
                border="2px solid"
                borderColor="purple.100"
                borderRadius="2xl"
                className="hover-lift"
                boxShadow="soft-lg"
              >
                <CardBody p={{ base: 4, md: 6 }}>
                  <HStack spacing={{ base: 3, md: 4 }}>
                    <Box 
                      p={{ base: 3, md: 4 }} 
                      bgGradient="linear-gradient(135deg, purple.500 0%, purple.600 100%)"
                      borderRadius="xl"
                      boxShadow="md"
                    >
                      <Icon as={FiMessageCircle} boxSize={{ base: 5, md: 6 }} color="white" />
                    </Box>
                    <Stat>
                      <StatLabel 
                        color="gray.700" 
                        fontWeight="600" 
                        fontSize={{ base: 'xs', md: 'sm' }}
                        fontFamily="body"
                      >
                        Conversations Kaïros
                      </StatLabel>
                      <StatNumber 
                        fontSize={{ base: '2xl', md: '3xl' }} 
                        fontWeight="700" 
                        color="gray.900"
                        fontFamily="heading"
                      >
                        {historyStats.total_questions || 0}
                      </StatNumber>
                      <StatHelpText 
                        color="gray.600" 
                        fontSize={{ base: '2xs', md: 'xs' }}
                        fontFamily="body"
                      >
                        Questions posées à Kaïros
                      </StatHelpText>
                    </Stat>
                  </HStack>
                </CardBody>
              </Card>
            )}
          </SimpleGrid>
        )}

        {/* Statistiques par matière */}
        {historyStats && historyStats.by_subject && Object.keys(historyStats.by_subject).length > 0 && (
          <Card 
            bg="white" 
            p={{ base: 6, md: 8 }} 
            borderRadius="2xl" 
            boxShadow="soft-lg"
            border="2px solid"
            borderColor="blue.100"
          >
            <VStack spacing={6} align="stretch">
              <HStack spacing={3} align="center">
                <Box
                  p={2}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  borderRadius="lg"
                  boxShadow="md"
                >
                  <Icon as={FiBarChart2} boxSize={4} color="white" />
                </Box>
                <Heading 
                  size="md" 
                  color="gray.900"
                  fontWeight="700"
                  letterSpacing="-0.02em"
                  fontFamily="heading"
                >
                  Statistiques par matière
                </Heading>
              </HStack>
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                {Object.entries(historyStats.by_subject).map(([subject, count]) => (
                  <Card key={subject} bg="gray.50" border="1px solid" borderColor="gray.200">
                    <CardBody>
                      <HStack justify="space-between">
                        <VStack align="start" spacing={1}>
                          <Text 
                            fontWeight="600" 
                            color="gray.700"
                            fontSize="sm"
                            textTransform="capitalize"
                            fontFamily="body"
                          >
                            {subject === 'computer_science' ? 'Informatique' : 
                             subject === 'mathematics' ? 'Mathématiques' : subject}
                          </Text>
                          <Text 
                            fontSize="2xl" 
                            fontWeight="700" 
                            color="blue.600"
                            fontFamily="heading"
                          >
                            {count as number}
                          </Text>
                        </VStack>
                        <Icon as={FiCpu} boxSize={6} color="blue.500" />
                      </HStack>
                    </CardBody>
                  </Card>
                ))}
              </SimpleGrid>
            </VStack>
          </Card>
        )}

        {/* Liste des modules disponibles */}
        {modules && Array.isArray(modules) && modules.length > 0 && (
          <Card 
            bg="white" 
            p={{ base: 6, md: 8 }} 
            borderRadius="2xl" 
            boxShadow="soft-lg"
            border="2px solid"
            borderColor="blue.100"
          >
            <VStack spacing={6} align="stretch">
              <Flex justify="space-between" align="center">
                <HStack spacing={3} align="center">
                  <Box
                    p={2}
                    bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                    borderRadius="lg"
                    boxShadow="md"
                  >
                    <Icon as={FiBook} boxSize={4} color="white" />
                  </Box>
                  <Heading 
                    size="md" 
                    color="gray.900"
                    fontWeight="700"
                    letterSpacing="-0.02em"
                    fontFamily="heading"
                  >
                    Modules disponibles
                  </Heading>
                </HStack>
                <Link to="/modules">
                  <Button 
                    size="sm" 
                    colorScheme="blue" 
                    variant="ghost"
                    rightIcon={<FiArrowRight />}
                    fontFamily="body"
                  >
                    Voir tout
                  </Button>
                </Link>
              </Flex>
              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                {modules.slice(0, 6).map((module: any) => {
                  const moduleProgress = progress && Array.isArray(progress) 
                    ? progress.find((p: any) => p.module_id === module.id)
                    : null
                  const isCompleted = moduleProgress?.completed || false
                  const isValidated = validatedModules?.includes(module.id) || false
                  
                  return (
                    <Link key={module.id} to={`/modules/${module.id}`}>
                      <Card 
                        _hover={{ 
                          bg: 'blue.50', 
                          transform: { base: 'none', md: 'translateY(-4px) scale(1.02)' },
                          borderColor: 'blue.400',
                          boxShadow: { base: 'sm', md: 'lg' }
                        }} 
                        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                        border="2px solid"
                        borderColor={isCompleted ? 'green.200' : 'blue.100'}
                        borderRadius="xl"
                        bg="white"
                        h="100%"
                      >
                        <CardBody p={{ base: 4, md: 6 }}>
                          <VStack align="start" spacing={3}>
                            <HStack spacing={2} w="100%" justify="space-between">
                              <Badge 
                                bg={subjectColors[module.subject] || 'gray' + '.600'}
                                color="white"
                                fontWeight="600"
                                px={3}
                                py={1}
                                borderRadius="full"
                                boxShadow="sm"
                                textTransform="capitalize"
                              >
                                {module.subject === 'computer_science' ? 'Informatique' : 
                                 module.subject === 'mathematics' ? 'Mathématiques' : module.subject}
                              </Badge>
                              {isCompleted && (
                                <Badge 
                                  bg="green.500"
                                  color="white"
                                  variant="solid"
                                  fontWeight="600"
                                  px={3}
                                  py={1}
                                  borderRadius="full"
                                  boxShadow="sm"
                                >
                                  <Icon as={FiCheckCircle} mr={1} />
                                  Complété
                                </Badge>
                              )}
                              {isValidated && (
                                <Badge 
                                  bg="purple.500"
                                  color="white"
                                  variant="solid"
                                  fontWeight="600"
                                  px={3}
                                  py={1}
                                  borderRadius="full"
                                  boxShadow="sm"
                                >
                                  Validé
                                </Badge>
                              )}
                            </HStack>
                            <Heading 
                              size="sm" 
                              color="gray.900" 
                              fontWeight="700"
                              fontFamily="heading"
                              noOfLines={2}
                            >
                              {module.title}
                            </Heading>
                            {module.description && (
                              <Text 
                                fontSize="sm" 
                                color="gray.600" 
                                noOfLines={2}
                                fontFamily="body"
                              >
                                {module.description}
                              </Text>
                            )}
                            {moduleProgress && (
                              <Box w="100%">
                                <HStack justify="space-between" mb={1}>
                                  <Text fontSize="xs" color="gray.600" fontFamily="body">
                                    Progression
                                  </Text>
                                  <Text fontSize="xs" fontWeight="600" color="gray.700" fontFamily="body">
                                    {moduleProgress.score ? `${Math.round(moduleProgress.score)}%` : '0%'}
                                  </Text>
                                </HStack>
                                <Progress 
                                  value={moduleProgress.score || 0} 
                                  colorScheme="blue" 
                                  size="sm" 
                                  borderRadius="full"
                                  bg="blue.50"
                                />
                              </Box>
                            )}
                            <HStack spacing={2} fontSize="xs" color="gray.500" fontFamily="body">
                              <Icon as={FiClock} />
                              <Text>
                                {module.difficulty === 'beginner' ? 'Débutant' : 
                                 module.difficulty === 'intermediate' ? 'Intermédiaire' : 
                                 module.difficulty === 'advanced' ? 'Avancé' : module.difficulty}
                              </Text>
                            </HStack>
                          </VStack>
                        </CardBody>
                      </Card>
                    </Link>
                  )
                })}
              </SimpleGrid>
            </VStack>
          </Card>
        )}

        {progressError && !isLoading && (
          <Box 
            bg="yellow.50" 
            borderRadius="xl" 
            p={4} 
            border="2px solid" 
            borderColor="yellow.200"
            boxShadow="soft"
          >
            <Text 
              color="yellow.800" 
              fontWeight="600"
              fontFamily="body"
            >
              {t('dashboard.progressFetchError') || 'Impossible de charger la progression utilisateur pour le moment.'}
            </Text>
            {progressErrorObj?.message && (
              <Text 
                color="yellow.700" 
                fontSize="sm"
                fontFamily="body"
                mt={2}
              >
                {progressErrorObj.message}
              </Text>
            )}
          </Box>
        )}

        {stats && stats.average_score !== null && stats.average_score !== undefined && (
          <Card 
            bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
            color="white"
            borderRadius="2xl"
            boxShadow="xl"
            border="2px solid"
            borderColor="blue.400"
            _hover={{
              transform: 'scale(1.02)',
              boxShadow: 'glow-blue-lg'
            }}
            transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
          >
            <CardBody>
              <HStack spacing={4}>
                <Box 
                  p={4} 
                  bg="whiteAlpha.300"
                  backdropFilter="blur(10px)"
                  borderRadius="xl"
                  boxShadow="md"
                >
                  <Icon as={FiAward} boxSize={6} color="white" />
                </Box>
                <Stat>
                  <StatLabel 
                    color="whiteAlpha.900" 
                    fontWeight="600"
                    fontFamily="body"
                  >
                    {t('dashboard.averageScore')}
                  </StatLabel>
                  <StatNumber 
                    fontSize="3xl" 
                    color="white"
                    fontWeight="700"
                    fontFamily="heading"
                  >
                    {(stats.average_score ?? 0).toFixed(1)}%
                  </StatNumber>
                  <StatHelpText 
                    color="whiteAlpha.800"
                    fontFamily="body"
                  >
                    {t('dashboard.onAllQuizzes')}
                  </StatHelpText>
                </Stat>
              </HStack>
            </CardBody>
          </Card>
        )}

        {recentModules.length > 0 && (
          <Box 
            bg="white" 
            p={{ base: 6, md: 8 }} 
            borderRadius="2xl" 
            boxShadow="soft-lg"
            border="2px solid"
            borderColor="blue.100"
          >
            <VStack spacing={6} align="stretch">
              <HStack spacing={3} align="center">
                <Box
                  p={2}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  borderRadius="lg"
                  boxShadow="md"
                >
                  <Icon as={FiBook} boxSize={4} color="white" />
                </Box>
                <Heading 
                  size="md" 
                  color="gray.900"
                  fontWeight="700"
                  letterSpacing="-0.02em"
                  fontFamily="heading"
                >
                  Modules récents
                </Heading>
              </HStack>
              <VStack spacing={3} align="stretch">
                {recentModules.map((item: any) => (
                  <Link key={item.module_id} to={`/modules/${item.module_id}`}>
                    <Card 
                      _hover={{ 
                        bg: 'blue.50', 
                        transform: { base: 'none', md: 'translateX(8px) scale(1.01)' },
                        borderColor: 'blue.400',
                        boxShadow: { base: 'sm', md: 'lg' }
                      }} 
                      transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                      border="2px solid"
                      borderColor="blue.100"
                      borderRadius="xl"
                      bg="white"
                    >
                      <CardBody p={{ base: 4, md: 6 }}>
                        <HStack justify="space-between" align="start">
                          <VStack align="start" spacing={2} flex="1">
                            <HStack spacing={2}>
                              <Badge 
                                bg="blue.600"
                                color="white"
                                fontWeight="600"
                                px={3}
                                py={1}
                                borderRadius="full"
                                boxShadow="sm"
                              >
                                {item.module?.subject || 'Non disponible'}
                              </Badge>
                              {item.completed && (
                                <Badge 
                                  bg="green.500"
                                  color="white"
                                  variant="solid"
                                  fontWeight="600"
                                  px={3}
                                  py={1}
                                  borderRadius="full"
                                  boxShadow="sm"
                                >
                                  Complété
                                </Badge>
                              )}
                            </HStack>
                            <Heading 
                              size="sm" 
                              color="gray.900" 
                              fontWeight="700"
                              fontFamily="heading"
                            >
                              {item.module?.title || 'Module'}
                            </Heading>
                            <HStack spacing={4} fontSize="sm" color="gray.700" fontFamily="body">
                              {item.score !== null && item.score !== undefined && (
                                <Text fontWeight="600">Score : {(item.score ?? 0).toFixed(0)}%</Text>
                              )}
                              <Text fontWeight="600">⏱️ {Math.floor((item.time_spent || 0) / 60)} min</Text>
                            </HStack>
                          </VStack>
                          <Icon as={FiArrowRight} boxSize={5} color="blue.600" />
                        </HStack>
                      </CardBody>
                    </Card>
                  </Link>
                ))}
              </VStack>
            </VStack>
          </Box>
        )}

        <Box 
          bg="white" 
          p={{ base: 6, md: 8 }} 
          borderRadius="2xl" 
          boxShadow="soft-lg"
          border="2px solid"
          borderColor="blue.100"
        >
          <VStack spacing={6} align="stretch">
            <HStack spacing={3} align="center">
              <Box
                p={2}
                bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                borderRadius="lg"
                boxShadow="md"
              >
                <Icon as={FiFileText} boxSize={4} color="white" />
              </Box>
              <Heading 
                size="md" 
                color="gray.900"
                fontWeight="700"
                letterSpacing="-0.02em"
                fontFamily="heading"
              >
                Examens
              </Heading>
            </HStack>
            <Text 
              color="gray.700" 
              fontSize={{ base: 'sm', md: 'md' }} 
              fontWeight="500"
              fontFamily="body"
              lineHeight="1.7"
            >
              Passez les examens pour valider vos matières
            </Text>
            {validatedModules && validatedModules.length > 0 && (
              <Badge
                bg="blue.600"
                color="white"
                fontSize="sm"
                fontWeight="600"
                px={4}
                py={2}
                borderRadius="full"
                boxShadow="md"
                w="fit-content"
              >
                {validatedModules.length} module{validatedModules.length > 1 ? 's' : ''} validé{validatedModules.length > 1 ? 's' : ''}
              </Badge>
            )}
            <Link to="/exams">
              <Button 
                bg="blue.600"
                color="white"
                size="lg" 
                width={{ base: 'full', md: 'auto' }} 
                rightIcon={<FiFileText />}
                boxShadow="md"
                fontWeight="600"
                _hover={{
                  bg: 'blue.700',
                  transform: 'translateY(-2px)',
                  boxShadow: 'lg',
                }}
                transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                fontFamily="body"
              >
                Voir les examens
              </Button>
            </Link>
          </VStack>
        </Box>

        <Box 
          bg="white" 
          p={{ base: 6, md: 8 }} 
          borderRadius="2xl" 
          boxShadow="soft-lg"
          border="2px solid"
          borderColor="blue.100"
        >
          <VStack spacing={6} align="stretch">
            <HStack spacing={3} align="center">
              <Box
                p={2}
                bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                borderRadius="lg"
                boxShadow="md"
              >
                <Icon as={FiBook} boxSize={4} color="white" />
              </Box>
              <Heading 
                size="md" 
                color="gray.900"
                fontWeight="700"
                letterSpacing="-0.02em"
                fontFamily="heading"
              >
                {t('dashboard.continueLearning')}
              </Heading>
            </HStack>
            <Text 
              color="gray.700" 
              fontSize={{ base: 'sm', md: 'md' }} 
              fontWeight="500"
              fontFamily="body"
              lineHeight="1.7"
            >
              Explorez nos modules interactifs et continuez votre apprentissage
            </Text>
            <Link to="/modules">
              <Button 
                bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                color="white"
                size="lg" 
                width={{ base: 'full', md: 'auto' }} 
                rightIcon={<FiArrowRight />}
                boxShadow="md"
                fontWeight="600"
                _hover={{
                  bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)',
                  transform: 'translateY(-2px)',
                  boxShadow: 'lg',
                }}
                transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
                fontFamily="body"
              >
                {t('dashboard.exploreModules')}
              </Button>
            </Link>
          </VStack>
        </Box>
      </VStack>
      </Container>
    </Box>
  )
}

export default Dashboard

