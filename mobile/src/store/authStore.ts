import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api, { apiService } from '../services/api';

export interface User {
  id: string;
  email: string;
  username: string;
  first_name?: string;
  last_name?: string;
  date_of_birth?: string;
  country?: string;
  phone?: string;
  is_admin?: boolean;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  setAuth: (user: User, token: string) => void;
  updateUser: (user: User) => void;
  checkAuth: () => Promise<void>;
}

export interface RegisterData {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  country: string;
  phone: string;
  password: string;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const formData = new FormData();
          formData.append('username', email);
          formData.append('password', password);

          const response = await api.post('/auth/login', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });

          const { access_token, user } = response.data;
          apiService.setToken(access_token);

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true });
        try {
          const payload = {
            email: data.email.trim(),
            username: data.username.trim(),
            first_name: data.first_name.trim(),
            last_name: data.last_name.trim(),
            date_of_birth: data.date_of_birth,
            country: data.country.trim(),
            phone: data.phone.trim(),
            password: data.password,
          };

          const response = await api.post('/auth/register', payload);
          const user = response.data;

          if (!user || !user.id) {
            throw new Error('Réponse invalide du serveur');
          }

          set({ user, isAuthenticated: false, isLoading: false });
        } catch (error: any) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: async () => {
        try {
          await api.post('/auth/logout');
        } catch (error) {
          // Ignorer les erreurs de déconnexion
        }
        apiService.setToken(null);
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        });
      },

      setAuth: (user: User, token: string) => {
        apiService.setToken(token);
        set({
          user,
          token,
          isAuthenticated: true,
        });
      },

      updateUser: (updatedUser: User) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...updatedUser } : null,
        }));
      },

      checkAuth: async () => {
        const { token } = get();
        if (!token) {
          return;
        }

        try {
          apiService.setToken(token);
          const response = await api.get('/auth/me');
          set({
            user: response.data,
            isAuthenticated: true,
          });
        } catch (error) {
          // Token invalide, déconnexion
          await get().logout();
        }
      },
    }),
    {
      name: 'kairos-auth',
      storage: createJSONStorage(() => AsyncStorage),
      onRehydrateStorage: () => (state) => {
        if (state?.token) {
          apiService.setToken(state.token);
        }
      },
    }
  )
);



