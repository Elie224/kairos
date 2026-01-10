/**
 * Hook personnalisé pour gérer les modules
 */
import { useQuery } from 'react-query'
import api from '../services/api'
import { Module, ModuleFilters, GroupedModules } from '../types/module'
import { SUBJECT_ORDER } from '../constants/modules'
import { useMemo } from 'react'

export const useModules = (filters: Partial<ModuleFilters> = {}) => {
  // Requête pour tous les modules (pour le groupement) - seulement si pas de filtre
  const { data: allModules } = useQuery<Module[]>(
    ['modules', 'all'],
    async () => {
      const response = await api.get('/modules/')
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
    ['modules', filters.subject || 'all'],
    async () => {
      const params = new URLSearchParams()
      if (filters.subject) params.append('subject', filters.subject)
      const response = await api.get(`/modules/?${params.toString()}`)
      return response.data
    },
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnMount: false,
      refetchOnWindowFocus: false,
    }
  )

  // Utiliser allModules pour le groupement si aucun filtre de matière n'est appliqué
  const modulesForGrouping = filters.subject ? modules : allModules

  const filteredModules = useMemo(() => {
    if (!modules) return []
    
    let filtered = [...modules]
    
    // Filtrage par recherche textuelle
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase()
      filtered = filtered.filter(
        (module) =>
          module.title.toLowerCase().includes(query) ||
          module.description.toLowerCase().includes(query)
      )
    }
    
    return filtered
  }, [modules, filters.searchQuery])

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

