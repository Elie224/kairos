import { Box, Skeleton, SkeletonText, VStack, HStack } from '@chakra-ui/react'

export const CardSkeleton = () => (
  <Box p={6} bg="white" borderRadius="lg" boxShadow="sm">
    <VStack align="stretch" spacing={4}>
      <Skeleton height="20px" width="60%" />
      <SkeletonText noOfLines={3} spacing="2" />
    </VStack>
  </Box>
)

export const ModuleCardSkeleton = () => (
  <Box p={6} bg="white" borderRadius="lg" boxShadow="sm">
    <VStack align="start" spacing={4}>
      <HStack spacing={2} width="full">
        <Skeleton height="24px" width="80px" borderRadius="md" />
        <Skeleton height="24px" width="100px" borderRadius="md" />
      </HStack>
      <Skeleton height="24px" width="80%" />
      <SkeletonText noOfLines={2} spacing="2" />
      <Skeleton height="16px" width="40%" />
    </VStack>
  </Box>
)

export const StatCardSkeleton = () => (
  <Box p={6} bg="white" borderRadius="lg" boxShadow="sm">
    <HStack spacing={4}>
      <Skeleton height="60px" width="60px" borderRadius="lg" />
      <VStack align="start" spacing={2} flex="1">
        <Skeleton height="16px" width="60%" />
        <Skeleton height="32px" width="40%" />
        <Skeleton height="12px" width="80%" />
      </VStack>
    </HStack>
  </Box>
)




