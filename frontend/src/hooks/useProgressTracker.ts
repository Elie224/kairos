import { useEffect, useRef, useCallback } from 'react'
import { useMutation, useQueryClient } from 'react-query'
import api from '../services/api'

interface UseProgressTrackerProps {
  moduleId: string
  enabled?: boolean
}

export const useProgressTracker = ({ moduleId, enabled = true }: UseProgressTrackerProps) => {
  const startTimeRef = useRef<number>(Date.now())
  const intervalRef = useRef<ReturnType<typeof setInterval>>()
  const lastSaveRef = useRef<number>(0)
  const pendingSaveRef = useRef<boolean>(false)
  const queryClient = useQueryClient()

  const saveProgressMutation = useMutation(
    async (completed: boolean) => {
      const timeSpent = Math.max(1, Math.floor((Date.now() - startTimeRef.current) / 1000))
      return api.post('/progress/', {
        module_id: moduleId,
        completed,
        time_spent: timeSpent,
      })
    },
    {
      onSuccess: () => {
        lastSaveRef.current = Date.now()
        pendingSaveRef.current = false
        // Invalidate progress queries to refresh
        queryClient.invalidateQueries('progress')
      },
      onError: (error) => {
        pendingSaveRef.current = false
        console.error('Erreur lors de la sauvegarde de la progression:', error)
      }
    }
  )

  // Debounced save function
  const debouncedSave = useCallback(() => {
    // Éviter les sauvegardes trop fréquentes (minimum 10 secondes entre chaque)
    const now = Date.now()
    if (now - lastSaveRef.current < 10000 || pendingSaveRef.current) {
      return
    }
    
    pendingSaveRef.current = true
    saveProgressMutation.mutate(false)
  }, [saveProgressMutation])

  useEffect(() => {
    if (!enabled || !moduleId) return

    startTimeRef.current = Date.now()
    lastSaveRef.current = Date.now()

    // Sauvegarder la progression toutes les 30 secondes avec debounce
    intervalRef.current = setInterval(() => {
      debouncedSave()
    }, 30000)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      // Sauvegarder le temps total à la fermeture (si pas déjà en cours)
      if (startTimeRef.current && !pendingSaveRef.current) {
        const timeSpent = Math.max(1, Math.floor((Date.now() - startTimeRef.current) / 1000))
        // Sauvegarde synchrone à la fermeture
        api.post('/progress/', {
          module_id: moduleId,
          completed: false,
          time_spent: timeSpent,
        }).catch((error) => {
          console.error('Erreur lors de la sauvegarde finale:', error)
        })
      }
    }
  }, [moduleId, enabled, debouncedSave])

  const markAsCompleted = useCallback(() => {
    if (!pendingSaveRef.current) {
      saveProgressMutation.mutate(true)
    }
  }, [saveProgressMutation])

  return { markAsCompleted }
}





