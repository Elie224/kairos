import { useState, useRef, useEffect } from 'react'
import { Box, VStack, HStack, Button, Text, Card, CardBody, Radio, RadioGroup, Stack, Heading, Progress, Badge, Alert, AlertIcon, AlertTitle, AlertDescription } from '@chakra-ui/react'
import { useMutation } from 'react-query'
import { useTranslation } from 'react-i18next'
import api from '../services/api'
import { useQueryClient } from 'react-query'

interface ExamProps {
  examId: string
  moduleId: string
}

interface ExamQuestion {
  question: string
  options: string[]
  correct_answer: number
  explanation: string
  points: number
}

interface Exam {
  id: string
  module_id: string
  questions: ExamQuestion[]
  num_questions: number
  passing_score: number
  time_limit: number
}

interface ExamAnswer {
  question_index: number
  answer: number
}

const Exam = ({ examId, moduleId }: ExamProps) => {
  const { t } = useTranslation()
  const [exam, setExam] = useState<Exam | null>(null)
  const [answers, setAnswers] = useState<{ [key: number]: number }>({})
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [showResults, setShowResults] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [attemptId, setAttemptId] = useState<string | null>(null)
  const queryClient = useQueryClient()
  const startTimeRef = useRef<number>(Date.now())
  const timerRef = useRef<number | null>(null)

  // Démarrer une tentative d'examen
  const startExamMutation = useMutation(
    async () => {
      const response = await api.post('/exams/start', {
        exam_id: examId,
      })
      return response.data
    },
    {
      onSuccess: (data) => {
        setAttemptId(data.id)
        if (exam) {
          setTimeRemaining(exam.time_limit * 60) // Convertir en secondes
          startTimeRef.current = Date.now()
        }
      },
    }
  )

  const handleStartExam = () => {
    if (exam) {
      startExamMutation.mutate()
    }
  }

  // Charger l'examen
  useEffect(() => {
    const loadExam = async () => {
      try {
        const response = await api.get(`/exams/module/${moduleId}`, {
          timeout: API_TIMEOUTS.STANDARD, // 15 secondes pour le chargement de l'examen
        })
        setExam(response.data)
      } catch (error: any) {
        console.error('Erreur lors du chargement de l\'examen:', error)
      }
    }
    if (moduleId) {
      loadExam()
    }
  }, [moduleId])

  // Timer pour le temps restant
  useEffect(() => {
    if (exam && attemptId && timeRemaining > 0 && !showResults) {
      timerRef.current = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            handleSubmit()
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [exam, attemptId, timeRemaining, showResults])

  const handleAnswerChange = (value: string) => {
    setAnswers({
      ...answers,
      [currentQuestion]: parseInt(value),
    })
  }

  const handleNext = () => {
    if (exam && currentQuestion < exam.questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleSubmit = async () => {
    if (!exam || !attemptId) return

    const timeSpent = Math.max(1, Math.floor((Date.now() - startTimeRef.current) / 1000))

    const submission = {
      exam_id: examId,
      answers: Object.keys(answers).map((key) => ({
        question_index: parseInt(key),
        answer: answers[parseInt(key)],
      })),
      time_spent: timeSpent,
    }

    try {
      const response = await api.post('/exams/submit', submission)
      setResult(response.data)
      setShowResults(true)
      queryClient.invalidateQueries('exam-attempts')
      queryClient.invalidateQueries('validations')
    } catch (error: any) {
      console.error('Erreur lors de la soumission:', error)
    }
  }

  if (!exam) {
    return (
      <Card>
        <CardBody>
          <Text>Chargement de l'examen...</Text>
        </CardBody>
      </Card>
    )
  }

  if (!attemptId && !showResults) {
    return (
      <Card>
        <CardBody>
          <VStack spacing={6}>
            <Heading size="md">Examen du module</Heading>
            <VStack spacing={4} align="stretch">
              <Text>
                <strong>Nombre de questions:</strong> {exam.num_questions}
              </Text>
              <Text>
                <strong>Score de passage:</strong> {exam.passing_score}%
              </Text>
              <Text>
                <strong>Temps limite:</strong> {exam.time_limit} minutes
              </Text>
            </VStack>
            <Button
              colorScheme="gray"
              onClick={handleStartExam}
              isLoading={startExamMutation.isLoading}
              size="lg"
              w="full"
            >
              Démarrer l'examen
            </Button>
          </VStack>
        </CardBody>
      </Card>
    )
  }

  if (showResults && result) {
    return (
      <Card>
        <CardBody>
          <VStack spacing={6}>
            <Heading size="lg">Résultats de l'examen</Heading>
            
            <Alert status={result.passed ? 'success' : 'error'} borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>
                  {result.passed ? 'Examen réussi !' : 'Examen échoué'}
                </AlertTitle>
                <AlertDescription>
                  Score: {result.percentage.toFixed(1)}% (Score minimum: {exam.passing_score}%)
                </AlertDescription>
              </Box>
            </Alert>

            {result.module_validated && (
              <Alert status="success" borderRadius="md">
                <AlertIcon />
                <AlertTitle>Module validé !</AlertTitle>
                <AlertDescription>
                  Félicitations ! Vous avez validé ce module.
                </AlertDescription>
              </Alert>
            )}

            <Box w="full">
              <Progress value={result.percentage} colorScheme={result.passed ? 'green' : 'red'} size="lg" />
              <Text mt={2} fontSize="2xl" fontWeight="bold" textAlign="center">
                {result.score.toFixed(1)} / {result.max_score.toFixed(1)}
              </Text>
            </Box>

            <VStack spacing={4} align="stretch" w="full">
              {exam.questions.map((question, index) => {
                const answer = answers[index]
                const isCorrect = answer === question.correct_answer
                return (
                  <Card key={index} bg={isCorrect ? 'green.50' : 'red.50'}>
                    <CardBody>
                      <VStack align="start" spacing={2}>
                        <HStack>
                          <Badge colorScheme={isCorrect ? 'green' : 'red'}>
                            {isCorrect ? 'Correct' : 'Incorrect'}
                          </Badge>
                          <Badge colorScheme="gray">{question.points} point(s)</Badge>
                        </HStack>
                        <Text fontWeight="bold">{question.question}</Text>
                        <Text fontSize="sm" color="gray.600">
                          <strong>Votre réponse:</strong> {answer !== undefined ? question.options[answer] : 'Non répondue'}
                        </Text>
                        {!isCorrect && (
                          <Text fontSize="sm" color="green.600">
                            <strong>Réponse correcte:</strong> {question.options[question.correct_answer]}
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
          </VStack>
        </CardBody>
      </Card>
    )
  }

  const currentQ = exam.questions[currentQuestion]
  const progress = ((currentQuestion + 1) / exam.questions.length) * 100
  const allAnswered = Object.keys(answers).length === exam.questions.length

  return (
    <Card>
      <CardBody>
        <VStack spacing={6} align="stretch">
          <HStack justify="space-between">
            <Badge colorScheme="red" fontSize="md" p={2}>
              Temps restant: {formatTime(timeRemaining)}
            </Badge>
            <Badge colorScheme="gray" fontSize="md" p={2}>
              Question {currentQuestion + 1} / {exam.questions.length}
            </Badge>
          </HStack>

          <Box>
            <HStack justify="space-between" mb={2}>
              <Text fontSize="sm" color="gray.600">
                Progression
              </Text>
              <Text fontSize="sm" color="gray.600">
                {Math.round(progress)}%
              </Text>
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
              Précédent
            </Button>
            <HStack>
              {currentQuestion < exam.questions.length - 1 ? (
                <Button
                  onClick={handleNext}
                  colorScheme="gray"
                  isDisabled={answers[currentQuestion] === undefined}
                >
                  Suivant
                </Button>
              ) : (
                <Button
                  onClick={handleSubmit}
                  colorScheme="green"
                  isDisabled={!allAnswered}
                >
                  Soumettre l'examen
                </Button>
              )}
            </HStack>
          </HStack>
        </VStack>
      </CardBody>
    </Card>
  )
}

export default Exam

