/**
 * Page des modules d'apprentissage
 * 
 * Affiche tous les modules disponibles organisés par matière :
 * - Grille de sélection de matière (Mathématiques, Physique, Chimie, etc.)
 * - Liste filtrée des modules par matière sélectionnée
 * - Barre de recherche avancée pour filtrer les modules
 * - Filtres par niveau et difficulté
 * 
 * L'utilisateur peut cliquer sur une matière pour voir ses modules,
 * ou utiliser la recherche pour trouver un module spécifique
 * 
 * @module pages/Modules
 */
import { useState, useEffect } from 'react'
import {
  Container,
  VStack,
  Heading,
  Text,
  Box,
  Alert,
  AlertIcon,
  HStack,
  Badge,
  Button,
  Icon,
  Divider,
} from '@chakra-ui/react'
import { useTranslation } from 'react-i18next'
import { FiArrowLeft, FiBook } from 'react-icons/fi'
import { ModuleFilters } from '../types/module'
import { useModules } from '../hooks/useModules'
import { FilterBar } from '../components/modules/FilterBar'
import { AdvancedSearch } from '../components/AdvancedSearch'
import { ModuleGrid } from '../components/modules/ModuleGrid'
import { SubjectsGrid } from '../components/modules/SubjectsGrid'
import { ModuleCardSkeleton } from '../components/SkeletonLoader'
import { SUBJECT_COLORS } from '../constants/modules'

const Modules = () => {
  const { t } = useTranslation()
  const [filters, setFilters] = useState<ModuleFilters>({
    subject: '',
    searchQuery: '',
  })
  const [selectedSubject, setSelectedSubject] = useState<string | null>(null)

  // Log pour déboguer - s'assurer qu'on est bien sur /modules et pas /modules/:id
  useEffect(() => {
    const pathname = window.location.pathname
    console.log('🟢 Modules component RENDERED', { pathname, timestamp: new Date().toISOString() })
    // Si on est sur /modules/:id, on ne devrait PAS être ici - rediriger immédiatement
    if (pathname.match(/^\/modules\/[^/]+$/)) {
      console.error('❌ ERREUR CRITIQUE: Modules component rendu sur une route /modules/:id!', { pathname })
      console.error('❌ Redirection immédiate vers la bonne route...')
      // Redirection immédiate vers la route correcte
      window.location.href = pathname
      return
    }
  }, [])

  const { modules, groupedModules, isLoading, totalCount } = useModules(filters)

  // Synchroniser selectedSubject avec filters.subject
  useEffect(() => {
    if (filters.subject && filters.subject !== selectedSubject) {
      setSelectedSubject(filters.subject)
    } else if (!filters.subject && selectedSubject) {
      setSelectedSubject(null)
    }
  }, [filters.subject, selectedSubject])

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


  const handleFilterChange = (newFilters: Partial<ModuleFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }))
    if (newFilters.subject !== undefined) {
      setSelectedSubject(newFilters.subject || null)
    }
  }

  const handleSubjectClick = (subject: string) => {
    setSelectedSubject(subject)
    setFilters((prev) => ({ ...prev, subject }))
  }

  const handleBackToSubjects = () => {
    setSelectedSubject(null)
    setFilters((prev) => ({ ...prev, subject: '', searchQuery: '' }))
  }

  return (
    <Box bgGradient="linear-gradient(180deg, blue.50 0%, white 100%)" minH="100vh" py={{ base: 6, md: 10 }}>
      <Container maxW="1400px">
        <VStack spacing={{ base: 8, md: 10 }} align="stretch">
          {/* En-tête amélioré avec thème bleu */}
          <Box>
            <VStack spacing={4} align="start" mb={6}>
              <HStack spacing={4} align="center">
                <Box
                  p={3}
                  bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                  borderRadius="xl"
                  boxShadow="lg"
                >
                  <Icon as={FiBook} boxSize={6} color="white" />
                </Box>
                <Heading 
                  size={{ base: 'xl', md: '2xl' }} 
                  color="gray.900" 
                  fontWeight="700"
                  letterSpacing="-0.02em"
                  fontFamily="heading"
                >
                  {t('modules.title')}
                </Heading>
              </HStack>
              <Text 
                color="gray.700" 
                fontSize={{ base: 'md', md: 'lg' }} 
                maxW="2xl"
                lineHeight="1.7"
                letterSpacing="0.01em"
                fontFamily="body"
              >
                {t('modules.subtitle')}
              </Text>
            </VStack>
          </Box>

          {/* Bouton retour si une matière est sélectionnée */}
          {selectedSubject && (
            <Box>
              <Button
                leftIcon={<Icon as={FiArrowLeft} />}
                variant="ghost"
                colorScheme="blue"
                onClick={handleBackToSubjects}
                size="md"
                color="blue.600"
                fontWeight="600"
                _hover={{
                  bg: 'blue.50',
                  transform: 'translateX(-4px)',
                  color: 'blue.700',
                }}
                transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
              >
                {t('modules.backToSubjects') || 'Retour aux matières'}
              </Button>
              <Divider mt={4} borderColor="blue.100" />
            </Box>
          )}

          {/* Barre de recherche avancée - toujours visible */}
          <Box>
            <AdvancedSearch
              onSearch={(query) => handleFilterChange({ searchQuery: query })}
              placeholder="Rechercher des modules..."
              showSuggestions={true}
              showRecentSearches={true}
            />
          </Box>

          {/* Barre de filtres - seulement si une matière est sélectionnée */}
          {selectedSubject && (
            <Box>
              <FilterBar filters={filters} onFilterChange={handleFilterChange} />
            </Box>
          )}

          {/* Contenu principal */}
          {isLoading ? (
            <VStack spacing={6}>
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <ModuleCardSkeleton key={i} />
              ))}
            </VStack>
          ) : selectedSubject ? (
            // Affichage des modules de la matière sélectionnée
            <Box>
              {/* En-tête de la matière amélioré avec thème bleu */}
              <Box 
                mb={8} 
                p={{ base: 5, md: 6 }} 
                bg="white" 
                borderRadius="2xl" 
                boxShadow="soft-lg" 
                border="2px solid" 
                borderColor="blue.100"
              >
                <VStack spacing={4} align="stretch">
                  <HStack spacing={4} align="center" flexWrap="wrap">
                    <Badge
                      bg="blue.600"
                      color="white"
                      fontSize={{ base: 'md', md: 'lg' }}
                      px={6}
                      py={3}
                      borderRadius="xl"
                      fontWeight="700"
                      textTransform="uppercase"
                      letterSpacing="wide"
                      boxShadow="md"
                    >
                      {subjectLabels[selectedSubject]}
                    </Badge>
                    <Divider orientation="vertical" height="30px" borderColor="blue.200" />
                    <Text 
                      fontSize={{ base: 'md', md: 'lg' }} 
                      color="gray.700" 
                      fontWeight="600"
                      fontFamily="body"
                    >
                      {totalCount} {totalCount > 1 ? t('modules.modules') : t('modules.module')} disponible{totalCount > 1 ? 's' : ''}
                    </Text>
                  </HStack>
                  {totalCount === 0 && (
                    <Alert status="info" borderRadius="xl" mt={2} bg="blue.50" border="1px solid" borderColor="blue.200">
                      <AlertIcon color="blue.500" />
                      <Text color="gray.700" fontWeight="500">{t('modules.noModulesFound')}</Text>
                    </Alert>
                  )}
                </VStack>
              </Box>

              {/* Grille de modules */}
              {totalCount > 0 && (
                <ModuleGrid
                  modules={modules}
                  subjectLabels={subjectLabels}
                />
              )}
            </Box>
          ) : (
            // Affichage des cartes de matières
            <Box>
              {/* Section d'introduction améliorée */}
              <Box 
                mb={8} 
                textAlign="center"
                p={6}
                bg="white"
                borderRadius="2xl"
                boxShadow="soft"
                border="1px solid"
                borderColor="blue.100"
              >
                <Badge
                  bg="blue.600"
                  color="white"
                  fontSize="sm"
                  px={4}
                  py={2}
                  borderRadius="full"
                  fontWeight="600"
                  mb={4}
                  boxShadow="md"
                >
                  Matières Disponibles
                </Badge>
                <Heading 
                  size={{ base: 'lg', md: 'xl' }} 
                  color="gray.900" 
                  fontWeight="700"
                  mb={3}
                  letterSpacing="-0.02em"
                  fontFamily="heading"
                >
                  {t('modules.selectSubject') || 'Sélectionnez une matière pour voir ses modules'}
                </Heading>
                <Text 
                  fontSize={{ base: 'sm', md: 'md' }} 
                  color="gray.700"
                  lineHeight="1.7"
                  fontFamily="body"
                >
                  Cliquez sur une carte pour explorer les modules disponibles
                </Text>
              </Box>
              
              {/* Grille de matières */}
              <SubjectsGrid
                groupedModules={groupedModules}
                onSubjectClick={handleSubjectClick}
              />
            </Box>
          )}
        </VStack>
      </Container>
    </Box>
  )
}

export default Modules
