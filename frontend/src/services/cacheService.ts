/**
 * Service de cache optimisé pour améliorer les performances
 */
import { QueryClient } from 'react-query'

interface CacheConfig {
  staleTime: number
  cacheTime: number
  refetchOnMount: boolean
  refetchOnWindowFocus: boolean
  retry: number
}

const DEFAULT_CONFIG: CacheConfig = {
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 10 * 60 * 1000, // 10 minutes
  refetchOnMount: false,
  refetchOnWindowFocus: false,
  retry: 1,
}

const HIGH_PRIORITY_CONFIG: CacheConfig = {
  staleTime: 2 * 60 * 1000, // 2 minutes
  cacheTime: 5 * 60 * 1000, // 5 minutes
  refetchOnMount: false,
  refetchOnWindowFocus: false,
  retry: 2,
}

const LOW_PRIORITY_CONFIG: CacheConfig = {
  staleTime: 15 * 60 * 1000, // 15 minutes
  cacheTime: 30 * 60 * 1000, // 30 minutes
  refetchOnMount: false,
  refetchOnWindowFocus: false,
  retry: 0,
}

export const cacheConfigs = {
  default: DEFAULT_CONFIG,
  high: HIGH_PRIORITY_CONFIG,
  low: LOW_PRIORITY_CONFIG,
}

/**
 * Prépare les données pour le cache
 */
export function prepareForCache<T>(data: T): T {
  // Ici on pourrait ajouter de la transformation/sérialisation si nécessaire
  return data
}

/**
 * Nettoie le cache d'une query spécifique
 */
export function clearQueryCache(queryClient: QueryClient, queryKey: string | string[]) {
  queryClient.removeQueries(queryKey)
}

/**
 * Précache des données pour améliorer les performances
 */
export function prefetchQuery<T>(
  queryClient: QueryClient,
  queryKey: string | string[],
  queryFn: () => Promise<T>,
  config: Partial<CacheConfig> = {}
) {
  return queryClient.prefetchQuery(
    queryKey,
    queryFn,
    {
      ...DEFAULT_CONFIG,
      ...config,
    }
  )
}

/**
 * Invalide et refetch une query
 */
export function invalidateAndRefetch(
  queryClient: QueryClient,
  queryKey: string | string[]
) {
  return queryClient.invalidateQueries(queryKey)
}

/**
 * Gère le cache avec stratégie LRU (Least Recently Used)
 */
class LRUCache<T> {
  private cache: Map<string, { data: T; timestamp: number }> = new Map()
  private maxSize: number

  constructor(maxSize: number = 50) {
    this.maxSize = maxSize
  }

  get(key: string): T | null {
    const item = this.cache.get(key)
    if (!item) return null

    // Mettre à jour l'ordre (LRU)
    this.cache.delete(key)
    this.cache.set(key, item)
    return item.data
  }

  set(key: string, data: T): void {
    // Si la clé existe déjà, la mettre à jour
    if (this.cache.has(key)) {
      this.cache.delete(key)
    } else if (this.cache.size >= this.maxSize) {
      // Supprimer le plus ancien (premier élément)
      const firstKey = this.cache.keys().next().value
      this.cache.delete(firstKey)
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    })
  }

  clear(): void {
    this.cache.clear()
  }

  size(): number {
    return this.cache.size
  }
}

// Instance globale du cache LRU
export const lruCache = new LRUCache<any>(50)

/**
 * Optimise les requêtes en batch
 */
export async function batchRequests<T>(
  requests: Array<() => Promise<T>>,
  batchSize: number = 5
): Promise<T[]> {
  const results: T[] = []
  
  for (let i = 0; i < requests.length; i += batchSize) {
    const batch = requests.slice(i, i + batchSize)
    const batchResults = await Promise.all(batch.map((req) => req()))
    results.push(...batchResults)
  }
  
  return results
}
