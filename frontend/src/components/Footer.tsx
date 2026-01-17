import React from 'react'
import {
  Box,
  Container,
  VStack,
  HStack,
  Text,
  SimpleGrid,
  Heading,
  Link,
  Divider,
  Icon,
  Flex,
  IconButton,
} from '@chakra-ui/react'
import { FiPhone, FiArrowUp } from 'react-icons/fi'
import { FaFacebook, FaWhatsapp } from 'react-icons/fa'
import { Link as RouterLink } from 'react-router-dom'

/**
 * Footer component - Design professionnel et moderne
 */
const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear()

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <Box 
      as="footer" 
      bg="gray.900"
      color="gray.100" 
      mt={20}
      position="relative"
      role="contentinfo"
      borderTop="1px solid"
      borderColor="gray.800"
    >
      {/* Gradient accent line */}
      <Box
        position="absolute"
        top={0}
        left={0}
        right={0}
        height="3px"
        bgGradient="linear(to-r, transparent, blue.500, purple.500, transparent)"
      />

      <Container maxW="1200px" py={{ base: 12, md: 16 }}>
        <SimpleGrid 
          columns={{ base: 1, md: 3 }} 
          spacing={{ base: 10, md: 12 }} 
          mb={12}
        >
          {/* Brand Section */}
          <VStack align="start" spacing={4}>
            <VStack align="start" spacing={2}>
              <Heading 
                size="lg" 
                color="white" 
                fontWeight="bold"
                letterSpacing="tight"
              >
                Kaïrox
              </Heading>
              <Text 
                fontSize="xs" 
                color="gray.300"
                fontWeight="medium"
                letterSpacing="wide"
                textTransform="uppercase"
              >
                Apprentissage Intelligent
              </Text>
            </VStack>
            <Text 
              fontSize="sm" 
              color="gray.200" 
              lineHeight="1.7"
              maxW="300px"
            >
              Plateforme d'apprentissage immersive avec intelligence artificielle.
              Maîtrisez l'Algèbre et le Machine Learning de manière interactive.
            </Text>
          </VStack>

          {/* Contact Section */}
          <VStack align="start" spacing={4}>
            <Heading 
              size="sm" 
              color="white" 
              fontWeight="semibold"
              fontSize="sm"
              mb={2}
            >
              Contact
            </Heading>
            <VStack align="start" spacing={3} w="100%">
              <Link 
                href="tel:+33689306432"
                display="flex"
                alignItems="center"
                gap={3}
                fontSize="sm"
                color="white"
                fontWeight="medium"
                _hover={{ color: 'green.400', textDecoration: 'none' }}
                transition="color 0.2s"
              >
                <Box
                  p={2.5}
                  borderRadius="md"
                  bg="green.500"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Icon as={FiPhone} boxSize={4} color="white" />
                </Box>
                <Text color="white" fontWeight="medium">+33 6 89 30 64 32</Text>
              </Link>
            </VStack>
          </VStack>

          {/* Social Section */}
          <VStack align="start" spacing={4}>
            <Heading 
              size="sm" 
              color="white" 
              fontWeight="semibold"
              fontSize="sm"
              mb={2}
            >
              Suivez-nous
            </Heading>
            <HStack spacing={3}>
              <IconButton
                as="a"
                href="https://www.facebook.com/profile.php?id=61584228366173"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Facebook"
                icon={<FaFacebook />}
                variant="ghost"
                color="gray.400"
                bg="gray.800"
                _hover={{ 
                  bg: '#1877F2', 
                  color: 'white',
                  transform: { base: 'none', md: 'translateY(-2px)' },
                }}
                size={{ base: 'lg', md: 'md' }}
                minW="44px"
                minH="44px"
                borderRadius="lg"
                transition="all 0.2s"
              />
              <IconButton
                as="a"
                href="https://wa.me/33689306432"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="WhatsApp"
                icon={<FaWhatsapp />}
                variant="ghost"
                color="gray.400"
                bg="gray.800"
                _hover={{ 
                  bg: '#25D366', 
                  color: 'white',
                  transform: { base: 'none', md: 'translateY(-2px)' },
                }}
                size={{ base: 'lg', md: 'md' }}
                minW="44px"
                minH="44px"
                borderRadius="lg"
                transition="all 0.2s"
              />
            </HStack>
          </VStack>
        </SimpleGrid>

        <Divider borderColor="gray.800" my={8} />

        {/* Bottom Section */}
        <Flex 
          direction={{ base: 'column', md: 'row' }} 
          justify="space-between" 
          align={{ base: 'start', md: 'center' }} 
          gap={4}
        >
          {/* Copyright */}
          <Text 
            fontSize="sm" 
            color="gray.300"
            fontWeight="medium"
          >
            © {currentYear} Kaïrox. Tous droits réservés.
          </Text>

          {/* Legal Links */}
          <HStack 
            spacing={4}
            fontSize="sm"
            flexWrap="wrap"
          >
            <RouterLink 
              to="/legal/mentions-legales"
              style={{ textDecoration: 'none' }}
            >
              <Text
                as="span"
                color="gray.300"
                fontWeight="medium"
                _hover={{ color: 'white', textDecoration: 'underline' }}
                transition="color 0.2s"
                cursor="pointer"
              >
                Mentions légales
              </Text>
            </RouterLink>
            <Text color="gray.500" fontWeight="bold">•</Text>
            <RouterLink 
              to="/legal/politique-confidentialite"
              style={{ textDecoration: 'none' }}
            >
              <Text
                as="span"
                color="gray.300"
                fontWeight="medium"
                _hover={{ color: 'white', textDecoration: 'underline' }}
                transition="color 0.2s"
                cursor="pointer"
              >
                Politique de confidentialité
              </Text>
            </RouterLink>
            <Text color="gray.500" fontWeight="bold">•</Text>
            <RouterLink 
              to="/legal/cgu"
              style={{ textDecoration: 'none' }}
            >
              <Text
                as="span"
                color="gray.300"
                fontWeight="medium"
                _hover={{ color: 'white', textDecoration: 'underline' }}
                transition="color 0.2s"
                cursor="pointer"
              >
                CGU
              </Text>
            </RouterLink>
          </HStack>

          {/* Back to top */}
          <IconButton
            aria-label="Retour en haut"
            icon={<FiArrowUp />}
            onClick={scrollToTop}
            variant="ghost"
            color="gray.200"
            bg="gray.800"
            _hover={{ 
              bg: 'blue.500',
              color: 'white',
              transform: 'translateY(-2px)',
            }}
            size="md"
            borderRadius="lg"
            transition="all 0.2s"
          />
        </Flex>
      </Container>
    </Box>
  )
}

export default Footer
