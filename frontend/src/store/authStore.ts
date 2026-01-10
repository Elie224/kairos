import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  username: string
  first_name?: string
  last_name?: string
  date_of_birth?: string
  country?: string
  phone?: string
  is_admin?: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, username: string, firstName: string, lastName: string, dateOfBirth: string, country: string, phone: string, password: string) => Promise<void>
  logout: () => void
  setAuth: (user: User, token: string) => void
  updateUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      
      login: async (email: string, password: string) => {
        const { default: api } = await import('../services/api')
        // OAuth2PasswordRequestForm attend application/x-www-form-urlencoded
        const params = new URLSearchParams()
        params.append('username', email)
        params.append('password', password)
        
        const response = await api.post('/auth/login', params.toString(), {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        })
        
        const { access_token, user } = response.data
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
        
        set({
          user,
          token: access_token,
          isAuthenticated: true,
        })
      },
      
      register: async (email: string, username: string, firstName: string, lastName: string, dateOfBirth: string, country: string, phone: string, password: string) => {
        const { default: api } = await import('../services/api')
        try {
          const payload = {
            email: email.trim(),
            username: username.trim(),
            first_name: firstName.trim(),
            last_name: lastName.trim(),
            date_of_birth: dateOfBirth,
            country: country.trim(),
            phone: phone.trim(),
            password: password,
          }
          
          console.log('Données envoyées pour l\'inscription:', { ...payload, password: '***' })
          
          const response = await api.post('/auth/register', payload)
          
          // La réponse devrait contenir les données de l'utilisateur créé
          const user = response.data
          
          // S'assurer que l'utilisateur a bien un id
          if (!user || !user.id) {
            throw new Error('Réponse invalide du serveur')
          }
          
          // Ne pas définir isAuthenticated ici car l'utilisateur doit se connecter après
          set({ user, isAuthenticated: false })
        } catch (error: any) {
          console.error('Erreur lors de l\'inscription:', error)
          // Propager l'erreur pour que le composant puisse la gérer
          throw error
        }
      },
      
      logout: async () => {
        const { default: api } = await import('../services/api')
        delete api.defaults.headers.common['Authorization']
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },
      
      setAuth: async (user: User, token: string) => {
        const { default: api } = await import('../services/api')
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        set({
          user,
          token,
          isAuthenticated: true,
        })
      },
      
      updateUser: (updatedUser: User) => {
        set((state) => ({
          user: { ...state.user, ...updatedUser },
        }))
      },
    }),
    {
      name: 'kairos-auth',
      onRehydrateStorage: () => (state) => {
        // Restaurer le token dans axios après rehydratation
        if (state?.token) {
          // Import dynamique pour éviter la dépendance circulaire
          import('../services/api').then(({ default: api }) => {
            api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
          })
        }
      },
    }
  )
)
