/**
 * Barre de filtres pour les modules
 */
import { VStack, HStack, Badge, Text, Input, InputGroup, InputLeftElement, Box } from '@chakra-ui/react'
import { SearchIcon } from '@chakra-ui/icons'
import { useTranslation } from 'react-i18next'
import { ModuleFilters } from '../../types/module'
import { SUBJECT_COLORS } from '../../constants/modules'

interface FilterBarProps {
  filters: ModuleFilters
  onFilterChange: (filters: Partial<ModuleFilters>) => void
}

export const FilterBar = ({ filters, onFilterChange }: FilterBarProps) => {
  const { t } = useTranslation()

  const subjectLabels: Record<string, string> = {
    physics: t('modules.physics'),
    chemistry: t('modules.chemistry'),
    mathematics: t('modules.mathematics'),
    english: t('modules.english'),
    computer_science: t('modules.computerScience'),
  }

  const handleSubjectFilter = (subject: string) => {
    onFilterChange({
      subject: filters.subject === subject ? '' : subject,
    })
  }

  return (
    <VStack 
      spacing={6} 
      align="stretch" 
      bg="white" 
      p={{ base: 5, md: 6 }} 
      borderRadius="2xl" 
      border="2px solid" 
      borderColor="blue.100" 
      boxShadow="soft-lg"
    >
      {/* Barre de recherche améliorée */}
      <Box>
        <Text 
          fontSize="sm" 
          fontWeight="600" 
          color="gray.800" 
          mb={3}
          fontFamily="body"
        >
          {t('modules.search') || 'Rechercher'}
        </Text>
        <InputGroup>
          <InputLeftElement pointerEvents="none">
            <SearchIcon color="blue.400" />
          </InputLeftElement>
          <Input
            placeholder={t('modules.searchPlaceholder')}
            value={filters.searchQuery}
            onChange={(e) => onFilterChange({ searchQuery: e.target.value })}
            size="lg"
            bg="white"
            borderRadius="xl"
            border="2px solid"
            borderColor="blue.100"
            _focus={{
              borderColor: 'blue.400',
              boxShadow: '0 0 0 3px rgba(37, 99, 235, 0.1)',
            }}
            _hover={{
              borderColor: 'blue.200',
            }}
            transition="all 0.3s"
          />
        </InputGroup>
      </Box>

      {/* Filtres par matière améliorés */}
      <Box>
        <Text 
          fontSize="sm" 
          fontWeight="600" 
          color="gray.800" 
          mb={3}
          fontFamily="body"
        >
          {t('modules.filterBySubject')}
        </Text>
        <HStack spacing={2} flexWrap="wrap">
          <Badge
            as="button"
            px={4}
            py={2}
            borderRadius="full"
            bg={filters.subject === '' ? 'blue.600' : 'transparent'}
            color={filters.subject === '' ? 'white' : 'blue.600'}
            border="2px solid"
            borderColor={filters.subject === '' ? 'blue.600' : 'blue.300'}
            cursor="pointer"
            onClick={() => handleSubjectFilter('')}
            _hover={{ 
              transform: 'scale(1.05)',
              bg: filters.subject === '' ? 'blue.700' : 'blue.50',
              borderColor: 'blue.500',
            }}
            transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
            fontWeight="600"
            boxShadow={filters.subject === '' ? 'md' : 'none'}
          >
            {t('modules.allSubjects')}
          </Badge>
          {Object.keys(subjectLabels).map((subject) => (
            <Badge
              key={subject}
              as="button"
              px={4}
              py={2}
              borderRadius="full"
              bg={filters.subject === subject ? 'blue.600' : 'transparent'}
              color={filters.subject === subject ? 'white' : 'blue.600'}
              border="2px solid"
              borderColor={filters.subject === subject ? 'blue.600' : 'blue.300'}
              cursor="pointer"
              onClick={() => handleSubjectFilter(subject)}
              _hover={{ 
                transform: 'scale(1.05)',
                bg: filters.subject === subject ? 'blue.700' : 'blue.50',
                borderColor: 'blue.500',
              }}
              transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
              fontWeight="600"
              boxShadow={filters.subject === subject ? 'md' : 'none'}
            >
              {subjectLabels[subject]}
            </Badge>
          ))}
        </HStack>
      </Box>

    </VStack>
  )
}

