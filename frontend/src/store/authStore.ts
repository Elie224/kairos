import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import api from '../services/api'

export interface User {
  id: string
  email: string
  username: string
  first_name?: string
  last_name?: string
  date_of_birth?: string
  country?: string
  phone?: string
  is_admin?: boolean
  is_active?: boolean
  created_at?: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  setAuth: (user: User, token: string) => void
  updateUser: (updatedUser: Partial<User>) => void
  checkAuth: () => Promise<void>
}

export interface RegisterData {
  email: string
  username: string
  password: string
  first_name?: string
  last_name?: string
  date_of_birth?: string
  country?: string
  phone?: string
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          // OAuth2PasswordRequestForm attend application/x-www-form-urlencoded
          const params = new URLSearchParams()
          params.append('username', email)
          params.append('password', password)

          const response = await api.post('/auth/login', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          })

          const { access_token, user } = response.data
          
          // Mettre à jour le header Authorization
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`

          set({
            user,
            token: access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error: any) {
          set({ isLoading: false })
          throw error
        }
      },

      register: async (data: RegisterData) => {
        set({ isLoading: true })
        try {
          const payload = {
            email: data.email.trim(),
            username: data.username.trim(),
            first_name: data.first_name?.trim(),
            last_name: data.last_name?.trim(),
            date_of_birth: data.date_of_birth,
            country: data.country?.trim(),
            phone: data.phone?.trim(),
            password: data.password,
          }

          const response = await api.post('/auth/register', payload)
          const user = response.data

          if (!user || !user.id) {
            throw new Error('Réponse invalide du serveur')
          }

          set({ user, isAuthenticated: false, isLoading: false })
        } catch (error: any) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        // Supprimer le token de l'API
        delete api.defaults.headers.common['Authorization']
        
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      setAuth: (user: User, token: string) => {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        set({
          user,
          token,
          isAuthenticated: true,
        })
      },

      updateUser: (updatedUser: Partial<User>) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...updatedUser } : null,
        }))
      },

      checkAuth: async () => {
        const { token } = get()
        if (!token) {
          return
        }

        try {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
          const response = await api.get('/auth/me')
          set({
            user: response.data,
            isAuthenticated: true,
          })
        } catch (error) {
          // Token invalide, déconnexion
          get().logout()
        }
      },
    }),
    {
      name: 'kairos-auth',
      storage: createJSONStorage(() => localStorage),
      onRehydrateStorage: () => (state) => {
        if (state?.token) {
          api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
        }
      },
    }
  )
)
