/**
 * Composant de recherche avancée avec suggestions et filtres
 */
import { useState, useEffect, useRef, useCallback } from 'react'
import {
  Box,
  Input,
  InputGroup,
  InputLeftElement,
  InputRightElement,
  VStack,
  HStack,
  Text,
  Badge,
  Button,
  Icon,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverBody,
  useDisclosure,
  Kbd,
  Divider,
  Spinner,
} from '@chakra-ui/react'
import { SearchIcon, XIcon } from '@chakra-ui/icons'
import { FiFilter, FiX, FiClock, FiTrendingUp } from 'react-icons/fi'
import { useQuery } from 'react-query'
import api from '../services/api'
import { API_TIMEOUTS } from '../constants/api'
import { useDebounce } from '../hooks/useDebounce'

interface SearchSuggestion {
  id: string
  title: string
  type: 'module' | 'subject' | 'recent'
  subject?: string
}

interface AdvancedSearchProps {
  onSearch: (query: string) => void
  onFilterChange?: (filters: Record<string, any>) => void
  placeholder?: string
  showSuggestions?: boolean
  showRecentSearches?: boolean
  debounceMs?: number
}

export const AdvancedSearch = ({
  onSearch,
  onFilterChange,
  placeholder = 'Rechercher des modules...',
  showSuggestions = true,
  showRecentSearches = true,
  debounceMs = 300,
}: AdvancedSearchProps) => {
  const [query, setQuery] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const [recentSearches, setRecentSearches] = useState<string[]>([])
  const inputRef = useRef<HTMLInputElement>(null)
  const { isOpen, onOpen, onClose } = useDisclosure()

  const debouncedQuery = useDebounce(query, debounceMs)

  // Charger les recherches récentes depuis localStorage
  useEffect(() => {
    const stored = localStorage.getItem('kairos-recent-searches')
    if (stored) {
      try {
        setRecentSearches(JSON.parse(stored))
      } catch {
        setRecentSearches([])
      }
    }
  }, [])

  // Recherche de suggestions
  const { data: suggestions, isLoading: suggestionsLoading } = useQuery<SearchSuggestion[]>(
    ['search-suggestions', debouncedQuery],
    async () => {
      if (!debouncedQuery || debouncedQuery.length < 2) return []
      
      try {
        const response = await api.get('/modules/', {
          timeout: API_TIMEOUTS.SIMPLE, // 10 secondes pour les suggestions de recherche
          params: {
            search: debouncedQuery,
            limit: 10, // Limiter à 10 suggestions
          },
        })
        
        return (response.data || []).map((module: any) => ({
          id: module.id,
          title: module.title,
          type: 'module' as const,
          subject: module.subject,
        }))
      } catch {
        return []
      }
    },
    {
      enabled: showSuggestions && debouncedQuery.length >= 2,
      staleTime: 5 * 60 * 1000,
    }
  )

  // Sauvegarder la recherche récente
  const saveRecentSearch = useCallback((searchQuery: string) => {
    if (!searchQuery.trim()) return
    
    setRecentSearches((prev) => {
      const updated = [searchQuery, ...prev.filter((s) => s !== searchQuery)].slice(0, 5)
      localStorage.setItem('kairos-recent-searches', JSON.stringify(updated))
      return updated
    })
  }, [])

  // Gérer la recherche
  const handleSearch = useCallback(
    (searchQuery: string) => {
      setQuery(searchQuery)
      onSearch(searchQuery)
      if (searchQuery.trim()) {
        saveRecentSearch(searchQuery)
      }
      onClose()
    },
    [onSearch, saveRecentSearch, onClose]
  )

  // Recherche avec debounce
  useEffect(() => {
    if (debouncedQuery !== undefined) {
      onSearch(debouncedQuery)
    }
  }, [debouncedQuery, onSearch])

  // Gérer les raccourcis clavier
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K pour ouvrir la recherche
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
        onOpen()
      }
      // Escape pour fermer
      if (e.key === 'Escape' && isOpen) {
        onClose()
        inputRef.current?.blur()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onOpen, onClose])

  const hasSuggestions = suggestions && suggestions.length > 0
  const hasRecentSearches = recentSearches.length > 0
  const showPopover = isFocused && (hasSuggestions || hasRecentSearches || query.length >= 2)

  return (
    <Box position="relative" w="full">
      <InputGroup size="lg">
        <InputLeftElement pointerEvents="none">
          <SearchIcon color="blue.400" />
        </InputLeftElement>
        <Input
          ref={inputRef}
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => {
            setIsFocused(true)
            onOpen()
          }}
          onBlur={() => {
            // Délai pour permettre le clic sur les suggestions
            setTimeout(() => setIsFocused(false), 200)
          }}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              handleSearch(query)
            }
          }}
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
          aria-label="Recherche avancée"
          aria-autocomplete="list"
          aria-expanded={showPopover}
          aria-controls="search-suggestions"
        />
        {query && (
          <InputRightElement>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                setQuery('')
                handleSearch('')
              }}
              aria-label="Effacer la recherche"
            >
              <Icon as={FiX} />
            </Button>
          </InputRightElement>
        )}
      </InputGroup>

      {/* Raccourci clavier hint */}
      <HStack
        position="absolute"
        right={2}
        top="50%"
        transform="translateY(-50%)"
        display={{ base: 'none', md: 'flex' }}
        spacing={1}
        pointerEvents="none"
      >
        <Kbd>Ctrl</Kbd>
        <Text>+</Text>
        <Kbd>K</Kbd>
      </HStack>

      {/* Suggestions et recherches récentes */}
      {showPopover && (
        <Popover
          isOpen={isOpen}
          onClose={onClose}
          placement="bottom-start"
          closeOnBlur={true}
          closeOnEsc={true}
          autoFocus={false}
        >
          <PopoverTrigger>
            <Box position="absolute" w="full" />
          </PopoverTrigger>
          <PopoverContent
            w="full"
            maxW="600px"
            mt={2}
            boxShadow="xl"
            border="2px solid"
            borderColor="blue.100"
            borderRadius="xl"
            _focus={{ outline: 'none' }}
          >
            <PopoverBody p={0} maxH="400px" overflowY="auto">
              <VStack align="stretch" spacing={0}>
                {/* Suggestions de recherche */}
                {showSuggestions && query.length >= 2 && (
                  <>
                    {suggestionsLoading ? (
                      <Box p={4} textAlign="center">
                        <Spinner size="sm" color="blue.500" />
                        <Text fontSize="sm" color="gray.600" mt={2}>
                          Recherche en cours...
                        </Text>
                      </Box>
                    ) : hasSuggestions ? (
                      <>
                        <Box p={3} bg="blue.50" borderTopRadius="xl">
                          <HStack spacing={2}>
                            <Icon as={FiTrendingUp} color="blue.600" />
                            <Text fontSize="sm" fontWeight="semibold" color="blue.900">
                              Suggestions
                            </Text>
                          </HStack>
                        </Box>
                        {suggestions.map((suggestion) => (
                          <Box
                            key={suggestion.id}
                            p={3}
                            cursor="pointer"
                            _hover={{ bg: 'blue.50' }}
                            onClick={() => handleSearch(suggestion.title)}
                            onMouseDown={(e) => e.preventDefault()}
                            role="option"
                            aria-label={`Suggestion: ${suggestion.title}`}
                          >
                            <HStack spacing={3} justify="space-between">
                              <VStack align="start" spacing={1} flex={1}>
                                <Text fontWeight="medium" fontSize="sm">
                                  {suggestion.title}
                                </Text>
                                {suggestion.subject && (
                                  <Badge colorScheme="blue" fontSize="xs">
                                    {suggestion.subject}
                                  </Badge>
                                )}
                              </VStack>
                              <Icon as={SearchIcon} color="gray.400" />
                            </HStack>
                          </Box>
                        ))}
                      </>
                    ) : (
                      <Box p={4} textAlign="center">
                        <Text fontSize="sm" color="gray.600">
                          Aucun résultat trouvé
                        </Text>
                      </Box>
                    )}
                  </>
                )}

                {/* Recherches récentes */}
                {showRecentSearches && hasRecentSearches && !query && (
                  <>
                    {hasSuggestions && <Divider />}
                    <Box p={3} bg="gray.50">
                      <HStack spacing={2}>
                        <Icon as={FiClock} color="gray.600" />
                        <Text fontSize="sm" fontWeight="semibold" color="gray.900">
                          Recherches récentes
                        </Text>
                      </HStack>
                    </Box>
                    {recentSearches.map((recent, idx) => (
                      <Box
                        key={idx}
                        p={3}
                        cursor="pointer"
                        _hover={{ bg: 'gray.50' }}
                        onClick={() => handleSearch(recent)}
                        onMouseDown={(e) => e.preventDefault()}
                        role="option"
                        aria-label={`Recherche récente: ${recent}`}
                      >
                        <HStack spacing={3} justify="space-between">
                          <Text fontSize="sm" color="gray.700">
                            {recent}
                          </Text>
                          <Button
                            size="xs"
                            variant="ghost"
                            onClick={(e) => {
                              e.stopPropagation()
                              setRecentSearches((prev) => {
                                const updated = prev.filter((_, i) => i !== idx)
                                localStorage.setItem('kairos-recent-searches', JSON.stringify(updated))
                                return updated
                              })
                            }}
                            aria-label={`Supprimer la recherche récente: ${recent}`}
                          >
                            <Icon as={FiX} />
                          </Button>
                        </HStack>
                      </Box>
                    ))}
                  </>
                )}

                {/* Message si aucune suggestion */}
                {!hasSuggestions && !hasRecentSearches && query.length >= 2 && !suggestionsLoading && (
                  <Box p={4} textAlign="center">
                    <Text fontSize="sm" color="gray.600">
                      Appuyez sur <Kbd>Entrée</Kbd> pour rechercher
                    </Text>
                  </Box>
                )}
              </VStack>
            </PopoverBody>
          </PopoverContent>
        </Popover>
      )}
    </Box>
  )
}
