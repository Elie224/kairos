/**
 * Page d'administration - Gestion complète avec onglets
 */
import { useState, useEffect } from 'react'
import {
  Container,
  VStack,
  Heading,
  Text,
  Box,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  IconButton,
  useDisclosure,
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
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  HStack,
  Badge,
  Alert,
  AlertIcon,
  useToast,
  Spinner,
  Flex,
  Divider,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  ModalFooter,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  Switch,
  Tooltip,
  Card,
  CardBody,
} from '@chakra-ui/react'
import { FiEdit, FiTrash2, FiPlus, FiSave, FiX, FiUsers, FiBook, FiBarChart2, FiShield, FiUserCheck, FiUserX, FiRefreshCw, FiMessageSquare, FiMail, FiPhone, FiCheck, FiClock } from 'react-icons/fi'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import { Module } from '../types/module'
import { ModuleContent } from '../types/moduleContent'
import ResourceManager from '../components/admin/ResourceManager'

const SUBJECTS = ['mathematics', 'computer_science'] as const
const DIFFICULTIES = ['beginner', 'intermediate', 'advanced'] as const

type Subject = typeof SUBJECTS[number]
type Difficulty = typeof DIFFICULTIES[number]

interface ModuleFormData {
  title: string
  description: string
  subject: Subject | ''
  difficulty: Difficulty | ''
  estimated_time: number
  learning_objectives: string[]
  content: ModuleContent
}

interface User {
  id: string
  email: string
  username: string
  first_name?: string
  last_name?: string
  is_admin?: boolean
  is_active?: boolean
  created_at?: string
}

interface Stats {
  total_users: number
  total_admins: number
  active_users: number
  total_modules: number
  total_progress: number
  total_support_messages: number
  modules_by_subject: Record<string, number>
  modules_by_difficulty: Record<string, number>
}

interface SupportMessage {
  id: string
  name: string
  email: string
  phone?: string
  subject: string
  message: string
  support_type: string
  created_at: string
  read: boolean
  responded: boolean
}

const Admin = () => {
  const { t } = useTranslation()
  const toast = useToast()
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [activeTab, setActiveTab] = useState(0)
  
  // Modules state
  const [modules, setModules] = useState<Module[]>([])
  const [isLoadingModules, setIsLoadingModules] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [editingModule, setEditingModule] = useState<Module | null>(null)
  const [formData, setFormData] = useState<ModuleFormData>({
    title: '',
    description: '',
    subject: '',
    difficulty: '',
    estimated_time: 30,
    learning_objectives: [''],
    content: {
      lessons: [
        {
          title: '',
          content: '',
          sections: [],
        },
      ],
    },
  })
  
  // Users state
  const [users, setUsers] = useState<User[]>([])
  const [isLoadingUsers, setIsLoadingUsers] = useState(true)
  
  // Stats state
  const [stats, setStats] = useState<Stats | null>(null)
  const [isLoadingStats, setIsLoadingStats] = useState(true)
  
  // Support messages state
  const [supportMessages, setSupportMessages] = useState<SupportMessage[]>([])
  const [isLoadingMessages, setIsLoadingMessages] = useState(true)
  const [showUnreadOnly, setShowUnreadOnly] = useState(false)

  useEffect(() => {
    if (activeTab === 0) {
      loadModules()
    } else if (activeTab === 1) {
      loadUsers()
    } else if (activeTab === 2) {
      loadStats()
    } else if (activeTab === 3) {
      loadSupportMessages()
    }
  }, [activeTab])

  useEffect(() => {
    if (activeTab === 3) {
      loadSupportMessages()
    }
  }, [showUnreadOnly])

  const loadModules = async () => {
    try {
      setIsLoadingModules(true)
      const response = await api.get('/modules/', {
        timeout: 60000, // 60 secondes pour le chargement des modules (peut être long avec validation)
      })
      setModules(response.data)
    } catch (error: any) {
      // Ne pas afficher d'erreur si c'est juste un timeout (le retry va gérer)
      if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
        // Le retry automatique va gérer cela
        return
      }
      toast({
        title: 'Erreur',
        description: 'Impossible de charger les modules',
        status: 'error',
        duration: 3000,
      })
    } finally {
      setIsLoadingModules(false)
    }
  }

  const loadUsers = async () => {
    try {
      setIsLoadingUsers(true)
      const response = await api.get('/auth/users')
      setUsers(response.data)
    } catch (error: any) {
      toast({
        title: 'Erreur',
        description: 'Impossible de charger les utilisateurs',
        status: 'error',
        duration: 3000,
      })
    } finally {
      setIsLoadingUsers(false)
    }
  }

  const loadStats = async () => {
    try {
      setIsLoadingStats(true)
      const response = await api.get('/auth/stats')
      setStats(response.data)
    } catch (error: any) {
      toast({
        title: 'Erreur',
        description: 'Impossible de charger les statistiques',
        status: 'error',
        duration: 3000,
      })
    } finally {
      setIsLoadingStats(false)
    }
  }

  const loadSupportMessages = async () => {
    try {
      setIsLoadingMessages(true)
      const response = await api.get('/support/messages', {
        params: {
          unread_only: showUnreadOnly,
        },
      })
      setSupportMessages(response.data)
    } catch (error: any) {
      toast({
        title: 'Erreur',
        description: 'Impossible de charger les messages de support',
        status: 'error',
        duration: 3000,
      })
    } finally {
      setIsLoadingMessages(false)
    }
  }

  const markAsRead = async (messageId: string) => {
    try {
      await api.put(`/support/messages/${messageId}/read`)
      toast({
        title: 'Succès',
        description: 'Message marqué comme lu',
        status: 'success',
        duration: 2000,
      })
      loadSupportMessages()
    } catch (error: any) {
      toast({
        title: 'Erreur',
        description: error.response?.data?.detail || 'Erreur lors de la mise à jour',
        status: 'error',
        duration: 3000,
      })
    }
  }

  const markAsResponded = async (messageId: string) => {
    try {
      await api.put(`/support/messages/${messageId}/responded`)
      toast({
        title: 'Succès',
        description: 'Message marqué comme ayant reçu une réponse',
        status: 'success',
        duration: 2000,
      })
      loadSupportMessages()
    } catch (error: any) {
      toast({
        title: 'Erreur',
        description: error.response?.data?.detail || 'Erreur lors de la mise à jour',
        status: 'error',
        duration: 3000,
      })
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getSupportTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      general: 'Soutien Général',
      financial: 'Soutien Financier',
      technical: 'Soutien Technique',
      partnership: 'Partenariat',
    }
    return labels[type] || type
  }

  const handleCreate = () => {
    setEditingModule(null)
    setFormData({
      title: '',
      description: '',
      subject: '',
      difficulty: '',
      estimated_time: 30,
      learning_objectives: [''],
      content: {
        lessons: [
          {
            title: '',
            content: '',
            sections: [],
          },
        ],
      },
    })
    onOpen()
  }

  const handleEdit = (module: Module) => {
    setEditingModule(module)
    setFormData({
      title: module.title,
      description: module.description,
      subject: (module.subject || '') as Subject,
      difficulty: (module.difficulty || '') as Difficulty,
      estimated_time: module.estimated_time,
      learning_objectives: module.learning_objectives || [''],
      content: module.content || {
        lessons: [
          {
            title: '',
            content: '',
            sections: [],
          },
        ],
      },
    })
    onOpen()
  }

  const handleDelete = async (moduleId: string) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce module ?')) {
      return
    }

    try {
      await api.delete(`/modules/${moduleId}`)
      toast({
        title: 'Succès',
        description: 'Module supprimé avec succès',
        status: 'success',
        duration: 3000,
      })
      loadModules()
    } catch (error: any) {
      toast({
        title: 'Erreur',
        description: error.response?.data?.detail || 'Impossible de supprimer le module',
        status: 'error',
        duration: 3000,
      })
    }
  }

  const handleSubmit = async () => {
    if (!formData.title || !formData.description || !formData.subject || !formData.difficulty) {
      toast({
        title: 'Erreur',
        description: 'Veuillez remplir tous les champs obligatoires',
        status: 'error',
        duration: 3000,
      })
      return
    }
    
    // Vérifier qu'au moins un objectif d'apprentissage est rempli (minimum 5 caractères)
    const validObjectives = formData.learning_objectives.filter((obj) => obj.trim() !== '' && obj.trim().length >= 5)
    if (validObjectives.length === 0) {
      toast({
        title: 'Erreur de validation',
        description: 'Au moins un objectif d\'apprentissage est requis (minimum 5 caractères par objectif)',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
      return
    }

    try {
      setIsSubmitting(true)
      
      // Filtrer les leçons vides avant la sauvegarde
      const validLessons = (formData.content?.lessons || []).filter(lesson => {
        const hasTitle = lesson.title && lesson.title.trim() !== ''
        const hasSummary = lesson.summary && lesson.summary.trim() !== ''
        const hasContent = lesson.content && lesson.content.trim() !== ''
        const hasSections = lesson.sections && lesson.sections.length > 0 && 
          lesson.sections.some(section => 
            (section.heading && section.heading.trim() !== '') ||
            (section.paragraphs && section.paragraphs.length > 0) ||
            (section.bulletPoints && section.bulletPoints.length > 0)
          )
        return hasTitle || hasSummary || hasContent || hasSections
      })
      
      // S'assurer que les champs sont correctement formatés
      const payload = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        subject: formData.subject as Subject,
        difficulty: formData.difficulty as Difficulty,
        estimated_time: formData.estimated_time || 30,
        learning_objectives: validObjectives.map(obj => obj.trim()).filter(obj => obj.length >= 5),
        content: {
          ...formData.content,
          lessons: validLessons
        },
      }
      
      // Validation finale avant envoi
      if (!payload.learning_objectives || payload.learning_objectives.length === 0) {
        toast({
          title: 'Erreur de validation',
          description: 'Au moins un objectif d\'apprentissage valide (minimum 5 caractères) est requis',
          status: 'error',
          duration: 5000,
          isClosable: true,
        })
        return
      }
      
      // Logging via le système centralisé (seulement en dev)
      if (import.meta.env.DEV) {
        import('../utils/logger').then(({ logger }) => {
          logger.debug('Payload envoyé', { ...payload, content: { ...payload.content, lessons: `${payload.content.lessons.length} leçons` } }, 'Admin')
        })
      }

      if (editingModule) {
        await api.put(`/modules/${editingModule.id}`, payload, {
          timeout: 30000, // 30 secondes pour la modification du module
        })
        toast({
          title: 'Succès',
          description: 'Module modifié avec succès !',
          status: 'success',
          duration: 5000,
          isClosable: true,
        })
      } else {
        await api.post('/modules/', payload)
        toast({
          title: 'Succès',
          description: 'Module créé avec succès. Génération automatique du contenu en cours...',
          status: 'success',
          duration: 5000,
        })
        // La génération automatique se fera côté backend
      }

      onClose()
      loadModules()
    } catch (error: any) {
      import('../utils/logger').then(({ logger }) => {
        logger.error('Erreur lors de la création/modification du module', error, 'Admin')
      })
      const errorDetail = error.response?.data?.detail
      let errorMessage = 'Une erreur est survenue'
      
      if (errorDetail) {
        if (typeof errorDetail === 'string') {
          errorMessage = errorDetail
        } else if (Array.isArray(errorDetail)) {
          // Erreur de validation Pydantic
          const validationErrors = errorDetail.map((err: any) => {
            const field = err.loc?.join('.') || err.field || 'champ'
            return `${field}: ${err.msg || err.message || 'Erreur de validation'}`
          }).join('\n')
          errorMessage = `Erreurs de validation:\n${validationErrors}`
        } else if (errorDetail.msg) {
          errorMessage = errorDetail.msg
        }
      }
      
      toast({
        title: 'Erreur',
        description: errorMessage,
        status: 'error',
        duration: 8000,
        isClosable: true,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleGenerateContent = async (moduleId: string) => {
    try {
      toast({
        title: 'Génération en cours',
        description: 'Génération des quiz, TD et TP...',
        status: 'info',
        duration: 3000,
      })
      
      // Timeout de 5 minutes pour la génération de contenu (peut prendre du temps avec OpenAI + MongoDB)
      const response = await api.post(`/modules/${moduleId}/generate-content`, {}, {
        timeout: 300000 // 5 minutes
      })
      const result = response.data
      
      // Log pour debug (seulement en dev)
      if (import.meta.env.DEV) {
        import('../utils/logger').then(({ logger }) => {
          logger.debug('Résultat de la génération', result, 'Admin')
        })
      }
      
      // Toujours afficher le message complet de la réponse
      const message = result.message || `Génération terminée: ${result.tds_generated} TD, ${result.tps_generated} TP générés.`
      
      // Afficher les erreurs si présentes
      if (result.errors && result.errors.length > 0) {
        const errorMessages = result.errors.map((err: any) => {
          if (typeof err === 'string') return err
          if (err.error) return `${err.type || 'Erreur'}: ${err.error}`
          return JSON.stringify(err)
        }).join('; ')
        
        toast({
          title: 'Génération avec erreurs',
          description: `${message} Erreurs: ${errorMessages}`,
          status: 'warning',
          duration: 15000,
          isClosable: true,
        })
        
        // Logger les erreurs
        import('../utils/logger').then(({ logger }) => {
          logger.error('Erreurs de génération', result.errors, 'Admin')
        })
      } else if (result.tds_generated === 0 && result.tps_generated === 0) {
        // Si aucun TD/TP généré et pas d'erreurs, c'est suspect
        toast({
          title: 'Aucun contenu généré',
          description: message + ' Vérifiez que les leçons ont du contenu valide.',
          status: 'warning',
          duration: 10000,
          isClosable: true,
        })
      } else {
        toast({
          title: 'Génération terminée',
          description: message,
          status: 'success',
          duration: 5000,
        })
      }
      
      loadModules()
    } catch (error: any) {
      toast({
        title: 'Erreur',
        description: error.response?.data?.detail || 'Erreur lors de la génération',
        status: 'error',
        duration: 5000,
      })
    }
  }

  const handleToggleAdmin = async (user: User) => {
    try {
      await api.put(`/auth/users/${user.id}`, {
        is_admin: !user.is_admin,
      })
      toast({
        title: 'Succès',
        description: `Utilisateur ${user.is_admin ? 'rétrogradé' : 'promu'} avec succès`,
        status: 'success',
        duration: 3000,
      })
      loadUsers()
    } catch (error: any) {
      toast({
        title: 'Erreur',
        description: error.response?.data?.detail || 'Une erreur est survenue',
        status: 'error',
        duration: 3000,
      })
    }
  }

  const handleToggleActive = async (user: User) => {
    try {
      await api.put(`/auth/users/${user.id}`, {
        is_active: !user.is_active,
      })
      toast({
        title: 'Succès',
        description: `Utilisateur ${user.is_active ? 'désactivé' : 'activé'} avec succès`,
        status: 'success',
        duration: 3000,
      })
      loadUsers()
    } catch (error: any) {
      toast({
        title: 'Erreur',
        description: error.response?.data?.detail || 'Une erreur est survenue',
        status: 'error',
        duration: 3000,
      })
    }
  }

  const addLearningObjective = () => {
    setFormData({
      ...formData,
      learning_objectives: [...formData.learning_objectives, ''],
    })
  }

  const updateLearningObjective = (index: number, value: string) => {
    const newObjectives = [...formData.learning_objectives]
    newObjectives[index] = value
    setFormData({ ...formData, learning_objectives: newObjectives })
  }

  const removeLearningObjective = (index: number) => {
    const newObjectives = formData.learning_objectives.filter((_, i) => i !== index)
    setFormData({ ...formData, learning_objectives: newObjectives.length > 0 ? newObjectives : [''] })
  }

  // Fonctions pour gérer les leçons
  const addLesson = () => {
    const newLessons = [...(formData.content?.lessons || []), {
      title: '',
      content: '',
      sections: [],
    }]
    setFormData({
      ...formData,
      content: {
        ...formData.content,
        lessons: newLessons,
      },
    })
  }

  const updateLesson = (index: number, field: 'title' | 'content' | 'summary' | 'resource_ids', value: string | string[]) => {
    const newLessons = [...(formData.content?.lessons || [])]
    newLessons[index] = {
      ...newLessons[index],
      [field]: value,
    }
    setFormData({
      ...formData,
      content: {
        ...formData.content,
        lessons: newLessons,
      },
    })
  }

  const removeLesson = (index: number) => {
    const newLessons = (formData.content?.lessons || []).filter((_, i) => i !== index)
    setFormData({
      ...formData,
      content: {
        ...formData.content,
        lessons: newLessons.length > 0 ? newLessons : [],
      },
    })
  }

  // Fonctions pour gérer les sections d'une leçon
  const addSection = (lessonIndex: number) => {
    const newLessons = [...(formData.content?.lessons || [])]
    if (!newLessons[lessonIndex].sections) {
      newLessons[lessonIndex].sections = []
    }
    newLessons[lessonIndex].sections.push({
      heading: '',
      paragraphs: [],
      bulletPoints: [],
    })
    setFormData({
      ...formData,
      content: {
        ...formData.content,
        lessons: newLessons,
      },
    })
  }

  const updateSection = (lessonIndex: number, sectionIndex: number, field: 'heading' | 'paragraphs' | 'bulletPoints', value: string | string[]) => {
    const newLessons = [...(formData.content?.lessons || [])]
    if (!newLessons[lessonIndex].sections) {
      newLessons[lessonIndex].sections = []
    }
    newLessons[lessonIndex].sections[sectionIndex] = {
      ...newLessons[lessonIndex].sections[sectionIndex],
      [field]: value,
    }
    setFormData({
      ...formData,
      content: {
        ...formData.content,
        lessons: newLessons,
      },
    })
  }

  const removeSection = (lessonIndex: number, sectionIndex: number) => {
    const newLessons = [...(formData.content?.lessons || [])]
    if (newLessons[lessonIndex].sections) {
      newLessons[lessonIndex].sections = newLessons[lessonIndex].sections.filter((_, i) => i !== sectionIndex)
    }
    setFormData({
      ...formData,
      content: {
        ...formData.content,
        lessons: newLessons,
      },
    })
  }

  const getSubjectLabel = (subject: string) => {
    const labels: Record<string, string> = {
      mathematics: t('modules.mathematics'),
      computer_science: t('modules.computerScience'),
    }
    return labels[subject] || subject
  }

  const getDifficultyLabel = (difficulty: string) => {
    const labels: Record<string, string> = {
      beginner: t('modules.beginner'),
      intermediate: t('modules.intermediate'),
      advanced: t('modules.advanced'),
    }
    return labels[difficulty] || difficulty
  }

  const getDifficultyColor = (difficulty: string) => {
    const colors: Record<string, string> = {
      beginner: 'gray',
      intermediate: 'gray',
      advanced: 'gray',
    }
    return colors[difficulty] || 'gray'
  }

  return (
    <Box bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)" minH="100vh" py={{ base: 4, md: 8 }} px={{ base: 4, md: 0 }}>
      <Container maxW="1400px" px={{ base: 4, md: 6 }}>
        <VStack spacing={{ base: 4, md: 8 }} align="stretch">
          {/* En-tête */}
          <Box>
            <Heading size={{ base: 'xl', md: '2xl' }} color="gray.800" fontWeight="bold" mb={2}>
              Administration
            </Heading>
            <Text color="gray.600" fontSize={{ base: 'md', md: 'lg' }}>
              Gestion complète de la plateforme Kaïrox
            </Text>
          </Box>

          <Divider borderColor="gray.300" />

          {/* Onglets */}
          <Tabs index={activeTab} onChange={setActiveTab} colorScheme="gray">
            <TabList>
              <Tab>
                <HStack spacing={2}>
                  <FiBook />
                  <Text>Modules</Text>
                </HStack>
              </Tab>
              <Tab>
                <HStack spacing={2}>
                  <FiUsers />
                  <Text>Utilisateurs</Text>
                </HStack>
              </Tab>
              <Tab>
                <HStack spacing={2}>
                  <FiBarChart2 />
                  <Text>Statistiques</Text>
                </HStack>
              </Tab>
              <Tab>
                <HStack spacing={2}>
                  <FiMessageSquare />
                  <Text>Messages Support</Text>
                  {supportMessages.filter((m) => !m.read).length > 0 && (
                    <Badge colorScheme="red" borderRadius="full" fontSize="xs">
                      {supportMessages.filter((m) => !m.read).length}
                    </Badge>
                  )}
                </HStack>
              </Tab>
            </TabList>

            <TabPanels>
              {/* Panel Modules */}
              <TabPanel px={0}>
                <VStack spacing={6} align="stretch">
                  <Flex justify="space-between" align="center" flexWrap="wrap" gap={4}>
                    <Text color="gray.700" fontSize={{ base: 'md', md: 'lg' }} fontWeight="medium">
                      Gestion des modules d'apprentissage
                    </Text>
                    <Button
                      leftIcon={<FiPlus />}
                      colorScheme="gray"
                      bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                      _hover={{ bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)' }}
                      onClick={handleCreate}
                      size={{ base: 'sm', md: 'md' }}
                      minH="48px"
                      w={{ base: 'full', md: 'auto' }}
                      data-touch-target="true"
                    >
                      Nouveau Module
                    </Button>
                  </Flex>

                  {isLoadingModules ? (
                    <Flex justify="center" py={10}>
                      <Spinner size="xl" color="gray.500" />
                    </Flex>
                  ) : modules.length === 0 ? (
                    <Alert status="info" borderRadius="md">
                      <AlertIcon />
                      Aucun module trouvé. Créez votre premier module !
                    </Alert>
                  ) : (
                    <>
                      {/* Version Desktop - Tableau */}
                      <Box bg="white" borderRadius="lg" boxShadow="sm" overflow="hidden" display={{ base: 'none', md: 'block' }}>
                        <Box overflowX="auto" className="table-container">
                          <Table variant="simple">
                            <Thead bg="gray.100">
                              <Tr>
                                <Th color="gray.700" fontWeight="bold">Titre</Th>
                                <Th color="gray.700" fontWeight="bold">Matière</Th>
                                <Th color="gray.700" fontWeight="bold">Difficulté</Th>
                                <Th color="gray.700" fontWeight="bold">Temps estimé</Th>
                                <Th color="gray.700" fontWeight="bold">Actions</Th>
                              </Tr>
                            </Thead>
                            <Tbody>
                              {modules.map((module) => (
                                <Tr key={module.id} _hover={{ bg: 'gray.50' }}>
                                  <Td fontWeight="medium" data-label="Titre">{module.title}</Td>
                                  <Td data-label="Matière">
                                    <Badge colorScheme="gray" variant="subtle">
                                      {getSubjectLabel(module.subject)}
                                    </Badge>
                                  </Td>
                                  <Td>
                                    <Badge colorScheme={getDifficultyColor(module.difficulty)}>
                                      {getDifficultyLabel(module.difficulty)}
                                    </Badge>
                                  </Td>
                                  <Td>{module.estimated_time} min</Td>
                                  <Td>
                                    <HStack spacing={2}>
                                      <Tooltip label="Générer Quiz, TD et TP">
                                        <IconButton
                                          icon={<FiRefreshCw />}
                                          aria-label="Générer le contenu"
                                          size="sm"
                                          colorScheme="blue"
                                          variant="ghost"
                                          onClick={() => handleGenerateContent(module.id)}
                                          minH="48px"
                                          minW="48px"
                                          data-touch-target="true"
                                        />
                                      </Tooltip>
                                      <IconButton
                                        icon={<FiEdit />}
                                        aria-label="Modifier"
                                        size="sm"
                                        colorScheme="gray"
                                        variant="ghost"
                                        onClick={() => handleEdit(module)}
                                        minH="48px"
                                        minW="48px"
                                        data-touch-target="true"
                                      />
                                      <IconButton
                                        icon={<FiTrash2 />}
                                        aria-label="Supprimer"
                                        size="sm"
                                        colorScheme="gray"
                                        variant="ghost"
                                        onClick={() => handleDelete(module.id)}
                                        minH="48px"
                                        minW="48px"
                                        data-touch-target="true"
                                      />
                                    </HStack>
                                  </Td>
                                </Tr>
                              ))}
                            </Tbody>
                          </Table>
                        </Box>
                      </Box>

                      {/* Version Mobile - Cards */}
                      <SimpleGrid columns={{ base: 1, md: 0 }} spacing={4} display={{ base: 'grid', md: 'none' }}>
                        {modules.map((module) => (
                          <Card key={module.id} bg="white" borderRadius="lg" boxShadow="sm">
                            <CardBody p={{ base: 4, md: 6 }}>
                              <VStack spacing={4} align="stretch">
                                <Box>
                                  <Heading size="sm" color="gray.800" mb={2} fontWeight="bold">
                                    {module.title}
                                  </Heading>
                                </Box>
                                
                                <HStack spacing={2} flexWrap="wrap">
                                  <Badge colorScheme="gray" variant="subtle" fontSize={{ base: 'xs', md: 'sm' }}>
                                    {getSubjectLabel(module.subject)}
                                  </Badge>
                                  <Badge colorScheme={getDifficultyColor(module.difficulty)} fontSize={{ base: 'xs', md: 'sm' }}>
                                    {getDifficultyLabel(module.difficulty)}
                                  </Badge>
                                  <Badge colorScheme="blue" variant="outline" fontSize={{ base: 'xs', md: 'sm' }}>
                                    {module.estimated_time} min
                                  </Badge>
                                </HStack>

                                <Divider />

                                <HStack spacing={2} justify="flex-end" flexWrap="wrap">
                                  <Tooltip label="Générer Quiz, TD et TP">
                                    <IconButton
                                      icon={<FiRefreshCw />}
                                      aria-label="Générer le contenu"
                                      size={{ base: 'md', md: 'sm' }}
                                      colorScheme="blue"
                                      variant="ghost"
                                      onClick={() => handleGenerateContent(module.id)}
                                      minH="48px"
                                      minW="48px"
                                      data-touch-target="true"
                                    />
                                  </Tooltip>
                                  <IconButton
                                    icon={<FiEdit />}
                                    aria-label="Modifier"
                                    size={{ base: 'md', md: 'sm' }}
                                    colorScheme="gray"
                                    variant="ghost"
                                    onClick={() => handleEdit(module)}
                                    minH="48px"
                                    minW="48px"
                                    data-touch-target="true"
                                  />
                                  <IconButton
                                    icon={<FiTrash2 />}
                                    aria-label="Supprimer"
                                    size={{ base: 'md', md: 'sm' }}
                                    colorScheme="red"
                                    variant="ghost"
                                    onClick={() => handleDelete(module.id)}
                                    minH="48px"
                                    minW="48px"
                                    data-touch-target="true"
                                  />
                                </HStack>
                              </VStack>
                            </CardBody>
                          </Card>
                        ))}
                      </SimpleGrid>
                    </>
                  )}
                </VStack>
              </TabPanel>

              {/* Panel Utilisateurs */}
              <TabPanel px={0}>
                <VStack spacing={6} align="stretch">
                  <Text color="gray.700" fontSize={{ base: 'md', md: 'lg' }} fontWeight="medium">
                    Gestion des utilisateurs
                  </Text>

                  {isLoadingUsers ? (
                    <Flex justify="center" py={10}>
                      <Spinner size="xl" color="gray.500" />
                    </Flex>
                  ) : users.length === 0 ? (
                    <Alert status="info" borderRadius="md">
                      <AlertIcon />
                      Aucun utilisateur trouvé.
                    </Alert>
                  ) : (
                    <>
                      {/* Version Desktop - Tableau */}
                      <Box bg="white" borderRadius="lg" boxShadow="sm" overflow="hidden" display={{ base: 'none', md: 'block' }}>
                        <Box overflowX="auto" className="table-container">
                          <Table variant="simple">
                            <Thead bg="gray.100">
                              <Tr>
                                <Th color="gray.700" fontWeight="bold">Email</Th>
                                <Th color="gray.700" fontWeight="bold">Nom d'utilisateur</Th>
                                <Th color="gray.700" fontWeight="bold">Admin</Th>
                                <Th color="gray.700" fontWeight="bold">Actif</Th>
                                <Th color="gray.700" fontWeight="bold">Actions</Th>
                              </Tr>
                            </Thead>
                            <Tbody>
                              {users.map((user) => (
                                <Tr key={user.id} _hover={{ bg: 'gray.50' }}>
                                  <Td data-label="Email">{user.email}</Td>
                                  <Td fontWeight="medium" data-label="Nom d'utilisateur">{user.username}</Td>
                                  <Td data-label="Admin">
                                    <Badge colorScheme={user.is_admin ? 'gray' : 'gray'}>
                                      {user.is_admin ? 'Admin' : 'Utilisateur'}
                                    </Badge>
                                  </Td>
                                  <Td>
                                    <Badge colorScheme={user.is_active !== false ? 'gray' : 'gray'}>
                                      {user.is_active !== false ? 'Actif' : 'Inactif'}
                                    </Badge>
                                  </Td>
                                  <Td>
                                    <HStack spacing={2}>
                                      <Tooltip label={user.is_admin ? 'Rétrograder' : 'Promouvoir admin'}>
                                        <IconButton
                                          icon={user.is_admin ? <FiShield /> : <FiUserCheck />}
                                          aria-label={user.is_admin ? 'Rétrograder' : 'Promouvoir admin'}
                                          size="sm"
                                          colorScheme={user.is_admin ? 'gray' : 'gray'}
                                          variant="ghost"
                                          onClick={() => handleToggleAdmin(user)}
                                          minH="48px"
                                          minW="48px"
                                          data-touch-target="true"
                                        />
                                      </Tooltip>
                                      <Tooltip label={user.is_active !== false ? 'Désactiver' : 'Activer'}>
                                        <IconButton
                                          icon={user.is_active !== false ? <FiUserX /> : <FiUserCheck />}
                                          aria-label={user.is_active !== false ? 'Désactiver' : 'Activer'}
                                          size="sm"
                                          colorScheme="gray"
                                          variant="ghost"
                                          onClick={() => handleToggleActive(user)}
                                          minH="48px"
                                          minW="48px"
                                          data-touch-target="true"
                                        />
                                      </Tooltip>
                                    </HStack>
                                  </Td>
                                </Tr>
                              ))}
                            </Tbody>
                          </Table>
                        </Box>
                      </Box>

                      {/* Version Mobile - Cards */}
                      <SimpleGrid columns={{ base: 1, md: 0 }} spacing={4} display={{ base: 'grid', md: 'none' }}>
                        {users.map((user) => (
                          <Card key={user.id} bg="white" borderRadius="lg" boxShadow="sm">
                            <CardBody p={{ base: 4, md: 6 }}>
                              <VStack spacing={4} align="stretch">
                                <Box>
                                  <Heading size="sm" color="gray.800" mb={1} fontWeight="bold">
                                    {user.username}
                                  </Heading>
                                  <Text fontSize={{ base: 'xs', md: 'sm' }} color="gray.600">
                                    {user.email}
                                  </Text>
                                </Box>
                                
                                <HStack spacing={2} flexWrap="wrap">
                                  <Badge colorScheme={user.is_admin ? 'purple' : 'gray'} fontSize={{ base: 'xs', md: 'sm' }}>
                                    {user.is_admin ? 'Admin' : 'Utilisateur'}
                                  </Badge>
                                  <Badge colorScheme={user.is_active !== false ? 'green' : 'red'} fontSize={{ base: 'xs', md: 'sm' }}>
                                    {user.is_active !== false ? 'Actif' : 'Inactif'}
                                  </Badge>
                                </HStack>

                                <Divider />

                                <HStack spacing={2} justify="flex-end" flexWrap="wrap">
                                  <Tooltip label={user.is_admin ? 'Rétrograder' : 'Promouvoir admin'}>
                                    <IconButton
                                      icon={user.is_admin ? <FiShield /> : <FiUserCheck />}
                                      aria-label={user.is_admin ? 'Rétrograder' : 'Promouvoir admin'}
                                      size={{ base: 'md', md: 'sm' }}
                                      colorScheme={user.is_admin ? 'purple' : 'gray'}
                                      variant="ghost"
                                      onClick={() => handleToggleAdmin(user)}
                                      minH="48px"
                                      minW="48px"
                                      data-touch-target="true"
                                    />
                                  </Tooltip>
                                  <Tooltip label={user.is_active !== false ? 'Désactiver' : 'Activer'}>
                                    <IconButton
                                      icon={user.is_active !== false ? <FiUserX /> : <FiUserCheck />}
                                      aria-label={user.is_active !== false ? 'Désactiver' : 'Activer'}
                                      size={{ base: 'md', md: 'sm' }}
                                      colorScheme={user.is_active !== false ? 'red' : 'green'}
                                      variant="ghost"
                                      onClick={() => handleToggleActive(user)}
                                      minH="48px"
                                      minW="48px"
                                      data-touch-target="true"
                                    />
                                  </Tooltip>
                                </HStack>
                              </VStack>
                            </CardBody>
                          </Card>
                        ))}
                      </SimpleGrid>
                    </>
                  )}
                </VStack>
              </TabPanel>

              {/* Panel Statistiques */}
              <TabPanel px={0}>
                <VStack spacing={6} align="stretch">
                  <Text color="gray.700" fontSize={{ base: 'md', md: 'lg' }} fontWeight="medium">
                    Statistiques de la plateforme
                  </Text>

                  {isLoadingStats ? (
                    <Flex justify="center" py={10}>
                      <Spinner size="xl" color="gray.500" />
                    </Flex>
                  ) : stats ? (
                    <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
                      <Stat bg="white" p={6} borderRadius="lg" boxShadow="sm">
                        <StatLabel>Utilisateurs totaux</StatLabel>
                        <StatNumber color="gray.600">{stats.total_users}</StatNumber>
                        <StatHelpText>{stats.active_users} actifs</StatHelpText>
                      </Stat>
                      <Stat bg="white" p={6} borderRadius="lg" boxShadow="sm">
                        <StatLabel>Administrateurs</StatLabel>
                        <StatNumber color="gray.600">{stats.total_admins}</StatNumber>
                      </Stat>
                      <Stat bg="white" p={6} borderRadius="lg" boxShadow="sm">
                        <StatLabel>Modules</StatLabel>
                        <StatNumber color="blue.500">{stats.total_modules}</StatNumber>
                      </Stat>
                      <Stat bg="white" p={6} borderRadius="lg" boxShadow="sm">
                        <StatLabel>Progression</StatLabel>
                        <StatNumber color="gray.600">{stats.total_progress}</StatNumber>
                      </Stat>
                      <Stat bg="white" p={6} borderRadius="lg" boxShadow="sm">
                        <StatLabel>Messages de support</StatLabel>
                        <StatNumber color="gray.600">{stats.total_support_messages}</StatNumber>
                      </Stat>
                    </SimpleGrid>
                  ) : (
                    <Alert status="warning" borderRadius="md">
                      <AlertIcon />
                      Impossible de charger les statistiques
                    </Alert>
                  )}
                </VStack>
              </TabPanel>

              {/* Panel Messages de Support */}
              <TabPanel px={0}>
                <VStack spacing={6} align="stretch">
                  <Flex justify="space-between" align="center" flexWrap="wrap" gap={4}>
                    <Text color="gray.700" fontSize={{ base: 'md', md: 'lg' }} fontWeight="medium">
                      Messages de support
                    </Text>
                    <VStack spacing={2} align={{ base: 'stretch', md: 'flex-end' }} w={{ base: 'full', md: 'auto' }}>
                      <HStack spacing={2} w={{ base: 'full', md: 'auto' }}>
                        <Switch
                          isChecked={showUnreadOnly}
                          onChange={(e) => setShowUnreadOnly(e.target.checked)}
                          colorScheme="blue"
                          size={{ base: 'md', md: 'sm' }}
                        />
                        <Text fontSize={{ base: 'xs', md: 'sm' }} color="gray.600">
                          Non lus uniquement
                        </Text>
                      </HStack>
                      <Button
                        leftIcon={<FiRefreshCw />}
                        size={{ base: 'sm', md: 'sm' }}
                        variant="outline"
                        colorScheme="gray"
                        onClick={loadSupportMessages}
                        minH="48px"
                        w={{ base: 'full', md: 'auto' }}
                        data-touch-target="true"
                      >
                        Actualiser
                      </Button>
                    </VStack>
                  </Flex>

                  {isLoadingMessages ? (
                    <Flex justify="center" py={10}>
                      <Spinner size="xl" color="gray.500" />
                    </Flex>
                  ) : supportMessages.length === 0 ? (
                    <Alert status="info" borderRadius="md">
                      <AlertIcon />
                      Aucun message de support trouvé.
                    </Alert>
                  ) : (
                    <VStack spacing={4} align="stretch">
                      {supportMessages.map((msg) => (
                        <Box
                          key={msg.id}
                          bg="white"
                          borderRadius="lg"
                          boxShadow="sm"
                          p={6}
                          borderLeft="4px solid"
                          borderLeftColor={msg.read ? 'gray.300' : 'blue.500'}
                        >
                          <VStack spacing={4} align="stretch">
                            <Flex justify="space-between" align="start">
                              <VStack align="start" spacing={2}>
                                <HStack spacing={3}>
                                  <Heading size="sm" color="gray.800">
                                    {msg.subject}
                                  </Heading>
                                  <Badge colorScheme="blue" variant="subtle">
                                    {getSupportTypeLabel(msg.support_type)}
                                  </Badge>
                                  {!msg.read && (
                                    <Badge colorScheme="red" borderRadius="full" fontSize="xs">
                                      Non lu
                                    </Badge>
                                  )}
                                  {msg.responded && (
                                    <Badge colorScheme="green" borderRadius="full" fontSize="xs">
                                      Répondu
                                    </Badge>
                                  )}
                                </HStack>
                                <HStack spacing={4} fontSize="sm" color="gray.600">
                                  <HStack spacing={1}>
                                    <FiMail />
                                    <Text>{msg.email}</Text>
                                  </HStack>
                                  {msg.phone && (
                                    <HStack spacing={1}>
                                      <FiPhone />
                                      <Text>{msg.phone}</Text>
                                    </HStack>
                                  )}
                                  <HStack spacing={1}>
                                    <FiClock />
                                    <Text>{formatDate(msg.created_at)}</Text>
                                  </HStack>
                                </HStack>
                                <Text fontWeight="medium" color="gray.700">
                                  De: {msg.name}
                                </Text>
                              </VStack>
                              <HStack spacing={2}>
                                {!msg.read && (
                                  <Tooltip label="Marquer comme lu">
                                    <IconButton
                                      icon={<FiCheck />}
                                      aria-label="Marquer comme lu"
                                      size="sm"
                                      colorScheme="blue"
                                      variant="ghost"
                                      onClick={() => markAsRead(msg.id)}
                                    />
                                  </Tooltip>
                                )}
                                {!msg.responded && (
                                  <Tooltip label="Marquer comme répondu">
                                    <IconButton
                                      icon={<FiMail />}
                                      aria-label="Marquer comme répondu"
                                      size="sm"
                                      colorScheme="green"
                                      variant="ghost"
                                      onClick={() => markAsResponded(msg.id)}
                                    />
                                  </Tooltip>
                                )}
                              </HStack>
                            </Flex>
                            <Divider />
                            <Box
                              bg="gray.50"
                              p={4}
                              borderRadius="md"
                              border="1px solid"
                              borderColor="gray.200"
                            >
                              <Text color="gray.800" whiteSpace="pre-wrap">
                                {msg.message}
                              </Text>
                            </Box>
                          </VStack>
                        </Box>
                      ))}
                    </VStack>
                  )}
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>

          {/* Modal de création/édition de module */}
          <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
            <ModalOverlay bg="blackAlpha.600" backdropFilter="blur(4px)" />
            <ModalContent bg="white" borderRadius="lg" maxH="90vh">
              <ModalHeader color="gray.800" fontWeight="bold">
                {editingModule ? 'Modifier le module' : 'Nouveau module'}
              </ModalHeader>
              <ModalCloseButton />
              <ModalBody pb={6}>
                {editingModule ? (
                  <Tabs>
                    <TabList>
                      <Tab>Informations</Tab>
                      <Tab>Ressources</Tab>
                    </TabList>
                    <TabPanels>
                      <TabPanel px={0}>
                        <VStack spacing={4} align="stretch">
                  <FormControl isRequired>
                    <FormLabel color="gray.700" fontWeight="medium">Titre</FormLabel>
                    <Input
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      placeholder="Ex: Introduction à la physique quantique"
                      bg="white"
                      borderColor="gray.300"
                      _hover={{ borderColor: 'gray.400' }}
                      _focus={{ borderColor: 'gray.500', boxShadow: '0 0 0 1px rgba(128, 128, 128, 0.3)' }}
                    />
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel color="gray.700" fontWeight="medium">Description</FormLabel>
                    <Textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="Description du module..."
                      rows={4}
                      bg="white"
                      borderColor="gray.300"
                      _hover={{ borderColor: 'gray.400' }}
                      _focus={{ borderColor: 'gray.500', boxShadow: '0 0 0 1px rgba(128, 128, 128, 0.3)' }}
                    />
                  </FormControl>

                  <HStack spacing={4}>
                    <FormControl isRequired>
                      <FormLabel color="gray.700" fontWeight="medium">Matière</FormLabel>
                      <Select
                        value={formData.subject}
                        onChange={(e) => setFormData({ ...formData, subject: e.target.value as Subject })}
                        placeholder="Sélectionner une matière"
                        bg="white"
                        borderColor="gray.300"
                        _hover={{ borderColor: 'gray.400' }}
                        _focus={{ borderColor: 'gray.500', boxShadow: '0 0 0 1px rgba(128, 128, 128, 0.3)' }}
                      >
                        {SUBJECTS.map((subject) => (
                          <option key={subject} value={subject}>
                            {getSubjectLabel(subject)}
                          </option>
                        ))}
                      </Select>
                    </FormControl>

                    <FormControl isRequired>
                      <FormLabel color="gray.700" fontWeight="medium">Difficulté</FormLabel>
                      <Select
                        value={formData.difficulty}
                        onChange={(e) => setFormData({ ...formData, difficulty: e.target.value as Difficulty })}
                        placeholder="Sélectionner une difficulté"
                        bg="white"
                        borderColor="gray.300"
                        _hover={{ borderColor: 'gray.400' }}
                        _focus={{ borderColor: 'gray.500', boxShadow: '0 0 0 1px rgba(128, 128, 128, 0.3)' }}
                      >
                        {DIFFICULTIES.map((difficulty) => (
                          <option key={difficulty} value={difficulty}>
                            {getDifficultyLabel(difficulty)}
                          </option>
                        ))}
                      </Select>
                    </FormControl>
                  </HStack>

                  <FormControl isRequired>
                    <FormLabel color="gray.700" fontWeight="medium">Temps estimé (minutes)</FormLabel>
                    <NumberInput
                      value={formData.estimated_time}
                      onChange={(_, value) => setFormData({ ...formData, estimated_time: value || 30 })}
                      min={1}
                      max={1000}
                    >
                      <NumberInputField
                        bg="white"
                        borderColor="gray.300"
                        _hover={{ borderColor: 'gray.400' }}
                        _focus={{ borderColor: 'gray.500', boxShadow: '0 0 0 1px rgba(128, 128, 128, 0.3)' }}
                      />
                      <NumberInputStepper>
                        <NumberIncrementStepper />
                        <NumberDecrementStepper />
                      </NumberInputStepper>
                    </NumberInput>
                  </FormControl>

                  <FormControl isRequired>
                    <FormLabel color="gray.700" fontWeight="medium">
                      Objectifs d'apprentissage <Text as="span" color="red.500">*</Text>
                      <Text fontSize="xs" color="gray.500" fontWeight="normal" ml={2}>
                        (Au moins 1 objectif de 5 caractères minimum)
                      </Text>
                    </FormLabel>
                    <VStack spacing={2} align="stretch">
                      {formData.learning_objectives.map((objective, index) => {
                        const isValid = objective.trim().length >= 5
                        const isEmpty = objective.trim() === ''
                        return (
                          <HStack key={index}>
                            <Input
                              value={objective}
                              onChange={(e) => updateLearningObjective(index, e.target.value)}
                              placeholder={`Objectif ${index + 1} (minimum 5 caractères)...`}
                              bg="white"
                              borderColor={isEmpty ? "gray.300" : (isValid ? "green.300" : "orange.300")}
                              _hover={{ borderColor: isEmpty ? 'gray.400' : (isValid ? 'green.400' : 'orange.400') }}
                              _focus={{ 
                                borderColor: isValid ? 'green.500' : 'orange.500', 
                                boxShadow: `0 0 0 1px ${isValid ? 'rgba(34, 197, 94, 0.3)' : 'rgba(251, 146, 60, 0.3)'}` 
                              }}
                            />
                            {formData.learning_objectives.length > 1 && (
                              <IconButton
                                icon={<FiX />}
                                aria-label="Supprimer"
                                size="sm"
                                colorScheme="gray"
                                variant="ghost"
                                onClick={() => removeLearningObjective(index)}
                              />
                            )}
                          </HStack>
                        )
                      })}
                      <Button
                        leftIcon={<FiPlus />}
                        size="sm"
                        variant="outline"
                        colorScheme="gray"
                        onClick={addLearningObjective}
                      >
                        Ajouter un objectif
                      </Button>
                    </VStack>
                  </FormControl>

                  {/* Gestion des leçons pour module existant */}
                  <FormControl>
                    <FormLabel color="gray.700" fontWeight="medium">Leçons du module</FormLabel>
                    <VStack spacing={4} align="stretch" mt={2}>
                      {(formData.content?.lessons || []).map((lesson, lessonIndex) => (
                        <Box
                          key={lessonIndex}
                          p={4}
                          border="1px solid"
                          borderColor="gray.300"
                          borderRadius="md"
                          bg="gray.50"
                        >
                          <VStack spacing={3} align="stretch">
                            <HStack justify="space-between" align="center">
                              <Text fontWeight="bold" color="gray.700">
                                Leçon {lessonIndex + 1}
                              </Text>
                              {(formData.content?.lessons || []).length > 0 && (
                                <IconButton
                                  icon={<FiTrash2 />}
                                  aria-label="Supprimer la leçon"
                                  size="sm"
                                  colorScheme="red"
                                  variant="ghost"
                                  onClick={() => removeLesson(lessonIndex)}
                                />
                              )}
                            </HStack>

                            <FormControl>
                              <FormLabel fontSize="sm" color="gray.600">Titre de la leçon *</FormLabel>
                              <Input
                                value={lesson.title || ''}
                                onChange={(e) => updateLesson(lessonIndex, 'title', e.target.value)}
                                placeholder="Ex: Introduction à l'apprentissage supervisé"
                                bg="white"
                                borderColor="gray.300"
                                size="sm"
                              />
                            </FormControl>

                            <FormControl>
                              <FormLabel fontSize="sm" color="gray.600">Résumé/Description de la leçon</FormLabel>
                              <Textarea
                                value={lesson.summary || ''}
                                onChange={(e) => updateLesson(lessonIndex, 'summary', e.target.value)}
                                placeholder="Brève description de ce que couvre cette leçon..."
                                rows={3}
                                bg="white"
                                borderColor="gray.300"
                                size="sm"
                              />
                              <Text fontSize="xs" color="gray.500" mt={1}>
                                💡 Le contenu détaillé de la leçon provient des ressources (PDF, Word, PPT, Vidéo, Audio) ajoutées dans l'onglet "Ressources"
                              </Text>
                            </FormControl>
                          </VStack>
                        </Box>
                      ))}

                      <Button
                        leftIcon={<FiPlus />}
                        size="sm"
                        variant="outline"
                        colorScheme="blue"
                        onClick={addLesson}
                      >
                        Ajouter une leçon
                      </Button>
                    </VStack>
                  </FormControl>

                          <HStack spacing={4} pt={4}>
                            <Button
                              leftIcon={<FiSave />}
                              colorScheme="gray"
                              bgGradient="gradient.primary"
                              _hover={{ bgGradient: 'gradient.secondary' }}
                              onClick={handleSubmit}
                              isLoading={isSubmitting}
                              flex={1}
                            >
                              Enregistrer
                            </Button>
                            <Button
                              leftIcon={<FiX />}
                              variant="outline"
                              colorScheme="gray"
                              onClick={onClose}
                              flex={1}
                            >
                              Annuler
                            </Button>
                          </HStack>
                        </VStack>
                      </TabPanel>
                      <TabPanel px={0}>
                        <ResourceManager 
                          moduleId={editingModule.id} 
                          moduleTitle={editingModule.title}
                        />
                      </TabPanel>
                    </TabPanels>
                  </Tabs>
                ) : (
                  <VStack spacing={4} align="stretch">
                    <FormControl isRequired>
                      <FormLabel color="gray.700" fontWeight="medium">Titre</FormLabel>
                      <Input
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        placeholder="Ex: Introduction à la physique quantique"
                        bg="white"
                        borderColor="gray.300"
                        _hover={{ borderColor: 'gray.400' }}
                        _focus={{ borderColor: 'gray.500', boxShadow: '0 0 0 1px rgba(128, 128, 128, 0.3)' }}
                      />
                    </FormControl>

                    <FormControl isRequired>
                      <FormLabel color="gray.700" fontWeight="medium">Description</FormLabel>
                      <Textarea
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        placeholder="Description du module..."
                        rows={4}
                        bg="white"
                        borderColor="gray.300"
                        _hover={{ borderColor: 'gray.400' }}
                        _focus={{ borderColor: 'gray.500', boxShadow: '0 0 0 1px rgba(128, 128, 128, 0.3)' }}
                      />
                    </FormControl>

                    <HStack spacing={4}>
                      <FormControl isRequired>
                        <FormLabel color="gray.700" fontWeight="medium">Matière</FormLabel>
                        <Select
                          value={formData.subject || ''}
                          onChange={(e) => setFormData({ ...formData, subject: e.target.value as Subject })}
                          placeholder="Sélectionner une matière"
                          bg="white"
                          borderColor="gray.300"
                          _hover={{ borderColor: 'gray.400' }}
                          _focus={{ borderColor: 'gray.500', boxShadow: '0 0 0 1px rgba(128, 128, 128, 0.3)' }}
                        >
                          {SUBJECTS.map((subject) => (
                            <option key={subject} value={subject}>
                              {getSubjectLabel(subject)}
                            </option>
                          ))}
                        </Select>
                      </FormControl>

                      <FormControl isRequired>
                        <FormLabel color="gray.700" fontWeight="medium">Difficulté</FormLabel>
                        <Select
                          value={formData.difficulty || ''}
                          onChange={(e) => setFormData({ ...formData, difficulty: e.target.value as Difficulty })}
                          placeholder="Sélectionner une difficulté"
                          bg="white"
                          borderColor="gray.300"
                          _hover={{ borderColor: 'gray.400' }}
                          _focus={{ borderColor: 'gray.500', boxShadow: '0 0 0 1px rgba(128, 128, 128, 0.3)' }}
                        >
                          {DIFFICULTIES.map((difficulty) => (
                            <option key={difficulty} value={difficulty}>
                              {getDifficultyLabel(difficulty)}
                            </option>
                          ))}
                        </Select>
                      </FormControl>
                    </HStack>

                    <FormControl isRequired>
                      <FormLabel color="gray.700" fontWeight="medium">Temps estimé (minutes)</FormLabel>
                      <NumberInput
                        value={formData.estimated_time}
                        onChange={(_, value) => setFormData({ ...formData, estimated_time: value || 30 })}
                        min={1}
                        max={1000}
                      >
                        <NumberInputField
                          bg="white"
                          borderColor="gray.300"
                          _hover={{ borderColor: 'gray.400' }}
                          _focus={{ borderColor: 'gray.500', boxShadow: '0 0 0 1px rgba(128, 128, 128, 0.3)' }}
                        />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>

                    <FormControl isRequired>
                      <FormLabel color="gray.700" fontWeight="medium">
                        Objectifs d'apprentissage <Text as="span" color="red.500">*</Text>
                        <Text fontSize="xs" color="gray.500" fontWeight="normal" ml={2}>
                          (Au moins 1 objectif de 5 caractères minimum)
                        </Text>
                      </FormLabel>
                      <VStack spacing={2} align="stretch">
                        {formData.learning_objectives.map((objective, index) => {
                          const isValid = objective.trim().length >= 5
                          const isEmpty = objective.trim() === ''
                          return (
                            <HStack key={index}>
                              <Input
                                value={objective}
                                onChange={(e) => updateLearningObjective(index, e.target.value)}
                                placeholder={`Objectif ${index + 1} (minimum 5 caractères)...`}
                                bg="white"
                                borderColor={isEmpty ? "gray.300" : (isValid ? "green.300" : "orange.300")}
                                _hover={{ borderColor: isEmpty ? 'gray.400' : (isValid ? 'green.400' : 'orange.400') }}
                                _focus={{ 
                                  borderColor: isValid ? 'green.500' : 'orange.500', 
                                  boxShadow: `0 0 0 1px ${isValid ? 'rgba(34, 197, 94, 0.3)' : 'rgba(251, 146, 60, 0.3)'}` 
                                }}
                              />
                              {formData.learning_objectives.length > 1 && (
                                <IconButton
                                  icon={<FiX />}
                                  aria-label="Supprimer"
                                  size="sm"
                                  colorScheme="gray"
                                  variant="ghost"
                                  onClick={() => removeLearningObjective(index)}
                                />
                              )}
                            </HStack>
                          )
                        })}
                        <Button
                          leftIcon={<FiPlus />}
                          size="sm"
                          variant="outline"
                          colorScheme="gray"
                          onClick={addLearningObjective}
                        >
                          Ajouter un objectif
                        </Button>
                      </VStack>
                    </FormControl>

                    {/* Gestion des leçons pour nouveau module */}
                    <FormControl>
                      <FormLabel color="gray.700" fontWeight="medium">Leçons du module</FormLabel>
                      <VStack spacing={4} align="stretch" mt={2}>
                        {(formData.content?.lessons || []).map((lesson, lessonIndex) => (
                          <Box
                            key={lessonIndex}
                            p={4}
                            border="1px solid"
                            borderColor="gray.300"
                            borderRadius="md"
                            bg="gray.50"
                          >
                            <VStack spacing={3} align="stretch">
                              <HStack justify="space-between" align="center">
                                <Text fontWeight="bold" color="gray.700">
                                  Leçon {lessonIndex + 1}
                                </Text>
                                {(formData.content?.lessons || []).length > 0 && (
                                  <IconButton
                                    icon={<FiTrash2 />}
                                    aria-label="Supprimer la leçon"
                                    size="sm"
                                    colorScheme="red"
                                    variant="ghost"
                                    onClick={() => removeLesson(lessonIndex)}
                                  />
                                )}
                              </HStack>

                              <FormControl>
                                <FormLabel fontSize="sm" color="gray.600">Titre de la leçon *</FormLabel>
                                <Input
                                  value={lesson.title || ''}
                                  onChange={(e) => updateLesson(lessonIndex, 'title', e.target.value)}
                                  placeholder="Ex: Introduction à l'apprentissage supervisé"
                                  bg="white"
                                  borderColor="gray.300"
                                  size="sm"
                                />
                              </FormControl>

                              <FormControl>
                                <FormLabel fontSize="sm" color="gray.600">Résumé/Description de la leçon</FormLabel>
                                <Textarea
                                  value={lesson.summary || ''}
                                  onChange={(e) => updateLesson(lessonIndex, 'summary', e.target.value)}
                                  placeholder="Brève description de ce que couvre cette leçon..."
                                  rows={3}
                                  bg="white"
                                  borderColor="gray.300"
                                  size="sm"
                                />
                                <Text fontSize="xs" color="gray.500" mt={1}>
                                  💡 Le contenu détaillé de la leçon provient des ressources (PDF, Word, PPT, Vidéo, Audio) ajoutées dans l'onglet "Ressources"
                                </Text>
                              </FormControl>
                            </VStack>
                          </Box>
                        ))}

                        <Button
                          leftIcon={<FiPlus />}
                          size="sm"
                          variant="outline"
                          colorScheme="blue"
                          onClick={addLesson}
                        >
                          Ajouter une leçon
                        </Button>
                      </VStack>
                    </FormControl>

                    <HStack spacing={4} pt={4}>
                      <Button
                        leftIcon={<FiSave />}
                        colorScheme="gray"
                        bgGradient="gradient.primary"
                        _hover={{ bgGradient: 'gradient.secondary' }}
                        onClick={handleSubmit}
                        isLoading={isSubmitting}
                        flex={1}
                      >
                        Créer
                      </Button>
                      <Button
                        leftIcon={<FiX />}
                        variant="outline"
                        colorScheme="gray"
                        onClick={onClose}
                        flex={1}
                      >
                        Annuler
                      </Button>
                    </HStack>
                  </VStack>
                )}
              </ModalBody>
            </ModalContent>
          </Modal>
        </VStack>
      </Container>
    </Box>
  )
}

export default Admin
