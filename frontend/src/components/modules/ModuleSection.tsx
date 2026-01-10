/**
 * Section de modules groupés par matière
 */
import { Box, HStack, Badge, Text, SimpleGrid } from '@chakra-ui/react'
import { useTranslation } from 'react-i18next'
import { Module } from '../../types/module'
import { SUBJECT_COLORS } from '../../constants/modules'
import { ModuleCard } from './ModuleCard'

interface ModuleSectionProps {
  subject: string
  modules: Module[]
  subjectLabel: string
}

export const ModuleSection = ({ subject, modules, subjectLabel }: ModuleSectionProps) => {
  const { t } = useTranslation()
  const subjectColor = SUBJECT_COLORS[subject] || 'gray'

  if (modules.length === 0) return null

  return (
    <Box mb={10}>
      {/* En-tête de la section */}
      <HStack spacing={4} mb={6} align="center">
        <Badge
          colorScheme={subjectColor}
          fontSize="lg"
          px={4}
          py={2}
          borderRadius="md"
          fontWeight="bold"
        >
          {subjectLabel}
        </Badge>
        <Text fontSize="sm" color="gray.500" fontWeight="medium">
          {modules.length} {modules.length > 1 ? t('modules.modules') : t('modules.module')}
        </Text>
        <Box flex="1" height="2px" bg={`${subjectColor}.200`} borderRadius="full" />
      </HStack>

      {/* Grille de modules */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
        {modules.map((module) => (
          <ModuleCard
            key={module.id}
            module={module}
            subjectColor={subjectColor}
            subjectLabel={subjectLabel}
          />
        ))}
      </SimpleGrid>
    </Box>
  )
}


