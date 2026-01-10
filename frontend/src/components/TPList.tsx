import React from 'react'
import { useQuery } from 'react-query'
import { Box, VStack, Heading, Text, Card, CardBody, Spinner, Badge, HStack, Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon, List, ListItem, ListIcon, Button, useToast, Modal, ModalOverlay, ModalContent, ModalHeader, ModalBody, ModalCloseButton, useDisclosure } from '@chakra-ui/react'
import { CheckIcon } from '@chakra-ui/icons'
import { FiDownload, FiEye } from 'react-icons/fi'
import api from '../services/api'

interface TPStep {
  step_number: number
  title: string
  instructions: string
  expected_result?: string
  tips?: string[]
}

interface TP {
  id: string
  module_id: string
  title: string
  description: string
  objectives: string[]
  steps: TPStep[]
  estimated_time: number
  materials_needed?: string[]
  pdf_url?: string
  created_at: string
  updated_at?: string
}

interface TPListProps {
  moduleId: string
}

const TPList = ({ moduleId }: TPListProps) => {
  const toast = useToast()
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [selectedPdfUrl, setSelectedPdfUrl] = React.useState<string | null>(null)
  
  const { data: tps, isLoading } = useQuery<TP[]>(
    ['tps', moduleId],
    async () => {
      const response = await api.get(`/tps/module/${moduleId}`)
      return response.data
    },
    {
      enabled: !!moduleId,
      staleTime: 5 * 60 * 1000,
    }
  )

  const handleDownloadPdf = async (tpId: string, title: string) => {
    try {
      const response = await api.get(`/tps/${tpId}/pdf`, {
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

  const handleViewPdf = async (tpId: string) => {
    try {
      const response = await api.get(`/tps/${tpId}/pdf`, {
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

  if (!tps || tps.length === 0) {
    return (
      <Card>
        <CardBody>
          <Box textAlign="center" py={8}>
            <Text fontSize="4xl" mb={4}>🔬</Text>
            <Text color="gray.600" fontSize="lg" mb={2}>
              Aucun Travaux Pratique disponible pour ce module
            </Text>
            <Text color="gray.500" fontSize="sm">
              Les TP seront ajoutés prochainement
            </Text>
          </Box>
        </CardBody>
      </Card>
    )
  }

  return (
    <VStack spacing={6} align="stretch">
      {tps.map((tp) => (
        <Card key={tp.id} _hover={{ boxShadow: 'md' }} transition="all 0.2s">
          <CardBody>
            <VStack align="stretch" spacing={4}>
              <HStack justify="space-between" align="start">
                <Box flex="1">
                  <Heading size="md" color="gray.800" mb={2}>
                    {tp.title}
                  </Heading>
                  <Text color="gray.600" mb={3}>
                    {tp.description}
                  </Text>
                </Box>
                <VStack spacing={2} align="end">
                  <Badge colorScheme="purple" fontSize="sm" px={3} py={1}>
                    {tp.steps.length} {tp.steps.length > 1 ? 'étapes' : 'étape'}
                  </Badge>
                  <Badge colorScheme="gray" fontSize="sm" px={3} py={1}>
                    ~{tp.estimated_time} min
                  </Badge>
                  {tp.pdf_url && (
                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        colorScheme="red"
                        leftIcon={<FiEye />}
                        onClick={() => handleViewPdf(tp.id)}
                      >
                        Voir PDF
                      </Button>
                      <Button
                        size="sm"
                        colorScheme="purple"
                        leftIcon={<FiDownload />}
                        onClick={() => handleDownloadPdf(tp.id, tp.title)}
                      >
                        Télécharger
                      </Button>
                    </HStack>
                  )}
                </VStack>
              </HStack>

              {tp.objectives && tp.objectives.length > 0 && (
                <Box p={4} bg="purple.50" borderRadius="md">
                  <Heading size="sm" color="purple.800" mb={3}>
                    Objectifs :
                  </Heading>
                  <List spacing={2}>
                    {tp.objectives.map((objective, index) => (
                      <ListItem key={index} color="purple.700">
                        <ListIcon as={CheckIcon} color="purple.500" />
                        {objective}
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {tp.materials_needed && tp.materials_needed.length > 0 && (
                <Box p={4} bg="orange.50" borderRadius="md">
                  <Heading size="sm" color="orange.800" mb={3}>
                    Matériel nécessaire :
                  </Heading>
                  <List spacing={2}>
                    {tp.materials_needed.map((material, index) => (
                      <ListItem key={index} color="orange.700">
                        <ListIcon as={CheckIcon} color="orange.500" />
                        {material}
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              <Accordion allowToggle>
                <AccordionItem border="none">
                  <AccordionButton px={0} py={2} _hover={{ bg: 'transparent' }}>
                    <Box flex="1" textAlign="left">
                      <Text fontWeight="semibold" color="gray.700">
                        Voir les étapes ({tp.steps.length})
                      </Text>
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                  <AccordionPanel px={0} pb={4}>
                    <VStack spacing={4} align="stretch">
                      {tp.steps.map((step) => (
                        <Box
                          key={step.step_number}
                          p={4}
                          bg="gray.50"
                          borderRadius="md"
                          borderLeft="3px solid"
                          borderColor="purple.500"
                        >
                          <HStack mb={2} spacing={2}>
                            <Badge colorScheme="purple" fontSize="xs">
                              Étape {step.step_number}
                            </Badge>
                            <Heading size="sm" color="gray.800">
                              {step.title}
                            </Heading>
                          </HStack>
                          <Text color="gray.700" mb={3}>
                            {step.instructions}
                          </Text>
                          {step.expected_result && (
                            <Box mt={3} p={3} bg="green.50" borderRadius="md">
                              <Text fontSize="sm" fontWeight="semibold" color="green.800" mb={1}>
                                Résultat attendu :
                              </Text>
                              <Text fontSize="sm" color="green.700">
                                {step.expected_result}
                              </Text>
                            </Box>
                          )}
                          {step.tips && step.tips.length > 0 && (
                            <Box mt={3} p={3} bg="yellow.50" borderRadius="md">
                              <Text fontSize="sm" fontWeight="semibold" color="yellow.800" mb={1}>
                                Conseils :
                              </Text>
                              <List spacing={1}>
                                {step.tips.map((tip, index) => (
                                  <ListItem key={index} fontSize="sm" color="yellow.700">
                                    • {tip}
                                  </ListItem>
                                ))}
                              </List>
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
      <Modal isOpen={isOpen} onClose={() => {
        if (selectedPdfUrl) {
          window.URL.revokeObjectURL(selectedPdfUrl)
        }
        setSelectedPdfUrl(null)
        onClose()
      }} size="full">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>PDF - TP</ModalHeader>
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
  )
}

export default TPList














