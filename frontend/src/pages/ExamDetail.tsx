import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from 'react-query'
import { Container, VStack, Heading, Card, CardBody, Text, Button, Badge, HStack, Box, Alert, AlertIcon, AlertTitle, AlertDescription, Spinner, useToast, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton, useDisclosure } from '@chakra-ui/react'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import Exam from '../components/Exam'
import { FiArrowLeft, FiDownload, FiEye } from 'react-icons/fi'

const ExamDetail = () => {
  const { moduleId } = useParams<{ moduleId: string }>()
  const navigate = useNavigate()
  const { t } = useTranslation()
  const toast = useToast()
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [selectedPdfUrl, setSelectedPdfUrl] = useState<string | null>(null)
  const [prerequisites, setPrerequisites] = useState<any>(null)
  const [loadingPrerequisites, setLoadingPrerequisites] = useState(true)

  useEffect(() => {
    const checkPrereqs = async () => {
      if (!moduleId) return
      setLoadingPrerequisites(true)
      try {
        const response = await api.get(`/exams/module/${moduleId}/prerequisites`, {
          timeout: API_TIMEOUTS.STANDARD, // 15 secondes pour prerequisites/exam
        })
        setPrerequisites(response.data)
      } catch (error) {
        console.error('Erreur lors de la vérification des prérequis:', error)
      } finally {
        setLoadingPrerequisites(false)
      }
    }
    checkPrereqs()
  }, [moduleId])

  const { data: exam, isLoading: examLoading } = useQuery(
    ['exam', moduleId],
    async () => {
      if (!moduleId) return null
      const response = await api.get(`/exams/module/${moduleId}`, {
        timeout: 1000, // Timeout de 1 seconde
      })
      return response.data
    },
    {
      enabled: !!(moduleId && prerequisites?.can_take_exam),
      retry: 2,
      retryDelay: 2000,
    }
  )

  const { data: module } = useQuery(
    ['module', moduleId],
    async () => {
      if (!moduleId) return null
      const response = await api.get(`/modules/${moduleId}`)
      return response.data
    },
    {
      enabled: Boolean(moduleId),
    }
  )

  const { data: validation } = useQuery(
    ['module-validation', moduleId],
    async () => {
      if (!moduleId) return null
      const response = await api.get(`/validations/module/${moduleId}`)
      return response.data
    },
    {
      enabled: Boolean(moduleId),
    }
  )

  const handleDownloadPDF = async () => {
    if (!moduleId) return
    
    try {
      const response = await api.get(`/exams/module/${moduleId}/pdf`, {
        responseType: 'blob',
        timeout: 1000, // Timeout de 1 seconde
        headers: {
          'Accept': 'application/pdf',
        },
      })
      
      // Créer un lien de téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = url
      const moduleTitle = module?.title || 'examen'
      const filename = `examen_${moduleTitle.replace(/\s+/g, '_').toLowerCase()}.pdf`
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast({
        title: 'Téléchargement réussi',
        description: `Le PDF ${filename} a été téléchargé`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error: any) {
      console.error('Erreur lors du téléchargement du PDF:', error)
      toast({
        title: 'Erreur de téléchargement',
        description: error.response?.data?.detail || 'Impossible de télécharger le PDF',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const handleViewPdf = async () => {
    if (!moduleId) return
    
    try {
      const response = await api.get(`/exams/module/${moduleId}/pdf`, {
        responseType: 'blob',
        timeout: 1000, // Timeout de 1 seconde
      })
      
      const blob = new Blob([response.data], { type: 'application/pdf' })
      const url = window.URL.createObjectURL(blob)
      setSelectedPdfUrl(url)
      onOpen()
    } catch (error: any) {
      console.error('Erreur lors du chargement du PDF:', error)
      toast({
        title: 'Erreur de chargement',
        description: error.response?.data?.detail || 'Impossible de charger le PDF',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  if (loadingPrerequisites) {
    return (
      <Box minH="100vh" bgGradient="linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)" py={{ base: 6, md: 8 }} px={{ base: 4, md: 0 }}>
        <Container maxW="1200px" px={{ base: 4, md: 6 }}>
          <Box textAlign="center" py={{ base: 8, md: 12 }}>
            <Spinner size="xl" color="gray.500" />
          </Box>
        </Container>
      </Box>
    )
  }

  if (!prerequisites?.can_take_exam) {
    return (
      <Box minH="100vh" bgGradient="linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)" py={{ base: 6, md: 8 }} px={{ base: 4, md: 0 }}>
        <Container maxW="1200px" px={{ base: 4, md: 6 }}>
          <VStack spacing={6} align="stretch">
            <Button
              leftIcon={<FiArrowLeft />}
              onClick={() => navigate(`/modules/${moduleId}`)}
              variant="ghost"
              alignSelf="flex-start"
              size={{ base: 'sm', md: 'md' }}
              minH="48px"
              data-touch-target="true"
            >
              Retour au module
            </Button>

            <Card>
              <CardBody p={{ base: 4, md: 6 }}>
                <VStack spacing={{ base: 4, md: 6 }}>
                  <Heading size={{ base: 'md', md: 'lg' }}>
                    Examen du module
                  </Heading>

                  <Alert status="warning" borderRadius="md">
                    <AlertIcon />
                    <Box>
                      <AlertTitle>Prérequis non satisfaits</AlertTitle>
                      <AlertDescription>
                        {prerequisites?.reason || 'Vous devez compléter le module et faire le quiz avant de pouvoir passer l\'examen.'}
                      </AlertDescription>
                    </Box>
                  </Alert>

                  <VStack spacing={4} align="stretch" w="full">
                    <Box>
                      <Text fontWeight="bold" mb={2}>Progression requise:</Text>
                      <Text>Module complété: {prerequisites?.module_completed ? 'Oui' : 'Non'}</Text>
                      <Text>Quiz complété: {prerequisites?.quiz_completed ? 'Oui' : 'Non'}</Text>
                    </Box>
                  </VStack>

                  <Button
                    colorScheme="gray"
                    onClick={() => navigate(`/modules/${moduleId}`)}
                    size={{ base: 'md', md: 'lg' }}
                    minH="48px"
                    w="full"
                    data-touch-target="true"
                  >
                    Continuer l'apprentissage
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </VStack>
        </Container>
      </Box>
    )
  }

  if (examLoading) {
    return (
      <Box minH="100vh" bgGradient="linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)" py={{ base: 6, md: 8 }} px={{ base: 4, md: 0 }}>
        <Container maxW="1200px" px={{ base: 4, md: 6 }}>
          <VStack spacing={{ base: 4, md: 6 }} align="center" py={{ base: 8, md: 12 }}>
            <Spinner size="xl" color="blue.500" thickness="4px" />
            <Text fontSize={{ base: 'md', md: 'lg' }} color="gray.600" textAlign="center">
              Génération de l'examen en cours...
            </Text>
            <Text fontSize={{ base: 'xs', md: 'sm' }} color="gray.500" textAlign="center" maxW="500px" px={4}>
              Cela peut prendre quelques instants, surtout pour les examens de mathématiques avec exercices pratiques.
            </Text>
          </VStack>
        </Container>
      </Box>
    )
  }

  if (!exam) {
    return (
      <Box minH="100vh" bgGradient="linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)" py={{ base: 6, md: 8 }} px={{ base: 4, md: 0 }}>
        <Container maxW="1200px" px={{ base: 4, md: 6 }}>
          <VStack spacing={{ base: 4, md: 6 }} align="stretch">
            <Button
              leftIcon={<FiArrowLeft />}
              onClick={() => navigate(`/modules/${moduleId}`)}
              variant="ghost"
              alignSelf="flex-start"
              size={{ base: 'sm', md: 'md' }}
              minH="48px"
              data-touch-target="true"
            >
              Retour au module
            </Button>
            <Card>
              <CardBody>
                <Text>Examen non trouvé</Text>
              </CardBody>
            </Card>
          </VStack>
        </Container>
      </Box>
    )
  }

  return (
    <Box minH="100vh" bgGradient="linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)" py={{ base: 6, md: 8 }} px={{ base: 4, md: 0 }}>
      <Container maxW="1200px" px={{ base: 4, md: 6 }}>
        <VStack spacing={{ base: 4, md: 6 }} align="stretch">
          <Button
            leftIcon={<FiArrowLeft />}
            onClick={() => navigate(`/modules/${moduleId}`)}
            variant="ghost"
            alignSelf="flex-start"
            size={{ base: 'sm', md: 'md' }}
            minH="48px"
            data-touch-target="true"
          >
            Retour au module
          </Button>

          {module && (
            <Box>
              <Heading size={{ base: 'md', md: 'lg' }} mb={2}>{module.title}</Heading>
              <Text color="gray.600" fontSize={{ base: 'sm', md: 'md' }}>{module.description}</Text>
            </Box>
          )}

          {validation?.validated && (
            <Alert status="success" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle fontSize={{ base: 'sm', md: 'md' }}>Module validé !</AlertTitle>
                <AlertDescription fontSize={{ base: 'xs', md: 'sm' }}>
                  Vous avez validé ce module le {new Date(validation.validated_at).toLocaleDateString()} avec un score de {validation.exam_score?.toFixed(1)}%.
                </AlertDescription>
              </Box>
            </Alert>
          )}

          {exam && (
            <HStack spacing={4} justify={{ base: 'stretch', md: 'flex-end' }} flexWrap="wrap">
              <Button
                leftIcon={<FiEye />}
                onClick={handleViewPdf}
                colorScheme="red"
                size={{ base: 'md', md: 'md' }}
                minH="48px"
                flex={{ base: 1, md: 'none' }}
                data-touch-target="true"
              >
                Voir PDF
              </Button>
              <Button
                leftIcon={<FiDownload />}
                onClick={handleDownloadPDF}
                colorScheme="brand"
                variant="outline"
                size={{ base: 'md', md: 'md' }}
                minH="48px"
                flex={{ base: 1, md: 'none' }}
                data-touch-target="true"
              >
                Télécharger PDF
              </Button>
            </HStack>
          )}

          {exam && <Exam examId={exam.id} moduleId={moduleId || ''} />}
          
          {/* Modal pour afficher le PDF */}
          <Modal isOpen={isOpen} onClose={() => {
            if (selectedPdfUrl) {
              window.URL.revokeObjectURL(selectedPdfUrl)
            }
            setSelectedPdfUrl(null)
            onClose()
          }} size="full">
            <ModalOverlay />
            <ModalContent>
              <ModalHeader>PDF - Examen</ModalHeader>
              <ModalCloseButton />
              <ModalBody p={0}>
                {selectedPdfUrl && (
                  <iframe
                    src={selectedPdfUrl}
                    style={{ width: '100%', height: '100vh', border: 'none' }}
                    title="PDF Viewer"
                  />
                )}
              </ModalBody>
            </ModalContent>
          </Modal>
        </VStack>
      </Container>
    </Box>
  )
}

export default ExamDetail
