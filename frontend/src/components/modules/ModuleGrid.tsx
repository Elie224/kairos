/**
 * Grille simple de modules (sans groupement par matière)
 */
import { SimpleGrid } from '@chakra-ui/react'
import { Module } from '../../types/module'
import { SUBJECT_COLORS } from '../../constants/modules'
import { ModuleCard } from './ModuleCard'

interface ModuleGridProps {
  modules: Module[]
  subjectLabels: Record<string, string>
}

export const ModuleGrid = ({ modules, subjectLabels }: ModuleGridProps) => {
  return (
    <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
      {modules.map((module) => {
        const subjectColor = SUBJECT_COLORS[module.subject] || 'gray'
        const subjectLabel = subjectLabels[module.subject] || module.subject

        return (
          <ModuleCard
            key={module.id}
            module={module}
            subjectColor={subjectColor}
            subjectLabel={subjectLabel}
          />
        )
      })}
    </SimpleGrid>
  )
}


