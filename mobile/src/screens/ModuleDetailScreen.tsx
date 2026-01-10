import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { RouteProp, useRoute, useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { MainStackParamList } from '../navigation/MainNavigator';
import { moduleService } from '../services/moduleService';
import { Module } from '../types';
import AITutorComponent from '../components/AITutorComponent';
import Icon from 'react-native-vector-icons/MaterialIcons';

type ModuleDetailScreenRouteProp = RouteProp<MainStackParamList, 'ModuleDetail'>;
type ModuleDetailScreenNavigationProp = NativeStackNavigationProp<MainStackParamList>;

const ModuleDetailScreen = () => {
  const route = useRoute<ModuleDetailScreenRouteProp>();
  const navigation = useNavigation<ModuleDetailScreenNavigationProp>();
  const { moduleId } = route.params;
  const [module, setModule] = useState<Module | null>(null);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    loadModule();
    loadProgress();
  }, [moduleId]);

  const loadModule = async () => {
    try {
      setLoading(true);
      const data = await moduleService.getById(moduleId);
      setModule(data);
    } catch (error) {
      console.error('Erreur lors du chargement du module:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadProgress = async () => {
    try {
      const data = await moduleService.getProgress(moduleId);
      setProgress(data.progress_percentage || 0);
    } catch (error) {
      // Ignorer les erreurs de progression
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  if (!module) {
    return (
      <View style={styles.centerContainer}>
        <Text>Module non trouvé</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>{module.title}</Text>
        <Text style={styles.description}>{module.description}</Text>
        
        <View style={styles.metaContainer}>
          <View style={styles.metaItem}>
            <Icon name="access-time" size={16} color="#666" />
            <Text style={styles.metaText}>{module.estimated_time} min</Text>
          </View>
          {module.difficulty && (
            <View style={styles.metaItem}>
              <Icon name="trending-up" size={16} color="#666" />
              <Text style={styles.metaText}>
                {module.difficulty === 'beginner' && 'Débutant'}
                {module.difficulty === 'intermediate' && 'Intermédiaire'}
                {module.difficulty === 'advanced' && 'Avancé'}
              </Text>
            </View>
          )}
        </View>

        {progress > 0 && (
          <View style={styles.progressContainer}>
            <View style={styles.progressBar}>
              <View style={[styles.progressFill, { width: `${progress}%` }]} />
            </View>
            <Text style={styles.progressText}>{progress}% complété</Text>
          </View>
        )}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tutorat IA</Text>
        <AITutorComponent moduleId={moduleId} />
      </View>

      <View style={styles.actions}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => {
            // Navigation vers quiz si disponible
          }}
        >
          <Icon name="quiz" size={20} color="#fff" />
          <Text style={styles.actionButtonText}>Commencer le Quiz</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
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
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
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
    marginBottom: 15,
  },
  metaContainer: {
    flexDirection: 'row',
    marginBottom: 15,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 20,
  },
  metaText: {
    marginLeft: 5,
    fontSize: 14,
    color: '#666',
  },
  progressContainer: {
    marginTop: 10,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 5,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#2563eb',
  },
  progressText: {
    fontSize: 12,
    color: '#666',
  },
  section: {
    padding: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  actions: {
    padding: 20,
  },
  actionButton: {
    backgroundColor: '#2563eb',
    borderRadius: 8,
    padding: 15,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginLeft: 10,
  },
});

export default ModuleDetailScreen;

