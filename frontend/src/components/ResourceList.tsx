import { useQuery } from 'react-query'
import { 
  Box, 
  VStack, 
  Heading, 
  Text, 
  Card, 
  CardBody, 
  Spinner, 
  HStack, 
  Icon, 
  Button,
  Badge,
  Link,
  SimpleGrid,
  useToast,
  Image,
  AspectRatio,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure
} from '@chakra-ui/react'
import { useState } from 'react'
import { FiFile, FiDownload, FiExternalLink, FiFileText, FiVideo, FiLink, FiPlay } from 'react-icons/fi'
import api from '../services/api'
import { detectVideoPlatform, extractYouTubeVideoId, isValidVideoUrl } from '../utils/videoUtils'

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
  created_at: string
}

interface ResourceListProps {
  moduleId: string
}

const ResourceList = ({ moduleId }: ResourceListProps) => {
  const toast = useToast()
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [selectedVideoUrl, setSelectedVideoUrl] = useState<string | null>(null)
  const [selectedVideoTitle, setSelectedVideoTitle] = useState<string>('')
  
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

  const handleDownload = async (fileUrl: string, fileName: string) => {
    try {
      // Extraire le nom du fichier de l'URL
      const filename = fileUrl.split('/').pop() || fileName
      
      // Télécharger via l'API avec authentification
      const response = await api.get(`/resources/files/${filename}`, {
        responseType: 'blob', // Important pour les fichiers binaires
      })
      
      // Créer un lien temporaire et déclencher le téléchargement
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', fileName || filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast({
        title: 'Téléchargement réussi',
        description: `Le fichier ${fileName || filename} a été téléchargé`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    } catch (error: any) {
      console.error('Erreur lors du téléchargement:', error)
      toast({
        title: 'Erreur de téléchargement',
        description: error.response?.data?.detail || 'Impossible de télécharger le fichier',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const getResourceIcon = (type: string, externalUrl?: string) => {
    // Si c'est un lien et qu'on peut détecter une plateforme vidéo
    if (type === 'link' && externalUrl && isValidVideoUrl(externalUrl)) {
      return FiVideo
    }
    switch (type) {
      case 'pdf':
        return FiFileText
      case 'word':
        return FiFile
      case 'ppt':
        return FiFile
      case 'video':
        return FiVideo
      case 'link':
        return FiLink
      default:
        return FiFile
    }
  }
  
  const handleVideoClick = (url: string, title: string) => {
    setSelectedVideoUrl(url)
    setSelectedVideoTitle(title)
    onOpen()
  }
  
  const getVideoEmbedUrl = (url: string): string | null => {
    const platform = detectVideoPlatform(url)
    if (platform?.embedUrl) {
      return platform.embedUrl(url)
    }
    return null
  }

  const getResourceColor = (type: string) => {
    switch (type) {
      case 'pdf':
        return 'red'
      case 'word':
        return 'blue'
      case 'ppt':
        return 'orange'
      case 'video':
        return 'purple'
      case 'link':
        return 'green'
      default:
        return 'gray'
    }
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return ''
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  if (isLoading) {
    return (
      <Box textAlign="center" py={8}>
        <Spinner size="xl" color="blue.500" />
      </Box>
    )
  }

  if (!resources || resources.length === 0) {
    return (
      <Card bg="white" border="2px solid" borderColor="blue.100" borderRadius="2xl">
        <CardBody>
          <Box textAlign="center" py={8}>
            <Text fontSize="4xl" mb={4}>📚</Text>
            <Text color="gray.600" fontSize="lg" mb={2}>
              Aucune ressource disponible pour ce module
            </Text>
            <Text color="gray.500" fontSize="sm">
              Les ressources seront ajoutées prochainement
            </Text>
          </Box>
        </CardBody>
      </Card>
    )
  }

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="md" color="gray.900" fontWeight="700" fontFamily="heading">
        Ressources du cours ({resources.length})
      </Heading>
      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
        {resources.map((resource) => {
          const IconComponent = getResourceIcon(resource.resource_type, resource.external_url)
          const colorScheme = getResourceColor(resource.resource_type)
          const isVideoLink = resource.resource_type === 'link' && resource.external_url && isValidVideoUrl(resource.external_url)
          const videoPlatform = resource.external_url ? detectVideoPlatform(resource.external_url) : null
          const youtubeThumbnail = videoPlatform?.name === 'YouTube' && resource.external_url 
            ? videoPlatform.thumbnailUrl?.(resource.external_url) 
            : null
          
          return (
            <Card 
              key={resource.id} 
              bg="white"
              border="2px solid"
              borderColor="blue.100"
              borderRadius="xl"
              _hover={{ 
                boxShadow: 'lg',
                borderColor: 'blue.300',
                transform: 'translateY(-2px)'
              }} 
              transition="all 0.3s"
            >
              <CardBody>
                <VStack align="stretch" spacing={3}>
                  {/* Miniature vidéo si disponible (YouTube) */}
                  {isVideoLink && youtubeThumbnail && (
                    <Box position="relative" borderRadius="lg" overflow="hidden" cursor="pointer" onClick={() => resource.external_url && handleVideoClick(resource.external_url, resource.title)}>
                      <AspectRatio ratio={16 / 9}>
                        <Image src={youtubeThumbnail} alt={resource.title} objectFit="cover" />
                      </AspectRatio>
                      <Box position="absolute" top="50%" left="50%" transform="translate(-50%, -50%)" bg="blackAlpha.700" borderRadius="full" p={3}>
                        <Icon as={FiPlay} boxSize={6} color="white" />
                      </Box>
                      {videoPlatform && (
                        <Badge 
                          position="absolute" 
                          top={2} 
                          right={2}
                          colorScheme={videoPlatform.color}
                          fontSize="xs"
                          px={2}
                          py={1}
                        >
                          {videoPlatform.icon} {videoPlatform.name}
                        </Badge>
                      )}
                    </Box>
                  )}
                  
                  <HStack justify="space-between" align="start">
                    <HStack spacing={3} flex="1">
                      <Box
                        p={3}
                        bgGradient={`linear-gradient(135deg, ${colorScheme}.500 0%, ${colorScheme}.600 100%)`}
                        borderRadius="lg"
                        boxShadow="md"
                      >
                        <Icon as={IconComponent} boxSize={5} color="white" />
                      </Box>
                      <VStack align="start" spacing={1} flex="1">
                        <Heading size="sm" color="gray.900" fontWeight="700" fontFamily="heading">
                          {resource.title}
                        </Heading>
                        {resource.description && (
                          <Text fontSize="sm" color="gray.600" fontFamily="body" noOfLines={2}>
                            {resource.description}
                          </Text>
                        )}
                      </VStack>
                    </HStack>
                    <Badge 
                      colorScheme={isVideoLink && videoPlatform ? videoPlatform.color : colorScheme}
                      fontSize="xs"
                      px={2}
                      py={1}
                      borderRadius="full"
                      textTransform="uppercase"
                    >
                      {isVideoLink && videoPlatform ? `${videoPlatform.icon} ${videoPlatform.name}` : resource.resource_type}
                    </Badge>
                  </HStack>
                  
                  <HStack justify="space-between" mt={2}>
                    {resource.file_size && (
                      <Text fontSize="xs" color="gray.500" fontFamily="body">
                        {formatFileSize(resource.file_size)}
                      </Text>
                    )}
                    {resource.resource_type === 'link' || isVideoLink ? (
                      isVideoLink ? (
                        <Button
                          onClick={() => resource.external_url && handleVideoClick(resource.external_url, resource.title)}
                          size="sm"
                          colorScheme={videoPlatform?.color || colorScheme}
                          leftIcon={<FiPlay />}
                          bgGradient={`linear-gradient(135deg, ${videoPlatform?.color || colorScheme}.500 0%, ${videoPlatform?.color || colorScheme}.600 100%)`}
                          color="white"
                          _hover={{
                            bgGradient: `linear-gradient(135deg, ${videoPlatform?.color || colorScheme}.600 0%, ${videoPlatform?.color || colorScheme}.700 100%)`,
                          }}
                        >
                          Regarder la vidéo
                        </Button>
                      ) : (
                        <Button
                          as={Link}
                          href={resource.external_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          size="sm"
                          colorScheme={colorScheme}
                          leftIcon={<FiExternalLink />}
                          variant="outline"
                        >
                          Ouvrir le lien
                        </Button>
                      )
                    ) : (
                      <Button
                        onClick={() => resource.file_url && handleDownload(resource.file_url, resource.file_name || resource.title)}
                        size="sm"
                        colorScheme={colorScheme}
                        leftIcon={<FiDownload />}
                        bgGradient={`linear-gradient(135deg, ${colorScheme}.500 0%, ${colorScheme}.600 100%)`}
                        color="white"
                        _hover={{
                          bgGradient: `linear-gradient(135deg, ${colorScheme}.600 0%, ${colorScheme}.700 100%)`,
                        }}
                      >
                        Télécharger
                      </Button>
                    )}
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          )
        })}
      </SimpleGrid>
      
      {/* Modal pour afficher la vidéo */}
      <Modal isOpen={isOpen} onClose={onClose} size="full" isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{selectedVideoTitle}</ModalHeader>
          <ModalCloseButton />
          <ModalBody p={0}>
            {selectedVideoUrl && (
              <AspectRatio ratio={16 / 9} maxH="90vh">
                {getVideoEmbedUrl(selectedVideoUrl) ? (
                  <iframe
                    src={getVideoEmbedUrl(selectedVideoUrl) || ''}
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    style={{ border: 'none' }}
                    title={selectedVideoTitle}
                  />
                ) : (
                  <Box p={8} textAlign="center">
                    <Text fontSize="lg" mb={4} color="gray.600">
                      Ouverture de la vidéo dans un nouvel onglet...
                    </Text>
                    <Button
                      as={Link}
                      href={selectedVideoUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      colorScheme="blue"
                      size="lg"
                      leftIcon={<FiExternalLink />}
                    >
                      Ouvrir la vidéo
                    </Button>
                  </Box>
                )}
              </AspectRatio>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  )
}

export default ResourceList

