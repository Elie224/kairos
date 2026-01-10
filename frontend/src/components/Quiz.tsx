import { useState, useRef, useEffect } from 'react'
import { Box, VStack, HStack, Button, Text, Card, CardBody, Radio, RadioGroup, Stack, Heading, Progress, Badge, Select, FormControl, FormLabel, Alert, AlertIcon, AlertTitle, AlertDescription } from '@chakra-ui/react'
import { useMutation, useQuery } from 'react-query'
import { useTranslation } from 'react-i18next'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import { useQueryClient } from 'react-query'

interface QuizProps {
  moduleId: string
  subject?: string
}

interface QuizQuestion {
  question: string
  options: string[]
  correct_answer: number
  explanation: string
}

interface QuizResponse {
  questions: QuizQuestion[]
  quiz_id: string
}

const Quiz = ({ moduleId }: QuizProps) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [quiz, setQuiz] = useState<QuizQuestion[]>([])
  const [answers, setAnswers] = useState<{ [key: number]: number }>({})
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [showResults, setShowResults] = useState(false)
  const [score, setScore] = useState(0)
  const [numQuestions, setNumQuestions] = useState(40)
  const [canTakeExam, setCanTakeExam] = useState(false)
  const [examPrerequisites, setExamPrerequisites] = useState<any>(null)
  const [quizId, setQuizId] = useState<string | null>(null)
  const [timeElapsed, setTimeElapsed] = useState(0)
  const queryClient = useQueryClient()
  const startTimeRef = useRef<number>(Date.now())
  const timerIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const generateQuizMutation = useMutation(
    async () => {
      // Utiliser le nouvel endpoint de quiz qui garantit un quiz unique par module
      const response = await api.post('/quiz/generate', {
        module_id: moduleId,
        num_questions: numQuestions,
      })
      return response.data as QuizResponse
    },
    {
      onSuccess: (data) => {
        setQuiz(data.questions)
        setAnswers({})
        setCurrentQuestion(0)
        setShowResults(false)
        setScore(0)
        setQuizId(data.quiz_id || null)
        setTimeElapsed(0)
        startTimeRef.current = Date.now()
        
        // Démarrer le timer
        if (timerIntervalRef.current) {
          clearInterval(timerIntervalRef.current)
        }
        timerIntervalRef.current = setInterval(() => {
          setTimeElapsed(Math.floor((Date.now() - startTimeRef.current) / 1000))
        }, 1000)
      },
    }
  )

  // Nettoyer le timer au démontage
  useEffect(() => {
    return () => {
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current)
      }
    }
  }, [])

  const handleAnswerChange = (value: string) => {
    setAnswers({
      ...answers,
      [currentQuestion]: parseInt(value),
    })
  }

  const handleNext = () => {
    if (currentQuestion < quiz.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    } else {
      calculateScore()
      setShowResults(true)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const calculateScore = async () => {
    // Arrêter le timer
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current)
      timerIntervalRef.current = null
    }
    
    let correct = 0
    quiz.forEach((q, index) => {
      if (answers[index] === q.correct_answer) {
        correct++
      }
    })
    const calculatedScore = (correct / quiz.length) * 100
    setScore(calculatedScore)
    
    // Sauvegarder la progression avec temps réel calculé
    const startTime = startTimeRef.current
    if (startTime) {
      const timeSpent = Math.max(1, Math.floor((Date.now() - startTime) / 1000)) // Minimum 1 seconde
      try {
        // Sauvegarder la progression
        await api.post('/progress/', {
          module_id: moduleId,
          completed: true,
          score: calculatedScore,
          time_spent: timeSpent,
        })
        queryClient.invalidateQueries('progress')
        
        // Sauvegarder la tentative de quiz si on a un quiz_id
        if (quizId) {
          try {
            await api.post('/quiz/attempt', {
              module_id: moduleId,
              quiz_id: quizId,
              answers: answers,
              score: calculatedScore,
              time_spent: timeSpent,
              num_questions: quiz.length,
              num_correct: correct,
            })
          } catch (error) {
            console.error('Erreur lors de la sauvegarde de la tentative de quiz:', error)
          }
        }
        
        // Vérifier les prérequis pour l'examen après avoir sauvegardé la progression
        if (moduleId) {
          checkExamPrerequisites(moduleId)
        }
      } catch (error) {
        console.error('Erreur lors de la sauvegarde de la progression:', error)
      }
    }
  }

  const checkExamPrerequisites = async (moduleId: string) => {
    try {
      const response = await api.get(`/exams/module/${moduleId}/prerequisites`)
      setExamPrerequisites(response.data)
      setCanTakeExam(response.data.can_take_exam || false)
    } catch (error) {
      console.error('Erreur lors de la vérification des prérequis:', error)
      setCanTakeExam(false)
    }
  }

  const handleTakeExam = () => {
    if (moduleId) {
      navigate(`/modules/${moduleId}/exam`)
    }
  }

  const handleRestart = () => {
    setAnswers({})
    setCurrentQuestion(0)
    setShowResults(false)
    setScore(0)
    setTimeElapsed(0)
    startTimeRef.current = Date.now()
    
    // Redémarrer le timer
    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current)
    }
    timerIntervalRef.current = setInterval(() => {
      setTimeElapsed(Math.floor((Date.now() - startTimeRef.current) / 1000))
    }, 1000)
  }

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  if (generateQuizMutation.isLoading) {
    return (
      <Card>
        <CardBody>
          <Text>{t('quiz.generating')}</Text>
        </CardBody>
      </Card>
    )
  }

  if (quiz.length === 0) {
    return (
      <Card>
        <CardBody>
          <VStack spacing={6}>
            <Heading size="md">{t('quiz.title')}</Heading>
            <Text textAlign="center" color="gray.600">
              {t('quiz.subtitle')}
            </Text>
            
            <VStack spacing={4} w="full" align="stretch">
              <FormControl>
                <FormLabel>{t('quiz.numQuestions') || 'Nombre de questions'}</FormLabel>
                <Select
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                >
                  <option value={10}>10 questions</option>
                  <option value={20}>20 questions</option>
                  <option value={30}>30 questions</option>
                  <option value={40}>40 questions</option>
                  <option value={50}>50 questions</option>
                </Select>
                <Text fontSize="xs" color="gray.500" mt={1}>
                  {t('quiz.uniqueQuiz') || 'Chaque module a son propre quiz unique qui ne change pas.'}
                </Text>
              </FormControl>
            </VStack>

            <Button
              colorScheme="gray"
              onClick={() => generateQuizMutation.mutate()}
              isLoading={generateQuizMutation.isLoading}
              size="lg"
              w="full"
            >
              {t('quiz.generate')}
            </Button>
          </VStack>
        </CardBody>
      </Card>
    )
  }

  if (showResults) {
    const correctAnswers = quiz.filter((q, index) => answers[index] === q.correct_answer).length
    
    return (
      <Card>
        <CardBody>
          <VStack spacing={6}>
            <Heading size="lg">{t('quiz.results')}</Heading>
            <Box w="full">
              <Progress value={score} colorScheme="gray" size="lg" />
              <Text mt={2} fontSize="2xl" fontWeight="bold" textAlign="center">
                {t('quiz.score', { score: score.toFixed(0) })}
              </Text>
            </Box>
            <Text fontSize="lg">
              {t('quiz.correctAnswers', { correct: correctAnswers, total: quiz.length })}
            </Text>

            {/* Afficher l'alerte pour passer l'examen si les prérequis sont satisfaits */}
            {canTakeExam && moduleId && (
              <Alert status="success" borderRadius="md">
                <AlertIcon />
                <Box flex="1">
                  <AlertTitle>Prêt pour l'examen !</AlertTitle>
                  <AlertDescription>
                    Vous avez complété le module et fait le quiz. Vous pouvez maintenant passer l'examen pour valider ce module.
                  </AlertDescription>
                </Box>
                <Button
                  colorScheme="green"
                  size="sm"
                  onClick={handleTakeExam}
                  ml={4}
                >
                  Passer l'examen
                </Button>
              </Alert>
            )}

            {examPrerequisites && !canTakeExam && moduleId && (
              <Alert status="info" borderRadius="md">
                <AlertIcon />
                <Box flex="1">
                  <AlertTitle>Continuez votre apprentissage</AlertTitle>
                  <AlertDescription>
                    {examPrerequisites.reason || 'Vous devez compléter le module et faire le quiz avant de pouvoir passer l\'examen.'}
                  </AlertDescription>
                </Box>
              </Alert>
            )}
            
            <VStack spacing={4} align="stretch" w="full">
              {quiz.map((question, index) => {
                const isCorrect = answers[index] === question.correct_answer
                return (
                  <Card key={index} bg={isCorrect ? 'green.50' : 'red.50'}>
                    <CardBody>
                      <VStack align="start" spacing={2}>
                        <HStack>
                          <Badge colorScheme="gray">
                            {isCorrect ? t('quiz.correct') : t('quiz.incorrect')}
                          </Badge>
                        </HStack>
                        <Text fontWeight="bold">{question.question}</Text>
                        <Text fontSize="sm" color="gray.600">
                          <strong>{t('quiz.yourAnswer')}:</strong> {question.options[answers[index] || -1] || t('quiz.notAnswered')}
                        </Text>
                        {!isCorrect && (
                          <Text fontSize="sm" color="green.600">
                            <strong>{t('quiz.correctAnswer')}:</strong> {question.options[question.correct_answer]}
                          </Text>
                        )}
                        <Text fontSize="sm" color="gray.700" fontStyle="italic">
                          {question.explanation}
                        </Text>
                      </VStack>
                    </CardBody>
                  </Card>
                )
              })}
            </VStack>

            <HStack spacing={4}>
              <Button onClick={handleRestart} variant="outline">
                {t('common.restart')}
              </Button>
              <Button onClick={() => generateQuizMutation.mutate()} colorScheme="brand">
                {t('quiz.newQuiz')}
              </Button>
            </HStack>
          </VStack>
        </CardBody>
      </Card>
    )
  }

  const currentQ = quiz[currentQuestion]
  const progress = ((currentQuestion + 1) / quiz.length) * 100

  return (
    <Card>
      <CardBody>
        <VStack spacing={6} align="stretch">
          <Box>
            <HStack justify="space-between" mb={2}>
              <Text fontSize="sm" color="gray.600">
                {t('quiz.question', { current: currentQuestion + 1, total: quiz.length })}
              </Text>
              <HStack spacing={4}>
                <Text fontSize="sm" color="gray.600">
                  ⏱️ {formatTime(timeElapsed)}
                </Text>
                <Text fontSize="sm" color="gray.600">
                  {Math.round(progress)}%
                </Text>
              </HStack>
            </HStack>
            <Progress value={progress} colorScheme="gray" size="sm" />
          </Box>

          <Heading size="md">{currentQ.question}</Heading>

          <RadioGroup
            value={answers[currentQuestion]?.toString() || ''}
            onChange={handleAnswerChange}
          >
            <Stack spacing={3}>
              {currentQ.options.map((option, index) => (
                <Radio key={index} value={index.toString()} size="lg">
                  <Text>{option}</Text>
                </Radio>
              ))}
            </Stack>
          </RadioGroup>

          <HStack justify="space-between">
            <Button
              onClick={handlePrevious}
              isDisabled={currentQuestion === 0}
              variant="outline"
            >
              {t('common.previous')}
            </Button>
            <Button
              onClick={handleNext}
              colorScheme="gray"
              isDisabled={answers[currentQuestion] === undefined}
            >
              {currentQuestion === quiz.length - 1 ? t('common.finish') : t('common.next')}
            </Button>
          </HStack>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default Quiz

