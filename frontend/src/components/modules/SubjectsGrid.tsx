/**
 * Grille des cartes de matières
 */
import { SimpleGrid } from '@chakra-ui/react'
import { useTranslation } from 'react-i18next'
import { SubjectCard } from './SubjectCard'
import { SUBJECT_ORDER } from '../../constants/modules'
import { GroupedModules } from '../../types/module'

interface SubjectsGridProps {
  groupedModules: GroupedModules
  onSubjectClick: (subject: string) => void
}

export const SubjectsGrid = ({ groupedModules, onSubjectClick }: SubjectsGridProps) => {
  const { t } = useTranslation()

  const subjectLabels: Record<string, string> = {
    mathematics: '📐 Mathématiques',
    computer_science: '🤖 Informatique & IA',
    physics: '⚙️ Physique',
    chemistry: '🧪 Chimie',
    biology: '🧬 Biologie',
    geography: '🌍 Géographie',
    economics: '💰 Économie',
    history: '🏛️ Histoire',
  }

  return (
    <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
      {SUBJECT_ORDER.map((subject) => {
        const modules = groupedModules[subject] || []
        const moduleCount = modules.length

        // Ne pas afficher les matières sans modules
        if (moduleCount === 0) return null

        return (
          <SubjectCard
            key={subject}
            subject={subject}
            subjectLabel={subjectLabels[subject] || subject}
            moduleCount={moduleCount}
            onClick={() => onSubjectClick(subject)}
          />
        )
      })}
    </SimpleGrid>
  )
}


