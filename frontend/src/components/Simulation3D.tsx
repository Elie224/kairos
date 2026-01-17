import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Stars, Text } from '@react-three/drei'
import React, { Suspense, useRef, useEffect, useState, useMemo } from 'react'
import { Box, Text as ChakraText, Spinner, VStack, HStack, Progress, Badge } from '@chakra-ui/react'
import * as THREE from 'three'
import { ModuleContent } from '../types/moduleContent'

interface Module {
  id?: string
  title?: string
  content?: ModuleContent
  subject: string
}

interface Simulation3DProps {
  module: Module
  visualizationData?: any
  onGenerateVisualization?: (moduleId: string, subject: string, concept: string) => Promise<void>
}

const Simulation3D = ({ module, visualizationData, onGenerateVisualization }: Simulation3DProps) => {
  const subject = module.subject?.toLowerCase()
  const [isGenerating, setIsGenerating] = useState(false)
  
  // Générer la visualisation avec OpenAI si elle n'existe pas encore
  useEffect(() => {
    if (!visualizationData && onGenerateVisualization && module.id && !isGenerating) {
      setIsGenerating(true)
      const concept = module.title || module.content?.scene || 'default'
      onGenerateVisualization(module.id, subject, concept)
        .finally(() => setIsGenerating(false))
    }
  }, [module.id, subject, visualizationData, onGenerateVisualization, isGenerating])
  
  // Afficher un loader pendant la génération
  if (isGenerating || (!visualizationData && onGenerateVisualization)) {
    return (
      <Box h="100%" w="100%" display="flex" alignItems="center" justifyContent="center" bg="gray.900">
        <Box textAlign="center">
          <Spinner size="xl" color="blue.400" thickness="4px" mb={4} />
          <ChakraText color="white" fontSize="sm">
            Génération de la simulation 3D par l'IA...
          </ChakraText>
          <ChakraText color="gray.400" fontSize="xs" mt={2}>
            Création d'une visualisation 3D interactive personnalisée
          </ChakraText>
        </Box>
      </Box>
    )
  }
  
  const renderScene = () => {
    // Utiliser les données générées par OpenAI si disponibles
    const sceneType = visualizationData?.scene_type || 
                     visualizationData?.type || 
                     visualizationData?.visualization?.type ||
                     visualizationData?.visualization_3d?.type ||
                     module.content?.scene || 
                     'default'
    
    const subjectLower = module.subject?.toLowerCase()
    
    // Mapper les scènes selon la matière et les données générées par OpenAI
    switch (subjectLower) {
      case 'physics':
        if (visualizationData?.visualization_3d?.type === 'gravitation' || sceneType === 'gravitation') {
          return <GravitationSimulation visualizationData={visualizationData} />
        } else {
          return <MechanicsSimulation visualizationData={visualizationData} />
        }
      
      case 'chemistry':
        return <ChemicalReaction visualizationData={visualizationData} />
      
      case 'mathematics':
        return <MathematicsSimulation3D visualizationData={visualizationData} />
      
      case 'computer_science':
        return <ComputerScienceSimulation3D visualizationData={visualizationData} />
      
      case 'biology':
        return <BiologySimulation3D visualizationData={visualizationData} />
      
      case 'geography':
        return <GeographySimulation3D visualizationData={visualizationData} />
      
      case 'economics':
        return <EconomicsSimulation3D visualizationData={visualizationData} />
      
      case 'history':
        return <HistorySimulation3D visualizationData={visualizationData} />
      
      default:
        return <DefaultScene />
    }
  }

  // Gestion du contexte WebGL perdu
  useEffect(() => {
    const handleContextLost = (event: Event) => {
      event.preventDefault()
      logger.warn('Contexte WebGL perdu, tentative de récupération', null, 'Simulation3D')
    }

    const handleContextRestored = () => {
      logger.info('Contexte WebGL restauré avec succès', null, 'Simulation3D')
      // Forcer un re-render pour réinitialiser la scène
      if (onGenerateVisualization && module.id && visualizationData) {
        const concept = module.title || module.content?.scene || 'default'
        onGenerateVisualization(module.id, subject, concept)
      }
    }

    // Écouter les événements de perte/restauration du contexte
    const canvas = document.querySelector('canvas')
    if (canvas) {
      canvas.addEventListener('webglcontextlost', handleContextLost)
      canvas.addEventListener('webglcontextrestored', handleContextRestored)
    }

    return () => {
      if (canvas) {
        canvas.removeEventListener('webglcontextlost', handleContextLost)
        canvas.removeEventListener('webglcontextrestored', handleContextRestored)
      }
    }
  }, [module.id, subject, visualizationData, onGenerateVisualization])

  return (
    <Box h="100%" w="100%" position="relative">
      <Canvas
        gl={{ 
          antialias: true, 
          alpha: false,
          preserveDrawingBuffer: false, // Libérer la mémoire
          powerPreference: 'high-performance', // Utiliser GPU haute performance si disponible
          failIfMajorPerformanceCaveat: false, // Ne pas échouer si performance limitée
        }}
        dpr={[1, 2]}
        onCreated={({ gl }) => {
          gl.setClearColor('#000000')
          // Limiter la taille du viewport pour éviter les pertes de contexte
          const maxSize = 4096 // Limite WebGL standard
          if (gl.drawingBufferWidth > maxSize || gl.drawingBufferHeight > maxSize) {
            logger.warn(
              `Viewport trop grand: ${gl.drawingBufferWidth}x${gl.drawingBufferHeight}. Limitation à ${maxSize}x${maxSize}`,
              null,
              'Simulation3D'
            )
          }
        }}
      >
        <Suspense fallback={
          <mesh>
            <boxGeometry args={[1, 1, 1]} />
            <meshStandardMaterial color="#6366f1" />
          </mesh>
        }>
          <PerspectiveCamera makeDefault position={[0, 0, 5]} fov={75} />
          <ambientLight intensity={0.6} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} />
          <Stars radius={100} depth={50} count={5000} factor={4} fade speed={1} />
          {renderScene()}
          <OrbitControls 
            enableZoom={true} 
            enablePan={true} 
            enableRotate={true}
            minDistance={2}
            maxDistance={20}
            autoRotate={false}
          />
        </Suspense>
      </Canvas>
      {/* Indicateur de chargement si nécessaire */}
      <Box
        position="absolute"
        top={2}
        right={2}
        bg="blackAlpha.600"
        color="white"
        px={3}
        py={1}
        borderRadius="md"
        fontSize="xs"
      >
        {module.subject === 'physics' ? '⚙️ Physique' : 
         module.subject === 'chemistry' ? '🧪 Chimie' :
         module.subject === 'mathematics' ? '📐 Mathématiques' :
         module.subject === 'computer_science' ? '🤖 Informatique' :
         module.subject === 'biology' ? '🧬 Biologie' :
         module.subject === 'geography' ? '🌍 Géographie' :
         module.subject === 'economics' ? '💰 Économie' :
         module.subject === 'history' ? '🏛️ Histoire' : '📊 Simulation 3D'}
      </Box>
    </Box>
  )
}

// Simulation de gravitation avec animation - TRÈS RÉALISTE
const GravitationSimulation = ({ visualizationData }: { visualizationData?: any }) => {
  const satelliteRef1 = useRef<THREE.Mesh>(null)
  const satelliteRef2 = useRef<THREE.Mesh>(null)
  const planetRef = useRef<THREE.Mesh>(null)
  
  // Utiliser les paramètres générés par OpenAI si disponibles
  const orbitRadius1 = visualizationData?.visualization_3d?.parameters?.radius || 
                       visualizationData?.parameters?.orbit_radius || 
                       3.5
  const orbitRadius2 = orbitRadius1 * 1.8 // Orbite extérieure
  const orbitSpeed1 = visualizationData?.visualization_3d?.parameters?.speed || 
                      visualizationData?.parameters?.orbit_speed || 
                      0.8
  const orbitSpeed2 = orbitSpeed1 * 0.6 // Plus lent pour l'orbite extérieure (loi de Kepler)
  
  useFrame((state) => {
    const time = state.clock.getElapsedTime()
    
    // Planète en rotation
    if (planetRef.current) {
      planetRef.current.rotation.y += 0.005
    }
    
    // Satellite 1 - orbite circulaire
    if (satelliteRef1.current) {
      satelliteRef1.current.position.x = Math.cos(time * orbitSpeed1) * orbitRadius1
      satelliteRef1.current.position.z = Math.sin(time * orbitSpeed1) * orbitRadius1
      satelliteRef1.current.rotation.y += 0.02
    }
    
    // Satellite 2 - orbite elliptique (plus réaliste)
    if (satelliteRef2.current) {
      const eccentricity = 0.3 // Excentricité
      const a = orbitRadius2 / (1 - eccentricity) // Demi-grand axe
      const angle = time * orbitSpeed2
      const r = a * (1 - eccentricity * eccentricity) / (1 + eccentricity * Math.cos(angle))
      satelliteRef2.current.position.x = Math.cos(angle) * r
      satelliteRef2.current.position.z = Math.sin(angle) * r * 0.8 // Ellipse aplatie
      satelliteRef2.current.rotation.y += 0.015
    }
  })

  return (
    <>
      {/* Planète centrale avec atmosphère - TRÈS RÉALISTE */}
      <group ref={planetRef}>
        {/* Atmosphère (sphère plus grande et transparente) */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.65, 64, 64]} />
          <meshStandardMaterial 
            color="#87CEEB" 
            transparent 
            opacity={0.15}
            emissive="#4A90E2"
            emissiveIntensity={0.1}
          />
        </mesh>
        
        {/* Planète principale avec détails de surface */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[0.6, 64, 64]} />
          <meshStandardMaterial 
            color={visualizationData?.visualization_3d?.parameters?.planet_color || "#4A90E2"}
            roughness={0.7}
            metalness={0.1}
          />
        </mesh>
        
        {/* Continents/textures de surface simulés */}
        {Array.from({ length: 8 }).map((_, i) => {
          const angle1 = (i / 8) * Math.PI * 2
          const angle2 = Math.random() * Math.PI
          const radius = 0.61
          const x = Math.cos(angle1) * Math.sin(angle2) * radius
          const y = Math.cos(angle2) * radius
          const z = Math.sin(angle1) * Math.sin(angle2) * radius
          return (
            <mesh key={i} position={[x, y, z]}>
              <sphereGeometry args={[0.08, 16, 16]} />
              <meshStandardMaterial color="#2ECC71" roughness={0.8} />
            </mesh>
          )
        })}
      </group>
      
      {/* Satellite 1 - orbite circulaire */}
      <mesh ref={satelliteRef1} position={[orbitRadius1, 0, 0]}>
        <sphereGeometry args={[0.15, 32, 32]} />
        <meshStandardMaterial 
          color={visualizationData?.visualization_3d?.parameters?.satellite_color || "#F5A623"}
          emissive="#F5A623"
          emissiveIntensity={0.3}
          metalness={0.5}
        />
      </mesh>
      
      {/* Panneaux solaires du satellite 1 */}
      <group ref={satelliteRef1}>
        <mesh position={[orbitRadius1 + 0.2, 0, 0]} rotation={[0, 0, Math.PI / 4]}>
          <boxGeometry args={[0.3, 0.01, 0.3]} />
          <meshStandardMaterial color="#1E88E5" emissive="#64B5F6" emissiveIntensity={0.5} />
        </mesh>
      </group>
      
      {/* Satellite 2 - orbite elliptique */}
      <mesh ref={satelliteRef2} position={[orbitRadius2, 0, 0]}>
        <sphereGeometry args={[0.12, 32, 32]} />
        <meshStandardMaterial 
          color="#E74C3C"
          emissive="#E74C3C"
          emissiveIntensity={0.25}
          metalness={0.4}
        />
      </mesh>
      
      {/* Orbites visibles - TRÈS RÉALISTES */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[orbitRadius1 - 0.05, orbitRadius1 + 0.05, 128]} />
        <meshBasicMaterial color="#888" side={2} transparent opacity={0.4} />
      </mesh>
      
      <mesh rotation={[Math.PI / 2, 0, 0]} scale={[1, 0.8, 1]}>
        <torusGeometry args={[orbitRadius2, 0.05, 8, 128]} />
        <meshBasicMaterial color="#999" side={2} transparent opacity={0.3} />
      </mesh>
      
      {/* Champ gravitationnel visuel (lignes de force) */}
      {Array.from({ length: 16 }).map((_, i) => {
        const angle = (i / 16) * Math.PI * 2
        const points = [
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(Math.cos(angle) * 5, 0, Math.sin(angle) * 5)
        ]
        return (
          <line key={i}>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                count={points.length}
                array={new Float32Array(points.flatMap(p => [p.x, p.y, p.z]))}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial 
              color="#4A90E2" 
              opacity={0.2} 
              transparent 
              linewidth={1}
            />
          </line>
        )
      })}
      
      {/* Étoiles en arrière-plan */}
      {Array.from({ length: 100 }).map((_, i) => {
        const radius = 8 + Math.random() * 4
        const theta = Math.random() * Math.PI * 2
        const phi = Math.acos(Math.random() * 2 - 1)
        const x = radius * Math.sin(phi) * Math.cos(theta)
        const y = radius * Math.sin(phi) * Math.sin(theta)
        const z = radius * Math.cos(phi)
        return (
          <mesh key={i} position={[x, y, z]}>
            <sphereGeometry args={[0.02, 8, 8]} />
            <meshBasicMaterial color="#FFFFFF" />
          </mesh>
        )
      })}
    </>
  )
}

// Formes géométriques avec rotation
const GeometricShapes = () => {
  const cubeRef = useRef<THREE.Mesh>(null)
  const sphereRef = useRef<THREE.Mesh>(null)
  const cylinderRef = useRef<THREE.Mesh>(null)
  
  useFrame(() => {
    if (cubeRef.current) cubeRef.current.rotation.x += 0.01
    if (cubeRef.current) cubeRef.current.rotation.y += 0.01
    if (sphereRef.current) sphereRef.current.rotation.y += 0.02
    if (cylinderRef.current) cylinderRef.current.rotation.z += 0.015
  })

  return (
    <>
      <mesh ref={cubeRef} position={[-2, 0, 0]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="#E74C3C" />
      </mesh>
      
      <mesh ref={sphereRef} position={[0, 0, 0]}>
        <sphereGeometry args={[0.7, 32, 32]} />
        <meshStandardMaterial color="#3498DB" />
      </mesh>
      
      <mesh ref={cylinderRef} position={[2, 0, 0]} rotation={[0, 0, Math.PI / 4]}>
        <cylinderGeometry args={[0.5, 0.5, 1.5, 32]} />
        <meshStandardMaterial color="#2ECC71" />
      </mesh>
    </>
  )
}

// Réaction chimique - TRÈS RÉALISTE avec liaisons atomiques
const ChemicalReaction = ({ visualizationData }: { visualizationData?: any }) => {
  const moleculeGroupRef = useRef<THREE.Group>(null)
  const [reactionProgress, setReactionProgress] = useState(0)
  
  useEffect(() => {
    const interval = setInterval(() => {
      setReactionProgress((prev) => (prev + 0.01) % 1)
    }, 50)
    return () => clearInterval(interval)
  }, [])
  
  useFrame(() => {
    if (moleculeGroupRef.current) {
      moleculeGroupRef.current.rotation.y += 0.005
    }
  })
  
  // Molécule H2O (eau) - TRÈS DÉTAILLÉE
  const createWaterMolecule = (position: [number, number, number]) => (
    <group key={`water-${position[0]}`} position={position}>
      {/* Atome O (oxygène) - centre */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.25, 32, 32]} />
        <meshStandardMaterial 
          color="#FF4444" 
          emissive="#FF4444"
          emissiveIntensity={0.2}
          metalness={0.3}
          roughness={0.5}
        />
      </mesh>
      
      {/* Atomes H (hydrogène) - position angulaire réaliste (104.5°) */}
      {[
        { angle: -52.25 * (Math.PI / 180), dist: 0.58 },
        { angle: 52.25 * (Math.PI / 180), dist: 0.58 }
      ].map((h, i) => {
        const x = Math.cos(h.angle) * h.dist
        const z = Math.sin(h.angle) * h.dist
        return (
          <group key={`h-${i}`}>
            <mesh position={[x, 0, z]}>
              <sphereGeometry args={[0.15, 32, 32]} />
              <meshStandardMaterial 
                color="#4ECDC4" 
                emissive="#4ECDC4"
                emissiveIntensity={0.15}
              />
            </mesh>
            {/* Liaison covalente O-H */}
            <line>
              <bufferGeometry>
                <bufferAttribute
                  attach="attributes-position"
                  count={2}
                  array={new Float32Array([0, 0, 0, x, 0, z])}
                  itemSize={3}
                />
              </bufferGeometry>
              <lineBasicMaterial color="#CCCCCC" linewidth={3} />
            </line>
          </group>
        )
      })}
    </group>
  )
  
  // Molécule CO2 (dioxyde de carbone) - TRÈS DÉTAILLÉE
  const createCO2Molecule = (position: [number, number, number]) => (
    <group key={`co2-${position[0]}`} position={position}>
      {/* Atome C (carbone) - centre */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.2, 32, 32]} />
        <meshStandardMaterial 
          color="#333333" 
          emissive="#333333"
          emissiveIntensity={0.1}
          metalness={0.4}
        />
      </mesh>
      
      {/* Atomes O (oxygène) - linéaire */}
      {[-0.6, 0.6].map((offset, i) => (
        <group key={`o-${i}`}>
          <mesh position={[offset, 0, 0]}>
            <sphereGeometry args={[0.22, 32, 32]} />
            <meshStandardMaterial 
              color="#FF4444" 
              emissive="#FF4444"
              emissiveIntensity={0.2}
            />
          </mesh>
          {/* Double liaison C=O */}
          {[0, 0.15].map((yOffset, bondIdx) => (
            <line key={`bond-${i}-${bondIdx}`}>
              <bufferGeometry>
                <bufferAttribute
                  attach="attributes-position"
                  count={2}
                  array={new Float32Array([0, yOffset, 0, offset, yOffset, 0])}
                  itemSize={3}
                />
              </bufferGeometry>
              <lineBasicMaterial color="#AAAAAA" linewidth={2} />
            </line>
          ))}
        </group>
      ))}
    </group>
  )
  
  // Animation de la réaction
  const animationX = -2 + reactionProgress * 4

  return (
    <>
      <ambientLight intensity={0.8} />
      <pointLight position={[5, 5, 5]} intensity={1.5} />
      <pointLight position={[-5, -5, -5]} intensity={0.8} />
      
      {/* Réactants - H2O à gauche (animation) */}
      <group position={[animationX < 0 ? animationX : -2, 0, 0]}>
        {createWaterMolecule([0, 0, 0])}
      </group>
      
      {/* Flèche de réaction animée */}
      <group position={[0, 0, 0]}>
        {/* Corps de la flèche */}
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[1.5, 0.08, 0.08]} />
          <meshStandardMaterial color="#95A5A6" />
        </mesh>
        {/* Pointe de la flèche */}
        <mesh position={[0.75, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
          <coneGeometry args={[0.15, 0.4, 8]} />
          <meshStandardMaterial color="#95A5A6" />
        </mesh>
        {/* Particules de réaction animées */}
        {Array.from({ length: 6 }).map((_, i) => {
          const angle = (i / 6) * Math.PI * 2 + reactionProgress * Math.PI * 2
          const radius = 0.3 + Math.sin(reactionProgress * Math.PI * 4) * 0.1
          return (
            <mesh 
              key={`particle-${i}`} 
              position={[
                Math.cos(angle) * radius, 
                Math.sin(angle) * radius, 
                0
              ]}
            >
              <sphereGeometry args={[0.03, 8, 8]} />
              <meshStandardMaterial 
                color="#FFD700" 
                emissive="#FFD700"
                emissiveIntensity={0.8}
              />
            </mesh>
          )
        })}
      </group>
      
      {/* Produits - CO2 à droite */}
      <group position={[2, 0, 0]} ref={moleculeGroupRef}>
        {createCO2Molecule([0, 0, 0])}
      </group>
      
      {/* Énergie de réaction - zone d'activation */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.8, 32, 32]} />
        <meshStandardMaterial 
          color="#FFD700" 
          transparent 
          opacity={0.1 * Math.sin(reactionProgress * Math.PI * 2)}
          emissive="#FFD700"
          emissiveIntensity={0.2}
        />
      </mesh>
    </>
  )
}

// Grammaire anglaise interactive
const EnglishGrammar = () => {
  return (
    <>
      {/* Structure de phrase */}
      <mesh position={[-2, 0, 0]}>
        <boxGeometry args={[0.8, 0.3, 0.1]} />
        <meshStandardMaterial color="#FF6B6B" />
      </mesh>
      <Text position={[-2, 0.5, 0]} fontSize={0.3} color="white">
        Sujet
      </Text>
      
      <mesh position={[-0.5, 0, 0]}>
        <boxGeometry args={[0.8, 0.3, 0.1]} />
        <meshStandardMaterial color="#4ECDC4" />
      </mesh>
      <Text position={[-0.5, 0.5, 0]} fontSize={0.3} color="white">
        Verbe
      </Text>
      
      <mesh position={[1, 0, 0]}>
        <boxGeometry args={[0.8, 0.3, 0.1]} />
        <meshStandardMaterial color="#95E1D3" />
      </mesh>
      <Text position={[1, 0.5, 0]} fontSize={0.3} color="white">
        Complément
      </Text>
      
      {/* Flèche */}
      <mesh position={[0, -1, 0]} rotation={[0, 0, Math.PI / 2]}>
        <boxGeometry args={[0.1, 2, 0.1]} />
        <meshStandardMaterial color="#F38181" />
      </mesh>
    </>
  )
}

// Simulation de mécanique classique
const MechanicsSimulation = ({ visualizationData }: { visualizationData?: any }) => {
  const pendulumRef = useRef<THREE.Group>(null)
  const fallingObjectRef = useRef<THREE.Mesh>(null)
  const springRef = useRef<THREE.Group>(null)
  const forceVectorRef = useRef<THREE.Group>(null)
  
  useFrame((state) => {
    const t = state.clock.getElapsedTime()
    
    // Pendule oscillant (mouvement harmonique simple)
    if (pendulumRef.current) {
      const amplitude = Math.PI / 4 // 45 degrés
      const frequency = 1.5 // Hz
      const angle = amplitude * Math.cos(frequency * t)
      pendulumRef.current.rotation.z = angle
    }
    
    // Objet en chute libre
    if (fallingObjectRef.current) {
      const gravity = 9.8
      const initialHeight = 3
      const cycleTime = t % 2.5
      const y = initialHeight - 0.5 * gravity * cycleTime * cycleTime
      if (y < -2) {
        fallingObjectRef.current.position.y = initialHeight
      } else {
        fallingObjectRef.current.position.y = y
      }
      
      // Mettre à jour le vecteur de force
      if (forceVectorRef.current) {
        forceVectorRef.current.position.y = y
      }
    }
    
    // Ressort oscillant
    if (springRef.current) {
      const amplitude = 0.5
      const frequency = 2
      const offset = amplitude * Math.sin(frequency * t)
      springRef.current.position.y = offset
    }
  })

  return (
    <>
      {/* Sol */}
      <mesh position={[0, -2.5, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#4a5568" />
      </mesh>
      
      {/* Pendule */}
      <group ref={pendulumRef} position={[-3, 2, 0]}>
        {/* Point de suspension */}
        <mesh position={[0, 0.5, 0]}>
          <sphereGeometry args={[0.1, 16, 16]} />
          <meshStandardMaterial color="#e2e8f0" />
        </mesh>
        
        {/* Fil du pendule */}
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={2}
              array={new Float32Array([0, 0.5, 0, 0, -1.5, 0])}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#cbd5e0" linewidth={2} />
        </line>
        
        {/* Masse du pendule */}
        <mesh position={[0, -1.5, 0]}>
          <sphereGeometry args={[0.3, 32, 32]} />
          <meshStandardMaterial color="#f56565" />
        </mesh>
      </group>
      
      {/* Objet en chute libre */}
      <mesh ref={fallingObjectRef} position={[0, 3, 0]}>
        <boxGeometry args={[0.4, 0.4, 0.4]} />
        <meshStandardMaterial color="#4299e1" />
      </mesh>
      
      {/* Vecteur de force gravitationnelle */}
      <group ref={forceVectorRef} position={[0, 3, 0]}>
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={2}
              array={new Float32Array([0, 0, 0, 0, -0.8, 0])}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#48bb78" linewidth={3} />
        </line>
        
        {/* Flèche de force */}
        <mesh position={[0, -0.8, 0]}>
          <coneGeometry args={[0.1, 0.2, 8]} />
          <meshStandardMaterial color="#48bb78" />
        </mesh>
      </group>
      
      {/* Ressort oscillant */}
      <group ref={springRef} position={[3, 0, 0]}>
        {/* Support fixe */}
        <mesh position={[0, 1.5, 0]}>
          <boxGeometry args={[0.6, 0.2, 0.6]} />
          <meshStandardMaterial color="#718096" />
        </mesh>
        
        {/* Ressort (représenté par des sphères en spirale) */}
        {Array.from({ length: 10 }).map((_, i) => {
          const y = 1.5 - (i * 0.15)
          const x = Math.sin(i * 0.5) * 0.1
          return (
            <mesh key={i} position={[x, y, 0]}>
              <sphereGeometry args={[0.05, 8, 8]} />
              <meshStandardMaterial color="#ed8936" />
            </mesh>
          )
        })}
        
        {/* Masse suspendue */}
        <mesh position={[0, 0, 0]}>
          <boxGeometry args={[0.5, 0.5, 0.5]} />
          <meshStandardMaterial color="#9f7aea" />
        </mesh>
      </group>
      
      {/* Légendes avec Text */}
      <Text position={[-3, 3.5, 0]} fontSize={0.2} color="white" anchorX="center">
        Pendule
      </Text>
      <Text position={[0, 4.5, 0]} fontSize={0.2} color="white" anchorX="center">
        Chute libre
      </Text>
      <Text position={[3, 2.5, 0]} fontSize={0.2} color="white" anchorX="center">
        Ressort
      </Text>
    </>
  )
}

// Scène par défaut
const DefaultScene = () => {
  return (
    <>
      <mesh>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="#6366f1" />
      </mesh>
    </>
  )
}

// Simulation 3D pour les mathématiques - TRÈS RÉALISTE avec surfaces 3D complexes
const MathematicsSimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  const surfaceRef = useRef<THREE.Group>(null)
  const [animationProgress, setAnimationProgress] = useState(0)
  
  useEffect(() => {
    const interval = setInterval(() => {
      setAnimationProgress((prev) => (prev + 0.01) % (Math.PI * 2))
    }, 50)
    return () => clearInterval(interval)
  }, [])
  
  useFrame(() => {
    if (surfaceRef.current) {
      surfaceRef.current.rotation.y += 0.002
    }
  })
  
  // Surface 3D complexe - Paraboloïde hyperbolique (selle de cheval)
  const createSurface = () => {
    const resolution = 50
    const size = 4
    const vertices: number[] = []
    const indices: number[] = []
    
    for (let i = 0; i <= resolution; i++) {
      for (let j = 0; j <= resolution; j++) {
        const x = (i / resolution) * size - size / 2
        const z = (j / resolution) * size - size / 2
        // Fonction mathématique : f(x,z) = x² - z² (paraboloïde hyperbolique)
        const y = (x * x - z * z) * 0.3 + Math.sin(animationProgress + x * 0.5) * 0.2
        vertices.push(x, y, z)
        
        if (i < resolution && j < resolution) {
          const a = i * (resolution + 1) + j
          const b = a + 1
          const c = a + resolution + 1
          const d = c + 1
          
          indices.push(a, b, c)
          indices.push(b, d, c)
        }
      }
    }
    
    return { vertices, indices }
  }
  
  const { vertices, indices } = createSurface()
  
  // Courbe paramétrique 3D - Hélice
  const createHelix = () => {
    const points: number[] = []
    const numPoints = 100
    for (let i = 0; i <= numPoints; i++) {
      const t = (i / numPoints) * Math.PI * 4 + animationProgress
      const radius = 1.5
      const x = Math.cos(t) * radius
      const y = t * 0.3 - Math.PI * 2 * 0.3
      const z = Math.sin(t) * radius
      points.push(x, y, z)
    }
    return points
  }
  
  const helixPoints = createHelix()

  return (
    <>
      <ambientLight intensity={0.6} />
      <pointLight position={[5, 5, 5]} intensity={1.2} />
      <pointLight position={[-5, -5, -5]} intensity={0.6} />
      <directionalLight position={[0, 10, 0]} intensity={0.5} />
      
      <gridHelper args={[10, 10, '#888888', '#444444']} />
      <axesHelper args={[5]} />
      
      {/* Surface 3D complexe - TRÈS RÉALISTE */}
      <group ref={surfaceRef} position={[0, 0, 0]}>
        <mesh>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={vertices.length / 3}
              array={new Float32Array(vertices)}
              itemSize={3}
            />
            <bufferAttribute
              attach="index"
              count={indices.length}
              array={new Uint16Array(indices)}
              itemSize={1}
            />
          </bufferGeometry>
          <meshStandardMaterial 
            color="#805AD5" 
            wireframe={false}
            side={2}
            transparent
            opacity={0.8}
            metalness={0.3}
            roughness={0.4}
          />
        </mesh>
        
        {/* Lignes de contour de la surface */}
        <lineSegments>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={vertices.length / 3}
              array={new Float32Array(vertices)}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#805AD5" opacity={0.3} transparent />
        </lineSegments>
      </group>
      
      {/* Courbe paramétrique 3D - Hélice */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={helixPoints.length / 3}
            array={new Float32Array(helixPoints)}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#E74C3C" linewidth={3} />
      </line>
      
      {/* Points sur l'hélice pour visualisation */}
      {Array.from({ length: 20 }).map((_, i) => {
        const t = (i / 20) * Math.PI * 4 + animationProgress
        const radius = 1.5
        return (
          <mesh 
            key={i}
            position={[
              Math.cos(t) * radius,
              t * 0.3 - Math.PI * 2 * 0.3,
              Math.sin(t) * radius
            ]}
          >
            <sphereGeometry args={[0.06, 16, 16]} />
            <meshStandardMaterial color="#E74C3C" emissive="#E74C3C" emissiveIntensity={0.5} />
          </mesh>
        )
      })}
      
      {/* Formes géométriques 3D avancées */}
      <group position={[-3.5, 2, 0]}>
        {/* Tore (donut) */}
        <mesh rotation={[Math.PI / 2, animationProgress, 0]}>
          <torusGeometry args={[0.4, 0.2, 16, 32]} />
          <meshStandardMaterial color="#E74C3C" metalness={0.5} roughness={0.3} />
        </mesh>
      </group>
      
      <group position={[3.5, 2, 0]}>
        {/* Icosaèdre */}
        <mesh rotation={[animationProgress, animationProgress * 0.5, 0]}>
          <icosahedronGeometry args={[0.6, 1]} />
          <meshStandardMaterial 
            color="#3498DB" 
            wireframe={true}
            transparent
            opacity={0.7}
          />
        </mesh>
        <mesh rotation={[animationProgress, animationProgress * 0.5, 0]}>
          <icosahedronGeometry args={[0.6, 0]} />
          <meshStandardMaterial color="#3498DB" metalness={0.6} roughness={0.2} />
        </mesh>
      </group>
      
      {/* Labels mathématiques */}
      <Text position={[-3.5, 3, 0]} fontSize={0.15} color="white" anchorX="center">
        Tore
      </Text>
      <Text position={[3.5, 3, 0]} fontSize={0.15} color="white" anchorX="center">
        Icosaèdre
      </Text>
      <Text position={[0, -2.5, 0]} fontSize={0.15} color="white" anchorX="center">
        z = x² - z²
      </Text>
    </>
  )
}

// Simulation 3D pour l'informatique - TRÈS RÉALISTE (réseaux de neurones, structures de données)
const ComputerScienceSimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  const networkRef = useRef<THREE.Group>(null)
  const [step, setStep] = useState(0)
  const [pulse, setPulse] = useState(0)
  
  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev + 1) % 10)
    }, 800)
    return () => clearInterval(interval)
  }, [])
  
  useEffect(() => {
    const interval = setInterval(() => {
      setPulse((prev) => (prev + 0.1) % (Math.PI * 2))
    }, 50)
    return () => clearInterval(interval)
  }, [])
  
  useFrame(() => {
    if (networkRef.current) {
      networkRef.current.rotation.y += 0.001
    }
  })
  
  // Réseau de neurones 3D - TRÈS RÉALISTE
  const createNeuralNetwork = () => {
    const layers = [4, 6, 4, 2] // Input, Hidden1, Hidden2, Output
    const layerSpacing = 2.5
    const nodeSpacing = 1.2
    const nodes: any[] = []
    const connections: any[] = []
    
    layers.forEach((nodeCount, layerIdx) => {
      const x = (layerIdx - (layers.length - 1) / 2) * layerSpacing
      const startY = -((nodeCount - 1) * nodeSpacing) / 2
      
      for (let nodeIdx = 0; nodeIdx < nodeCount; nodeIdx++) {
        const y = startY + nodeIdx * nodeSpacing
        nodes.push({ layer: layerIdx, index: nodeIdx, x, y, z: 0 })
        
        // Connexions avec la couche suivante
        if (layerIdx < layers.length - 1) {
          const nextLayerCount = layers[layerIdx + 1]
          const nextStartY = -((nextLayerCount - 1) * nodeSpacing) / 2
          const nextX = ((layerIdx + 1) - (layers.length - 1) / 2) * layerSpacing
          
          for (let nextIdx = 0; nextIdx < nextLayerCount; nextIdx++) {
            const nextY = nextStartY + nextIdx * nodeSpacing
            connections.push({
              from: { x, y, z: 0 },
              to: { x: nextX, y: nextY, z: 0 },
              weight: Math.random() * 0.5 + 0.5,
              active: layerIdx === step % (layers.length - 1) && nodeIdx === (step % nodeCount)
            })
          }
        }
      }
    })
    
    return { nodes, connections }
  }
  
  const { nodes, connections } = createNeuralNetwork()
  const arrayData = [8, 3, 6, 2, 5, 1, 9, 4]

  return (
    <>
      <ambientLight intensity={0.6} />
      <pointLight position={[5, 5, 5]} intensity={1.5} />
      <pointLight position={[-5, -5, -5]} intensity={0.8} />
      
      <gridHelper args={[12, 12, '#888888', '#444444']} />
      
      {/* Réseau de neurones 3D - TRÈS RÉALISTE */}
      <group ref={networkRef} position={[0, 0, -1]}>
        {/* Connexions entre neurones */}
        {connections.map((conn, idx) => {
          const isActive = conn.active && Math.sin(pulse) > 0
          const points = [
            new THREE.Vector3(conn.from.x, conn.from.y, conn.from.z),
            new THREE.Vector3(conn.to.x, conn.to.y, conn.to.z)
          ]
          return (
            <line key={`conn-${idx}`}>
              <bufferGeometry>
                <bufferAttribute
                  attach="attributes-position"
                  count={points.length}
                  array={new Float32Array(points.flatMap(p => [p.x, p.y, p.z]))}
                  itemSize={3}
                />
              </bufferGeometry>
              <lineBasicMaterial 
                color={isActive ? '#00FF00' : '#805AD5'} 
                linewidth={isActive ? 3 : 1}
                opacity={conn.weight}
                transparent
              />
            </line>
          )
        })}
        
        {/* Neurones (nœuds) */}
        {nodes.map((node, idx) => {
          const isActive = node.layer === (step % (nodes.length / nodes[0].index + 1))
          const activation = isActive ? 0.3 + Math.sin(pulse) * 0.2 : 0.1
          
          return (
            <group key={`node-${idx}`} position={[node.x, node.y, node.z]}>
              <mesh>
                <sphereGeometry args={[0.2, 32, 32]} />
                <meshStandardMaterial 
                  color={node.layer === 0 ? '#4ECDC4' : node.layer === nodes.length - 1 ? '#E74C3C' : '#805AD5'}
                  emissive={isActive ? '#805AD5' : '#000000'}
                  emissiveIntensity={activation}
                  metalness={0.4}
                  roughness={0.3}
                />
              </mesh>
              {/* Anneau d'activation */}
              {isActive && (
                <mesh>
                  <torusGeometry args={[0.25, 0.02, 8, 32]} />
                  <meshStandardMaterial 
                    color="#00FF00" 
                    emissive="#00FF00"
                    emissiveIntensity={0.8}
                    transparent
                    opacity={0.6}
                  />
                </mesh>
              )}
            </group>
          )
        })}
      </group>
      
      {/* Structure de données - Arbre binaire 3D */}
      <group position={[-6, 2, 0]}>
        <Text position={[0, 2, 0]} fontSize={0.2} color="white" anchorX="center">
          Arbre binaire
        </Text>
        
        {/* Structure de l'arbre binaire */}
        {[
          { value: 5, pos: [0, 1.5, 0], level: 0 },
          { value: 3, pos: [-1, 0.5, 0], level: 1, parent: [0, 1.5, 0] },
          { value: 7, pos: [1, 0.5, 0], level: 1, parent: [0, 1.5, 0] },
          { value: 2, pos: [-1.5, -0.5, 0], level: 2, parent: [-1, 0.5, 0] },
          { value: 4, pos: [-0.5, -0.5, 0], level: 2, parent: [-1, 0.5, 0] },
          { value: 6, pos: [0.5, -0.5, 0], level: 2, parent: [1, 0.5, 0] },
          { value: 8, pos: [1.5, -0.5, 0], level: 2, parent: [1, 0.5, 0] }
        ].map((node, idx) => (
          <group key={`tree-${idx}`}>
            {/* Connexion au parent */}
            {node.parent && (
              <line>
                <bufferGeometry>
                  <bufferAttribute
                    attach="attributes-position"
                    count={2}
                    array={new Float32Array([
                      node.parent[0], node.parent[1], node.parent[2],
                      node.pos[0], node.pos[1], node.pos[2]
                    ])}
                    itemSize={3}
                  />
                </bufferGeometry>
                <lineBasicMaterial color="#805AD5" linewidth={2} />
              </line>
            )}
            
            {/* Nœud de l'arbre */}
            <mesh position={node.pos}>
              <boxGeometry args={[0.4, 0.4, 0.4]} />
              <meshStandardMaterial 
                color={step % 7 === idx ? '#00FF00' : '#805AD5'} 
                emissive={step % 7 === idx ? '#00FF00' : '#000000'}
                emissiveIntensity={step % 7 === idx ? 0.5 : 0}
              />
            </mesh>
            
            <Text 
              position={[node.pos[0], node.pos[1], node.pos[2] + 0.3]} 
              fontSize={0.15} 
              color="white"
              anchorX="center"
              anchorY="middle"
            >
              {node.value}
            </Text>
          </group>
        ))}
      </group>
      
      {/* Tableau trié 3D */}
      <group position={[6, -2, 0]}>
        <Text position={[0, 1.5, 0]} fontSize={0.2} color="white" anchorX="center">
          Tri de tableau
        </Text>
        
        {arrayData.map((value, index) => {
          const x = (index - arrayData.length / 2) * 0.8
          const isActive = index === step % arrayData.length
          const height = (value / 10) * 1.5
          
          return (
            <group key={`array-${index}`} position={[x, height / 2 - 0.5, 0]}>
              <mesh>
                <boxGeometry args={[0.6, height, 0.6]} />
                <meshStandardMaterial 
                  color={isActive ? '#00FF00' : '#3498DB'} 
                  emissive={isActive ? '#00FF00' : '#000000'}
                  emissiveIntensity={isActive ? 0.4 : 0}
                />
              </mesh>
              
              <Text 
                position={[0, height / 2 + 0.2, 0.35]} 
                fontSize={0.15} 
                color="white"
                anchorX="center"
              >
                {value}
              </Text>
              
              <Text 
                position={[0, -height / 2 - 0.2, 0.35]} 
                fontSize={0.12} 
                color="#718096"
                anchorX="center"
              >
                [{index}]
              </Text>
            </group>
          )
        })}
      </group>
      
      {/* Labels */}
      <Text position={[0, -4.5, -1]} fontSize={0.18} color="white" anchorX="center">
        Réseau de Neurones | Arbre binaire | Tri de tableau
      </Text>
    </>
  )
}

// Simulation 3D pour la biologie - TRÈS RÉALISTE (cellule détaillée avec organites)
const BiologySimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  const cellRef = useRef<THREE.Group>(null)
  const [rotation, setRotation] = useState(0)
  
  useEffect(() => {
    const interval = setInterval(() => {
      setRotation((prev) => prev + 0.005)
    }, 50)
    return () => clearInterval(interval)
  }, [])
  
  useFrame(() => {
    if (cellRef.current) {
      cellRef.current.rotation.y += 0.002
    }
  })

  return (
    <>
      <ambientLight intensity={0.8} />
      <pointLight position={[5, 5, 5]} intensity={1.5} />
      <pointLight position={[-5, -5, -5]} intensity={0.8} />
      <directionalLight position={[0, 10, 0]} intensity={0.6} />
      
      <group ref={cellRef}>
        {/* Membrane cellulaire - TRÈS RÉALISTE */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[1.8, 64, 64]} />
          <meshStandardMaterial 
            color="#4ECDC4" 
            transparent 
            opacity={0.6}
            roughness={0.9}
            metalness={0.1}
          />
        </mesh>
        
        {/* Membrane interne (double couche lipidique) */}
        <mesh position={[0, 0, 0]}>
          <sphereGeometry args={[1.75, 64, 64]} />
          <meshStandardMaterial 
            color="#2ECC71" 
            transparent 
            opacity={0.3}
          />
        </mesh>
        
        {/* Noyau de la cellule - TRÈS DÉTAILLÉ */}
        <group position={[0, 0, 0]}>
          {/* Enveloppe nucléaire */}
          <mesh>
            <sphereGeometry args={[0.65, 64, 64]} />
            <meshStandardMaterial 
              color="#E74C3C" 
              transparent 
              opacity={0.7}
              roughness={0.8}
            />
          </mesh>
          
          {/* Membrane nucléaire interne */}
          <mesh>
            <sphereGeometry args={[0.62, 64, 64]} />
            <meshStandardMaterial 
              color="#C0392B" 
              transparent 
              opacity={0.5}
            />
          </mesh>
          
          {/* Chromosomes (structure en X) */}
          {Array.from({ length: 4 }).map((_, i) => {
            const angle = (i / 4) * Math.PI * 2
            const radius = 0.3
            const x = Math.cos(angle) * radius
            const z = Math.sin(angle) * radius
            return (
              <group key={`chromosome-${i}`} position={[x, 0, z]} rotation={[0, angle, 0]}>
                {/* Structure en X du chromosome */}
                {[
                  { x: -0.15, y: -0.1, z: 0 },
                  { x: 0.15, y: -0.1, z: 0 },
                  { x: -0.15, y: 0.1, z: 0 },
                  { x: 0.15, y: 0.1, z: 0 }
                ].map((pos, j) => (
                  <mesh key={`chr-part-${j}`} position={[pos.x, pos.y, pos.z]}>
                    <cylinderGeometry args={[0.03, 0.03, 0.15, 8]} />
                    <meshStandardMaterial color="#8E44AD" />
                  </mesh>
                ))}
                {/* Centre du chromosome */}
                <mesh position={[0, 0, 0]}>
                  <sphereGeometry args={[0.05, 16, 16]} />
                  <meshStandardMaterial color="#8E44AD" />
                </mesh>
              </group>
            )
          })}
        </group>
        
        {/* Organites - TRÈS RÉALISTES */}
        {/* Mitochondries (en forme de haricot) */}
        {[
          { angle: 0.8, radius: 1.3, z: 0.2 },
          { angle: 2.5, radius: 1.25, z: -0.15 },
          { angle: 4.2, radius: 1.35, z: 0.1 }
        ].map((mito, i) => (
          <group 
            key={`mitochondria-${i}`} 
            position={[
              Math.cos(mito.angle) * mito.radius,
              Math.sin(mito.angle) * mito.radius,
              mito.z
            ]}
          >
            {/* Forme de haricot pour mitochondrie */}
            <mesh rotation={[0, mito.angle, 0]}>
              <torusGeometry args={[0.12, 0.08, 16, 32, Math.PI]} />
              <meshStandardMaterial color="#F39C12" emissive="#F39C12" emissiveIntensity={0.2} />
            </mesh>
            {/* Crêtes internes */}
            {Array.from({ length: 5 }).map((_, j) => (
              <mesh 
                key={`cristae-${j}`} 
                position={[0, (j - 2) * 0.04, 0]} 
                rotation={[0, Math.PI / 2, 0]}
              >
                <planeGeometry args={[0.05, 0.15]} />
                <meshStandardMaterial color="#E67E22" transparent opacity={0.6} />
              </mesh>
            ))}
          </group>
        ))}
        
        {/* Réticulum endoplasmique (réseau de tubes) */}
        {Array.from({ length: 8 }).map((_, i) => {
          const angle = (i / 8) * Math.PI * 2
          const radius = 1.0 + Math.sin(i) * 0.2
          const x = Math.cos(angle) * radius
          const y = Math.sin(angle) * radius * 0.3
          const z = Math.sin(i * 0.5) * 0.4
          return (
            <mesh key={`er-${i}`} position={[x, y, z]} rotation={[0, angle, Math.PI / 4]}>
              <torusGeometry args={[0.1, 0.05, 8, 32]} />
              <meshStandardMaterial color="#9B59B6" transparent opacity={0.7} />
            </mesh>
          )
        })}
        
        {/* Ribosomes (petites sphères) */}
        {Array.from({ length: 20 }).map((_, i) => {
          const angle1 = Math.random() * Math.PI * 2
          const angle2 = Math.acos(Math.random() * 2 - 1)
          const radius = 1.4
          const x = radius * Math.sin(angle2) * Math.cos(angle1)
          const y = radius * Math.sin(angle2) * Math.sin(angle1)
          const z = radius * Math.cos(angle2)
          return (
            <mesh key={`ribosome-${i}`} position={[x, y, z]}>
              <sphereGeometry args={[0.04, 16, 16]} />
              <meshStandardMaterial color="#3498DB" />
            </mesh>
          )
        })}
        
        {/* Appareil de Golgi (structure empilée) */}
        <group position={[-1.2, 0.3, 0.5]}>
          {Array.from({ length: 5 }).map((_, i) => (
            <mesh key={`golgi-${i}`} position={[0, i * 0.08, 0]} rotation={[0, Math.PI / 4, 0]}>
              <boxGeometry args={[0.15, 0.05, 0.2]} />
              <meshStandardMaterial 
                color={i % 2 === 0 ? '#E74C3C' : '#C0392B'} 
                transparent 
                opacity={0.8}
              />
            </mesh>
          ))}
        </group>
      </group>
      
      {/* ADN double hélice en arrière-plan */}
      <group position={[3, 0, -2]} rotation={[0, Math.PI / 6, 0]}>
        {Array.from({ length: 30 }).map((_, i) => {
          const t = (i / 30) * Math.PI * 4
          const radius = 0.2
          const y = i * 0.15 - 2.25
          const x1 = Math.cos(t) * radius
          const z1 = Math.sin(t) * radius
          const x2 = Math.cos(t + Math.PI) * radius
          const z2 = Math.sin(t + Math.PI) * radius
          
          return (
            <group key={`dna-${i}`} position={[0, y, 0]}>
              {/* Brins d'ADN */}
              <mesh position={[x1, 0, z1]}>
                <sphereGeometry args={[0.06, 16, 16]} />
                <meshStandardMaterial color="#3498DB" />
              </mesh>
              <mesh position={[x2, 0, z2]}>
                <sphereGeometry args={[0.06, 16, 16]} />
                <meshStandardMaterial color="#E74C3C" />
              </mesh>
              
              {/* Liaisons (échelles) */}
              <line>
                <bufferGeometry>
                  <bufferAttribute
                    attach="attributes-position"
                    count={2}
                    array={new Float32Array([x1, 0, z1, x2, 0, z2])}
                    itemSize={3}
                  />
                </bufferGeometry>
                <lineBasicMaterial color="#95A5A6" linewidth={1} />
              </line>
            </group>
          )
        })}
      </group>
      
      <Text position={[0, -3, 0]} fontSize={0.18} color="white" anchorX="center">
        Cellule eucaryote avec organites | ADN double hélice
      </Text>
    </>
  )
}

// Simulation 3D pour la géographie - TRÈS RÉALISTE (relief montagneux, vallées, rivières)
const GeographySimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  const terrainRef = useRef<THREE.Group>(null)
  
  // Génération de terrain réaliste avec bruit de Perlin simplifié
  const generateTerrain = () => {
    const resolution = 40
    const size = 8
    const vertices: number[] = []
    const indices: number[] = []
    const colors: number[] = []
    
    const noise = (x: number, z: number) => {
      return Math.sin(x * 0.5) * Math.cos(z * 0.5) * 0.5 +
             Math.sin(x * 1.5) * Math.cos(z * 1.5) * 0.25 +
             Math.sin(x * 3) * Math.cos(z * 3) * 0.125
    }
    
    for (let i = 0; i <= resolution; i++) {
      for (let j = 0; j <= resolution; j++) {
        const x = (i / resolution) * size - size / 2
        const z = (j / resolution) * size - size / 2
        const height = noise(x, z) * 1.5
        vertices.push(x, height, z)
        
        // Couleur selon l'altitude
        if (height > 0.5) {
          colors.push(0.5, 0.4, 0.3) // Montagne (brun)
        } else if (height > 0) {
          colors.push(0.2, 0.7, 0.2) // Colline (vert)
        } else if (height > -0.3) {
          colors.push(0.1, 0.5, 0.8) // Mer peu profonde (bleu clair)
        } else {
          colors.push(0.0, 0.2, 0.5) // Mer profonde (bleu foncé)
        }
        
        if (i < resolution && j < resolution) {
          const a = i * (resolution + 1) + j
          const b = a + 1
          const c = a + resolution + 1
          const d = c + 1
          
          indices.push(a, b, c)
          indices.push(b, d, c)
        }
      }
    }
    
    return { vertices, indices, colors }
  }
  
  const { vertices, indices, colors } = generateTerrain()

  return (
    <>
      <ambientLight intensity={0.8} />
      <directionalLight position={[10, 10, 5]} intensity={1.2} castShadow />
      <directionalLight position={[-5, 5, -5]} intensity={0.4} />
      
      {/* Soleil (source de lumière) */}
      <mesh position={[8, 8, 8]}>
        <sphereGeometry args={[0.3, 32, 32]} />
        <meshStandardMaterial 
          color="#FFD700" 
          emissive="#FFD700"
          emissiveIntensity={1}
        />
      </mesh>
      
      {/* Relief 3D - TRÈS RÉALISTE */}
      <group ref={terrainRef} position={[0, -1, 0]}>
        <mesh receiveShadow>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={vertices.length / 3}
              array={new Float32Array(vertices)}
              itemSize={3}
            />
            <bufferAttribute
              attach="attributes-color"
              count={colors.length / 3}
              array={new Float32Array(colors)}
              itemSize={3}
            />
            <bufferAttribute
              attach="index"
              count={indices.length}
              array={new Uint16Array(indices)}
              itemSize={1}
            />
          </bufferGeometry>
          <meshStandardMaterial 
            vertexColors={true}
            roughness={0.9}
            metalness={0.1}
            flatShading={false}
          />
        </mesh>
      </group>
      
      {/* Montagnes supplémentaires (pic élevé) */}
      <group position={[-2, 0, 2]}>
        <mesh>
          <coneGeometry args={[0.8, 1.8, 16]} />
          <meshStandardMaterial color="#8B7355" roughness={0.9} />
        </mesh>
        {/* Neige au sommet */}
        <mesh position={[0, 1.8, 0]}>
          <coneGeometry args={[0.4, 0.3, 16]} />
          <meshStandardMaterial color="#FFFFFF" roughness={0.3} metalness={0.1} />
        </mesh>
      </group>
      
      {/* Vallée/rivière */}
      <group position={[2, -0.8, -1]}>
        {Array.from({ length: 20 }).map((_, i) => {
          const x = (i / 20) * 3 - 1.5
          const z = Math.sin(i * 0.3) * 0.2
          const width = 0.3 + Math.sin(i * 0.5) * 0.1
          return (
            <mesh key={`river-${i}`} position={[x, 0, z]}>
              <boxGeometry args={[width, 0.05, width]} />
              <meshStandardMaterial 
                color="#4A90E2" 
                transparent 
                opacity={0.7}
                roughness={0.2}
              />
            </mesh>
          )
        })}
      </group>
      
      {/* Arbres (forêt) */}
      {Array.from({ length: 30 }).map((_, i) => {
        const angle = (i / 30) * Math.PI * 2
        const radius = 2.5 + Math.random() * 1.5
        const x = Math.cos(angle) * radius + (Math.random() - 0.5) * 1
        const z = Math.sin(angle) * radius + (Math.random() - 0.5) * 1
        const height = 0.5 + Math.random() * 0.3
        
        return (
          <group key={`tree-${i}`} position={[x, height / 2 - 1, z]}>
            {/* Tronc */}
            <mesh>
              <cylinderGeometry args={[0.05, 0.05, height, 8]} />
              <meshStandardMaterial color="#8B4513" />
            </mesh>
            {/* Feuillage */}
            <mesh position={[0, height / 2 + 0.2, 0]}>
              <coneGeometry args={[0.3, 0.5, 8]} />
              <meshStandardMaterial color="#2ECC71" />
            </mesh>
          </group>
        )
      })}
      
      {/* Nuages */}
      {Array.from({ length: 5 }).map((_, i) => {
        const x = (i - 2) * 2 + Math.sin(i) * 0.5
        const z = Math.cos(i) * 3
        const y = 4 + Math.sin(i) * 0.3
        
        return (
          <group key={`cloud-${i}`} position={[x, y, z]}>
            {[0, 0.2, -0.2].map((offset, j) => (
              <mesh key={`cloud-part-${j}`} position={[offset, 0, j * 0.1]}>
                <sphereGeometry args={[0.4, 16, 16]} />
                <meshStandardMaterial color="#FFFFFF" transparent opacity={0.8} />
              </mesh>
            ))}
          </group>
        )
      })}
      
      <Text position={[0, -3, 0]} fontSize={0.18} color="white" anchorX="center">
        Relief montagneux | Vallées | Rivières | Forêts
      </Text>
    </>
  )
}

// Simulation 3D pour l'économie - TRÈS RÉALISTE (surfaces d'offre/demande, graphiques 3D)
const EconomicsSimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  const [time, setTime] = useState(0)
  const [equilibrium, setEquilibrium] = useState({ price: 2.5, quantity: 3 })
  
  useEffect(() => {
    const interval = setInterval(() => {
      setTime((prev) => prev + 0.05)
      // Point d'équilibre animé
      setEquilibrium({
        price: 2.5 + Math.sin(time * 0.3) * 0.3,
        quantity: 3 + Math.cos(time * 0.3) * 0.2
      })
    }, 100)
    return () => clearInterval(interval)
  }, [time])
  
  // Surface 3D d'offre et demande
  const createSupplySurface = () => {
    const resolution = 30
    const vertices: number[] = []
    const indices: number[] = []
    
    for (let i = 0; i <= resolution; i++) {
      for (let j = 0; j <= resolution; j++) {
        const x = (i / resolution) * 6 - 3
        const z = (j / resolution) * 4 - 2
        // Courbe d'offre croissante
        const price = 1 + (x + 3) * 0.5 + Math.sin(time * 0.5 + z) * 0.2
        const y = Math.max(0.5, price)
        vertices.push(x, y, z)
        
        if (i < resolution && j < resolution) {
          const a = i * (resolution + 1) + j
          const b = a + 1
          const c = a + resolution + 1
          const d = c + 1
          
          indices.push(a, b, c)
          indices.push(b, d, c)
        }
      }
    }
    
    return { vertices, indices }
  }
  
  const createDemandSurface = () => {
    const resolution = 30
    const vertices: number[] = []
    const indices: number[] = []
    
    for (let i = 0; i <= resolution; i++) {
      for (let j = 0; j <= resolution; j++) {
        const x = (i / resolution) * 6 - 3
        const z = (j / resolution) * 4 - 2
        // Courbe de demande décroissante
        const price = 4 - (x + 3) * 0.4 - Math.sin(time * 0.5 + z) * 0.2
        const y = Math.max(0.5, price)
        vertices.push(x, y, z)
        
        if (i < resolution && j < resolution) {
          const a = i * (resolution + 1) + j
          const b = a + 1
          const c = a + resolution + 1
          const d = c + 1
          
          indices.push(a, b, c)
          indices.push(b, d, c)
        }
      }
    }
    
    return { vertices, indices }
  }
  
  const supplySurface = createSupplySurface()
  const demandSurface = createDemandSurface()

  return (
    <>
      <ambientLight intensity={0.7} />
      <pointLight position={[5, 5, 5]} intensity={1.5} />
      <pointLight position={[-5, -5, -5]} intensity={0.8} />
      <directionalLight position={[0, 10, 0]} intensity={0.6} />
      
      <gridHelper args={[10, 10, '#888888', '#444444']} />
      <axesHelper args={[5]} />
      
      {/* Surface 3D d'offre - TRÈS RÉALISTE */}
      <mesh position={[0, 0, -1]}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={supplySurface.vertices.length / 3}
            array={new Float32Array(supplySurface.vertices)}
            itemSize={3}
          />
          <bufferAttribute
            attach="index"
            count={supplySurface.indices.length}
            array={new Uint16Array(supplySurface.indices)}
            itemSize={1}
          />
        </bufferGeometry>
        <meshStandardMaterial 
          color="#2ECC71" 
          transparent 
          opacity={0.6}
          side={2}
          roughness={0.6}
          metalness={0.2}
        />
      </mesh>
      
      {/* Surface 3D de demande - TRÈS RÉALISTE */}
      <mesh position={[0, 0, 1]}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={demandSurface.vertices.length / 3}
            array={new Float32Array(demandSurface.vertices)}
            itemSize={3}
          />
          <bufferAttribute
            attach="index"
            count={demandSurface.indices.length}
            array={new Uint16Array(demandSurface.indices)}
            itemSize={1}
          />
        </bufferGeometry>
        <meshStandardMaterial 
          color="#E74C3C" 
          transparent 
          opacity={0.6}
          side={2}
          roughness={0.6}
          metalness={0.2}
        />
      </mesh>
      
      {/* Courbes 2D projetées pour clarté */}
      {Array.from({ length: 50 }).map((_, i) => {
        const x = (i / 50) * 6 - 3
        // Courbe d'offre
        const supplyY = 1 + (x + 3) * 0.5
        // Courbe de demande
        const demandY = 4 - (x + 3) * 0.4
        
        return (
          <group key={`curves-${i}`}>
            {/* Point d'offre */}
            <mesh position={[x, supplyY, -1]}>
              <sphereGeometry args={[0.04, 8, 8]} />
              <meshStandardMaterial 
                color="#2ECC71" 
                emissive="#2ECC71"
                emissiveIntensity={0.5}
              />
            </mesh>
            {/* Point de demande */}
            <mesh position={[x, demandY, 1]}>
              <sphereGeometry args={[0.04, 8, 8]} />
              <meshStandardMaterial 
                color="#E74C3C" 
                emissive="#E74C3C"
                emissiveIntensity={0.5}
              />
            </mesh>
          </group>
        )
      })}
      
      {/* Point d'équilibre 3D - TRÈS RÉALISTE */}
      <group position={[equilibrium.quantity - 3, equilibrium.price, 0]}>
        {/* Point d'équilibre */}
        <mesh>
          <sphereGeometry args={[0.2, 32, 32]} />
          <meshStandardMaterial 
            color="#FFD700" 
            emissive="#FFD700"
            emissiveIntensity={0.8}
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
        
        {/* Anneau d'équilibre */}
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <torusGeometry args={[0.3, 0.05, 16, 32]} />
          <meshStandardMaterial 
            color="#FFD700" 
            transparent 
            opacity={0.6}
            emissive="#FFD700"
            emissiveIntensity={0.5}
          />
        </mesh>
        
        {/* Lignes de projection vers les axes */}
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={2}
              array={new Float32Array([
                equilibrium.quantity - 3, equilibrium.price, 0,
                equilibrium.quantity - 3, 0, 0
              ])}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#FFD700" linewidth={2} dashed={true} />
        </line>
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={2}
              array={new Float32Array([
                equilibrium.quantity - 3, equilibrium.price, 0,
                -3, equilibrium.price, 0
              ])}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#FFD700" linewidth={2} dashed={true} />
        </line>
      </group>
      
      {/* Graphique de croissance économique 3D */}
      <group position={[-4, 3, -2]}>
        <Text position={[0, 0.5, 0]} fontSize={0.15} color="white" anchorX="center">
          PIB (3D)
        </Text>
        {Array.from({ length: 20 }).map((_, i) => {
          const x = (i / 20) * 2
          const y = Math.log(i + 1) * 0.3 + Math.sin(time + i * 0.3) * 0.2
          const z = Math.cos(time + i * 0.2) * 0.3
          
          return (
            <mesh key={`gdp-${i}`} position={[x, y, z]}>
              <boxGeometry args={[0.08, y + 0.1, 0.08]} />
              <meshStandardMaterial 
                color="#3498DB" 
                emissive="#3498DB"
                emissiveIntensity={0.3}
              />
            </mesh>
          )
        })}
      </group>
      
      {/* Labels et légendes */}
      <Text position={[-4, 5, 0]} fontSize={0.2} color="#2ECC71" anchorX="center">
        Offre (Supply)
      </Text>
      <Text position={[-4, 0.5, 0]} fontSize={0.2} color="#E74C3C" anchorX="center">
        Demande (Demand)
      </Text>
      <Text position={[0, -2.5, 0]} fontSize={0.18} color="white" anchorX="center">
        Quantité
      </Text>
      <Text position={[-3.5, 2.5, 0]} fontSize={0.18} color="white" anchorX="center" rotation={[0, 0, Math.PI / 2]}>
        Prix
      </Text>
      <Text position={[equilibrium.quantity - 3, -3.5, 0]} fontSize={0.15} color="#FFD700" anchorX="center">
        Équilibre
      </Text>
    </>
  )
}

// Simulation 3D pour l'histoire - TRÈS RÉALISTE (timeline 3D interactive avec événements détaillés)
const HistorySimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  const [currentYear, setCurrentYear] = useState(0)
  const timelineRef = useRef<THREE.Group>(null)
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentYear((prev) => (prev + 0.5) % 200)
    }, 100)
    return () => clearInterval(interval)
  }, [])
  
  useFrame(() => {
    if (timelineRef.current) {
      timelineRef.current.rotation.y += 0.001
    }
  })
  
  // Événements historiques majeurs - TRÈS DÉTAILLÉS
  const events = [
    { year: 1789, title: 'Révolution', height: 1.2, color: '#E74C3C', description: 'Révolution Française' },
    { year: 1914, title: 'Guerre', height: 1.5, color: '#C0392B', description: 'WWI' },
    { year: 1945, title: 'Paix', height: 1.8, color: '#3498DB', description: 'WWII End' },
    { year: 1969, title: 'Espace', height: 1.0, color: '#9B59B6', description: 'Apollo 11' },
    { year: 1989, title: 'Chute', height: 0.8, color: '#2ECC71', description: 'Mur Berlin' },
    { year: 2001, title: 'Terrorisme', height: 1.3, color: '#95A5A6', description: '11 Sept' },
    { year: 2020, title: 'Pandémie', height: 1.6, color: '#F39C12', description: 'COVID-19' },
  ]
  
  // Timeline spiralée 3D - TRÈS RÉALISTE
  const createTimeline = () => {
    const points: number[] = []
    const numPoints = 100
    const startYear = 1700
    const endYear = 2024
    const radius = 2.5
    
    for (let i = 0; i <= numPoints; i++) {
      const progress = i / numPoints
      const year = startYear + (endYear - startYear) * progress
      const angle = progress * Math.PI * 4 // Spiral de 2 tours
      const currentRadius = radius + Math.sin(progress * Math.PI * 2) * 0.5
      const x = Math.cos(angle) * currentRadius
      const z = Math.sin(angle) * currentRadius
      const y = progress * 3 - 1.5
      
      points.push(x, y, z)
    }
    
    return points
  }
  
  const timelinePoints = createTimeline()

  return (
    <>
      <ambientLight intensity={0.7} />
      <pointLight position={[5, 5, 5]} intensity={1.5} />
      <pointLight position={[-5, -5, -5]} intensity={0.8} />
      <directionalLight position={[0, 10, 0]} intensity={0.6} />
      
      <gridHelper args={[10, 10, '#888888', '#444444']} />
      
      {/* Timeline spiralée 3D - TRÈS RÉALISTE */}
      <group ref={timelineRef}>
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={timelinePoints.length / 3}
              array={new Float32Array(timelinePoints)}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#E74C3C" linewidth={3} />
        </line>
        
        {/* Points de repère sur la timeline */}
        {Array.from({ length: 50 }).map((_, i) => {
          const progress = i / 50
          const angle = progress * Math.PI * 4
          const currentRadius = 2.5 + Math.sin(progress * Math.PI * 2) * 0.5
          const x = Math.cos(angle) * currentRadius
          const z = Math.sin(angle) * currentRadius
          const y = progress * 3 - 1.5
          const year = 1700 + (2024 - 1700) * progress
          
          return (
            <mesh key={`marker-${i}`} position={[x, y, z]}>
              <sphereGeometry args={[0.03, 8, 8]} />
              <meshStandardMaterial 
                color={year % 100 === 0 ? '#FFD700' : '#888888'} 
                emissive={year % 100 === 0 ? '#FFD700' : '#000000'}
                emissiveIntensity={year % 100 === 0 ? 0.5 : 0}
              />
            </mesh>
          )
        })}
      </group>
      
      {/* Événements historiques 3D - TRÈS DÉTAILLÉS */}
      {events.map((event, index) => {
        const progress = (event.year - 1700) / (2024 - 1700)
        const angle = progress * Math.PI * 4
        const currentRadius = 2.5 + Math.sin(progress * Math.PI * 2) * 0.5
        const x = Math.cos(angle) * currentRadius
        const z = Math.sin(angle) * currentRadius
        const y = progress * 3 - 1.5
        const isActive = Math.abs(currentYear - (event.year - 1700)) < 10
        
        return (
          <group 
            key={`event-${index}`} 
            position={[x, y + event.height / 2, z]}
          >
            {/* Colonne de l'événement */}
            <mesh>
              <cylinderGeometry args={[0.15, 0.15, event.height, 16]} />
              <meshStandardMaterial 
                color={event.color}
                emissive={isActive ? event.color : '#000000'}
                emissiveIntensity={isActive ? 0.6 : 0}
                metalness={0.5}
                roughness={0.4}
              />
            </mesh>
            
            {/* Base de la colonne */}
            <mesh position={[0, -event.height / 2, 0]}>
              <cylinderGeometry args={[0.2, 0.2, 0.1, 16]} />
              <meshStandardMaterial color="#333333" />
            </mesh>
            
            {/* Plaque commémorative */}
            <mesh position={[0, event.height / 2 + 0.2, 0]} rotation={[-Math.PI / 2, 0, angle]}>
              <boxGeometry args={[0.6, 0.3, 0.02]} />
              <meshStandardMaterial 
                color="#2C3E50" 
                emissive="#2C3E50"
                emissiveIntensity={isActive ? 0.2 : 0}
                metalness={0.6}
                roughness={0.3}
              />
            </mesh>
            
            {/* Texte de l'année */}
            <Text 
              position={[0, event.height / 2 + 0.35, 0]} 
              fontSize={0.18} 
              color="white"
              anchorX="center"
            >
              {event.year}
            </Text>
            
            {/* Texte du titre */}
            <Text 
              position={[0, event.height / 2 + 0.55, 0]} 
              fontSize={0.12} 
              color="#ECF0F1"
              anchorX="center"
            >
              {event.title}
            </Text>
            
            {/* Rayon de lumière pour événements actifs */}
            {isActive && (
              <mesh position={[0, event.height / 2, 0]} rotation={[Math.PI / 2, 0, 0]}>
                <coneGeometry args={[0.5, 1, 8]} />
                <meshStandardMaterial 
                  color={event.color} 
                  transparent 
                  opacity={0.3}
                  emissive={event.color}
                  emissiveIntensity={0.5}
                />
              </mesh>
            )}
            
            {/* Connexion à la timeline */}
            <line>
              <bufferGeometry>
                <bufferAttribute
                  attach="attributes-position"
                  count={2}
                  array={new Float32Array([
                    0, event.height / 2, 0,
                    0, 0, 0
                  ])}
                  itemSize={3}
                />
              </bufferGeometry>
              <lineBasicMaterial 
                color={event.color} 
                linewidth={2} 
                transparent 
                opacity={0.5}
              />
            </line>
          </group>
        )
      })}
      
      {/* Globe terrestre en arrière-plan (contexte géographique) */}
      <group position={[4, 0, -3]}>
        <mesh rotation={[0, currentYear * 0.01, 0]}>
          <sphereGeometry args={[1, 32, 32]} />
          <meshStandardMaterial 
            color="#4ECDC4" 
            transparent 
            opacity={0.3}
            wireframe={true}
          />
        </mesh>
        {/* Continents */}
        {Array.from({ length: 7 }).map((_, i) => {
          const angle = (i / 7) * Math.PI * 2
          const x = Math.cos(angle) * 1.05
          const z = Math.sin(angle) * 1.05
          return (
            <mesh key={`continent-${i}`} position={[x, 0, z]}>
              <boxGeometry args={[0.3, 0.2, 0.3]} />
              <meshStandardMaterial color="#2ECC71" />
            </mesh>
          )
        })}
      </group>
      
      {/* Indicateur de temps actuel */}
      <group position={[0, -2.5, 0]}>
        <Text position={[0, 0, 0]} fontSize={0.25} color="#FFD700" anchorX="center">
          {Math.floor(1700 + currentYear)} - Histoire Interactive
        </Text>
      </group>
      
      {/* Labels */}
      <Text position={[0, 3.5, 0]} fontSize={0.2} color="white" anchorX="center">
        Timeline Historique 3D - 1700 à 2024
      </Text>
    </>
  )
}

// Visualisation interactive pour informatique (algorithmes, structures de données) - 2D fallback
const ComputerScienceVisualization = ({ visualizationData }: { visualizationData?: any }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [currentStep, setCurrentStep] = useState(0)
  
  const algorithmData = useMemo(() => {
    if (visualizationData?.data_flow?.steps) {
      return visualizationData.data_flow.steps
    }
    if (visualizationData?.step_by_step_execution?.steps) {
      return visualizationData.step_by_step_execution.steps
    }
    // Données par défaut pour un tri
    return [
      { step: 1, action: 'Comparer les éléments', result: '[3, 1, 4, 2] → Comparer 3 et 1' },
      { step: 2, action: 'Échanger si nécessaire', result: '[1, 3, 4, 2] → Échanger 3 et 1' },
      { step: 3, action: 'Continuer la comparaison', result: '[1, 3, 4, 2] → Comparer 3 et 4' },
      { step: 4, action: 'Comparer avec l\'élément suivant', result: '[1, 3, 4, 2] → Comparer 4 et 2' },
      { step: 5, action: 'Échanger', result: '[1, 3, 2, 4] → Échanger 4 et 2' },
      { step: 6, action: 'Résultat final', result: '[1, 2, 3, 4] → Tri terminé' }
    ]
  }, [visualizationData])
  
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    // Nettoyer le canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    // Dessiner la structure de données (tableau)
    const arrayData = visualizationData?.step_by_step_execution?.input || 
                     visualizationData?.data_flow?.steps?.[currentStep]?.result || 
                     [3, 1, 4, 2]
    const isArray = Array.isArray(arrayData)
    const data = isArray ? arrayData : [1, 2, 3, 4]
    
    const cellWidth = 60
    const cellHeight = 40
    const startX = (canvas.width - (data.length * cellWidth + (data.length - 1) * 10)) / 2
    const startY = canvas.height / 2 - cellHeight / 2
    
    data.forEach((value: number, index: number) => {
      const x = startX + index * (cellWidth + 10)
      const y = startY
      
      // Rectangle pour la cellule
      ctx.fillStyle = index === currentStep % data.length ? '#805AD5' : '#EDF2F7'
      ctx.fillRect(x, y, cellWidth, cellHeight)
      
      // Bordure
      ctx.strokeStyle = '#CBD5E0'
      ctx.lineWidth = 2
      ctx.strokeRect(x, y, cellWidth, cellHeight)
      
      // Valeur
      ctx.fillStyle = index === currentStep % data.length ? 'white' : '#2D3748'
      ctx.font = 'bold 16px Arial'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(String(value), x + cellWidth / 2, y + cellHeight / 2)
      
      // Index
      ctx.fillStyle = '#718096'
      ctx.font = '12px Arial'
      ctx.fillText(`[${index}]`, x + cellWidth / 2, y + cellHeight + 15)
    })
    
    // Dessiner les flèches entre les étapes si on est en train d'animer
    if (currentStep > 0 && currentStep < algorithmData.length) {
      const arrowX = startX + ((currentStep - 1) % data.length) * (cellWidth + 10) + cellWidth
      const arrowY = startY + cellHeight / 2
      
      ctx.strokeStyle = '#805AD5'
      ctx.lineWidth = 3
      ctx.beginPath()
      ctx.moveTo(arrowX, arrowY)
      ctx.lineTo(arrowX + 10, arrowY)
      ctx.stroke()
      
      // Pointe de flèche
      ctx.fillStyle = '#805AD5'
      ctx.beginPath()
      ctx.moveTo(arrowX + 10, arrowY)
      ctx.lineTo(arrowX + 5, arrowY - 5)
      ctx.lineTo(arrowX + 5, arrowY + 5)
      ctx.closePath()
      ctx.fill()
    }
  }, [currentStep, visualizationData, algorithmData])
  
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev + 1) % algorithmData.length)
    }, 1500)
    return () => clearInterval(interval)
  }, [algorithmData.length])
  
  return (
    <VStack spacing={4} p={6} h="100%" w="100%" bg="gray.50">
      <Box w="100%" textAlign="center">
        <ChakraText fontSize="lg" fontWeight="bold" color="gray.800" mb={2}>
          {visualizationData?.algorithm || visualizationData?.concept || 'Algorithme de tri'}
        </ChakraText>
        {visualizationData?.explanation && (
          <ChakraText fontSize="sm" color="gray.600" mb={4}>
            {visualizationData.explanation}
          </ChakraText>
        )}
      </Box>
      
      <Box 
        bg="white" 
        p={4} 
        borderRadius="lg" 
        boxShadow="md"
        w="100%"
        flex={1}
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
      >
        <canvas
          ref={canvasRef}
          width={400}
          height={200}
          style={{ maxWidth: '100%', height: 'auto' }}
        />
      </Box>
      
      <VStack spacing={2} w="100%">
        <HStack w="100%" justify="space-between">
          <ChakraText fontSize="sm" color="gray.700" fontWeight="medium">
            Étape {currentStep + 1} / {algorithmData.length}
          </ChakraText>
          <Badge colorScheme="purple" fontSize="xs">
            {algorithmData[currentStep]?.action || 'Exécution...'}
          </Badge>
        </HStack>
        <Progress 
          value={((currentStep + 1) / algorithmData.length) * 100} 
          colorScheme="purple" 
          size="sm"
          w="100%"
          borderRadius="full"
        />
        <Box 
          bg="purple.50" 
          p={3} 
          borderRadius="md" 
          w="100%"
          border="1px solid"
          borderColor="purple.200"
        >
          <ChakraText fontSize="xs" color="gray.700" fontFamily="mono">
            {algorithmData[currentStep]?.result || 'En cours...'}
          </ChakraText>
        </Box>
      </VStack>
    </VStack>
  )
}

// Visualisation 2D pour les autres matières
const Visualization2D = ({ module, visualizationData }: { module: Module, visualizationData?: any }) => {
  const subject = module.subject?.toLowerCase()
  
  // Pour computer_science, utiliser une visualisation interactive spéciale
  if (subject === 'computer_science') {
    return <ComputerScienceVisualization visualizationData={visualizationData} />
  }
  
  const getVisualizationContent = () => {
    switch (subject) {
      case 'mathematics':
        return {
          title: '📐 Visualisation Mathématique',
          description: 'Graphiques, fonctions, et visualisations mathématiques interactives',
          icon: '📐',
          color: 'purple'
        }
      case 'biology':
        return {
          title: '🧬 Visualisation Biologique',
          description: 'Diagrammes, schémas et représentations biologiques interactives',
          icon: '🧬',
          color: 'teal'
        }
      case 'geography':
        return {
          title: '🌍 Visualisation Géographique',
          description: 'Cartes, reliefs et données géospatiales interactives',
          icon: '🌍',
          color: 'orange'
        }
      case 'economics':
        return {
          title: '💰 Visualisation Économique',
          description: 'Graphiques économiques, courbes et analyses interactives',
          icon: '💰',
          color: 'yellow'
        }
      case 'history':
        return {
          title: '🏛️ Visualisation Historique',
          description: 'Frise chronologique et événements historiques interactifs',
          icon: '🏛️',
          color: 'red'
        }
      case 'computer_science':
        return {
          title: '🤖 Visualisation Informatique',
          description: 'Algorithmes, structures de données et visualisations IA',
          icon: '🤖',
          color: 'purple'
        }
      default:
        return {
          title: '📊 Visualisation Interactive',
          description: 'Visualisation interactive pour cette matière',
          icon: '📊',
          color: 'gray'
        }
    }
  }
  
  const content = getVisualizationContent()
  
  return (
    <Box 
      h="100%" 
      w="100%" 
      display="flex" 
      alignItems="center" 
      justifyContent="center" 
      p={8} 
      bgGradient={`linear(to-br, ${content.color}.50, ${content.color}.100)`}
    >
      <Box textAlign="center" maxW="500px">
        <ChakraText fontSize="6xl" mb={4}>
          {content.icon}
        </ChakraText>
        <ChakraText fontSize="2xl" fontWeight="bold" color="gray.800" mb={4}>
          {content.title}
        </ChakraText>
        <ChakraText color="gray.600" fontSize="md" mb={6}>
          {content.description}
        </ChakraText>
        <Box 
          bg="white" 
          p={6} 
          borderRadius="lg" 
          boxShadow="lg"
          border="2px solid"
          borderColor={`${content.color}.200`}
        >
          <ChakraText fontSize="sm" color="gray.700" mb={2}>
            Module : <strong>{module.title || 'Module'}</strong>
          </ChakraText>
          {visualizationData ? (
            <>
              <ChakraText fontSize="sm" color="gray.700" mb={2} fontWeight="bold">
                Visualisation générée par l'IA
              </ChakraText>
              <ChakraText fontSize="xs" color="gray.600" mb={2}>
                {visualizationData.explanation || visualizationData.description || 'Visualisation interactive personnalisée'}
              </ChakraText>
              {visualizationData.visualization && (
                <Box mt={2} p={2} bg={`${content.color}.50`} borderRadius="md">
                  <ChakraText fontSize="xs" color="gray.600">
                    Type: {visualizationData.visualization.type || 'interactive'}
                  </ChakraText>
                </Box>
              )}
            </>
          ) : (
            <ChakraText fontSize="xs" color="gray.500">
              Génération de la visualisation par l'IA en cours...
              <br />
              Les visualisations 2D interactives pour cette matière seront bientôt disponibles.
            </ChakraText>
          )}
        </Box>
      </Box>
    </Box>
  )
}

export default Simulation3D

