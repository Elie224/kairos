import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  FlatList,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { MainStackParamList } from '../navigation/MainNavigator';
import { moduleService } from '../services/moduleService';
import { Module, Subject } from '../types';
import Icon from 'react-native-vector-icons/MaterialIcons';

type ModulesScreenNavigationProp = NativeStackNavigationProp<MainStackParamList>;

const ModulesScreen = () => {
  const navigation = useNavigation<ModulesScreenNavigationProp>();
  const [modules, setModules] = useState<Module[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState<Subject | null>(null);

  useEffect(() => {
    loadModules();
  }, [selectedSubject]);

  const loadModules = async () => {
    try {
      setLoading(true);
      const data = await moduleService.getAll(selectedSubject || undefined);
      setModules(data);
    } catch (error) {
      console.error('Erreur lors du chargement des modules:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadModules();
  };

  const renderModule = ({ item }: { item: Module }) => (
    <TouchableOpacity
      style={styles.moduleCard}
      onPress={() => navigation.navigate('ModuleDetail', { moduleId: item.id })}
    >
      <View style={styles.moduleHeader}>
        <Icon
          name={item.subject === Subject.MATHEMATICS ? 'calculate' : 'computer'}
          size={24}
          color="#2563eb"
        />
        <Text style={styles.moduleSubject}>
          {item.subject === Subject.MATHEMATICS ? 'Mathématiques' : 'Informatique'}
        </Text>
      </View>
      <Text style={styles.moduleTitle}>{item.title}</Text>
      <Text style={styles.moduleDescription} numberOfLines={2}>
        {item.description}
      </Text>
      <View style={styles.moduleFooter}>
        <Text style={styles.moduleTime}>
          <Icon name="access-time" size={14} color="#666" /> {item.estimated_time} min
        </Text>
        {item.difficulty && (
          <Text style={styles.moduleDifficulty}>
            {item.difficulty === 'beginner' && 'Débutant'}
            {item.difficulty === 'intermediate' && 'Intermédiaire'}
            {item.difficulty === 'advanced' && 'Avancé'}
          </Text>
        )}
      </View>
    </TouchableOpacity>
  );

  if (loading && !refreshing) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.filterContainer}>
        <TouchableOpacity
          style={[
            styles.filterButton,
            selectedSubject === null && styles.filterButtonActive,
          ]}
          onPress={() => setSelectedSubject(null)}
        >
          <Text
            style={[
              styles.filterButtonText,
              selectedSubject === null && styles.filterButtonTextActive,
            ]}
          >
            Tous
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[
            styles.filterButton,
            selectedSubject === Subject.MATHEMATICS && styles.filterButtonActive,
          ]}
          onPress={() => setSelectedSubject(Subject.MATHEMATICS)}
        >
          <Text
            style={[
              styles.filterButtonText,
              selectedSubject === Subject.MATHEMATICS && styles.filterButtonTextActive,
            ]}
          >
            Mathématiques
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[
            styles.filterButton,
            selectedSubject === Subject.COMPUTER_SCIENCE && styles.filterButtonActive,
          ]}
          onPress={() => setSelectedSubject(Subject.COMPUTER_SCIENCE)}
        >
          <Text
            style={[
              styles.filterButtonText,
              selectedSubject === Subject.COMPUTER_SCIENCE && styles.filterButtonTextActive,
            ]}
          >
            Informatique
          </Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={modules}
        renderItem={renderModule}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyText}>Aucun module disponible</Text>
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
  filterContainer: {
    flexDirection: 'row',
    padding: 15,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  filterButton: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 10,
    backgroundColor: '#f0f0f0',
  },
  filterButtonActive: {
    backgroundColor: '#2563eb',
  },
  filterButtonText: {
    color: '#666',
    fontSize: 14,
  },
  filterButtonTextActive: {
    color: '#fff',
    fontWeight: 'bold',
  },
  list: {
    padding: 15,
  },
  moduleCard: {
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
  moduleHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
  },
  moduleSubject: {
    marginLeft: 8,
    fontSize: 12,
    color: '#2563eb',
    fontWeight: '600',
  },
  moduleTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  moduleDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 10,
  },
  moduleFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  moduleTime: {
    fontSize: 12,
    color: '#666',
  },
  moduleDifficulty: {
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

export default ModulesScreen;



