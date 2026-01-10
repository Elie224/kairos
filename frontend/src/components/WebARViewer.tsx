import { useEffect, useRef, useState } from 'react'
import { Box, Button, VStack, Text, Alert, AlertIcon } from '@chakra-ui/react'
import * as THREE from 'three'
import ARControls from './ARControls'
// Note: ARButton sera chargé dynamiquement si WebXR est disponible

interface WebARViewerProps {
  moduleId: string
  sceneType?: string
  onARStart?: () => void
  onAREnd?: () => void
}

const WebARViewer = ({ moduleId, sceneType, onARStart, onAREnd }: WebARViewerProps) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const sceneRef = useRef<THREE.Scene | null>(null)
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null)
  const [isSupported, setIsSupported] = useState(false)
  const [isActive, setIsActive] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const sceneObjectsRef = useRef<THREE.Group[]>([])
  const currentScaleRef = useRef<number>(1)

  useEffect(() => {
    if (!containerRef.current) return

    // Vérifier le support WebXR
    if (!navigator.xr) {
      setError('WebXR n\'est pas supporté sur ce navigateur. Utilisez Chrome ou Edge sur Android.')
      setIsSupported(false)
      return
    }

    // Initialiser Three.js
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0xffffff)
    sceneRef.current = scene

    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      1000
    )
    cameraRef.current = camera

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
    renderer.xr.enabled = true
    rendererRef.current = renderer

    containerRef.current.appendChild(renderer.domElement)

    // Créer le bouton AR (chargement dynamique)
    import('three/examples/jsm/webxr/ARButton.js').then(({ ARButton }) => {
      const arButton = ARButton.createButton(renderer, {
        requiredFeatures: ['hit-test'],
        optionalFeatures: ['dom-overlay'],
        domOverlay: { root: containerRef.current }
      })

      if (arButton && containerRef.current) {
        containerRef.current.appendChild(arButton)
        setIsSupported(true)
      }
    }).catch(() => {
      setError('Impossible de charger le support WebXR AR')
      setIsSupported(false)
    })

    // Ajouter des objets selon le type de scène
    setupScene(scene, sceneType)

    // Gérer les événements de session AR
    renderer.xr.addEventListener('sessionstart', () => {
      setIsActive(true)
      onARStart?.()
    })

    renderer.xr.addEventListener('sessionend', () => {
      setIsActive(false)
      onAREnd?.()
    })

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate)
      if (renderer.xr.isPresenting) {
        renderer.render(scene, camera)
      }
    }
    animate()

    // Nettoyage
    return () => {
      if (rendererRef.current) {
        rendererRef.current.dispose()
      }
      if (containerRef.current && arButton) {
        containerRef.current.removeChild(arButton)
      }
    }
  }, [sceneType, onARStart, onAREnd])

  const setupScene = (scene: THREE.Scene, type?: string) => {
    // Lumière ambiante
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
    scene.add(ambientLight)

    // Lumière directionnelle
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.9)
    directionalLight.position.set(5, 10, 5)
    directionalLight.castShadow = true
    scene.add(directionalLight)

    // Lumière ponctuelle pour meilleur éclairage AR
    const pointLight = new THREE.PointLight(0xffffff, 0.5, 10)
    pointLight.position.set(0, 2, 0)
    scene.add(pointLight)

    // Objets selon le type de scène
    switch (type) {
      case 'mechanics':
        setupMechanicsScene(scene)
        break
      case 'chemical_reaction':
        setupChemistryScene(scene)
        break
      case 'gravitation':
        setupGravitationScene(scene)
        break
      default:
        setupDefaultScene(scene)
    }
  }

  const setupMechanicsScene = (scene: THREE.Scene) => {
    const mechanicsGroup = new THREE.Group()

    // Pendule oscillant avec animation
    const pendulumGroup = new THREE.Group()
    const pendulumString = new THREE.Line(
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0.3, 0),
        new THREE.Vector3(0, -0.4, 0)
      ]),
      new THREE.LineBasicMaterial({ color: 0x333333, linewidth: 2 })
    )
    const pendulumBall = new THREE.Mesh(
      new THREE.SphereGeometry(0.08, 16, 16),
      new THREE.MeshStandardMaterial({ color: 0xf56565, metalness: 0.3, roughness: 0.7 })
    )
    pendulumBall.position.y = -0.4
    pendulumBall.castShadow = true
    pendulumGroup.add(pendulumString)
    pendulumGroup.add(pendulumBall)
    pendulumGroup.position.set(-0.3, 1.5, -1)
    mechanicsGroup.add(pendulumGroup)

    // Objet en chute libre
    const fallingCube = new THREE.Mesh(
      new THREE.BoxGeometry(0.15, 0.15, 0.15),
      new THREE.MeshStandardMaterial({ color: 0x4299e1, metalness: 0.2, roughness: 0.8 })
    )
    fallingCube.position.set(0, 1.8, -1)
    fallingCube.castShadow = true
    mechanicsGroup.add(fallingCube)

    // Vecteur de force gravitationnelle
    const forceArrow = new THREE.ArrowHelper(
      new THREE.Vector3(0, -1, 0),
      new THREE.Vector3(0, 1.8, -1),
      0.3,
      0x48bb78,
      0.05,
      0.03
    )
    mechanicsGroup.add(forceArrow)

    // Ressort oscillant
    const springGroup = new THREE.Group()
    const springCoils = []
    for (let i = 0; i < 8; i++) {
      const coil = new THREE.Mesh(
        new THREE.TorusGeometry(0.02, 0.01, 8, 16),
        new THREE.MeshStandardMaterial({ color: 0xed8936 })
      )
      coil.position.y = -i * 0.1
      coil.rotation.x = Math.PI / 2
      springCoils.push(coil)
      springGroup.add(coil)
    }
    const springMass = new THREE.Mesh(
      new THREE.BoxGeometry(0.12, 0.12, 0.12),
      new THREE.MeshStandardMaterial({ color: 0x9f7aea })
    )
    springMass.position.y = -0.8
    springMass.castShadow = true
    springGroup.add(springMass)
    springGroup.position.set(0.3, 1.5, -1)
    mechanicsGroup.add(springGroup)

    // Sol virtuel pour référence
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(2, 2),
      new THREE.MeshStandardMaterial({ color: 0x888888, transparent: true, opacity: 0.3 })
    )
    ground.rotation.x = -Math.PI / 2
    ground.position.y = 1.2
    ground.receiveShadow = true
    mechanicsGroup.add(ground)

    mechanicsGroup.position.set(0, 0, -1.5)
    scene.add(mechanicsGroup)
    sceneObjectsRef.current.push(mechanicsGroup)
  }

  const setupChemistryScene = (scene: THREE.Scene) => {
    const chemistryGroup = new THREE.Group()

    // Molécule CH4 (méthane) avec liaisons
    const moleculeGroup = new THREE.Group()
    
    // Atome central (carbone)
    const carbonAtom = new THREE.Mesh(
      new THREE.SphereGeometry(0.12, 16, 16),
      new THREE.MeshStandardMaterial({ color: 0x333333, metalness: 0.5, roughness: 0.5 })
    )
    moleculeGroup.add(carbonAtom)

    // Atomes d'hydrogène et liaisons
    const hydrogenPositions = [
      [0.25, 0.25, 0.25],
      [-0.25, 0.25, -0.25],
      [0.25, -0.25, -0.25],
      [-0.25, -0.25, 0.25]
    ]

    hydrogenPositions.forEach((pos, i) => {
      // Atome d'hydrogène
      const hydrogen = new THREE.Mesh(
        new THREE.SphereGeometry(0.08, 16, 16),
        new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 0.3, roughness: 0.7 })
      )
      hydrogen.position.set(pos[0], pos[1], pos[2])
      moleculeGroup.add(hydrogen)

      // Liaison covalente
      const bond = new THREE.CylinderGeometry(0.02, 0.02, 0.25, 8)
      const bondMesh = new THREE.Mesh(
        bond,
        new THREE.MeshStandardMaterial({ color: 0xcccccc })
      )
      bondMesh.position.set(pos[0] / 2, pos[1] / 2, pos[2] / 2)
      bondMesh.lookAt(new THREE.Vector3(pos[0], pos[1], pos[2]))
      moleculeGroup.add(bondMesh)
    })

    moleculeGroup.position.set(0, 1.5, -1.5)
    chemistryGroup.add(moleculeGroup)

    // Rotation automatique pour visualisation 3D
    const animate = () => {
      moleculeGroup.rotation.y += 0.01
      requestAnimationFrame(animate)
    }
    animate()

    scene.add(chemistryGroup)
    sceneObjectsRef.current.push(chemistryGroup)
  }

  const setupGravitationScene = (scene: THREE.Scene) => {
    const gravitationGroup = new THREE.Group()

    // Planète centrale
    const planet = new THREE.Mesh(
      new THREE.SphereGeometry(0.2, 32, 32),
      new THREE.MeshStandardMaterial({ 
        color: 0x4A90E2,
        metalness: 0.3,
        roughness: 0.7
      })
    )
    planet.position.set(0, 1.5, -1.5)
    planet.castShadow = true
    gravitationGroup.add(planet)

    // Satellite en orbite
    const satellite = new THREE.Mesh(
      new THREE.SphereGeometry(0.05, 16, 16),
      new THREE.MeshStandardMaterial({ color: 0xF5A623 })
    )
    satellite.position.set(0.5, 1.5, -1.5)
    gravitationGroup.add(satellite)

    // Orbite visible
    const orbitGeometry = new THREE.RingGeometry(0.45, 0.55, 64)
    const orbitMaterial = new THREE.MeshBasicMaterial({ 
      color: 0x888888, 
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.3
    })
    const orbit = new THREE.Mesh(orbitGeometry, orbitMaterial)
    orbit.rotation.x = -Math.PI / 2
    orbit.position.y = 1.5
    gravitationGroup.add(orbit)

    // Animation de l'orbite
    let angle = 0
    const animate = () => {
      angle += 0.02
      satellite.position.x = Math.cos(angle) * 0.5
      satellite.position.z = -1.5 + Math.sin(angle) * 0.5
      requestAnimationFrame(animate)
    }
    animate()

    scene.add(gravitationGroup)
    sceneObjectsRef.current.push(gravitationGroup)
  }

  const setupDefaultScene = (scene: THREE.Scene) => {
    // Objet par défaut amélioré
    const defaultGroup = new THREE.Group()
    
    const cube = new THREE.Mesh(
      new THREE.BoxGeometry(0.25, 0.25, 0.25),
      new THREE.MeshStandardMaterial({ 
        color: 0x6366f1,
        metalness: 0.4,
        roughness: 0.6
      })
    )
    cube.position.set(0, 1.5, -1.5)
    cube.castShadow = true
    defaultGroup.add(cube)

    // Animation de rotation
    const animate = () => {
      cube.rotation.x += 0.01
      cube.rotation.y += 0.01
      requestAnimationFrame(animate)
    }
    animate()

    scene.add(defaultGroup)
    sceneObjectsRef.current.push(defaultGroup)
  }

  if (error) {
    return (
      <Box p={4}>
        <Alert status="warning">
          <AlertIcon />
          <Text>{error}</Text>
        </Alert>
        <Text mt={4} fontSize="sm" color="gray.600">
          Pour utiliser la réalité augmentée, utilisez Chrome ou Edge sur un appareil Android avec ARCore.
        </Text>
      </Box>
    )
  }

  if (!isSupported) {
    return (
      <Box p={4} textAlign="center">
        <Text>Vérification du support WebXR...</Text>
      </Box>
    )
  }

  return (
    <Box ref={containerRef} w="100%" h="100%" position="relative">
      {isActive && (
        <VStack
          position="absolute"
          top={4}
          left={4}
          bg="blackAlpha.700"
          color="white"
          p={3}
          borderRadius="md"
          zIndex={10}
        >
          <Text fontSize="sm" fontWeight="bold">Mode AR Actif</Text>
          <Text fontSize="xs">Déplacez votre appareil pour explorer</Text>
        </VStack>
      )}
      
      {/* Contrôles AR */}
      <ARControls
        isARActive={isActive}
        onRotate={() => {
          sceneObjectsRef.current.forEach(obj => {
            obj.rotation.y += Math.PI / 4
          })
        }}
        onZoomIn={() => {
          currentScaleRef.current = Math.min(currentScaleRef.current * 1.2, 2)
          sceneObjectsRef.current.forEach(obj => {
            obj.scale.setScalar(currentScaleRef.current)
          })
        }}
        onZoomOut={() => {
          currentScaleRef.current = Math.max(currentScaleRef.current / 1.2, 0.5)
          sceneObjectsRef.current.forEach(obj => {
            obj.scale.setScalar(currentScaleRef.current)
          })
        }}
        onReset={() => {
          currentScaleRef.current = 1
          sceneObjectsRef.current.forEach(obj => {
            obj.scale.setScalar(1)
            obj.rotation.set(0, 0, 0)
            obj.position.set(0, 1.5, -1.5)
          })
        }}
        onClose={() => {
          if (rendererRef.current?.xr?.isPresenting) {
            rendererRef.current.xr.getSession()?.end()
          }
          onAREnd?.()
        }}
      />
    </Box>
  )
}

export default WebARViewer

