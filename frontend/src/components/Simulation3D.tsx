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

  return (
    <Box h="100%" w="100%" position="relative">
      <Canvas
        gl={{ antialias: true, alpha: false }}
        dpr={[1, 2]}
        onCreated={({ gl }) => {
          gl.setClearColor('#000000')
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

// Simulation de gravitation avec animation
const GravitationSimulation = ({ visualizationData }: { visualizationData?: any }) => {
  const satelliteRef = useRef<THREE.Mesh>(null)
  
  // Utiliser les paramètres générés par OpenAI si disponibles
  const orbitRadius = visualizationData?.visualization_3d?.parameters?.radius || 
                     visualizationData?.parameters?.orbit_radius || 
                     3
  const orbitSpeed = visualizationData?.visualization_3d?.parameters?.speed || 
                    visualizationData?.parameters?.orbit_speed || 
                    1
  
  useFrame((state) => {
    if (satelliteRef.current) {
      const time = state.clock.getElapsedTime()
      satelliteRef.current.position.x = Math.cos(time * orbitSpeed) * orbitRadius
      satelliteRef.current.position.z = Math.sin(time * orbitSpeed) * orbitRadius
    }
  })

  return (
    <>
      {/* Planète centrale - taille selon données IA */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[
          visualizationData?.visualization_3d?.parameters?.planet_size || 0.5, 
          32, 
          32
        ]} />
        <meshStandardMaterial color={
          visualizationData?.visualization_3d?.parameters?.planet_color || "#4A90E2"
        } />
      </mesh>
      
      {/* Satellite en orbite */}
      <mesh ref={satelliteRef} position={[orbitRadius, 0, 0]}>
        <sphereGeometry args={[
          visualizationData?.visualization_3d?.parameters?.satellite_size || 0.2, 
          16, 
          16
        ]} />
        <meshStandardMaterial color={
          visualizationData?.visualization_3d?.parameters?.satellite_color || "#F5A623"
        } />
      </mesh>
      
      {/* Orbite */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[orbitRadius - 0.5, orbitRadius + 0.5, 64]} />
        <meshBasicMaterial color="#888" side={2} transparent opacity={0.3} />
      </mesh>
      
      {/* Lignes de force gravitationnelle */}
      {Array.from({ length: 8 }).map((_, i) => {
        const angle = (i / 8) * Math.PI * 2
        const points = [
          new THREE.Vector3(0, 0, 0),
          new THREE.Vector3(Math.cos(angle) * 4, 0, Math.sin(angle) * 4)
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
            <lineBasicMaterial color="#4A90E2" opacity={0.3} transparent />
          </line>
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

// Réaction chimique
const ChemicalReaction = ({ visualizationData }: { visualizationData?: any }) => {
  return (
    <>
      {/* Molécule - utiliser les données générées par OpenAI si disponibles */}
      {visualizationData?.molecular_visualization?.molecules ? (
        // Afficher les molécules selon les données IA
        visualizationData.molecular_visualization.molecules.map((mol: any, idx: number) => (
          <mesh key={idx} position={[mol.position?.x || -2 + idx * 2, mol.position?.y || 0, mol.position?.z || 0]}>
            <sphereGeometry args={[mol.size || 0.3, 16, 16]} />
            <meshStandardMaterial color={mol.color || "#FF6B6B"} />
          </mesh>
        ))
      ) : (
        <>
          {/* Molécule CH4 par défaut */}
          <mesh position={[-2, 0, 0]}>
            <sphereGeometry args={[0.3, 16, 16]} />
            <meshStandardMaterial color="#FF6B6B" />
          </mesh>
          {[0, 1, 2, 3].map((i) => {
            const angle = (i * Math.PI * 2) / 4
            return (
              <mesh key={i} position={[-2 + Math.cos(angle) * 0.4, Math.sin(angle) * 0.4, 0]}>
                <sphereGeometry args={[0.15, 16, 16]} />
                <meshStandardMaterial color="#4ECDC4" />
              </mesh>
            )
          })}
        </>
      )}
      
      {/* Flèche */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1, 0.1, 0.1]} />
        <meshStandardMaterial color="#95A5A6" />
      </mesh>
      
      {/* CO2 */}
      <mesh position={[2, 0, 0]}>
        <sphereGeometry args={[0.3, 16, 16]} />
        <meshStandardMaterial color="#FF6B6B" />
      </mesh>
      <mesh position={[2.5, 0, 0]}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshStandardMaterial color="#4ECDC4" />
      </mesh>
      <mesh position={[2.25, 0.3, 0]}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshStandardMaterial color="#4ECDC4" />
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

// Simulation 3D pour les mathématiques
const MathematicsSimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  const graphRef = useRef<THREE.Group>(null)
  const [animationProgress, setAnimationProgress] = useState(0)
  
  useEffect(() => {
    const interval = setInterval(() => {
      setAnimationProgress((prev) => (prev + 0.02) % (Math.PI * 2))
    }, 50)
    return () => clearInterval(interval)
  }, [])
  
  return (
    <>
      <gridHelper args={[10, 10, '#888888', '#444444']} />
      <axesHelper args={[5]} />
      
      {/* Graphique 3D d'une fonction mathématique */}
      <group ref={graphRef}>
        {Array.from({ length: 50 }).map((_, i) => {
          const x = (i / 50) * 4 - 2
          const y = Math.sin(x * 2 + animationProgress) * 0.5
          const z = Math.cos(x * 2 + animationProgress) * 0.3
          
          return (
            <mesh key={i} position={[x, y, z]}>
              <sphereGeometry args={[0.05, 8, 8]} />
              <meshStandardMaterial color="#805AD5" />
            </mesh>
          )
        })}
        
        {/* Courbe continue */}
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              count={50}
              array={new Float32Array(
                Array.from({ length: 50 }).flatMap((_, i) => {
                  const x = (i / 50) * 4 - 2
                  const y = Math.sin(x * 2 + animationProgress) * 0.5
                  const z = Math.cos(x * 2 + animationProgress) * 0.3
                  return [x, y, z]
                })
              )}
              itemSize={3}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#805AD5" linewidth={2} />
        </line>
      </group>
      
      {/* Formes géométriques */}
      <mesh position={[-3, 1, 0]}>
        <boxGeometry args={[0.8, 0.8, 0.8]} />
        <meshStandardMaterial color="#E74C3C" />
      </mesh>
      
      <mesh position={[3, 1, 0]}>
        <sphereGeometry args={[0.6, 32, 32]} />
        <meshStandardMaterial color="#3498DB" />
      </mesh>
    </>
  )
}

// Simulation 3D pour l'informatique (algorithmes, structures de données)
const ComputerScienceSimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  const nodesRef = useRef<THREE.Group[]>([])
  const [step, setStep] = useState(0)
  
  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev + 1) % 6)
    }, 1000)
    return () => clearInterval(interval)
  }, [])
  
  const arrayData = [1, 2, 3, 4]
  
  return (
    <>
      <gridHelper args={[8, 8, '#888888', '#444444']} />
      
      {/* Représentation 3D d'un tableau */}
      {arrayData.map((value, index) => {
        const x = (index - 1.5) * 1.5
        const y = Math.sin(step * 0.5 + index) * 0.2
        const isActive = index === step % arrayData.length
        
        return (
          <group key={index} position={[x, y, 0]}>
            <mesh>
              <boxGeometry args={[1, 1, 1]} />
              <meshStandardMaterial 
                color={isActive ? '#805AD5' : '#EDF2F7'} 
                emissive={isActive ? '#805AD5' : '#000000'}
                emissiveIntensity={isActive ? 0.3 : 0}
              />
            </mesh>
            
            <Text 
              position={[0, 0, 0.6]} 
              fontSize={0.3} 
              color={isActive ? 'white' : 'black'}
              anchorX="center"
              anchorY="middle"
            >
              {value}
            </Text>
            
            <Text 
              position={[0, -0.8, 0]} 
              fontSize={0.2} 
              color="#718096"
              anchorX="center"
            >
              [{index}]
            </Text>
          </group>
        )
      })}
      
      {/* Lignes de connexion */}
      {Array.from({ length: arrayData.length - 1 }).map((_, i) => {
        const startX = (i - 1.5) * 1.5 + 0.5
        const endX = (i + 1 - 1.5) * 1.5 - 0.5
        
        return (
          <line key={i}>
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                count={2}
                array={new Float32Array([startX, 0, 0, endX, 0, 0])}
                itemSize={3}
              />
            </bufferGeometry>
            <lineBasicMaterial color="#805AD5" linewidth={2} />
          </line>
        )
      })}
    </>
  )
}

// Simulation 3D pour la biologie
const BiologySimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  return (
    <>
      <ambientLight intensity={0.8} />
      <pointLight position={[5, 5, 5]} intensity={1} />
      
      {/* Cellule 3D */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[1.5, 32, 32]} />
        <meshStandardMaterial 
          color="#4ECDC4" 
          transparent 
          opacity={0.7}
        />
      </mesh>
      
      {/* Noyau de la cellule */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.6, 32, 32]} />
        <meshStandardMaterial color="#E74C3C" />
      </mesh>
      
      {/* Organites autour */}
      {Array.from({ length: 6 }).map((_, i) => {
        const angle = (i / 6) * Math.PI * 2
        const radius = 1.2
        const x = Math.cos(angle) * radius
        const y = Math.sin(angle) * radius
        const z = Math.sin(i) * 0.3
        
        return (
          <mesh key={i} position={[x, y, z]}>
            <sphereGeometry args={[0.15, 16, 16]} />
            <meshStandardMaterial color="#2ECC71" />
          </mesh>
        )
      })}
    </>
  )
}

// Simulation 3D pour la géographie
const GeographySimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  return (
    <>
      {/* Relief 3D */}
      {Array.from({ length: 10 }).map((_, x) => {
        return Array.from({ length: 10 }).map((_, z) => {
          const y = Math.sin(x * 0.5) * Math.cos(z * 0.5) * 0.3
          const color = y > 0 ? '#2ECC71' : '#3498DB'
          
          return (
            <mesh key={`${x}-${z}`} position={[x - 4.5, y, z - 4.5]}>
              <boxGeometry args={[0.9, 0.1, 0.9]} />
              <meshStandardMaterial color={color} />
            </mesh>
          )
        })
      }).flat()}
      
      {/* Éléments géographiques */}
      <mesh position={[0, 0.5, 0]}>
        <coneGeometry args={[0.5, 1, 8]} />
        <meshStandardMaterial color="#95A5A6" />
      </mesh>
    </>
  )
}

// Simulation 3D pour l'économie
const EconomicsSimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  const [time, setTime] = useState(0)
  
  useEffect(() => {
    const interval = setInterval(() => {
      setTime((prev) => prev + 0.1)
    }, 100)
    return () => clearInterval(interval)
  }, [])
  
  return (
    <>
      <gridHelper args={[10, 10, '#888888', '#444444']} />
      
      {/* Graphique 3D de courbe d'offre/demande */}
      {Array.from({ length: 30 }).map((_, i) => {
        const x = (i / 30) * 6 - 3
        const supplyY = Math.sin(x * 0.5 + time) * 0.5 + 1.5
        const demandY = -Math.sin(x * 0.5 + time) * 0.5 + 1.5
        
        return (
          <group key={i}>
            <mesh position={[x, supplyY, 0]}>
              <sphereGeometry args={[0.08, 8, 8]} />
              <meshStandardMaterial color="#2ECC71" />
            </mesh>
            <mesh position={[x, demandY, 0]}>
              <sphereGeometry args={[0.08, 8, 8]} />
              <meshStandardMaterial color="#E74C3C" />
            </mesh>
          </group>
        )
      })}
      
      {/* Légendes */}
      <Text position={[-2, 2.5, 0]} fontSize={0.2} color="green" anchorX="center">
        Offre
      </Text>
      <Text position={[-2, 0.5, 0]} fontSize={0.2} color="red" anchorX="center">
        Demande
      </Text>
    </>
  )
}

// Simulation 3D pour l'histoire (timeline 3D)
const HistorySimulation3D = ({ visualizationData }: { visualizationData?: any }) => {
  const events = [
    { year: '1900', height: 0.5 },
    { year: '1950', height: 1.0 },
    { year: '2000', height: 1.5 },
  ]
  
  return (
    <>
      <gridHelper args={[8, 8, '#888888', '#444444']} />
      
      {/* Timeline 3D */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={3}
            array={new Float32Array([
              -3, 0, 0,
              0, 0, 0,
              3, 0, 0
            ])}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#E74C3C" linewidth={3} />
      </line>
      
      {/* Événements historiques */}
      {events.map((event, index) => {
        const x = (index - 1) * 3
        
        return (
          <group key={index} position={[x, event.height / 2, 0]}>
            <mesh>
              <cylinderGeometry args={[0.2, 0.2, event.height, 8]} />
              <meshStandardMaterial color="#E74C3C" />
            </mesh>
            
            <Text 
              position={[0, event.height / 2 + 0.3, 0]} 
              fontSize={0.2} 
              color="white"
              anchorX="center"
            >
              {event.year}
            </Text>
          </group>
        )
      })}
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

