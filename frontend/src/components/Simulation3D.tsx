import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Stars, Text } from '@react-three/drei'
import { Suspense, useRef } from 'react'
import { Box, Text as ChakraText } from '@chakra-ui/react'
import * as THREE from 'three'
import { ModuleContent } from '../types/moduleContent'

interface Module {
  content?: ModuleContent
  subject: string
}

interface Simulation3DProps {
  module: Module
}

const Simulation3D = ({ module }: Simulation3DProps) => {
  const subject = module.subject?.toLowerCase()
  const allowedSubjects3D = ['physics', 'chemistry']
  const is3DSubject = allowedSubjects3D.includes(subject)
  
  // Pour les matières non-3D, afficher une visualisation 2D appropriée
  if (!is3DSubject) {
    return <Visualization2D module={module} />
  }
  
  const renderScene = () => {
    const sceneType = module.content?.scene || 'default'
    
    // Mapper les scènes selon la matière
    if (module.subject?.toLowerCase() === 'physics') {
      switch (sceneType) {
        case 'gravitation':
          return <GravitationSimulation />
        case 'mechanics':
          return <MechanicsSimulation />
        default:
          return <MechanicsSimulation /> // Par défaut pour la physique
      }
    } else if (module.subject?.toLowerCase() === 'chemistry') {
      switch (sceneType) {
        case 'chemical_reaction':
          return <ChemicalReaction />
        default:
          return <ChemicalReaction /> // Par défaut pour la chimie
      }
    }
    
    // Fallback par défaut
    return <DefaultScene />
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
        {module.subject === 'physics' ? '⚙️ Physique' : '🧪 Chimie'}
      </Box>
    </Box>
  )
}

// Simulation de gravitation avec animation
const GravitationSimulation = () => {
  const satelliteRef = useRef<THREE.Mesh>(null)
  
  useFrame((state) => {
    if (satelliteRef.current) {
      const time = state.clock.getElapsedTime()
      const radius = 3
      satelliteRef.current.position.x = Math.cos(time) * radius
      satelliteRef.current.position.z = Math.sin(time) * radius
    }
  })

  return (
    <>
      {/* Planète centrale */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial color="#4A90E2" />
      </mesh>
      
      {/* Satellite en orbite */}
      <mesh ref={satelliteRef} position={[3, 0, 0]}>
        <sphereGeometry args={[0.2, 16, 16]} />
        <meshStandardMaterial color="#F5A623" />
      </mesh>
      
      {/* Orbite */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[2.5, 3.5, 64]} />
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
const ChemicalReaction = () => {
  return (
    <>
      {/* Molécule CH4 */}
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
const MechanicsSimulation = () => {
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

// Visualisation 2D pour les autres matières
const Visualization2D = ({ module }: { module: Module }) => {
  const subject = module.subject?.toLowerCase()
  
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
          <ChakraText fontSize="xs" color="gray.500">
            Les visualisations 2D interactives pour cette matière seront bientôt disponibles.
            <br />
            En attendant, explorez le contenu du module dans la section détail.
          </ChakraText>
        </Box>
      </Box>
    </Box>
  )
}

export default Simulation3D

