import React, { useState } from 'react'
import {
  Box,
  Container,
  Heading,
  VStack,
  FormControl,
  FormLabel,
  Select,
  Textarea,
  Button,
  RadioGroup,
  Radio,
  Stack,
  Text,
  Alert,
  AlertIcon,
  useToast,
  Spinner,
  Center,
} from '@chakra-ui/react'
import { useTranslation } from 'react-i18next'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import api from '../services/api'
import { useNotification } from '../components/NotificationProvider'
import { logger } from '../utils/logger'

type FeedbackType = 'ai_response_quality' | 'bug_report' | 'feature_request' | 'general_comment'

interface FeedbackFormData {
  feedback_type: FeedbackType
  rating: number | null
  response: string
  comment: string
}

const Feedback = () => {
  const { t } = useTranslation()
  const { showNotification } = useNotification()
  const toast = useToast()
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState<FeedbackFormData>({
    feedback_type: 'ai_response_quality',
    rating: null,
    response: '',
    comment: '',
  })

  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Récupérer les feedbacks de l'utilisateur
  const { data: myFeedback, isLoading: isLoadingFeedback } = useQuery(
    ['my-feedback'],
    async () => {
      const response = await api.get('/feedback/my-feedback')
      return response.data
    },
    {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  )

  // Mutation pour créer un feedback
  const createFeedbackMutation = useMutation(
    async (feedbackData: FeedbackFormData) => {
      const response = await api.post('/feedback/', feedbackData)
      return response.data
    },
    {
      onSuccess: () => {
        showNotification('Merci pour votre feedback !', 'success')
        setFormData({
          feedback_type: 'ai_response_quality',
          rating: null,
          response: '',
          comment: '',
        })
        setErrors({})
        queryClient.invalidateQueries(['my-feedback'])
      },
      onError: (err: any) => {
        const errorMessage = err.response?.data?.detail || 'Erreur lors de l\'envoi du feedback'
        showNotification(errorMessage, 'error')
        logger.error('Erreur lors de l\'envoi du feedback:', err)
      },
    }
  )

  const handleChange = (field: keyof FeedbackFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    // Effacer l'erreur pour ce champ
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.feedback_type) {
      newErrors.feedback_type = 'Veuillez sélectionner un type de feedback'
    }

    if (formData.feedback_type === 'ai_response_quality' && !formData.rating) {
      newErrors.rating = 'Veuillez donner une note'
    }

    if (formData.feedback_type === 'ai_response_quality' && !formData.response) {
      newErrors.response = 'Veuillez indiquer la réponse IA concernée'
    }

    if (!formData.comment || formData.comment.trim().length < 10) {
      newErrors.comment = 'Veuillez fournir un commentaire d\'au moins 10 caractères'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      showNotification('Veuillez corriger les erreurs dans le formulaire', 'error')
      return
    }

    setIsSubmitting(true)

    try {
      await createFeedbackMutation.mutateAsync(formData)
    } catch (err) {
      // L'erreur est déjà gérée par onError
    } finally {
      setIsSubmitting(false)
    }
  }

  const feedbackTypes = [
    { value: 'ai_response_quality', label: 'Qualité de la réponse IA' },
    { value: 'bug_report', label: 'Rapport de bug' },
    { value: 'feature_request', label: 'Demande de fonctionnalité' },
    { value: 'general_comment', label: 'Commentaire général' },
  ]

  return (
    <Box minH="calc(100vh - 80px)" py={{ base: 6, md: 8 }} bg="gray.50">
      <Container maxW="container.md">
        <VStack spacing={6} align="stretch">
          <Heading size="lg" textAlign="center">
            {t('feedback.title', 'Feedback')}
          </Heading>

          <Text textAlign="center" color="gray.600">
            {t('feedback.description', 'Votre avis nous aide à améliorer Kaïrox. Partagez vos commentaires, signalez des bugs ou suggérez de nouvelles fonctionnalités.')}
          </Text>

          <Box bg="white" p={{ base: 4, md: 6 }} borderRadius="lg" boxShadow="md">
            <form onSubmit={handleSubmit}>
              <VStack spacing={4} align="stretch">
                {/* Type de feedback */}
                <FormControl isRequired isInvalid={!!errors.feedback_type}>
                  <FormLabel fontSize={{ base: '16px', md: '14px' }}>
                    {t('feedback.type', 'Type de feedback')}
                  </FormLabel>
                  <Select
                    value={formData.feedback_type}
                    onChange={(e) => handleChange('feedback_type', e.target.value as FeedbackType)}
                    fontSize={{ base: '16px', md: '14px' }}
                    minH="48px"
                  >
                    {feedbackTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </Select>
                  {errors.feedback_type && (
                    <Text color="red.500" fontSize="sm" mt={1}>
                      {errors.feedback_type}
                    </Text>
                  )}
                </FormControl>

                {/* Note (uniquement pour ai_response_quality) */}
                {formData.feedback_type === 'ai_response_quality' && (
                  <FormControl isRequired isInvalid={!!errors.rating}>
                    <FormLabel fontSize={{ base: '16px', md: '14px' }}>
                      {t('feedback.rating', 'Note (1-5)')}
                    </FormLabel>
                    <RadioGroup
                      value={formData.rating?.toString() || ''}
                      onChange={(value) => handleChange('rating', parseInt(value))}
                    >
                      <Stack direction="row" spacing={4}>
                        {[1, 2, 3, 4, 5].map((rating) => (
                          <Radio key={rating} value={rating.toString()} size="lg">
                            {rating}
                          </Radio>
                        ))}
                      </Stack>
                    </RadioGroup>
                    {errors.rating && (
                      <Text color="red.500" fontSize="sm" mt={1}>
                        {errors.rating}
                      </Text>
                    )}
                  </FormControl>
                )}

                {/* Réponse IA concernée (uniquement pour ai_response_quality) */}
                {formData.feedback_type === 'ai_response_quality' && (
                  <FormControl isRequired isInvalid={!!errors.response}>
                    <FormLabel fontSize={{ base: '16px', md: '14px' }}>
                      {t('feedback.response', 'Réponse IA concernée')}
                    </FormLabel>
                    <Textarea
                      value={formData.response}
                      onChange={(e) => handleChange('response', e.target.value)}
                      placeholder={t('feedback.responsePlaceholder', 'Collez ici la réponse de l\'IA que vous souhaitez commenter')}
                      rows={3}
                      fontSize={{ base: '16px', md: '14px' }}
                      minH="48px"
                    />
                    {errors.response && (
                      <Text color="red.500" fontSize="sm" mt={1}>
                        {errors.response}
                      </Text>
                    )}
                  </FormControl>
                )}

                {/* Commentaire */}
                <FormControl isRequired isInvalid={!!errors.comment}>
                  <FormLabel fontSize={{ base: '16px', md: '14px' }}>
                    {t('feedback.comment', 'Commentaire')}
                  </FormLabel>
                  <Textarea
                    value={formData.comment}
                    onChange={(e) => handleChange('comment', e.target.value)}
                    placeholder={t('feedback.commentPlaceholder', 'Décrivez votre feedback en détail...')}
                    rows={5}
                    fontSize={{ base: '16px', md: '14px' }}
                    minH="48px"
                    maxLength={1000}
                  />
                  <Text fontSize="xs" color="gray.500" mt={1}>
                    {formData.comment.length}/1000 caractères
                  </Text>
                  {errors.comment && (
                    <Text color="red.500" fontSize="sm" mt={1}>
                      {errors.comment}
                    </Text>
                  )}
                </FormControl>

                {/* Erreur générale */}
                {errors.general && (
                  <Alert status="error">
                    <AlertIcon />
                    {errors.general}
                  </Alert>
                )}

                {/* Bouton de soumission */}
                <Button
                  type="submit"
                  colorScheme="blue"
                  size="lg"
                  isLoading={isSubmitting}
                  loadingText={t('feedback.submitting', 'Envoi en cours...')}
                  width="100%"
                  minH="48px"
                  fontSize={{ base: '16px', md: '14px' }}
                >
                  {t('feedback.submit', 'Envoyer le feedback')}
                </Button>
              </VStack>
            </form>
          </Box>

          {/* Mes feedbacks précédents */}
          <Box bg="white" p={{ base: 4, md: 6 }} borderRadius="lg" boxShadow="md">
            <Heading size="md" mb={4}>
              {t('feedback.myFeedback', 'Mes feedbacks précédents')}
            </Heading>
            {isLoadingFeedback ? (
              <Center py={8}>
                <Spinner size="lg" />
              </Center>
            ) : myFeedback && myFeedback.length > 0 ? (
              <VStack spacing={4} align="stretch">
                {myFeedback.map((feedback: any) => (
                  <Box key={feedback.id} p={4} borderWidth={1} borderRadius="md">
                    <Text fontWeight="bold" mb={2}>
                      {feedbackTypes.find((t) => t.value === feedback.feedback_type)?.label}
                    </Text>
                    {feedback.rating && (
                      <Text color="gray.600" mb={2}>
                        Note: {feedback.rating}/5
                      </Text>
                    )}
                    {feedback.comment && (
                      <Text mb={2}>{feedback.comment}</Text>
                    )}
                    <Text fontSize="sm" color="gray.500">
                      {new Date(feedback.created_at).toLocaleDateString('fr-FR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </Text>
                  </Box>
                ))}
              </VStack>
            ) : (
              <Text color="gray.500" textAlign="center" py={4}>
                {t('feedback.noFeedback', 'Aucun feedback soumis pour le moment.')}
              </Text>
            )}
          </Box>
        </VStack>
      </Container>
    </Box>
  )
}

export default Feedback
