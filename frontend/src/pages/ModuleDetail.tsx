import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from 'react-query'
import { Container, Box, VStack, Heading, Text, Badge, Button, Tabs, TabList, TabPanels, Tab, TabPanel, Card, CardBody, Spinner, HStack } from '@chakra-ui/react'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import ImmersiveExperience from '../components/ImmersiveExperience'
import AITutor from '../components/AITutor'
import Quiz from '../components/Quiz'
import TDList from '../components/TDList'
import TPList from '../components/TPList'
import ResourceList from '../components/ResourceList'
import { useProgressTracker } from '../hooks/useProgressTracker'
import { useAuthStore } from '../store/authStore'
import { ModuleContent, Lesson, Section } from '../types/moduleContent'

interface Module {
  id: string
  title: string
  description: string
  subject: string
  difficulty: string
  estimated_time: number
  learning_objectives: string[]
  content?: ModuleContent
}

const ModuleDetail = () => {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const { isAuthenticated } = useAuthStore()
  const [tabIndex, setTabIndex] = useState(0)
  
  // Réinitialiser l'onglet à "Contenu" quand le module change
  useEffect(() => {
    setTabIndex(0)
  }, [id])
  
  // Suivi automatique de la progression
  useProgressTracker({ moduleId: id || '', enabled: isAuthenticated })

  const subjectLabels: Record<string, string> = {
    mathematics: t('modules.mathematics'),
    computer_science: t('modules.computerScience'),
  }

  const { data: module, isLoading } = useQuery<Module>(
    ['module', id],
    async () => {
      const response = await api.get(`/modules/${id}`)
      return response.data
    },
    { 
      enabled: !!id,
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
    }
  )

  if (isLoading) {
    return (
      <Box minH="100vh" bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)" py={{ base: 8, md: 12 }}>
        <Container maxW="1200px" px={{ base: 4, md: 6 }} textAlign="center">
          <Spinner size="xl" />
        </Container>
      </Box>
    )
  }

  if (!module) {
    return (
      <Box minH="100vh" bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)" py={{ base: 8, md: 12 }}>
        <Container maxW="1200px" px={{ base: 4, md: 6 }}>
          <Text fontSize={{ base: 'md', md: 'lg' }}>{t('moduleDetail.notFound')}</Text>
        </Container>
      </Box>
    )
  }

  // Vérifier si le module permet les simulations (aucune pour l'instant avec seulement algèbre et ML)
  const hasSimulation = false
  // Vérifier si le module ne doit pas avoir de TP (mathématiques)
  const hasNoTP = module.subject === 'mathematics'
  // Les quiz sont disponibles uniquement pour les modules d'informatique
  const hasQuiz = module.subject === 'computer_science'

  return (
    <Box minH="100vh" bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)" py={{ base: 4, md: 8 }}>
      <Container maxW="1200px" px={{ base: 4, md: 6 }}>
        <VStack spacing={{ base: 4, md: 6 }} align="stretch">
          <Box bg="white" p={{ base: 4, md: 6 }} borderRadius={{ base: 'xl', md: 'lg' }} boxShadow="sm">
            <HStack spacing={4} mb={4} flexWrap="wrap">
              <Badge colorScheme="gray" fontSize={{ base: 'sm', md: 'md' }} px={{ base: 2, md: 3 }} py={1} borderRadius="md">
                {subjectLabels[module.subject] || module.subject}
              </Badge>
            </HStack>
            <Heading mb={2} color="gray.600" size={{ base: 'lg', md: 'xl' }}>{module.title}</Heading>
            <Text color="gray.600" fontSize={{ base: 'md', md: 'lg' }}>{module.description}</Text>
          </Box>

          <Tabs index={tabIndex} onChange={setTabIndex} colorScheme="brand">
            <Box overflowX="auto" className="table-container" mb={4}>
              <TabList minW="max-content" flexWrap={{ base: 'nowrap', md: 'wrap' }}>
                <Tab fontSize={{ base: 'sm', md: 'md' }} minH="48px" px={{ base: 3, md: 4 }}>{t('moduleDetail.content') || 'Contenu'}</Tab>
                {hasSimulation && <Tab fontSize={{ base: 'sm', md: 'md' }} minH="48px" px={{ base: 3, md: 4 }}>{t('moduleDetail.simulation')}</Tab>}
                <Tab fontSize={{ base: 'sm', md: 'md' }} minH="48px" px={{ base: 3, md: 4 }}>{t('moduleDetail.objectives')}</Tab>
                <Tab fontSize={{ base: 'sm', md: 'md' }} minH="48px" px={{ base: 3, md: 4 }}>TD</Tab>
                {!hasNoTP && <Tab fontSize={{ base: 'sm', md: 'md' }} minH="48px" px={{ base: 3, md: 4 }}>TP</Tab>}
                <Tab fontSize={{ base: 'sm', md: 'md' }} minH="48px" px={{ base: 3, md: 4 }}>Ressources</Tab>
                <Tab fontSize={{ base: 'sm', md: 'md' }} minH="48px" px={{ base: 3, md: 4 }}>{t('moduleDetail.aiTutor')}</Tab>
                {hasQuiz && <Tab fontSize={{ base: 'sm', md: 'md' }} minH="48px" px={{ base: 3, md: 4 }}>{t('moduleDetail.quiz')}</Tab>}
              </TabList>
            </Box>

          <TabPanels>
            <TabPanel px={0}>
              <Card _hover={{ boxShadow: 'md' }} transition="all 0.2s" bg="white">
                <CardBody p={{ base: 4, md: 8 }}>
                  <VStack align="start" spacing={{ base: 4, md: 6 }}>
                    <Box width="full" mb={4}>
                      <HStack justify="space-between" align="center" mb={2} flexWrap="wrap" gap={2}>
                        <Box flex="1" minW="200px">
                          <Heading size={{ base: 'lg', md: 'xl' }} color="gray.600" mb={2}>
                            {t('moduleDetail.learningContent') || 'Contenu d\'apprentissage'}
                          </Heading>
                          <Text color="gray.600" fontSize={{ base: 'sm', md: 'md' }}>
                            {t('moduleDetail.learningContentDesc') || 'Apprenez les concepts de ce module étape par étape'}
                          </Text>
                        </Box>
                        {module.content?.lessons && module.content.lessons.length > 0 && (
                          <Badge colorScheme="gray" fontSize={{ base: 'sm', md: 'md' }} px={{ base: 3, md: 4 }} py={2} borderRadius="full">
                            {module.content.lessons.length} {module.content.lessons.length > 1 ? t('moduleDetail.lessons') : t('moduleDetail.lesson')}
                          </Badge>
                        )}
                      </HStack>
                    </Box>
                    
                    {module.content?.lessons && module.content.lessons.length > 0 ? (
                      module.content.lessons.map((lesson: Lesson, index: number) => (
                        <Box 
                          key={index} 
                          width="full" 
                          p={{ base: 4, md: 8 }} 
                          bg="white" 
                          borderRadius={{ base: 'md', md: 'lg' }} 
                          borderLeft="4px solid" 
                          borderColor="gray.500"
                          boxShadow="sm"
                          _hover={{ boxShadow: 'md', transform: { base: 'none', md: 'translateX(4px)' } }}
                          transition="all 0.2s"
                          mb={{ base: 4, md: 6 }}
                        >
                          <HStack mb={4} spacing={3} flexWrap="wrap">
                            <Box
                              bg="gray.500"
                              color="white"
                              borderRadius="full"
                              width={{ base: '28px', md: '32px' }}
                              height={{ base: '28px', md: '32px' }}
                              display="flex"
                              alignItems="center"
                              justifyContent="center"
                              fontWeight="bold"
                              fontSize={{ base: 'md', md: 'lg' }}
                              flexShrink={0}
                            >
                              {index + 1}
                            </Box>
                            <Heading size={{ base: 'md', md: 'lg' }} color="gray.700">
                              {lesson.title || t('moduleDetail.lessonNumber', { number: index + 1 })}
                            </Heading>
                          </HStack>
                          {lesson.sections?.map((section: Section, secIndex: number) => (
                            <Box key={secIndex} mb={6}>
                              {section.heading && (
                                <Heading size={{ base: 'sm', md: 'md' }} mb={3} color="gray.800" mt={secIndex > 0 ? { base: 4, md: 6 } : 0}>
                                  {section.heading}
                                </Heading>
                              )}
                              {section.paragraphs?.map((paragraph: string, pIndex: number) => (
                                <Text key={pIndex} mb={4} color="gray.700" lineHeight="1.8" fontSize={{ base: 'sm', md: 'md' }}>
                                  {paragraph}
                                </Text>
                              ))}
                              {section.bulletPoints && (
                                <VStack align="start" spacing={3} mt={4}>
                                  {section.bulletPoints.map((point: string, bpIndex: number) => (
                                    <HStack key={bpIndex} align="start" spacing={3}>
                                      <Box
                                        bg="gray.100"
                                        color="gray.600"
                                        borderRadius="sm"
                                        width="24px"
                                        height="24px"
                                        display="flex"
                                        alignItems="center"
                                        justifyContent="center"
                                        fontWeight="bold"
                                        fontSize="sm"
                                        flexShrink={0}
                                        mt={1}
                                      >
                                        ✓
                                      </Box>
                                      <Text color="gray.700" flex="1" fontSize={{ base: 'sm', md: 'md' }} lineHeight="1.7">
                                        {point}
                                      </Text>
                                    </HStack>
                                  ))}
                                </VStack>
                              )}
                            </Box>
                          ))}
                        </Box>
                      ))
                    ) : module.content?.text ? (
                      <Box width="full" p={8} bg="white" borderRadius="lg" boxShadow="sm">
                        <Text color="gray.700" lineHeight="1.9" whiteSpace="pre-wrap" fontSize="md">
                          {module.content.text}
                        </Text>
                      </Box>
                    ) : (
                      <Box width="full" p={12} bg="gradient-to-r" bgGradient="linear(to-r, gray.50, gray.50)" borderRadius="lg" textAlign="center" border="2px dashed" borderColor="gray.300">
                        <Text fontSize="4xl" mb={4}>📚</Text>
                        <Text color="gray.700" fontSize="xl" mb={4} fontWeight="bold">
                          {t('moduleDetail.noContent') || 'Le contenu d\'apprentissage sera bientôt disponible.'}
                        </Text>
                        <Text color="gray.600" fontSize="md" mb={8}>
                          {hasSimulation 
                            ? (t('moduleDetail.useOtherTabs') || 'En attendant, explorez les autres sections du module pour commencer votre apprentissage.')
                            : hasQuiz
                            ? 'En attendant, explorez les autres sections du module (objectifs, TD, ressources, Kaïrox et quiz) pour commencer votre apprentissage.'
                            : 'En attendant, explorez les autres sections du module (objectifs, TD, ressources, Kaïrox) pour commencer votre apprentissage.'
                          }
                        </Text>
                        <HStack spacing={4} justify="center" flexWrap="wrap">
                          {hasSimulation && (
                            <Button 
                              colorScheme="gray" 
                              size="lg"
                              onClick={() => setTabIndex(1)}
                            >
                              🎮 {t('moduleDetail.viewSimulation')}
                            </Button>
                          )}
                          <Button 
                            colorScheme="gray" 
                            size="lg"
                            variant="outline"
                            onClick={() => setTabIndex(hasSimulation ? 2 : 1)}
                          >
                            🎯 {t('moduleDetail.viewObjectives')}
                          </Button>
                          <Button 
                            colorScheme="gray" 
                            size="lg"
                            onClick={() => setTabIndex(hasSimulation ? 3 : 2)}
                          >
                            🤖 {t('moduleDetail.talkToTutor')}
                          </Button>
                          {hasQuiz && (
                            <Button 
                              colorScheme="gray" 
                              size="lg"
                              variant="outline"
                              onClick={() => setTabIndex(hasSimulation ? 4 : 3)}
                            >
                              📝 {t('moduleDetail.takeQuiz')}
                            </Button>
                          )}
                        </HStack>
                      </Box>
                    )}
                  </VStack>
                </CardBody>
              </Card>
            </TabPanel>

            {hasSimulation && (
              <TabPanel>
                <Box h="600px" bg="gray.900" borderRadius="lg" overflow="hidden">
                  <ImmersiveExperience module={module} />
                </Box>
              </TabPanel>
            )}

            <TabPanel>
              <Card _hover={{ boxShadow: 'md' }} transition="all 0.2s">
                <CardBody p={{ base: 4, md: 6 }}>
                  <VStack align="start" spacing={{ base: 3, md: 4 }}>
                    <Heading size={{ base: 'sm', md: 'md' }} color="gray.600">{t('moduleDetail.learningObjectives')}</Heading>
                    {module.learning_objectives && module.learning_objectives.length > 0 ? (
                      module.learning_objectives.map((objective, index) => (
                        <HStack key={index} align="start" spacing={3} p={{ base: 2, md: 3 }} bg="gray.50" borderRadius="md" width="full">
                          <Text fontWeight="bold" color="gray.600" fontSize={{ base: 'md', md: 'lg' }} flexShrink={0}>{index + 1}.</Text>
                          <Text color="gray.700" flex="1" fontSize={{ base: 'sm', md: 'md' }}>{objective}</Text>
                        </HStack>
                      ))
                    ) : (
                      <Text color="gray.500" fontSize={{ base: 'sm', md: 'md' }}>{t('moduleDetail.noObjectives')}</Text>
                    )}
                  </VStack>
                </CardBody>
              </Card>
            </TabPanel>

            <TabPanel>
              <TDList moduleId={module.id} />
            </TabPanel>

            {!hasNoTP && (
              <TabPanel>
                <TPList moduleId={module.id} />
              </TabPanel>
            )}

            <TabPanel>
              <ResourceList moduleId={module.id} />
            </TabPanel>

            <TabPanel>
              <AITutor moduleId={module.id} />
            </TabPanel>

            {hasQuiz && (
              <TabPanel>
                <Quiz moduleId={module.id} />
              </TabPanel>
            )}
          </TabPanels>
        </Tabs>
      </VStack>
    </Container>
    </Box>
  )
}

export default ModuleDetail

