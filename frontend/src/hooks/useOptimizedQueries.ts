/**
 * Hook pour optimiser les requêtes avec chargement progressif
 */
import { useQuery, UseQueryOptions } from 'react-query'
import api from '../services/api'

interface OptimizedQueryOptions<T> extends Omit<UseQueryOptions<T>, 'queryFn'> {
  endpoint: string
  priority?: 'high' | 'medium' | 'low'
  timeout?: number
  params?: Record<string, any>
}

export function useOptimizedQuery<T = any>({
  endpoint,
  priority = 'medium',
  timeout = 30000, // Timeout de 30 secondes par défaut
  params,
  ...options
}: OptimizedQueryOptions<T>) {
  return useQuery<T>(
    [endpoint, params],
    async () => {
      const response = await api.get(endpoint, {
        timeout,
        params,
      })
      return response.data
    },
    {
      staleTime: priority === 'high' ? 5 * 60 * 1000 : 10 * 60 * 1000,
      cacheTime: priority === 'high' ? 10 * 60 * 1000 : 30 * 60 * 1000,
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      retry: 1,
      ...options,
    }
  )
}














