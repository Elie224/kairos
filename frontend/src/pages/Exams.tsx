import { useQuery } from 'react-query'
import { Container, VStack, Heading, SimpleGrid, Card, CardBody, Text, Button, Badge, HStack, Box, Spinner } from '@chakra-ui/react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import { FiBook, FiCheckCircle, FiArrowRight } from 'react-icons/fi'

interface Module {
  id: string
  title: string
  subject: string
  difficulty: string
}

interface ModuleValidation {
  module_id: string
  validated: boolean
  validated_at?: string
  exam_score?: number
}

interface ExamAttempt {
  id: string
  module_id: string
  score: number
  percentage: number
  passed: boolean
  started_at: string
  completed_at: string
}

const Exams = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const { data: modules, isLoading: modulesLoading, error: modulesError } = useQuery<Module[]>(
    'modules',
    async () => {
      const response = await api.get('/modules/', {
        timeout: 1000, // Timeout de 1 seconde
        params: { limit: 50 }, // Limiter à 50 modules pour la performance
      })
      return response.data || []
    },
    {
      staleTime: 10 * 60 * 1000, // 10 minutes - cache plus long
      cacheTime: 30 * 60 * 1000,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      retry: 1, // Réessayer une seule fois
      retryDelay: 1000,
      onError: (error) => {
        console.error('Erreur lors du chargement des modules:', error)
      },
    }
  )

  const { data: validatedModules, isLoading: validationsLoading, error: validationsError } = useQuery<ModuleValidation[]>(
    'module-validations',
    async () => {
      const response = await api.get('/validations/modules', {
        timeout: 1000, // Timeout de 1 seconde
      })
      return response.data || []
    },
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      retry: 1,
      retryDelay: 1000,
      onError: (error) => {
        console.error('Erreur lors du chargement des validations:', error)
      },
    }
  )

  const { data: examAttempts, isLoading: attemptsLoading, error: attemptsError } = useQuery<ExamAttempt[]>(
    'exam-attempts',
    async () => {
      const response = await api.get('/exams/attempts', {
        timeout: 1000, // Timeout de 1 seconde
        params: { limit: 50 }, // Limiter à 50 tentatives pour la performance
      })
      return response.data || []
    },
    {
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      retry: 1,
      retryDelay: 1000,
      onError: (error) => {
        console.error('Erreur lors du chargement des tentatives d\'examen:', error)
      },
    }
  )

  return (
    <Box
      minH="100vh"
      bgGradient="linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
      py={{ base: 6, md: 8 }}
      px={{ base: 4, md: 0 }}
    >
      <Container maxW="1200px" px={{ base: 4, md: 6 }}>
        <VStack spacing={{ base: 6, md: 8 }} align="stretch">
          <Box>
            <Heading 
              size={{ base: 'lg', md: 'xl' }} 
              mb={2} 
              color="gray.800"
              fontWeight="bold"
            >
              Examens
            </Heading>
            <Text color="gray.700" fontSize={{ base: 'md', md: 'lg' }} fontWeight="medium">
              Passez les examens pour valider vos modules
            </Text>
          </Box>

          {modulesLoading || validationsLoading || attemptsLoading ? (
            <Box textAlign="center" py={8}>
              <Spinner size="xl" color="gray.500" />
            </Box>
          ) : modulesError ? (
            <Box textAlign="center" py={8}>
              <Text color="red.500" fontSize="lg" fontWeight="medium">
                Erreur lors du chargement des modules. Veuillez réessayer.
              </Text>
            </Box>
          ) : !modules || modules.length === 0 ? (
            <Box textAlign="center" py={8}>
              <Text color="gray.600" fontSize="lg" fontWeight="medium">
                Aucun module disponible pour le moment.
              </Text>
            </Box>
          ) : (
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
              {modules.map((module) => {
                const validation = validatedModules?.find(v => v.module_id === module.id)
                const attempts = examAttempts?.filter(a => a.module_id === module.id) || []
                const lastAttempt = attempts.length > 0 ? attempts[0] : null

                return (
                  <Card
                    key={module.id}
                    bg="white"
                    _hover={{
                      transform: 'translateY(-8px) scale(1.02)',
                      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.2)',
                      borderColor: validation?.validated ? 'green.300' : 'gray.300'
                    }}
                    transition="all 0.4s cubic-bezier(0.4, 0, 0.2, 1)"
                    border="2px solid"
                    borderColor={validation?.validated ? 'green.200' : 'gray.200'}
                    borderRadius="2xl"
                    boxShadow="md"
                  >
                    <CardBody p={{ base: 4, md: 6 }}>
                      <VStack spacing={{ base: 3, md: 4 }} align="stretch">
                        <HStack justify="space-between" flexWrap="wrap" gap={2}>
                          <Badge colorScheme="gray" fontSize={{ base: 'xs', md: 'md' }} px={{ base: 2, md: 2 }} py={1}>
                            {module.subject} - {module.difficulty}
                          </Badge>
                          {validation?.validated && (
                            <Badge colorScheme="green" fontSize={{ base: 'xs', md: 'md' }} px={{ base: 2, md: 2 }} py={1}>
                              <FiCheckCircle style={{ display: 'inline', marginRight: '4px' }} />
                              Validé
                            </Badge>
                          )}
                        </HStack>

                        <Heading size={{ base: 'xs', md: 'sm' }} color="gray.800" fontWeight="bold">
                          {module.title}
                        </Heading>

                        {lastAttempt && (
                          <Box>
                            <Text fontSize="sm" color="gray.700" fontWeight="medium">
                              Dernière tentative:
                            </Text>
                            <HStack spacing={2} mt={1}>
                              <Badge
                                colorScheme={lastAttempt.passed ? 'green' : 'red'}
                              >
                                {lastAttempt.percentage.toFixed(1)}%
                              </Badge>
                              <Text fontSize="xs" color="gray.600">
                                {new Date(lastAttempt.completed_at).toLocaleDateString()}
                              </Text>
                            </HStack>
                          </Box>
                        )}

                        <Button
                          colorScheme={validation?.validated ? 'green' : 'brand'}
                          w="full"
                          size={{ base: 'md', md: 'lg' }}
                          minH="48px"
                          variant={validation?.validated ? 'solid' : 'gradient'}
                          onClick={() => navigate(`/modules/${module.id}/exam`)}
                          rightIcon={<FiArrowRight />}
                          data-touch-target="true"
                        >
                          {validation?.validated ? 'Voir l\'examen' : 'Passer l\'examen'}
                        </Button>
                      </VStack>
                    </CardBody>
                  </Card>
                )
              })}
            </SimpleGrid>
          )}
        </VStack>
      </Container>
    </Box>
  )
}

export default Exams

