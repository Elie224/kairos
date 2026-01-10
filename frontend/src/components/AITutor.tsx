import { useState, useRef, useEffect } from 'react'
import { Box, VStack, HStack, Input, Button, Text, Card, CardBody, Badge, Spinner, Alert, AlertIcon, IconButton, Flex, Wrap, WrapItem, Image, CloseButton } from '@chakra-ui/react'
import { useMutation } from 'react-query'
import { useTranslation } from 'react-i18next'
import { FiSend, FiX, FiMessageCircle, FiPaperclip, FiImage } from 'react-icons/fi'
import { chatService, ChatMessage } from '../services/chatService'
import api from '../services/api'

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

  // Suggestions de questions initiales
  const initialSuggestions = [
    t('aiTutor.suggestions.explain') || "Peux-tu m'expliquer ce concept ?",
    t('aiTutor.suggestions.example') || "Peux-tu me donner un exemple concret ?",
    t('aiTutor.suggestions.application') || "Comment cela s'applique-t-il dans la vie quotidienne ?",
    t('aiTutor.suggestions.difference') || "Quelle est la différence avec un concept similaire ?"
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

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
        console.error('Erreur lors du chargement de l\'historique:', error)
        // Ne pas bloquer l'interface si l'historique ne peut pas être chargé
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
              setCurrentStreamingMessage(prev => prev + chunk)
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
              console.error('Erreur chat:', error)
              setIsStreaming(false)
              setCurrentStreamingMessage('')
            }
          }
        )
      } else {
        // Utiliser l'endpoint normal sans fichiers
        await chatService.sendMessageStream(textToSend, {
          moduleId,
          language: 'fr',
          onChunk: (chunk) => {
            setCurrentStreamingMessage(prev => prev + chunk)
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
          },
          onError: (error) => {
            console.error('Erreur chat:', error)
            setIsStreaming(false)
            setCurrentStreamingMessage('')
          }
        })
      }
    } catch (error) {
      console.error('Erreur:', error)
      setIsStreaming(false)
      setCurrentStreamingMessage('')
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
  }

  return (
    <VStack spacing={4} align="stretch" h={{ base: '500px', md: '700px' }}>
      <Card h="100%" display="flex" flexDirection="column">
        <CardBody display="flex" flexDirection="column" h="100%" p={0}>
          {/* Header */}
          <Box p={{ base: 3, md: 4 }} borderBottom="1px" borderColor="gray.200" bg="gray.50">
            <Flex justify="space-between" align="center">
              <HStack spacing={2}>
                <FiMessageCircle size={{ base: 18, md: 20 }} color="#1e88e5" />
                <Text fontSize={{ base: 'md', md: 'lg' }} fontWeight="bold" color="gray.700">
                  {t('aiTutor.title') || 'Kaïrox'}
                </Text>
              </HStack>
              {messages.length > 0 && (
                <IconButton
                  aria-label="Effacer la conversation"
                  icon={<FiX />}
                  size={{ base: 'md', md: 'sm' }}
                  minW="44px"
                  minH="44px"
                  variant="ghost"
                  onClick={clearChat}
                />
              )}
            </Flex>
          </Box>

          {/* Messages Area */}
          <Box flex={1} overflowY="auto" p={{ base: 3, md: 4 }} bg="gray.50">
            <VStack spacing={{ base: 3, md: 4 }} align="stretch">
              {messages.length === 0 && (
                <Box textAlign="center" py={{ base: 6, md: 8 }}>
                  <Box mb={4} display="flex" justifyContent="center">
                    <FiMessageCircle size={{ base: 36, md: 48 }} color="#1e88e5" />
                  </Box>
                  <Text fontSize={{ base: 'lg', md: 'xl' }} fontWeight="bold" mb={2} color="gray.700">
                    {t('aiTutor.welcome') || 'Bonjour ! Je suis Kaïrox'}
                  </Text>
                  <Text fontSize={{ base: 'sm', md: 'md' }} color="gray.600" mb={6}>
                    {t('aiTutor.subtitle') || 'Posez-moi vos questions sur ce module et je vous aiderai à comprendre les concepts.'}
                  </Text>
                  
                  {/* Suggestions initiales */}
                  <Wrap spacing={2} justify="center">
                    {initialSuggestions.map((suggestion, idx) => (
                      <WrapItem key={idx}>
                        <Button
                          size={{ base: 'xs', md: 'sm' }}
                          variant="outline"
                          colorScheme="brand"
                          minH="36px"
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

              {messages.map((msg, idx) => (
                <Box
                  key={idx}
                  alignSelf={msg.role === 'user' ? 'flex-end' : 'flex-start'}
                  maxW={{ base: '90%', md: '85%' }}
                  width="100%"
                >
                  <HStack
                    spacing={2}
                    align="start"
                    justify={msg.role === 'user' ? 'flex-end' : 'flex-start'}
                    mb={1}
                  >
                    {msg.role === 'assistant' && (
                      <Badge colorScheme="gray" borderRadius="full" px={2} py={1} fontSize={{ base: 'xs', md: 'sm' }}>
                        {t('aiTutor.tutor') || 'Kaïrox'}
                      </Badge>
                    )}
                    {msg.role === 'user' && (
                      <Badge colorScheme="brand" borderRadius="full" px={2} py={1} fontSize={{ base: 'xs', md: 'sm' }}>
                        {t('aiTutor.you') || 'Vous'}
                      </Badge>
                    )}
                  </HStack>
                  <Card
                    bg={msg.role === 'user' ? 'gray.500' : 'white'}
                    color={msg.role === 'user' ? 'white' : 'gray.800'}
                    boxShadow="sm"
                    borderRadius="lg"
                  >
                    <CardBody p={{ base: 3, md: 4 }}>
                      {/* Afficher les fichiers/images si présents */}
                      {msg.files && msg.files.length > 0 && (
                        <VStack spacing={2} align="stretch" mb={3}>
                          {msg.files.map((file, fileIdx) => (
                            <Box key={fileIdx} position="relative">
                              {file.type === 'image' && file.preview ? (
                                <Image
                                  src={file.preview}
                                  alt={file.name}
                                  maxH="300px"
                                  borderRadius="md"
                                  objectFit="contain"
                                />
                              ) : (
                                <Box
                                  p={3}
                                  bg={msg.role === 'user' ? 'gray.400' : 'gray.100'}
                                  borderRadius="md"
                                >
                                  <Text fontSize="sm">📎 {file.name}</Text>
                                </Box>
                              )}
                            </Box>
                          ))}
                        </VStack>
                      )}
                      <Text whiteSpace="pre-wrap" lineHeight="1.6">
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

              {/* Message en cours de streaming */}
              {isStreaming && currentStreamingMessage && (
                <Box
                  alignSelf="flex-start"
                  maxW="85%"
                  width="100%"
                >
                  <HStack spacing={2} align="start" mb={1}>
                    <Badge colorScheme="gray" borderRadius="full" px={2} py={1}>
                      {t('aiTutor.tutor') || 'Kaïrox'}
                    </Badge>
                  </HStack>
                  <Card bg="white" boxShadow="sm" borderRadius="lg">
                    <CardBody p={4}>
                      <Text whiteSpace="pre-wrap" lineHeight="1.6">
                        {currentStreamingMessage}
                        <Text as="span" opacity={0.5}>▋</Text>
                      </Text>
                    </CardBody>
                  </Card>
                </Box>
              )}

              {/* Indicateur de chargement */}
              {isStreaming && !currentStreamingMessage && (
                <HStack spacing={2} align="start">
                  <Badge colorScheme="gray" borderRadius="full" px={2} py={1}>
                    {t('aiTutor.tutor') || 'Kaïros'}
                  </Badge>
                  <Card bg="white" boxShadow="sm">
                    <CardBody p={4}>
                      <HStack spacing={2}>
                        <Spinner size="sm" color="gray.500" />
                        <Text color="gray.500" fontSize="sm">
                          {t('aiTutor.thinking') || 'Réflexion en cours...'}
                        </Text>
                      </HStack>
                    </CardBody>
                  </Card>
                </HStack>
              )}

              <div ref={messagesEndRef} />
            </VStack>
          </Box>

          {/* Input Area */}
          <Box p={{ base: 3, md: 4 }} borderTop="1px" borderColor="gray.200" bg="white">
            {/* Afficher les fichiers attachés */}
            {attachedFiles.length > 0 && (
              <Box mb={3}>
                <Wrap spacing={2}>
                  {attachedFiles.map((filePreview, idx) => (
                    <WrapItem key={idx}>
                      <Box position="relative" display="inline-block">
                        {filePreview.type === 'image' ? (
                          <Box position="relative">
                            <Image
                              src={filePreview.preview}
                              alt={filePreview.file.name}
                              maxH="80px"
                              maxW="80px"
                              borderRadius="md"
                              objectFit="cover"
                            />
                            <CloseButton
                              size="sm"
                              position="absolute"
                              top="-2"
                              right="-2"
                              bg="red.500"
                              color="white"
                              borderRadius="full"
                              onClick={() => removeFile(idx)}
                            />
                          </Box>
                        ) : (
                          <Box
                            p={2}
                            bg="gray.100"
                            borderRadius="md"
                            position="relative"
                          >
                            <Text fontSize="xs" noOfLines={1} maxW="100px">
                              📎 {filePreview.file.name}
                            </Text>
                            <CloseButton
                              size="xs"
                              position="absolute"
                              top="-1"
                              right="-1"
                              bg="red.500"
                              color="white"
                              borderRadius="full"
                              onClick={() => removeFile(idx)}
                            />
                          </Box>
                        )}
                      </Box>
                    </WrapItem>
                  ))}
                </Wrap>
              </Box>
            )}
            
            <HStack spacing={2}>
              <Input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept="image/*"
                multiple
                display="none"
              />
              <IconButton
                aria-label="Joindre un fichier"
                icon={<FiPaperclip />}
                onClick={() => fileInputRef.current?.click()}
                variant="ghost"
                size="lg"
                isDisabled={isStreaming}
              />
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSend()
                  }
                }}
                placeholder={t('aiTutor.placeholder') || 'Posez votre question...'}
                disabled={isStreaming}
                size="lg"
                bg="gray.50"
                _focus={{ bg: 'white', borderColor: 'gray.500' }}
                flex={1}
              />
              <IconButton
                aria-label="Envoyer"
                icon={<FiSend />}
                colorScheme="brand"
                onClick={() => handleSend()}
                isLoading={isStreaming}
                size="lg"
                isDisabled={(!input.trim() && attachedFiles.length === 0) || isStreaming}
              />
            </HStack>
            <Text fontSize="xs" color="gray.500" mt={2} textAlign="center">
              {t('aiTutor.hint') || 'Appuyez sur Entrée pour envoyer • Cliquez sur 📎 pour joindre une image'}
            </Text>
          </Box>
        </CardBody>
      </Card>
    </VStack>
  )
}

export default AITutor

