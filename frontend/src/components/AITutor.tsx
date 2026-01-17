import { useState, useRef, useEffect } from 'react'
import { Box, VStack, HStack, Input, Button, Text, Card, CardBody, Badge, Spinner, Alert, AlertIcon, IconButton, Flex, Wrap, WrapItem, Image, CloseButton } from '@chakra-ui/react'
import { useTranslation } from 'react-i18next'
import { FiSend, FiX, FiMessageCircle, FiPaperclip } from 'react-icons/fi'
import { chatService, ChatMessage } from '../services/chatService'
import logger from '../utils/logger'

interface AITutorProps {
  moduleId: string
}

interface FilePreview {
  file: File
  preview: string
  type: 'image' | 'file'
}

const AITutor = ({ moduleId }: AITutorProps) => {
  const { t } = useTranslation()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string>('')
  const [attachedFiles, setAttachedFiles] = useState<FilePreview[]>([])
  const [error, setError] = useState<string | null>(null)

  // Suggestions de questions initiales
  const initialSuggestions = [
    t('aiTutor.suggestions.explain') || "Peux-tu m'expliquer ce concept ?",
    t('aiTutor.suggestions.example') || "Peux-tu me donner un exemple concret ?",
    t('aiTutor.suggestions.application') || "Comment cela s'applique-t-il dans la vie quotidienne ?",
    t('aiTutor.suggestions.difference') || "Quelle est la différence avec un concept similaire ?"
  ]

  const scrollToBottom = () => {
    // Utiliser requestAnimationFrame pour s'assurer que le DOM est mis à jour
    requestAnimationFrame(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages]) // Scroller quand les messages changent

  useEffect(() => {
    // Scroller pendant le streaming aussi (avec un petit délai pour la performance)
    if (currentStreamingMessage && isStreaming) {
      const timer = setTimeout(() => scrollToBottom(), 100)
      return () => clearTimeout(timer)
    }
  }, [currentStreamingMessage, isStreaming])

  // Charger l'historique de conversation depuis le backend au démarrage
  useEffect(() => {
    const loadHistory = async () => {
      if (!moduleId) return
      
      try {
        const historyMessages = await chatService.loadHistory(moduleId)
        if (historyMessages.length > 0) {
          setMessages(historyMessages)
        }
      } catch (error) {
        // Logger l'erreur de manière centralisée (ne pas bloquer l'interface)
        logger.error('Erreur lors du chargement de l\'historique', error, 'AITutor')
      }
    }
    
    loadHistory()
  }, [moduleId])

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    const newFiles: FilePreview[] = []
    Array.from(files).forEach((file) => {
      const isImage = file.type.startsWith('image/')
      const preview: FilePreview = {
        file,
        preview: isImage ? URL.createObjectURL(file) : '',
        type: isImage ? 'image' : 'file'
      }
      newFiles.push(preview)
    })

    setAttachedFiles((prev) => [...prev, ...newFiles])
    
    // Réinitialiser l'input file
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const removeFile = (index: number) => {
    const file = attachedFiles[index]
    if (file.preview) {
      URL.revokeObjectURL(file.preview)
    }
    setAttachedFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input.trim()
    if ((!textToSend && attachedFiles.length === 0) || isStreaming) return

    // Créer le message utilisateur avec les fichiers
    const userMessage: ChatMessage = { 
      role: 'user', 
      content: textToSend || (attachedFiles.length > 0 ? '📎 Fichier(s) joint(s)' : ''),
      timestamp: new Date(),
      files: attachedFiles.map(f => ({ name: f.file.name, type: f.type, preview: f.preview }))
    }
    setMessages((prev) => [...prev, userMessage])
    setSuggestions([])
    setIsStreaming(true)
    setCurrentStreamingMessage('')

    try {
      // Si des fichiers sont attachés, utiliser l'endpoint avec fichiers
      if (attachedFiles.length > 0) {
        await chatService.sendMessageStreamWithFiles(
          textToSend || '',
          attachedFiles.map(f => f.file),
          {
            moduleId,
            language: 'fr',
            onChunk: (chunk) => {
              setCurrentStreamingMessage(prev => {
                const newMessage = prev + chunk
                // Faire défiler automatiquement pendant le streaming
                setTimeout(() => scrollToBottom(), 50)
                return newMessage
              })
            },
            onComplete: (fullResponse) => {
              const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: fullResponse,
                timestamp: new Date()
              }
              setMessages((prev) => [...prev, assistantMessage])
              setCurrentStreamingMessage('')
              setIsStreaming(false)
              // Nettoyer les fichiers attachés après envoi
              attachedFiles.forEach(f => {
                if (f.preview) URL.revokeObjectURL(f.preview)
              })
              setAttachedFiles([])
            },
            onError: (error) => {
              // Logger l'erreur de manière centralisée
              logger.error('Erreur chat avec fichiers', error, 'AITutor')
              setError(error instanceof Error ? error.message : 'Une erreur est survenue lors de la communication avec Kaïrox')
              setIsStreaming(false)
              setCurrentStreamingMessage('')
              // Retirer le message utilisateur en cas d'erreur pour permettre une nouvelle tentative
              setMessages((prev) => prev.slice(0, -1))
            }
          }
        )
      } else {
        // Utiliser l'endpoint normal sans fichiers
        await chatService.sendMessageStream(textToSend, {
          moduleId,
          language: 'fr',
          onChunk: (chunk) => {
            setCurrentStreamingMessage(prev => {
              const newMessage = prev + chunk
              // Faire défiler automatiquement pendant le streaming
              setTimeout(() => scrollToBottom(), 50)
              return newMessage
            })
          },
          onComplete: (fullResponse) => {
            const assistantMessage: ChatMessage = {
              role: 'assistant',
              content: fullResponse,
              timestamp: new Date()
            }
            setMessages((prev) => [...prev, assistantMessage])
            setCurrentStreamingMessage('')
            setIsStreaming(false)
            setError(null) // Effacer les erreurs précédentes en cas de succès
          },
          onError: (error) => {
            logger.error('Erreur chat', error, 'AITutor')
            setError(error instanceof Error ? error.message : 'Une erreur est survenue lors de la communication avec Kaïrox')
            setIsStreaming(false)
            setCurrentStreamingMessage('')
            // Retirer le message utilisateur en cas d'erreur pour permettre une nouvelle tentative
            setMessages((prev) => prev.slice(0, -1))
          }
        })
      }
    } catch (error) {
      // Logger l'erreur de manière centralisée
      logger.error('Erreur lors de l\'envoi du message', error, 'AITutor')
      setError(error instanceof Error ? error.message : 'Une erreur est survenue. Veuillez réessayer.')
      setIsStreaming(false)
      setCurrentStreamingMessage('')
      // Retirer le message utilisateur en cas d'erreur pour permettre une nouvelle tentative
      setMessages((prev) => prev.slice(0, -1))
    }

    if (!messageText) {
      setInput('')
    }
  }

  const handleSuggestionClick = (suggestion: string) => {
    handleSend(suggestion)
  }

  const clearChat = () => {
    setMessages([])
    setSuggestions([])
    setError(null)
    setCurrentStreamingMessage('')
    chatService.clearHistory()
  }

  return (
    <VStack spacing={0} align="stretch" h={{ base: '500px', md: '700px' }} w="100%">
      <Card h="100%" display="flex" flexDirection="column" borderRadius="lg" boxShadow="md" overflow="hidden">
        <CardBody display="flex" flexDirection="column" h="100%" p={0} gap={0}>
          {/* Header amélioré */}
          <Box 
            p={{ base: 4, md: 5 }} 
            borderBottom="1px" 
            borderColor="gray.200" 
            bgGradient="linear(to-r, blue.50, purple.50)"
          >
            <Flex justify="space-between" align="center">
              <HStack spacing={3}>
                <Box
                  p={2}
                  borderRadius="full"
                  bg="white"
                  boxShadow="sm"
                >
                  <FiMessageCircle size={24} color="#1e88e5" />
                </Box>
                <VStack align="start" spacing={0}>
                  <Text fontSize={{ base: 'lg', md: 'xl' }} fontWeight="bold" color="gray.800">
                    {t('aiTutor.title') || 'Kaïrox'}
                  </Text>
                  <Text fontSize="xs" color="gray.600">
                    Assistant IA personnel
                  </Text>
                </VStack>
              </HStack>
              {messages.length > 0 && (
                <IconButton
                  aria-label="Effacer la conversation"
                  icon={<FiX />}
                  size="sm"
                  variant="ghost"
                  colorScheme="gray"
                  onClick={clearChat}
                  _hover={{ bg: 'whiteAlpha.800' }}
                />
              )}
            </Flex>
          </Box>

          {/* Messages Area améliorée */}
          <Box 
            flex={1} 
            overflowY="auto" 
            p={{ base: 4, md: 6 }} 
            bg="gray.50"
            css={{
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: 'transparent',
              },
              '&::-webkit-scrollbar-thumb': {
                background: '#cbd5e0',
                borderRadius: '4px',
              },
              '&::-webkit-scrollbar-thumb:hover': {
                background: '#a0aec0',
              },
            }}
          >
            <VStack spacing={{ base: 3, md: 4 }} align="stretch">
              {/* Affichage des erreurs */}
              {error && (
                <Alert 
                  status="error" 
                  borderRadius="lg"
                  onClose={() => setError(null)}
                  closeButton
                >
                  <AlertIcon />
                  <Box>
                    <Text fontWeight="bold">Erreur de communication</Text>
                    <Text fontSize="sm">{error}</Text>
                  </Box>
                </Alert>
              )}
              {messages.length === 0 && (
                <Box textAlign="center" py={{ base: 8, md: 12 }}>
                  <Box 
                    mb={6} 
                    display="flex" 
                    justifyContent="center"
                    position="relative"
                  >
                    <Box
                      p={6}
                      borderRadius="full"
                      bgGradient="linear(to-br, blue.100, purple.100)"
                      boxShadow="lg"
                    >
                      <FiMessageCircle size={64} color="#1e88e5" />
                    </Box>
                  </Box>
                  <Text fontSize={{ base: 'xl', md: '2xl' }} fontWeight="bold" mb={3} color="gray.800">
                    {t('aiTutor.welcome') || 'Bonjour ! Je suis Kaïrox 👋'}
                  </Text>
                  <Text fontSize={{ base: 'md', md: 'lg' }} color="gray.600" mb={8} maxW="600px" mx="auto">
                    {t('aiTutor.subtitle') || 'Votre assistant IA personnel. Posez-moi vos questions sur ce module et je vous aiderai à comprendre les concepts.'}
                  </Text>
                  
                  {/* Suggestions initiales améliorées */}
                  <VStack spacing={3} align="stretch" maxW="600px" mx="auto">
                    <Text fontSize="sm" color="gray.500" fontWeight="medium" mb={2}>
                      Questions suggérées :
                    </Text>
                    <VStack spacing={2} align="stretch">
                      {initialSuggestions.map((suggestion, idx) => (
                        <Button
                          key={idx}
                          size="md"
                          variant="outline"
                          colorScheme="blue"
                          justifyContent="flex-start"
                          textAlign="left"
                          leftIcon={<FiMessageCircle />}
                          onClick={() => handleSuggestionClick(suggestion)}
                          _hover={{ bg: 'blue.50', borderColor: 'blue.300', transform: 'translateX(4px)' }}
                          transition="all 0.2s"
                          borderRadius="md"
                          py={6}
                          px={4}
                        >
                          <Text fontSize="sm">{suggestion}</Text>
                        </Button>
                      ))}
                    </VStack>
                  </VStack>
                </Box>
              )}

              {messages.map((msg, idx) => (
                <Box
                  key={idx}
                  alignSelf={msg.role === 'user' ? 'flex-end' : 'flex-start'}
                  maxW={{ base: '85%', md: '75%', lg: '65%' }}
                  width="fit-content"
                  mb={4}
                >
                  <HStack
                    spacing={2}
                    align="center"
                    justify={msg.role === 'user' ? 'flex-end' : 'flex-start'}
                    mb={2}
                  >
                    {msg.role === 'assistant' && (
                      <Badge 
                        colorScheme="blue" 
                        borderRadius="full" 
                        px={3} 
                        py={1} 
                        fontSize="xs"
                        fontWeight="medium"
                      >
                        🤖 {t('aiTutor.tutor') || 'Kaïrox'}
                      </Badge>
                    )}
                    {msg.role === 'user' && (
                      <Badge 
                        colorScheme="purple" 
                        borderRadius="full" 
                        px={3} 
                        py={1} 
                        fontSize="xs"
                        fontWeight="medium"
                      >
                        👤 {t('aiTutor.you') || 'Vous'}
                      </Badge>
                    )}
                    <Text fontSize="xs" color="gray.500">
                      {new Date(msg.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                    </Text>
                  </HStack>
                  <Card
                    bg={msg.role === 'user' 
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                      : 'white'}
                    color={msg.role === 'user' ? 'white' : 'gray.800'}
                    boxShadow={msg.role === 'user' ? 'md' : 'sm'}
                    borderRadius="xl"
                    border={msg.role === 'assistant' ? '1px solid' : 'none'}
                    borderColor={msg.role === 'assistant' ? 'gray.200' : 'transparent'}
                    _hover={{ boxShadow: 'lg' }}
                    transition="all 0.2s"
                  >
                    <CardBody p={{ base: 4, md: 5 }}>
                      {/* Afficher les fichiers/images si présents */}
                      {msg.files && msg.files.length > 0 && (
                        <VStack spacing={3} align="stretch" mb={4}>
                          {msg.files.map((file, fileIdx) => (
                            <Box key={fileIdx} position="relative">
                              {file.type === 'image' && file.preview ? (
                                <Box
                                  borderRadius="lg"
                                  overflow="hidden"
                                  boxShadow="sm"
                                >
                                  <Image
                                    src={file.preview}
                                    alt={file.name}
                                    maxH="400px"
                                    objectFit="contain"
                                  />
                                </Box>
                              ) : (
                                <Box
                                  p={4}
                                  bg={msg.role === 'user' ? 'whiteAlpha.200' : 'gray.100'}
                                  borderRadius="md"
                                  border="1px solid"
                                  borderColor={msg.role === 'user' ? 'whiteAlpha.300' : 'gray.200'}
                                >
                                  <HStack spacing={2}>
                                    <Text fontSize="lg">📎</Text>
                                    <Text fontSize="sm" fontWeight="medium">{file.name}</Text>
                                  </HStack>
                                </Box>
                              )}
                            </Box>
                          ))}
                        </VStack>
                      )}
                      <Text 
                        whiteSpace="pre-wrap" 
                        lineHeight="1.8"
                        fontSize={{ base: 'sm', md: 'md' }}
                      >
                        {msg.content}
                      </Text>
                    </CardBody>
                  </Card>
                  
                  {/* Suggestions après la réponse de l'IA */}
                  {msg.role === 'assistant' && msg.suggestions && msg.suggestions.length > 0 && (
                    <Wrap spacing={2} mt={2}>
                      {msg.suggestions.map((suggestion, sIdx) => (
                        <WrapItem key={sIdx}>
                          <Button
                            size="xs"
                            variant="ghost"
                            colorScheme="brand"
                            onClick={() => handleSuggestionClick(suggestion)}
                            _hover={{ bg: 'gray.50' }}
                          >
                            {suggestion}
                          </Button>
                        </WrapItem>
                      ))}
                    </Wrap>
                  )}
                </Box>
              ))}

              {/* Suggestions globales */}
              {suggestions.length > 0 && messages.length > 0 && (
                <Box mt={2}>
                  <Text fontSize="xs" color="gray.500" mb={2}>
                    {t('aiTutor.suggestions.title') || 'Suggestions de questions :'}
                  </Text>
                  <Wrap spacing={2}>
                    {suggestions.map((suggestion, idx) => (
                      <WrapItem key={idx}>
                        <Button
                          size="sm"
                          variant="outline"
                          colorScheme="brand"
                          onClick={() => handleSuggestionClick(suggestion)}
                          _hover={{ bg: 'gray.50' }}
                        >
                          {suggestion}
                        </Button>
                      </WrapItem>
                    ))}
                  </Wrap>
                </Box>
              )}

              {/* Message en cours de streaming amélioré */}
              {isStreaming && currentStreamingMessage && (
                <Box
                  alignSelf="flex-start"
                  maxW={{ base: '85%', md: '75%', lg: '65%' }}
                  width="fit-content"
                  mb={4}
                >
                  <HStack spacing={2} align="center" mb={2}>
                    <Badge 
                      colorScheme="blue" 
                      borderRadius="full" 
                      px={3} 
                      py={1} 
                      fontSize="xs"
                      fontWeight="medium"
                    >
                      🤖 {t('aiTutor.tutor') || 'Kaïrox'}
                    </Badge>
                    <Spinner size="xs" color="blue.500" />
                  </HStack>
                  <Card 
                    bg="white" 
                    boxShadow="md" 
                    borderRadius="xl"
                    border="1px solid"
                    borderColor="gray.200"
                  >
                    <CardBody p={{ base: 4, md: 5 }}>
                      <Text 
                        whiteSpace="pre-wrap" 
                        lineHeight="1.8"
                        fontSize={{ base: 'sm', md: 'md' }}
                      >
                        {currentStreamingMessage}
                        <Text 
                          as="span" 
                          opacity={0.7}
                          fontWeight="bold"
                          ml={1}
                          animation="blink 1s infinite"
                          css={{
                            '@keyframes blink': {
                              '0%, 50%': { opacity: 1 },
                              '51%, 100%': { opacity: 0.3 },
                            },
                          }}
                        >
                          ▋
                        </Text>
                      </Text>
                    </CardBody>
                  </Card>
                </Box>
              )}

              {/* Indicateur de chargement amélioré */}
              {isStreaming && !currentStreamingMessage && (
                <Box
                  alignSelf="flex-start"
                  maxW={{ base: '85%', md: '75%', lg: '65%' }}
                  width="fit-content"
                  mb={4}
                >
                  <HStack spacing={2} align="center" mb={2}>
                    <Badge 
                      colorScheme="blue" 
                      borderRadius="full" 
                      px={3} 
                      py={1} 
                      fontSize="xs"
                      fontWeight="medium"
                    >
                      🤖 {t('aiTutor.tutor') || 'Kaïrox'}
                    </Badge>
                  </HStack>
                  <Card 
                    bg="white" 
                    boxShadow="sm" 
                    borderRadius="xl"
                    border="1px solid"
                    borderColor="gray.200"
                  >
                    <CardBody p={4}>
                      <HStack spacing={3}>
                        <Spinner size="sm" color="blue.500" thickness="3px" />
                        <Text color="gray.600" fontSize="sm" fontWeight="medium">
                          {t('aiTutor.thinking') || 'Réflexion en cours...'}
                        </Text>
                      </HStack>
                    </CardBody>
                  </Card>
                </Box>
              )}

              <div ref={messagesEndRef} />
            </VStack>
          </Box>

          {/* Input Area améliorée */}
          <Box 
            p={{ base: 4, md: 5 }} 
            borderTop="1px" 
            borderColor="gray.200" 
            bg="white"
            boxShadow="0 -2px 10px rgba(0,0,0,0.05)"
          >
            {/* Afficher les fichiers attachés améliorés */}
            {attachedFiles.length > 0 && (
              <Box mb={4} p={3} bg="gray.50" borderRadius="lg" border="1px dashed" borderColor="gray.300">
                <HStack mb={2} spacing={2}>
                  <Text fontSize="xs" fontWeight="bold" color="gray.600">
                    Fichiers joints ({attachedFiles.length}) :
                  </Text>
                </HStack>
                <Wrap spacing={3}>
                  {attachedFiles.map((filePreview, idx) => (
                    <WrapItem key={idx}>
                      <Box 
                        position="relative" 
                        display="inline-block"
                        borderRadius="lg"
                        overflow="hidden"
                        boxShadow="sm"
                        border="1px solid"
                        borderColor="gray.200"
                      >
                        {filePreview.type === 'image' ? (
                          <Box position="relative">
                            <Image
                              src={filePreview.preview}
                              alt={filePreview.file.name}
                              maxH="100px"
                              maxW="100px"
                              objectFit="cover"
                            />
                            <CloseButton
                              size="sm"
                              position="absolute"
                              top={1}
                              right={1}
                              bg="red.500"
                              color="white"
                              borderRadius="full"
                              onClick={() => removeFile(idx)}
                              _hover={{ bg: 'red.600' }}
                              aria-label="Retirer le fichier"
                            />
                          </Box>
                        ) : (
                          <Box
                            p={3}
                            bg="white"
                            position="relative"
                            minW="120px"
                          >
                            <Text fontSize="xs" noOfLines={1} fontWeight="medium" color="gray.700">
                              📎 {filePreview.file.name}
                            </Text>
                            <CloseButton
                              size="xs"
                              position="absolute"
                              top={1}
                              right={1}
                              bg="red.500"
                              color="white"
                              borderRadius="full"
                              onClick={() => removeFile(idx)}
                              _hover={{ bg: 'red.600' }}
                              aria-label="Retirer le fichier"
                            />
                          </Box>
                        )}
                      </Box>
                    </WrapItem>
                  ))}
                </Wrap>
              </Box>
            )}
            
            <HStack spacing={3} align="flex-end">
              <Input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept="image/*"
                multiple
                display="none"
              />
              <IconButton
                aria-label="Joindre une image"
                icon={<FiPaperclip />}
                onClick={() => fileInputRef.current?.click()}
                variant="outline"
                colorScheme="gray"
                size="lg"
                isDisabled={isStreaming}
                _hover={{ bg: 'gray.50', borderColor: 'gray.400' }}
                borderRadius="lg"
              />
              <Box flex={1} position="relative">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSend()
                    }
                  }}
                  placeholder={t('aiTutor.placeholder') || 'Posez votre question à Kaïrox...'}
                  disabled={isStreaming}
                  size="lg"
                  bg="gray.50"
                  borderRadius="lg"
                  _focus={{ bg: 'white', borderColor: 'blue.400', boxShadow: '0 0 0 1px #3182ce' }}
                  _disabled={{ opacity: 0.6, cursor: 'not-allowed' }}
                  pr="60px"
                  minH="48px"
                />
                {input.trim() && (
                  <IconButton
                    aria-label="Envoyer"
                    icon={<FiSend />}
                    colorScheme="blue"
                    onClick={() => handleSend()}
                    isLoading={isStreaming}
                    size="sm"
                    position="absolute"
                    right="8px"
                    top="50%"
                    transform="translateY(-50%)"
                    isDisabled={(!input.trim() && attachedFiles.length === 0) || isStreaming}
                    borderRadius="md"
                    _hover={{ bg: 'blue.600' }}
                  />
                )}
              </Box>
              {!input.trim() && (
                <IconButton
                  aria-label="Envoyer"
                  icon={<FiSend />}
                  colorScheme="blue"
                  onClick={() => handleSend()}
                  isLoading={isStreaming}
                  size="lg"
                  isDisabled={(!input.trim() && attachedFiles.length === 0) || isStreaming}
                  borderRadius="lg"
                  _hover={{ bg: 'blue.600' }}
                />
              )}
            </HStack>
            <Text fontSize="xs" color="gray.500" mt={3} textAlign="center">
              💡 {t('aiTutor.hint') || 'Appuyez sur Entrée pour envoyer • Shift+Entrée pour une nouvelle ligne • Cliquez sur 📎 pour joindre une image'}
            </Text>
          </Box>
        </CardBody>
      </Card>
    </VStack>
  )
}

export default AITutor

