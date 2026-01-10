import axios, { AxiosError, AxiosInstance } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api' 
  : 'https://votre-domaine.com/api';

class ApiService {
  private api: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.loadToken();
  }

  private async loadToken() {
    try {
      const authData = await AsyncStorage.getItem('kairos-auth');
      if (authData) {
        const parsed = JSON.parse(authData);
        if (parsed.state?.token) {
          this.setToken(parsed.state.token);
        }
      }
    } catch (error) {
      console.error('Erreur lors du chargement du token:', error);
    }
  }

  public setToken(token: string | null) {
    this.token = token;
    if (token) {
      this.api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete this.api.defaults.headers.common['Authorization'];
    }
  }

  private setupInterceptors() {
    // Intercepteur de requête
    this.api.interceptors.request.use(
      async (config) => {
        // Vérifier la connexion réseau
        const netInfo = await NetInfo.fetch();
        if (!netInfo.isConnected) {
          throw new Error('Pas de connexion internet');
        }

        // Ajouter le token si disponible
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Intercepteur de réponse
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        // Gérer les erreurs 401 (non autorisé)
        if (error.response?.status === 401) {
          // Déconnexion automatique
          await AsyncStorage.removeItem('kairos-auth');
          this.setToken(null);
          return Promise.reject(error);
        }

        // Gérer les erreurs réseau
        if (!error.response) {
          if (error.request) {
            const netInfo = await NetInfo.fetch();
            if (!netInfo.isConnected) {
              error.message = 'Pas de connexion internet';
            } else {
              error.message = 'Erreur de connexion au serveur';
            }
          }
          return Promise.reject(error);
        }

        // Gérer les erreurs 429 (rate limiting)
        if (error.response?.status === 429) {
          const retryAfter = error.response.headers['retry-after'];
          const delay = retryAfter ? parseInt(retryAfter) * 1000 : 5000;
          
          if (originalRequest && !originalRequest._retry) {
            originalRequest._retry = true;
            await new Promise(resolve => setTimeout(resolve, delay));
            return this.api(originalRequest);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  public get instance() {
    return this.api;
  }
}

export const apiService = new ApiService();
export default apiService.instance;



