import { useEffect, useState } from 'react'
import { Box, VStack, Text, HStack, Badge } from '@chakra-ui/react'
import { performanceMonitor } from '../utils/performanceMonitor'

interface PerformanceOverlayProps {
  enabled?: boolean
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
}

const PerformanceOverlay = ({ 
  enabled = false, 
  position = 'top-right' 
}: PerformanceOverlayProps) => {
  const [stats, setStats] = useState(performanceMonitor.getStats())

  useEffect(() => {
    if (!enabled) {
      performanceMonitor.stopMonitoring()
      return
    }

    performanceMonitor.startMonitoring()
    const interval = setInterval(() => {
      setStats(performanceMonitor.getStats())
    }, 1000)

    return () => {
      clearInterval(interval)
      performanceMonitor.stopMonitoring()
    }
  }, [enabled])

  if (!enabled) return null

  const positionStyles = {
    'top-left': { top: 4, left: 4 },
    'top-right': { top: 4, right: 4 },
    'bottom-left': { bottom: 4, left: 4 },
    'bottom-right': { bottom: 4, right: 4 }
  }

  return (
    <Box
      position="absolute"
      {...positionStyles[position]}
      bg="blackAlpha.800"
      color="white"
      p={3}
      borderRadius="md"
      fontSize="xs"
      zIndex={1000}
      fontFamily="mono"
    >
      <VStack align="start" spacing={1}>
        <Text fontWeight="bold" fontSize="sm">Performance</Text>
        <HStack spacing={2}>
          <Text>FPS:</Text>
          <Badge colorScheme={stats.currentFPS >= 30 ? 'green' : stats.currentFPS >= 20 ? 'yellow' : 'red'}>
            {stats.currentFPS}
          </Badge>
        </HStack>
        <HStack spacing={2}>
          <Text>Avg:</Text>
          <Text>{stats.averageFPS}</Text>
        </HStack>
        <HStack spacing={2}>
          <Text>Min:</Text>
          <Badge colorScheme={stats.minFPS >= 20 ? 'green' : 'red'}>
            {stats.minFPS}
          </Badge>
        </HStack>
        {stats.memoryUsageMB > 0 && (
          <HStack spacing={2}>
            <Text>RAM:</Text>
            <Text>{stats.memoryUsageMB} MB</Text>
          </HStack>
        )}
        <Badge 
          colorScheme={stats.isHealthy ? 'green' : 'red'} 
          mt={1}
        >
          {stats.isHealthy ? '✓ Healthy' : '⚠ Low Performance'}
        </Badge>
      </VStack>
    </Box>
  )
}

export default PerformanceOverlay
















