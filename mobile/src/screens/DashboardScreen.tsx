import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import { useAuthStore } from '../store/authStore';
import api from '../services/api';
import Icon from 'react-native-vector-icons/MaterialIcons';

const DashboardScreen = () => {
  const { user } = useAuthStore();
  const [stats, setStats] = useState({
    modulesCompleted: 0,
    totalProgress: 0,
    badgesEarned: 0,
    timeSpent: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      // Charger les statistiques depuis l'API
      const [progressResponse, badgesResponse] = await Promise.all([
        api.get('/progress'),
        api.get('/badges/user'),
      ]);

      const progress = progressResponse.data || [];
      const badges = badgesResponse.data || [];

      const completed = progress.filter((p: any) => p.completed).length;
      const totalProgress = progress.length > 0
        ? progress.reduce((sum: number, p: any) => sum + (p.progress_percentage || 0), 0) / progress.length
        : 0;

      setStats({
        modulesCompleted: completed,
        totalProgress: Math.round(totalProgress),
        badgesEarned: badges.length,
        timeSpent: progress.reduce((sum: number, p: any) => sum + (p.time_spent || 0), 0),
      });
    } catch (error) {
      console.error('Erreur lors du chargement des statistiques:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Tableau de bord</Text>
        <Text style={styles.subtitle}>
          {user?.first_name || user?.username || 'Utilisateur'}
        </Text>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Icon name="check-circle" size={32} color="#2563eb" />
          <Text style={styles.statValue}>{stats.modulesCompleted}</Text>
          <Text style={styles.statLabel}>Modules complétés</Text>
        </View>

        <View style={styles.statCard}>
          <Icon name="trending-up" size={32} color="#2563eb" />
          <Text style={styles.statValue}>{stats.totalProgress}%</Text>
          <Text style={styles.statLabel}>Progression totale</Text>
        </View>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statCard}>
          <Icon name="star" size={32} color="#2563eb" />
          <Text style={styles.statValue}>{stats.badgesEarned}</Text>
          <Text style={styles.statLabel}>Badges obtenus</Text>
        </View>

        <View style={styles.statCard}>
          <Icon name="access-time" size={32} color="#2563eb" />
          <Text style={styles.statValue}>
            {Math.round(stats.timeSpent / 60)}h
          </Text>
          <Text style={styles.statLabel}>Temps passé</Text>
        </View>
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
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
  statsContainer: {
    flexDirection: 'row',
    padding: 15,
    justifyContent: 'space-between',
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginHorizontal: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
  },
  statLabel: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
    textAlign: 'center',
  },
});

export default DashboardScreen;



