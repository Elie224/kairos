import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { useAuthStore } from '../store/authStore';
import { MainStackParamList } from '../navigation/MainNavigator';
import Icon from 'react-native-vector-icons/MaterialIcons';

type HomeScreenNavigationProp = NativeStackNavigationProp<MainStackParamList>;

const HomeScreen = () => {
  const navigation = useNavigation<HomeScreenNavigationProp>();
  const { user } = useAuthStore();

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.greeting}>
          Bonjour, {user?.first_name || user?.username || 'Utilisateur'} !
        </Text>
        <Text style={styles.subtitle}>Bienvenue sur Kaïros</Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Accès rapide</Text>
        
        <TouchableOpacity
          style={styles.card}
          onPress={() => navigation.navigate('MainTabs', { screen: 'Modules' })}
        >
          <Icon name="book" size={32} color="#2563eb" />
          <View style={styles.cardContent}>
            <Text style={styles.cardTitle}>Modules</Text>
            <Text style={styles.cardDescription}>
              Accéder aux modules d'apprentissage
            </Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.card}
          onPress={() => navigation.navigate('MainTabs', { screen: 'Dashboard' })}
        >
          <Icon name="dashboard" size={32} color="#2563eb" />
          <View style={styles.cardContent}>
            <Text style={styles.cardTitle}>Tableau de bord</Text>
            <Text style={styles.cardDescription}>
              Voir votre progression
            </Text>
          </View>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.card}
          onPress={() => navigation.navigate('ExamDetail', { examId: '' })}
        >
          <Icon name="quiz" size={32} color="#2563eb" />
          <View style={styles.cardContent}>
            <Text style={styles.cardTitle}>Examens</Text>
            <Text style={styles.cardDescription}>
              Passer un examen
            </Text>
          </View>
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
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
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
  card: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 15,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardContent: {
    marginLeft: 15,
    flex: 1,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  cardDescription: {
    fontSize: 14,
    color: '#666',
  },
});

export default HomeScreen;



