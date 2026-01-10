import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { RouteProp, useRoute } from '@react-navigation/native';
import { examService } from '../services/examService';
import { Exam, QuizQuestion } from '../types';
import Icon from 'react-native-vector-icons/MaterialIcons';

type ExamDetailScreenRouteProp = RouteProp<{ ExamDetail: { examId: string } }, 'ExamDetail'>;

const ExamDetailScreen = () => {
  const route = useRoute<ExamDetailScreenRouteProp>();
  const { examId } = route.params;
  const [exam, setExam] = useState<Exam | null>(null);
  const [loading, setLoading] = useState(true);
  const [started, setStarted] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({});
  const [timeRemaining, setTimeRemaining] = useState(0);

  useEffect(() => {
    loadExam();
  }, [examId]);

  useEffect(() => {
    if (started && exam && timeRemaining > 0) {
      const timer = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            handleSubmit();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
      return () => clearInterval(timer);
    }
  }, [started, exam, timeRemaining]);

  const loadExam = async () => {
    try {
      setLoading(true);
      const data = await examService.getById(examId);
      setExam(data);
    } catch (error) {
      console.error('Erreur lors du chargement de l\'examen:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async () => {
    try {
      await examService.startExam(examId);
      setStarted(true);
      setTimeRemaining(exam?.duration ? exam.duration * 60 : 0);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de démarrer l\'examen');
    }
  };

  const handleAnswer = (questionId: string, answer: string | string[]) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
  };

  const handleSubmit = async () => {
    try {
      const result = await examService.submitExam(examId, answers);
      Alert.alert(
        'Examen terminé',
        `Score: ${result.score}%\n${result.passed ? 'Réussi !' : 'Échoué'}`
      );
      setStarted(false);
    } catch (error) {
      Alert.alert('Erreur', 'Impossible de soumettre l\'examen');
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  if (!exam) {
    return (
      <View style={styles.centerContainer}>
        <Text>Examen non trouvé</Text>
      </View>
    );
  }

  if (!started) {
    return (
      <ScrollView style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>{exam.title}</Text>
          <Text style={styles.description}>{exam.description}</Text>
          <View style={styles.infoContainer}>
            <View style={styles.infoItem}>
              <Icon name="access-time" size={20} color="#666" />
              <Text style={styles.infoText}>Durée: {exam.duration} minutes</Text>
            </View>
            <View style={styles.infoItem}>
              <Icon name="quiz" size={20} color="#666" />
              <Text style={styles.infoText}>
                {exam.questions.length} questions
              </Text>
            </View>
            <View style={styles.infoItem}>
              <Icon name="check-circle" size={20} color="#666" />
              <Text style={styles.infoText}>
                Score minimum: {exam.passing_score}%
              </Text>
            </View>
          </View>
        </View>
        <View style={styles.actions}>
          <TouchableOpacity style={styles.startButton} onPress={handleStart}>
            <Text style={styles.startButtonText}>Commencer l'examen</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    );
  }

  const currentQuestion = exam.questions[currentQuestionIndex];

  return (
    <View style={styles.container}>
      <View style={styles.timerContainer}>
        <Icon name="access-time" size={20} color="#dc2626" />
        <Text style={styles.timerText}>
          Temps restant: {formatTime(timeRemaining)}
        </Text>
      </View>

      <ScrollView style={styles.questionContainer}>
        <View style={styles.questionHeader}>
          <Text style={styles.questionNumber}>
            Question {currentQuestionIndex + 1} / {exam.questions.length}
          </Text>
          <Text style={styles.questionText}>{currentQuestion.question}</Text>
        </View>

        {currentQuestion.type === 'multiple_choice' && (
          <View style={styles.optionsContainer}>
            {currentQuestion.options?.map((option, index) => (
              <TouchableOpacity
                key={index}
                style={[
                  styles.option,
                  answers[currentQuestion.id] === option && styles.optionSelected,
                ]}
                onPress={() => handleAnswer(currentQuestion.id, option)}
              >
                <Text style={styles.optionText}>{option}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {currentQuestion.type === 'true_false' && (
          <View style={styles.optionsContainer}>
            <TouchableOpacity
              style={[
                styles.option,
                answers[currentQuestion.id] === 'true' && styles.optionSelected,
              ]}
              onPress={() => handleAnswer(currentQuestion.id, 'true')}
            >
              <Text style={styles.optionText}>Vrai</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[
                styles.option,
                answers[currentQuestion.id] === 'false' && styles.optionSelected,
              ]}
              onPress={() => handleAnswer(currentQuestion.id, 'false')}
            >
              <Text style={styles.optionText}>Faux</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>

      <View style={styles.navigationContainer}>
        <TouchableOpacity
          style={[
            styles.navButton,
            currentQuestionIndex === 0 && styles.navButtonDisabled,
          ]}
          onPress={() =>
            setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))
          }
          disabled={currentQuestionIndex === 0}
        >
          <Text style={styles.navButtonText}>Précédent</Text>
        </TouchableOpacity>

        {currentQuestionIndex < exam.questions.length - 1 ? (
          <TouchableOpacity
            style={styles.navButton}
            onPress={() =>
              setCurrentQuestionIndex((prev) =>
                Math.min(exam.questions.length - 1, prev + 1)
              )
            }
          >
            <Text style={styles.navButtonText}>Suivant</Text>
          </TouchableOpacity>
        ) : (
          <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
            <Text style={styles.submitButtonText}>Terminer</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  description: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
  },
  infoContainer: {
    marginTop: 10,
  },
  infoItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  infoText: {
    marginLeft: 10,
    fontSize: 14,
    color: '#666',
  },
  actions: {
    padding: 20,
  },
  startButton: {
    backgroundColor: '#2563eb',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  startButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  timerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  timerText: {
    marginLeft: 10,
    fontSize: 16,
    fontWeight: 'bold',
    color: '#dc2626',
  },
  questionContainer: {
    flex: 1,
    padding: 20,
  },
  questionHeader: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 20,
  },
  questionNumber: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  questionText: {
    fontSize: 18,
    color: '#333',
    fontWeight: '600',
  },
  optionsContainer: {
    marginTop: 10,
  },
  option: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 15,
    marginBottom: 10,
    borderWidth: 2,
    borderColor: '#e0e0e0',
  },
  optionSelected: {
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
  },
  optionText: {
    fontSize: 16,
    color: '#333',
  },
  navigationContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 20,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  navButton: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  navButtonDisabled: {
    opacity: 0.5,
  },
  navButtonText: {
    fontSize: 16,
    color: '#333',
    fontWeight: '600',
  },
  submitButton: {
    flex: 1,
    backgroundColor: '#2563eb',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
    marginHorizontal: 5,
  },
  submitButtonText: {
    fontSize: 16,
    color: '#fff',
    fontWeight: 'bold',
  },
});

export default ExamDetailScreen;



