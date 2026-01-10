import { useEffect, useRef, useState } from 'react'
import { Box, Button, VStack, Text, Alert, AlertIcon, Spinner } from '@chakra-ui/react'

interface UnityWebGLViewerProps {
  moduleId: string
  buildPath?: string
  onUnityReady?: () => void
  onUnityError?: (error: string) => void
}

declare global {
  interface Window {
    createUnityInstance: (canvas: HTMLCanvasElement, config: any, onProgress?: (progress: number) => void) => Promise<any>
    unityInstance?: any
  }
}

const UnityWebGLViewer = ({ moduleId, buildPath = '/unity-builds', onUnityReady, onUnityError }: UnityWebGLViewerProps) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)
  const unityInstanceRef = useRef<any>(null)

  useEffect(() => {
    if (!containerRef.current) return

    // Vérifier le support WebAssembly
    if (typeof window === 'undefined' || !window.WebAssembly) {
      setError('WebAssembly n\'est pas supporté sur ce navigateur.')
      setIsLoading(false)
      return
    }

    // Charger le script Unity loader
    const loadUnity = async () => {
      try {
        // Charger le script de build Unity
        const script = document.createElement('script')
        script.src = `${buildPath}/Build/${moduleId}.loader.js`
        script.async = true

        script.onload = () => {
          if (!window.createUnityInstance) {
            setError('Le loader Unity n\'a pas pu être chargé.')
            setIsLoading(false)
            return
          }

          // Créer le canvas
          const canvas = document.createElement('canvas')
          canvas.style.width = '100%'
          canvas.style.height = '100%'
          canvas.style.display = 'block'
          canvasRef.current = canvas
          containerRef.current?.appendChild(canvas)

          // Configuration Unity
          const config = {
            dataUrl: `${buildPath}/Build/${moduleId}.data`,
            frameworkUrl: `${buildPath}/Build/${moduleId}.framework.js`,
            codeUrl: `${buildPath}/Build/${moduleId}.wasm`,
            streamingAssetsUrl: 'StreamingAssets',
            companyName: 'Kaïrox',
            productName: 'Kaïrox Immersive',
            productVersion: '1.0.0'
          }

          // Créer l'instance Unity
          window.createUnityInstance(canvas, config, (progress: number) => {
            setProgress(Math.round(progress * 100))
          })
            .then((instance: any) => {
              unityInstanceRef.current = instance
              window.unityInstance = instance
              setIsLoading(false)
              onUnityReady?.()

              // Envoyer le module ID à Unity
              if (instance.SendMessage) {
                instance.SendMessage('GameManager', 'SetModuleId', moduleId)
              }
            })
            .catch((err: Error) => {
              setError(`Erreur lors du chargement Unity: ${err.message}`)
              setIsLoading(false)
              onUnityError?.(err.message)
            })
        }

        script.onerror = () => {
          setError('Impossible de charger le build Unity. Vérifiez que les fichiers sont présents dans le dossier public.')
          setIsLoading(false)
        }

        document.body.appendChild(script)
      } catch (err) {
        setError(`Erreur: ${err instanceof Error ? err.message : 'Erreur inconnue'}`)
        setIsLoading(false)
      }
    }

    loadUnity()

    // Nettoyage
    return () => {
      if (unityInstanceRef.current && unityInstanceRef.current.Quit) {
        try {
          unityInstanceRef.current.Quit()
        } catch (e) {
          console.warn('Erreur lors de la fermeture Unity:', e)
        }
      }
      if (canvasRef.current && containerRef.current) {
        containerRef.current.removeChild(canvasRef.current)
      }
    }
  }, [moduleId, buildPath, onUnityReady, onUnityError])

  // Fonction pour communiquer avec Unity
  const sendMessageToUnity = (gameObject: string, method: string, value: string | number) => {
    if (unityInstanceRef.current && unityInstanceRef.current.SendMessage) {
      unityInstanceRef.current.SendMessage(gameObject, method, value)
    }
  }

  if (error) {
    return (
      <Box p={4}>
        <Alert status="error">
          <AlertIcon />
          <VStack align="start" spacing={2}>
            <Text fontWeight="bold">{error}</Text>
            <Text fontSize="sm" color="gray.600">
              Assurez-vous que les builds Unity sont exportés dans le dossier public/unity-builds/
            </Text>
          </VStack>
        </Alert>
      </Box>
    )
  }

  return (
    <Box ref={containerRef} w="100%" h="100%" position="relative" bg="black">
      {isLoading && (
        <VStack
          position="absolute"
          top="50%"
          left="50%"
          transform="translate(-50%, -50%)"
          spacing={4}
          zIndex={10}
        >
          <Spinner size="xl" color="blue.500" />
          <Text color="white" fontSize="lg">
            Chargement de l'expérience Unity... {progress}%
          </Text>
        </VStack>
      )}
    </Box>
  )
}

// Export de la fonction pour utilisation externe
export const sendMessageToUnity = (gameObject: string, method: string, value: string | number) => {
  if (window.unityInstance && window.unityInstance.SendMessage) {
    window.unityInstance.SendMessage(gameObject, method, value)
  }
}

export default UnityWebGLViewer



