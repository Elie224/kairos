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
  Skeleton,
  SkeletonText,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Flex,
  UnorderedList,
  ListItem,
  Code,
} from '@chakra-ui/react'
import { FiEye, FiBox, FiCpu, FiZap, FiPlay, FiInfo, FiRotateCw, FiZoomIn, FiMove } from 'react-icons/fi'
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

  const { data: modules, isLoading, error } = useQuery<Module[]>(
    ['modules', selectedSubject],
    async () => {
      try {
        // Pour physics et chemistry, ne pas filtrer côté API mais côté client
        // car l'API peut ne pas encore supporter ces sujets dans tous les cas
        const params: any = {
          limit: 100,
        }
        
        // Envoyer le filtre pour toutes les matières supportées par l'API
        const supportedSubjects = ['mathematics', 'computer_science', 'physics', 'chemistry']
        if (selectedSubject !== 'all' && supportedSubjects.includes(selectedSubject)) {
          params.subject = selectedSubject
        }
        
        const response = await api.get('/modules/', { params })
        let filteredData = response.data || []
        
        // Filtrer côté client pour les matières non encore supportées par l'API
        const clientSideSubjects = ['biology', 'geography', 'economics', 'history']
        if (selectedSubject !== 'all' && clientSideSubjects.includes(selectedSubject)) {
          filteredData = filteredData.filter((module: Module) => 
            module.subject?.toLowerCase() === selectedSubject
          )
        }
        
        return filteredData
      } catch (err) {
        console.error('Erreur lors de la récupération des modules:', err)
        return []
      }
    },
    {
      enabled: !!user,
      staleTime: 5 * 60 * 1000,
      retry: 1,
    }
  )

  // Filtrer les modules avec visualisations disponibles (3D pour physique/chimie, 2D pour les autres)
  const modulesWithVisualizations = modules?.filter(
    (module) => {
      const subject = module.subject?.toLowerCase() || ''
      // Toutes les matières peuvent avoir des visualisations
      // Physique et Chimie : simulations 3D
      // Autres matières : visualisations 2D (graphiques, diagrammes, etc.)
      return ['physics', 'chemistry', 'mathematics', 'biology', 'geography', 'economics', 'history', 'computer_science'].includes(subject)
    }
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

  const getSimulationInfo = (module: Module) => {
    const subject = module.subject?.toLowerCase()
    const sceneType = module.content?.scene || 'default'
    
    if (subject === 'physics') {
      if (sceneType === 'gravitation') {
        return {
          title: 'Simulation de Gravitation',
          description: 'Visualisez l\'effet de la force gravitationnelle sur un satellite en orbite autour d\'une planète.',
          concepts: [
            'Force gravitationnelle',
            'Mouvement orbital',
            'Lois de Kepler',
            'Vitesse orbitale'
          ],
          controls: [
            'Rotation : Clic gauche + glisser',
            'Zoom : Molette de la souris',
            'Panoramique : Clic droit + glisser'
          ]
        }
      } else {
        return {
          title: 'Simulation de Mécanique',
          description: 'Explorez différents concepts de mécanique classique : pendule, chute libre et système masse-ressort.',
          concepts: [
            'Mouvement harmonique simple',
            'Chute libre',
            'Oscillations amorties',
            'Vecteurs de force'
          ],
          controls: [
            'Rotation : Clic gauche + glisser',
            'Zoom : Molette de la souris',
            'Panoramique : Clic droit + glisser'
          ]
        }
      }
    } else if (subject === 'chemistry') {
      return {
        title: 'Réaction Chimique',
        description: 'Observez la représentation 3D d\'une réaction chimique avec les molécules et leurs liaisons.',
        concepts: [
          'Structure moléculaire',
          'Liaisons chimiques',
          'Réactions chimiques',
          'Atomes et molécules'
        ],
        controls: [
          'Rotation : Clic gauche + glisser',
          'Zoom : Molette de la souris',
          'Panoramique : Clic droit + glisser'
        ]
      }
    }
    
    return {
      title: 'Visualisation 3D',
      description: 'Explorez cette simulation interactive en 3D.',
      concepts: [],
      controls: [
        'Rotation : Clic gauche + glisser',
        'Zoom : Molette de la souris',
        'Panoramique : Clic droit + glisser'
      ]
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
                Visualisations Interactives Avancées Pilotées par l'IA
              </Heading>
            </HStack>
            <Text color="gray.600" fontSize={{ base: 'sm', md: 'md' }}>
              Le modèle IA analyse votre niveau, génère des simulations 2D/3D interactives, adapte la difficulté en temps réel et propose des expériences exploratoires guidées. Couvre Mathématiques, Physique, Chimie, Biologie, et plus.
            </Text>
          </Box>

          {/* Filtres */}
          <HStack spacing={4}>
            <Select
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              maxW="250px"
              size="md"
            >
              <option value="all">Toutes les matières</option>
              <option value="mathematics">📐 Mathématiques</option>
              <option value="physics">⚙️ Physique</option>
              <option value="chemistry">🧪 Chimie</option>
              <option value="computer_science">🤖 Informatique & IA</option>
              <option value="biology">🧬 Biologie</option>
              <option value="geography">🌍 Géographie</option>
              <option value="economics">💰 Économie</option>
              <option value="history">🏛️ Histoire</option>
            </Select>
            <Badge colorScheme="blue" fontSize="sm" px={3} py={1}>
              {modulesWithVisualizations.length} simulation{modulesWithVisualizations.length > 1 ? 's' : ''} disponible{modulesWithVisualizations.length > 1 ? 's' : ''}
            </Badge>
          </HStack>

          <Divider />

          {selectedModule ? (
            /* Vue de la simulation */
            <VStack spacing={4} align="stretch">
              <Card>
                <CardBody>
                  <VStack spacing={4} align="stretch">
                    <HStack justify="space-between" flexWrap="wrap" gap={4}>
                      <VStack align="start" spacing={2}>
                        <Heading size="md">{selectedModule.title}</Heading>
                        <HStack>
                          <Badge colorScheme={getSubjectColor(selectedModule.subject)} fontSize="sm" px={2} py={1}>
                            {selectedModule.subject}
                          </Badge>
                          <Badge colorScheme="gray" fontSize="sm" px={2} py={1}>
                            {selectedModule.difficulty}
                          </Badge>
                        </HStack>
                      </VStack>
                      <Button
                        onClick={() => setSelectedModule(null)}
                        size="sm"
                        variant="outline"
                        leftIcon={<FiEye />}
                      >
                        Retour à la liste
                      </Button>
                    </HStack>

                    <Box
                      h={{ base: '400px', md: '600px' }}
                      w="100%"
                      borderRadius="lg"
                      overflow="hidden"
                      border="2px solid"
                      borderColor="gray.200"
                      bg="black"
                      position="relative"
                    >
                      <Simulation3D module={selectedModule} />
                    </Box>

                    <Alert status="info" borderRadius="md" fontSize="sm">
                      <AlertIcon />
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="bold">Contrôles de la simulation :</Text>
                        <UnorderedList fontSize="xs" spacing={1}>
                          <ListItem><Icon as={FiRotateCw} mr={1} /> Rotation : Clic gauche + glisser</ListItem>
                          <ListItem><Icon as={FiZoomIn} mr={1} /> Zoom : Molette de la souris</ListItem>
                          <ListItem><Icon as={FiMove} mr={1} /> Panoramique : Clic droit + glisser</ListItem>
                        </UnorderedList>
                      </VStack>
                    </Alert>
                  </VStack>
                </CardBody>
              </Card>

              {/* Informations sur la simulation */}
              <Card>
                <CardBody>
                  <VStack spacing={4} align="stretch">
                    <HStack spacing={2}>
                      <Icon as={FiInfo} color="blue.500" boxSize={5} />
                      <Heading size="sm">Informations sur la simulation</Heading>
                    </HStack>
                    <Divider />
                    
                    {(() => {
                      const info = getSimulationInfo(selectedModule)
                      return (
                        <VStack spacing={4} align="stretch">
                          <Box>
                            <Text fontWeight="semibold" mb={2} color="gray.700">
                              Description
                            </Text>
                            <Text fontSize="sm" color="gray.600" lineHeight="tall">
                              {info.description}
                            </Text>
                          </Box>

                          {info.concepts.length > 0 && (
                            <Box>
                              <Text fontWeight="semibold" mb={2} color="gray.700">
                                Concepts abordés
                              </Text>
                              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={2}>
                                {info.concepts.map((concept, idx) => (
                                  <HStack key={idx} spacing={2}>
                                    <Icon as={FiZap} color="blue.400" boxSize={4} />
                                    <Text fontSize="sm" color="gray.600">
                                      {concept}
                                    </Text>
                                  </HStack>
                                ))}
                              </SimpleGrid>
                            </Box>
                          )}

                          <Box>
                            <Text fontWeight="semibold" mb={2} color="gray.700">
                              Contrôles interactifs
                            </Text>
                            <UnorderedList spacing={1}>
                              {info.controls.map((control, idx) => (
                                <ListItem key={idx} fontSize="sm" color="gray.600">
                                  {control}
                                </ListItem>
                              ))}
                            </UnorderedList>
                          </Box>
                        </VStack>
                      )
                    })()}
                  </VStack>
                </CardBody>
              </Card>
            </VStack>
          ) : (
            /* Liste des modules avec visualisations */
            <VStack spacing={4} align="stretch">
              {error && (
                <Alert status="warning" borderRadius="md">
                  <AlertIcon />
                  <AlertTitle>Erreur de chargement</AlertTitle>
                  <AlertDescription>
                    Impossible de charger les modules. Veuillez réessayer plus tard.
                  </AlertDescription>
                </Alert>
              )}

              <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                {isLoading ? (
                  [...Array(6)].map((_, i) => (
                    <Card key={i}>
                      <CardBody>
                        <VStack spacing={3} align="stretch">
                          <Skeleton height="150px" borderRadius="md" />
                          <SkeletonText noOfLines={2} spacing={2} />
                          <Skeleton height="36px" borderRadius="md" />
                        </VStack>
                      </CardBody>
                    </Card>
                  ))
                ) : modulesWithVisualizations.length === 0 ? (
                  <Box textAlign="center" py={12} gridColumn="1 / -1">
                    <Icon as={FiEye} boxSize={16} color="gray.300" mb={4} />
                    <Text color="gray.600" fontSize="lg" mb={2} fontWeight="semibold">
                      Aucune visualisation disponible
                    </Text>
                    <Text color="gray.500" fontSize="sm" maxW="400px" mx="auto">
                      Les visualisations interactives sont disponibles pour toutes les matières :
                      <br />• <strong>⚙️ Physique</strong> et <strong>🧪 Chimie</strong> : Simulations 3D interactives
                      <br />• <strong>📐 Mathématiques</strong> : Graphiques et visualisations 2D
                      <br />• <strong>🧬 Biologie</strong> : Diagrammes et schémas interactifs
                      <br />• <strong>🌍 Géographie</strong> : Cartes et visualisations géospatiales
                      <br />• <strong>💰 Économie</strong> : Graphiques et courbes économiques
                      <br />• <strong>🏛️ Histoire</strong> : Frise chronologique interactive
                      <br /><br />
                      Sélectionnez une matière dans le filtre ci-dessus pour voir les visualisations disponibles.
                    </Text>
                  </Box>
                ) : (
                  modulesWithVisualizations.map((module) => {
                    const info = getSimulationInfo(module)
                    return (
                      <Card
                        key={module.id}
                        _hover={{
                          transform: 'translateY(-4px)',
                          boxShadow: 'lg',
                        }}
                        transition="all 0.3s"
                        cursor="pointer"
                        onClick={() => handleSelectModule(module)}
                        border="1px solid"
                        borderColor="gray.200"
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
                                fontSize="xs"
                                px={2}
                                py={1}
                              >
                                3D
                              </Badge>
                            </Box>
                            <VStack align="start" spacing={2}>
                              <Heading size="sm" noOfLines={2} color="gray.900">
                                {module.title}
                              </Heading>
                              <Text fontSize="xs" color="gray.600" noOfLines={2} lineHeight="short">
                                {info.description}
                              </Text>
                              <HStack spacing={2}>
                                <Badge colorScheme={getSubjectColor(module.subject)} fontSize="xs" px={2} py={0.5}>
                                  {module.subject}
                                </Badge>
                                <Badge colorScheme="gray" fontSize="xs" px={2} py={0.5}>
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
                              _hover={{
                                transform: 'scale(1.02)',
                              }}
                              transition="all 0.2s"
                            >
                              Lancer la simulation
                            </Button>
                          </VStack>
                        </CardBody>
                      </Card>
                    )
                  })
                )}
              </SimpleGrid>
            </VStack>
          )}
        </VStack>
      </Container>
    </Box>
  )
}

export default Visualizations
