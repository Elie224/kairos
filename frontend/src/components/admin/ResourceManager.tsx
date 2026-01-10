import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import {
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  useDisclosure,
  useToast,
  IconButton,
  Box,
  Card,
  CardBody,
  Badge,
  Icon,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Spinner,
  Flex,
  Alert,
  AlertIcon,
} from '@chakra-ui/react'
import { FiPlus, FiTrash2, FiFile, FiLink, FiUpload } from 'react-icons/fi'
import api from '../../services/api'

interface Resource {
  id: string
  module_id: string
  title: string
  description?: string
  resource_type: 'pdf' | 'word' | 'ppt' | 'video' | 'link'
  file_url?: string
  external_url?: string
  file_size?: number
  file_name?: string
}

interface ResourceManagerProps {
  moduleId: string
  moduleTitle: string
}

const ResourceManager = ({ moduleId, moduleTitle }: ResourceManagerProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const toast = useToast()
  const queryClient = useQueryClient()
  const [resourceType, setResourceType] = useState<'file' | 'link'>('file')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    external_url: '',
  })

  const { data: resources, isLoading } = useQuery<Resource[]>(
    ['resources', moduleId],
    async () => {
      const response = await api.get(`/resources/module/${moduleId}`)
      return response.data
    },
    {
      enabled: !!moduleId,
      staleTime: 5 * 60 * 1000,
    }
  )

  const deleteMutation = useMutation(
    async (resourceId: string) => {
      await api.delete(`/resources/${resourceId}`)
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['resources', moduleId])
        toast({
          title: 'Succès',
          description: 'Ressource supprimée avec succès',
          status: 'success',
          duration: 3000,
        })
      },
      onError: (error: any) => {
        toast({
          title: 'Erreur',
          description: error.response?.data?.detail || 'Erreur lors de la suppression',
          status: 'error',
          duration: 3000,
        })
      },
    }
  )

  const uploadMutation = useMutation(
    async (formDataToSend: FormData) => {
      // L'intercepteur axios gère automatiquement le Content-Type pour FormData
      const response = await api.post('/resources/upload', formDataToSend)
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['resources', moduleId])
        toast({
          title: 'Succès',
          description: 'Ressource ajoutée avec succès',
          status: 'success',
          duration: 3000,
        })
        onClose()
        resetForm()
      },
      onError: (error: any) => {
        console.error("Upload error:", error.response?.data || error.message);
        let errorMessage = 'Erreur lors de l\'upload';
        
        if (error.response?.data) {
          const errorData = error.response.data;
          // Gérer les erreurs de validation FastAPI (422)
          if (errorData.errors && Array.isArray(errorData.errors)) {
            const validationErrors = errorData.errors
              .map((e: any) => `${e.field}: ${e.message}`)
              .join(', ');
            errorMessage = `Erreur de validation: ${validationErrors}`;
          } else if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        }
        
        toast({
          title: 'Erreur',
          description: errorMessage,
          status: 'error',
          duration: 5000,
        })
      },
    }
  )

  const linkMutation = useMutation(
    async (data: any) => {
      const response = await api.post('/resources/link', data)
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['resources', moduleId])
        toast({
          title: 'Succès',
          description: 'Lien ajouté avec succès',
          status: 'success',
          duration: 3000,
        })
        onClose()
        resetForm()
      },
      onError: (error: any) => {
        toast({
          title: 'Erreur',
          description: error.response?.data?.detail || 'Erreur lors de l\'ajout du lien',
          status: 'error',
          duration: 3000,
        })
      },
    }
  )

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      external_url: '',
    })
    setSelectedFile(null)
    setResourceType('file')
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0])
    }
  }

  const getResourceTypeFromFile = (filename: string): 'pdf' | 'word' | 'ppt' | 'video' => {
    const ext = filename.split('.').pop()?.toLowerCase()
    if (ext === 'pdf') return 'pdf'
    if (['doc', 'docx'].includes(ext || '')) return 'word'
    if (['ppt', 'pptx'].includes(ext || '')) return 'ppt'
    if (['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'].includes(ext || '')) return 'video'
    return 'pdf' // Par défaut
  }

  const handleSubmit = async () => {
    if (!formData.title.trim()) {
      toast({
        title: 'Erreur',
        description: 'Le titre est requis',
        status: 'error',
        duration: 3000,
      })
      return
    }

    if (resourceType === 'file') {
      if (!selectedFile) {
        toast({
          title: 'Erreur',
          description: 'Veuillez sélectionner un fichier',
          status: 'error',
          duration: 3000,
        })
        return
      }

      // Vérifier que le moduleId est valide
      if (!moduleId || moduleId.trim() === '') {
        toast({
          title: 'Erreur',
          description: 'ID de module invalide',
          status: 'error',
          duration: 3000,
        })
        return
      }

      const formDataToSend = new FormData()
      formDataToSend.append('module_id', moduleId.trim())
      formDataToSend.append('title', formData.title.trim())
      // Ne pas envoyer description si vide (FastAPI gère mieux None que chaîne vide)
      if (formData.description?.trim()) {
        formDataToSend.append('description', formData.description.trim())
      }
      formDataToSend.append('resource_type', getResourceTypeFromFile(selectedFile.name))
      formDataToSend.append('file', selectedFile)

      // Debug: vérifier le contenu du FormData
      console.log('FormData contents:')
      console.log('module_id:', moduleId.trim())
      console.log('title:', formData.title.trim())
      console.log('resource_type:', getResourceTypeFromFile(selectedFile.name))
      console.log('file:', selectedFile.name, selectedFile.size, 'bytes')

      uploadMutation.mutate(formDataToSend)
    } else {
      if (!formData.external_url.trim()) {
        toast({
          title: 'Erreur',
          description: 'L\'URL est requise',
          status: 'error',
          duration: 3000,
        })
        return
      }

      linkMutation.mutate({
        module_id: moduleId,
        title: formData.title,
        description: formData.description || '',
        resource_type: 'link',
        external_url: formData.external_url,
      })
    }
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return ''
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <VStack spacing={6} align="stretch">
      <HStack justify="space-between" align="center">
        <Heading size="md" color="gray.900" fontWeight="700" fontFamily="heading">
          Ressources du module: {moduleTitle}
        </Heading>
        <Button
          leftIcon={<FiPlus />}
          bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
          color="white"
          onClick={onOpen}
          size="md"
          _hover={{
            bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)',
          }}
        >
          Ajouter une ressource
        </Button>
      </HStack>

      {isLoading ? (
        <Flex justify="center" py={10}>
          <Spinner size="xl" color="blue.500" />
        </Flex>
      ) : !resources || resources.length === 0 ? (
        <Alert status="info" borderRadius="md">
          <AlertIcon />
          Aucune ressource pour ce module. Ajoutez-en une !
        </Alert>
      ) : (
        <Card bg="white" borderRadius="lg" boxShadow="sm" overflow="hidden">
          <Table variant="simple">
            <Thead bg="blue.50">
              <Tr>
                <Th color="gray.700" fontWeight="bold">Titre</Th>
                <Th color="gray.700" fontWeight="bold">Type</Th>
                <Th color="gray.700" fontWeight="bold">Taille</Th>
                <Th color="gray.700" fontWeight="bold">Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {resources.map((resource) => (
                <Tr key={resource.id} _hover={{ bg: 'gray.50' }}>
                  <Td fontWeight="medium">{resource.title}</Td>
                  <Td>
                    <Badge colorScheme="blue" textTransform="uppercase">
                      {resource.resource_type}
                    </Badge>
                  </Td>
                  <Td>{formatFileSize(resource.file_size)}</Td>
                  <Td>
                    <IconButton
                      icon={<FiTrash2 />}
                      aria-label="Supprimer"
                      size="sm"
                      colorScheme="red"
                      variant="ghost"
                      onClick={() => deleteMutation.mutate(resource.id)}
                    />
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </Card>
      )}

      {/* Modal d'ajout de ressource */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Ajouter une ressource</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>Type de ressource</FormLabel>
                <Select
                  value={resourceType}
                  onChange={(e) => setResourceType(e.target.value as 'file' | 'link')}
                >
                  <option value="file">Fichier (PDF, Word, PPT, Vidéo)</option>
                  <option value="link">Lien externe</option>
                </Select>
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Titre</FormLabel>
                <Input
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Titre de la ressource"
                />
              </FormControl>

              <FormControl>
                <FormLabel>Description</FormLabel>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Description (optionnel)"
                  rows={3}
                />
              </FormControl>

              {resourceType === 'file' ? (
                <FormControl isRequired>
                  <FormLabel>Fichier</FormLabel>
                  <Input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx,.ppt,.pptx,.mp4,.avi,.mov,.wmv,.flv,.webm"
                  />
                  {selectedFile && (
                    <Text fontSize="sm" color="gray.600" mt={2}>
                      Fichier sélectionné: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                    </Text>
                  )}
                </FormControl>
              ) : (
                <FormControl isRequired>
                  <FormLabel>URL externe</FormLabel>
                  <Input
                    type="url"
                    value={formData.external_url}
                    onChange={(e) => setFormData({ ...formData, external_url: e.target.value })}
                    placeholder="https://example.com"
                  />
                </FormControl>
              )}

              <HStack justify="flex-end" mt={4}>
                <Button onClick={onClose} variant="ghost">
                  Annuler
                </Button>
                <Button
                  onClick={handleSubmit}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  color="white"
                  isLoading={uploadMutation.isLoading || linkMutation.isLoading}
                  _hover={{
                    bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)',
                  }}
                >
                  {resourceType === 'file' ? 'Uploader' : 'Ajouter'}
                </Button>
              </HStack>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  )
}

export default ResourceManager

