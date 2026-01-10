import { useState, useEffect, useCallback } from 'react'
import { useQuery } from 'react-query'
import api from '../services/api'

export type ImmersiveMode = '3d' | 'ar' | 'vr' | 'unity' | null

export interface ImmersiveCapabilities {
  webXR: boolean
  arSupported: boolean
  vrSupported: boolean
  unitySupported: boolean
}

interface UseImmersiveExperienceProps {
  moduleId: string
  sceneType?: string
}

export const useImmersiveExperience = ({ moduleId, sceneType }: UseImmersiveExperienceProps) => {
  const [currentMode, setCurrentMode] = useState<ImmersiveMode>('3d')
  const [capabilities, setCapabilities] = useState<ImmersiveCapabilities>({
    webXR: false,
    arSupported: false,
    vrSupported: false,
    unitySupported: false
  })

  // Détecter les capacités du navigateur
  useEffect(() => {
    const checkCapabilities = async () => {
      const webXRSupported = 'xr' in navigator
      let arSupported = false
      let vrSupported = false

      if (webXRSupported && navigator.xr) {
        try {
          arSupported = await navigator.xr.isSessionSupported('immersive-ar')
          vrSupported = await navigator.xr.isSessionSupported('immersive-vr')
        } catch (error) {
          console.warn('Erreur lors de la vérification WebXR:', error)
        }
      }

      // Vérifier le support Unity WebGL (basique)
      const unitySupported = typeof window !== 'undefined' && 'WebAssembly' in window

      setCapabilities({
        webXR: webXRSupported,
        arSupported,
        vrSupported,
        unitySupported
      })
    }

    checkCapabilities()
  }, [])

  // Requête IA contextuelle pour l'expérience immersive
  const { data: aiContext, isLoading: isLoadingContext } = useQuery(
    ['immersive-context', moduleId, currentMode],
    async () => {
      if (!currentMode || currentMode === '3d') return null
      
      const response = await api.post('/ai/immersive-context', {
        module_id: moduleId,
        mode: currentMode,
        scene_type: sceneType
      })
      return response.data
    },
    {
      enabled: !!moduleId && !!currentMode && currentMode !== '3d',
      staleTime: 5 * 60 * 1000,
      cacheTime: 10 * 60 * 1000
    }
  )

  const switchMode = useCallback((mode: ImmersiveMode) => {
    if (mode === 'ar' && !capabilities.arSupported) {
      console.warn('AR non supporté sur ce navigateur')
      return false
    }
    if (mode === 'vr' && !capabilities.vrSupported) {
      console.warn('VR non supporté sur ce navigateur')
      return false
    }
    setCurrentMode(mode)
    return true
  }, [capabilities])

  return {
    currentMode,
    capabilities,
    switchMode,
    aiContext,
    isLoadingContext
  }
}
















