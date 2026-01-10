import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { MainStackParamList } from '../navigation/MainNavigator';
import { examService } from '../services/examService';
import { Exam } from '../types';
import Icon from 'react-native-vector-icons/MaterialIcons';

type ExamsScreenNavigationProp = NativeStackNavigationProp<MainStackParamList>;

const ExamsScreen = () => {
  const navigation = useNavigation<ExamsScreenNavigationProp>();
  const [exams, setExams] = useState<Exam[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExams();
  }, []);

  const loadExams = async () => {
    try {
      setLoading(true);
      const data = await examService.getAll();
      setExams(data);
    } catch (error) {
      console.error('Erreur lors du chargement des examens:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderExam = ({ item }: { item: Exam }) => (
    <TouchableOpacity
      style={styles.examCard}
      onPress={() => navigation.navigate('ExamDetail', { examId: item.id })}
    >
      <View style={styles.examHeader}>
        <Icon name="quiz" size={24} color="#2563eb" />
        <View style={styles.examInfo}>
          <Text style={styles.examTitle}>{item.title}</Text>
          <Text style={styles.examDescription} numberOfLines={2}>
            {item.description}
          </Text>
        </View>
      </View>
      <View style={styles.examFooter}>
        <Text style={styles.examDuration}>
          <Icon name="access-time" size={14} color="#666" /> {item.duration} min
        </Text>
        <Text style={styles.examScore}>
          Score minimum: {item.passing_score}%
        </Text>
      </View>
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={exams}
        renderItem={renderExam}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Aucun examen disponible</Text>
          </View>
        }
      />
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
  list: {
    padding: 15,
  },
  examCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  examHeader: {
    flexDirection: 'row',
    marginBottom: 10,
  },
  examInfo: {
    flex: 1,
    marginLeft: 10,
  },
  examTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  examDescription: {
    fontSize: 14,
    color: '#666',
  },
  examFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: '#f0f0f0',
  },
  examDuration: {
    fontSize: 12,
    color: '#666',
  },
  examScore: {
    fontSize: 12,
    color: '#2563eb',
    fontWeight: '600',
  },
  emptyContainer: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
  },
});

export default ExamsScreen;



