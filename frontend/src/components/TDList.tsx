import React from 'react'
import { useQuery } from 'react-query'
import { Box, VStack, Heading, Text, Card, CardBody, Spinner, Badge, HStack, Button, Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon, useToast, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton, useDisclosure } from '@chakra-ui/react'
import { FiDownload, FiEye } from 'react-icons/fi'
import api from '../services/api'

interface TDExercise {
  question: string
  answer?: string
  solution?: string
  points: number
  difficulty?: string
}

interface TD {
  id: string
  module_id: string
  title: string
  description: string
  exercises: TDExercise[]
  estimated_time: number
  pdf_url?: string
  created_at: string
  updated_at?: string
}

interface TDListProps {
  moduleId: string
}

const TDList = ({ moduleId }: TDListProps) => {
  const toast = useToast()
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [selectedPdfUrl, setSelectedPdfUrl] = React.useState<string | null>(null)
  
  const { data: tds, isLoading } = useQuery<TD[]>(
    ['tds', moduleId],
    async () => {
      const response = await api.get(`/tds/module/${moduleId}`)
      return response.data
    },
    {
      enabled: !!moduleId,
      staleTime: 5 * 60 * 1000,
    }
  )

  const handleDownloadPdf = async (tdId: string, title: string) => {
    try {
      const response = await api.get(`/tds/${tdId}/pdf`, {
        responseType: 'blob',
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${title}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast({
        title: 'Téléchargement réussi',
        description: `Le PDF ${title} a été téléchargé`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error: any) {
      console.error('Erreur lors du téléchargement:', error)
      toast({
        title: 'Erreur de téléchargement',
        description: error.response?.data?.detail || 'Impossible de télécharger le PDF',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const handleViewPdf = async (tdId: string) => {
    try {
      const response = await api.get(`/tds/${tdId}/pdf`, {
        responseType: 'blob',
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

  if (isLoading) {
    return (
      <Box textAlign="center" py={8}>
        <Spinner size="xl" />
      </Box>
    )
  }

  if (!tds || tds.length === 0) {
    return (
      <Card>
        <CardBody>
          <Box textAlign="center" py={8}>
            <Text fontSize="4xl" mb={4}>📝</Text>
            <Text color="gray.600" fontSize="lg" mb={2}>
              Aucun Travaux Dirigé disponible pour ce module
            </Text>
            <Text color="gray.500" fontSize="sm">
              Les TD seront ajoutés prochainement
            </Text>
          </Box>
        </CardBody>
      </Card>
    )
  }

  return (
    <VStack spacing={6} align="stretch">
      {tds.map((td) => (
        <Card key={td.id} _hover={{ boxShadow: 'md' }} transition="all 0.2s">
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <HStack justify="space-between" align="start">
                <Box flex="1">
                  <Heading size="md" color="gray.800" mb={2}>
                    {td.title}
                  </Heading>
                  <Text color="gray.600" mb={3}>
                    {td.description}
                  </Text>
                </Box>
                <VStack spacing={2} align="end">
                  <Badge colorScheme="blue" fontSize="sm" px={3} py={1}>
                    {td.exercises.length} {td.exercises.length > 1 ? 'exercices' : 'exercice'}
                  </Badge>
                  <Badge colorScheme="gray" fontSize="sm" px={3} py={1}>
                    ~{td.estimated_time} min
                  </Badge>
                  {td.pdf_url && (
                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        colorScheme="red"
                        leftIcon={<FiEye />}
                        onClick={() => handleViewPdf(td.id)}
                      >
                        Voir PDF
                      </Button>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        leftIcon={<FiDownload />}
                        onClick={() => handleDownloadPdf(td.id, td.title)}
                      >
                        Télécharger
                      </Button>
                    </HStack>
                  )}
                </VStack>
              </HStack>

              <Accordion allowToggle>
                <AccordionItem border="none">
                  <AccordionButton px={0} py={2} _hover={{ bg: 'transparent' }}>
                    <Box flex="1" textAlign="left">
                      <Text fontWeight="semibold" color="gray.700">
                        Voir les exercices ({td.exercises.length})
                      </Text>
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                  <AccordionPanel px={0} pb={4}>
                    <VStack spacing={4} align="stretch">
                      {td.exercises.map((exercise, index) => (
                        <Box
                          key={index}
                          p={4}
                          bg="gray.50"
                          borderRadius="md"
                          borderLeft="3px solid"
                          borderColor="blue.500"
                        >
                          <HStack mb={2} spacing={2}>
                            <Badge colorScheme="blue" fontSize="xs">
                              Exercice {index + 1}
                            </Badge>
                            {exercise.difficulty && (
                              <Badge colorScheme="gray" fontSize="xs">
                                {exercise.difficulty}
                              </Badge>
                            )}
                            <Badge colorScheme="green" fontSize="xs">
                              {exercise.points} {exercise.points > 1 ? 'points' : 'point'}
                            </Badge>
                          </HStack>
                          <Text color="gray.800" fontWeight="medium" mb={2}>
                            {exercise.question}
                          </Text>
                          {exercise.solution && (
                            <Box mt={3} p={3} bg="blue.50" borderRadius="md">
                              <Text fontSize="sm" fontWeight="semibold" color="blue.800" mb={1}>
                                Solution :
                              </Text>
                              <Text fontSize="sm" color="blue.700">
                                {exercise.solution}
                              </Text>
                            </Box>
                          )}
                        </Box>
                      ))}
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              </Accordion>
            </VStack>
          </CardBody>
        </Card>
      ))}
      
      {/* Modal pour afficher le PDF */}
      <Modal isOpen={isOpen} onClose={onClose} size="full">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>PDF - TD</ModalHeader>
          <ModalCloseButton />
          <ModalBody p={0}>
            {selectedPdfUrl && (
              <iframe
                src={selectedPdfUrl}
                style={{ width: '100%', height: '100vh', border: 'none' }}
                title="PDF Viewer"
                onLoad={() => {
                  // Nettoyer l'URL blob après le chargement pour libérer la mémoire
                  // Ne pas nettoyer immédiatement car l'iframe en a besoin
                }}
              />
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  )
}

export default TDList














