/**
 * Hook personnalisé pour gérer les modules
 */
import { useQuery } from 'react-query'
import api from '../services/api'
import { Module, ModuleFilters, GroupedModules } from '../types/module'
import { SUBJECT_ORDER } from '../constants/modules'
import { useMemo } from 'react'
import { useDebounce } from './useDebounce'

export const useModules = (filters: Partial<ModuleFilters> = {}) => {
  // Debounce la recherche pour éviter trop de requêtes
  const debouncedSearchQuery = useDebounce(filters.searchQuery || '', 300)
  // Requête pour tous les modules (pour le groupement) - seulement si pas de filtre
  const { data: allModules } = useQuery<Module[]>(
    ['modules', 'all'],
    async () => {
      const response = await api.get('/modules/', {
        timeout: 1000, // Timeout de 1 seconde
        params: { limit: 100 }, // Limiter les résultats
      })
      return response.data
    },
    {
      enabled: !filters.subject, // Ne charger que si pas de filtre de matière
      staleTime: 5 * 60 * 1000, // 5 minutes - considérer les données fraîches pendant 5 min
      cacheTime: 10 * 60 * 1000, // 10 minutes - garder en cache 10 min
      refetchOnMount: false, // Ne pas refetch à chaque montage si les données sont fraîches
      refetchOnWindowFocus: false, // Ne pas refetch au focus de la fenêtre
    }
  )

  // Requête pour les modules filtrés
  const { data: modules, isLoading, error } = useQuery<Module[]>(
    ['modules', filters.subject || 'all', debouncedSearchQuery],
    async () => {
      const params = new URLSearchParams()
      if (filters.subject) params.append('subject', filters.subject)
      if (debouncedSearchQuery) params.append('search', debouncedSearchQuery)
      const response = await api.get(`/modules/?${params.toString()}`, {
        timeout: 1000, // Timeout de 1 seconde
        params: { limit: 100 }, // Limiter les résultats
      })
      return response.data
    },
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnMount: false,
      refetchOnWindowFocus: false,
      retry: 1,
      enabled: !filters.searchQuery || debouncedSearchQuery.length >= 2, // Attendre au moins 2 caractères
    }
  )

  // Utiliser allModules pour le groupement si aucun filtre de matière n'est appliqué
  const modulesForGrouping = filters.subject ? modules : allModules

  const filteredModules = useMemo(() => {
    if (!modules) return []
    
    // Si la recherche est faite côté serveur, retourner directement les modules
    // Sinon, filtrer côté client (seulement si nécessaire)
    let filtered = [...modules]
    
    // Filtrage côté client seulement si la recherche n'a pas été faite côté serveur
    // (pour les recherches très rapides ou pour les cas où le serveur ne supporte pas la recherche)
    if (debouncedSearchQuery && debouncedSearchQuery.length >= 2) {
      // Le serveur devrait déjà avoir filtré, mais on peut faire un filtrage supplémentaire côté client
      const query = debouncedSearchQuery.toLowerCase()
      filtered = filtered.filter(
        (module) =>
          module.title.toLowerCase().includes(query) ||
          module.description.toLowerCase().includes(query)
      )
    }
    
    return filtered
  }, [modules, debouncedSearchQuery])

  const groupedModules = useMemo<GroupedModules>(() => {
    const modulesToGroup = modulesForGrouping || []
    const grouped = modulesToGroup.reduce((acc, module) => {
      const subject = module.subject || 'other'
      if (!acc[subject]) {
        acc[subject] = []
      }
      acc[subject].push(module)
      return acc
    }, {} as GroupedModules)
    
    return grouped
  }, [modulesForGrouping])

  const modulesBySubject = useMemo(() => {
    return SUBJECT_ORDER.map((subject) => ({
      subject,
      modules: groupedModules[subject] || [],
    })).filter((group) => group.modules.length > 0)
  }, [groupedModules])

  return {
    modules: filteredModules,
    groupedModules,
    modulesBySubject,
    isLoading,
    error,
    totalCount: filteredModules.length,
  }
}

