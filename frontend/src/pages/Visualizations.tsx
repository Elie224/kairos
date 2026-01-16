/**
 * Page dédiée aux visualisations interactives
 */
import { useState } from 'react'
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  SimpleGrid,
  Card,
  CardBody,
  Button,
  Icon,
  Badge,
  Select,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Divider,
} from '@chakra-ui/react'
import { FiEye, FiBox, FiCpu, FiZap, FiPlay } from 'react-icons/fi'
import Simulation3D from '../components/Simulation3D'
import { useQuery } from 'react-query'
import api from '../services/api'
import { useAuthStore } from '../store/authStore'

interface Module {
  id: string
  title: string
  subject: string
  difficulty: string
  content?: {
    scene?: string
  }
}

const Visualizations = () => {
  const { user } = useAuthStore()
  const [selectedModule, setSelectedModule] = useState<Module | null>(null)
  const [selectedSubject, setSelectedSubject] = useState<string>('all')

  const { data: modules, isLoading } = useQuery<Module[]>(
    ['modules', selectedSubject],
    async () => {
      const response = await api.get('/modules/', {
        params: {
          limit: 100,
          ...(selectedSubject !== 'all' && { subject: selectedSubject }),
        },
      })
      return response.data
    },
    {
      enabled: !!user,
      staleTime: 5 * 60 * 1000,
    }
  )

  const modulesWithVisualizations = modules?.filter(
    (module) =>
      module.subject?.toLowerCase() === 'physics' ||
      module.subject?.toLowerCase() === 'chemistry' ||
      module.content?.scene
  ) || []

  const handleSelectModule = (module: Module) => {
    setSelectedModule(module)
  }

  const getSubjectColor = (subject: string) => {
    switch (subject?.toLowerCase()) {
      case 'physics':
        return 'blue'
      case 'chemistry':
        return 'green'
      case 'mathematics':
        return 'purple'
      default:
        return 'gray'
    }
  }

  return (
    <Box minH="calc(100vh - 80px)" py={{ base: 6, md: 8 }} px={{ base: 4, md: 0 }} bg="gray.50">
      <Container maxW="1400px" px={{ base: 4, md: 6 }}>
        <VStack spacing={6} align="stretch">
          {/* En-tête */}
          <Box>
            <HStack spacing={3} mb={2}>
              <Icon as={FiEye} boxSize={8} color="blue.500" />
              <Heading size={{ base: 'lg', md: 'xl' }} bgGradient="linear-gradient(135deg, blue.500 0%, purple.500 100%)" bgClip="text">
                Visualisations Interactives
              </Heading>
            </HStack>
            <Text color="gray.600" fontSize={{ base: 'sm', md: 'md' }}>
              Explorez des concepts complexes avec des simulations 3D interactives
            </Text>
          </Box>

          {/* Filtres */}
          <HStack spacing={4}>
            <Select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              maxW="200px"
              size="md"
            >
              <option value="all">Toutes les matières</option>
              <option value="physics">Physique</option>
              <option value="chemistry">Chimie</option>
              <option value="mathematics">Mathématiques</option>
            </Select>
            <Badge colorScheme="blue" fontSize="sm" px={3} py={1}>
              {modulesWithVisualizations.length} simulation{modulesWithVisualizations.length > 1 ? 's' : ''} disponible{modulesWithVisualizations.length > 1 ? 's' : ''}
            </Badge>
          </HStack>

          <Divider />

          {selectedModule ? (
            /* Vue de la simulation */
            <Card>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between">
                    <VStack align="start" spacing={1}>
                      <Heading size="md">{selectedModule.title}</Heading>
                      <HStack>
                        <Badge colorScheme={getSubjectColor(selectedModule.subject)}>
                          {selectedModule.subject}
                        </Badge>
                        <Badge colorScheme="gray">{selectedModule.difficulty}</Badge>
                      </HStack>
                    </VStack>
                    <Button
                      onClick={() => setSelectedModule(null)}
                      size="sm"
                      variant="outline"
                    >
                      Retour à la liste
                    </Button>
                  </HStack>

                  <Box
                    h="600px"
                    w="100%"
                    borderRadius="lg"
                    overflow="hidden"
                    border="2px solid"
                    borderColor="gray.200"
                    bg="black"
                  >
                    <Simulation3D module={selectedModule} />
                  </Box>

                  <Text fontSize="sm" color="gray.600" textAlign="center">
                    Utilisez la souris pour faire pivoter, zoomer et explorer la simulation
                  </Text>
                </VStack>
              </CardBody>
            </Card>
          ) : (
            /* Liste des modules avec visualisations */
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
              {isLoading ? (
                [...Array(6)].map((_, i) => (
                  <Card key={i}>
                    <CardBody>
                      <Box h="200px" bg="gray.100" borderRadius="md" />
                    </CardBody>
                  </Card>
                ))
              ) : modulesWithVisualizations.length === 0 ? (
                <Box textAlign="center" py={12} gridColumn="1 / -1">
                  <Icon as={FiEye} boxSize={16} color="gray.300" mb={4} />
                  <Text color="gray.600" fontSize="lg" mb={2}>
                    Aucune visualisation disponible
                  </Text>
                  <Text color="gray.500" fontSize="sm">
                    Les visualisations 3D sont disponibles pour les modules de Physique et Chimie
                  </Text>
                </Box>
              ) : (
                modulesWithVisualizations.map((module) => (
                  <Card
                    key={module.id}
                    _hover={{
                      transform: 'translateY(-4px)',
                      boxShadow: 'lg',
                    }}
                    transition="all 0.3s"
                    cursor="pointer"
                    onClick={() => handleSelectModule(module)}
                  >
                    <CardBody>
                      <VStack spacing={3} align="stretch">
                        <Box
                          h="150px"
                          bgGradient={`linear(to-br, ${getSubjectColor(module.subject)}.400, ${getSubjectColor(module.subject)}.600)`}
                          borderRadius="md"
                          display="flex"
                          alignItems="center"
                          justifyContent="center"
                          position="relative"
                          overflow="hidden"
                        >
                          <Icon
                            as={FiBox}
                            boxSize={12}
                            color="white"
                            opacity={0.8}
                          />
                          <Badge
                            position="absolute"
                            top={2}
                            right={2}
                            colorScheme="whiteAlpha"
                            bg="whiteAlpha.200"
                            color="white"
                          >
                            3D
                          </Badge>
                        </Box>
                        <VStack align="start" spacing={1}>
                          <Heading size="sm" noOfLines={2}>
                            {module.title}
                          </Heading>
                          <HStack>
                            <Badge colorScheme={getSubjectColor(module.subject)} fontSize="xs">
                              {module.subject}
                            </Badge>
                            <Badge colorScheme="gray" fontSize="xs">
                              {module.difficulty}
                            </Badge>
                          </HStack>
                        </VStack>
                        <Button
                          size="sm"
                          colorScheme={getSubjectColor(module.subject)}
                          leftIcon={<FiPlay />}
                          width="full"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleSelectModule(module)
                          }}
                        >
                          Lancer la simulation
                        </Button>
                      </VStack>
                    </CardBody>
                  </Card>
                ))
              )}
            </SimpleGrid>
          )}
        </VStack>
      </Container>
    </Box>
  )
}

export default Visualizations
