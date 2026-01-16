/**
 * Composant pour afficher la force du mot de passe
 */
import { Box, HStack, Text, Progress, VStack } from '@chakra-ui/react'
import { useMemo } from 'react'

interface PasswordStrengthProps {
  password: string
}

export const PasswordStrength = ({ password }: PasswordStrengthProps) => {
  const strength = useMemo(() => {
    if (!password) return { score: 0, label: '', color: 'gray' }

    let score = 0
    const checks = {
      length: password.length >= 8,
      lowercase: /[a-z]/.test(password),
      uppercase: /[A-Z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[^a-zA-Z0-9]/.test(password),
    }

    if (checks.length) score++
    if (checks.lowercase) score++
    if (checks.uppercase) score++
    if (checks.number) score++
    if (checks.special) score++

    const strengthLevels = [
      { score: 0, label: 'Très faible', color: 'red' },
      { score: 1, label: 'Faible', color: 'orange' },
      { score: 2, label: 'Moyen', color: 'yellow' },
      { score: 3, label: 'Bon', color: 'blue' },
      { score: 4, label: 'Très bon', color: 'green' },
      { score: 5, label: 'Excellent', color: 'green' },
    ]

    return strengthLevels[Math.min(score, 5)]
  }, [password])

  if (!password) return null

  return (
    <VStack spacing={2} align="stretch" mt={2}>
      <HStack spacing={2} justify="space-between">
        <Text fontSize="xs" color="gray.600" fontWeight="medium">
          Force du mot de passe
        </Text>
        <Text fontSize="xs" color={`${strength.color}.600`} fontWeight="bold">
          {strength.label}
        </Text>
      </HStack>
      <Progress
        value={(strength.score / 5) * 100}
        colorScheme={strength.color}
        size="sm"
        borderRadius="full"
        bg="gray.100"
      />
      <HStack spacing={4} fontSize="xs" color="gray.500" flexWrap="wrap">
        <Text color={password.length >= 8 ? 'green.500' : 'gray.400'}>
          {password.length >= 8 ? '✓' : '○'} 8+ caractères
        </Text>
        <Text color={/[a-z]/.test(password) ? 'green.500' : 'gray.400'}>
          {/[a-z]/.test(password) ? '✓' : '○'} Minuscule
        </Text>
        <Text color={/[A-Z]/.test(password) ? 'green.500' : 'gray.400'}>
          {/[A-Z]/.test(password) ? '✓' : '○'} Majuscule
        </Text>
        <Text color={/[0-9]/.test(password) ? 'green.500' : 'gray.400'}>
          {/[0-9]/.test(password) ? '✓' : '○'} Chiffre
        </Text>
        <Text color={/[^a-zA-Z0-9]/.test(password) ? 'green.500' : 'gray.400'}>
          {/[^a-zA-Z0-9]/.test(password) ? '✓' : '○'} Spécial
        </Text>
      </HStack>
    </VStack>
  )
}
