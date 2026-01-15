import { useState } from 'react'
import { 
  Box, 
  Flex, 
  Button, 
  Text, 
  HStack, 
  VStack,
  useColorModeValue, 
  Image,
  IconButton,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useDisclosure,
  Stack,
  Divider
} from '@chakra-ui/react'
import { HamburgerIcon } from '@chakra-ui/icons'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../store/authStore'
import Logo from '../components/Logo'

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuthStore()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const bg = useColorModeValue('rgba(255, 255, 255, 0.95)', 'gray.800')
  const { isOpen, onOpen, onClose } = useDisclosure()

  const handleLogout = async () => {
    logout()
    navigate('/')
    onClose()
  }

  const NavLinks = () => (
    <>
      {isAuthenticated ? (
        <>
          <Link to="/modules" onClick={onClose}>
            <Button 
              variant="ghost" 
              w={{ base: 'full', md: 'auto' }} 
              justifyContent={{ base: 'flex-start', md: 'center' }} 
              px={{ base: 4, md: 2 }}
              minH="44px"
              fontSize={{ base: 'md', md: 'sm' }}
            >
              {t('navbar.modules')}
            </Button>
          </Link>
          <Link to="/dashboard" onClick={onClose}>
            <Button 
              variant="ghost" 
              w={{ base: 'full', md: 'auto' }} 
              justifyContent={{ base: 'flex-start', md: 'center' }} 
              px={{ base: 4, md: 2 }}
              minH="44px"
              fontSize={{ base: 'md', md: 'sm' }}
            >
              {t('navbar.dashboard')}
            </Button>
          </Link>
          <Link to="/exams" onClick={onClose}>
            <Button 
              variant="ghost" 
              w={{ base: 'full', md: 'auto' }} 
              justifyContent={{ base: 'flex-start', md: 'center' }} 
              px={{ base: 4, md: 2 }}
              minH="44px"
              fontSize={{ base: 'md', md: 'sm' }}
            >
              Examens
            </Button>
          </Link>
          <Link to="/profile" onClick={onClose}>
            <Button 
              variant="ghost" 
              w={{ base: 'full', md: 'auto' }} 
              justifyContent={{ base: 'flex-start', md: 'center' }} 
              px={{ base: 4, md: 2 }}
              minH="44px"
              fontSize={{ base: 'md', md: 'sm' }}
            >
              Profil
            </Button>
          </Link>
          <Link to="/support" onClick={onClose}>
            <Button 
              variant="ghost" 
              w={{ base: 'full', md: 'auto' }} 
              justifyContent={{ base: 'flex-start', md: 'center' }} 
              px={{ base: 4, md: 2 }}
              minH="44px"
              fontSize={{ base: 'md', md: 'sm' }}
            >
              Soutenir
            </Button>
          </Link>
          {user?.is_admin && (
            <Link to="/admin" onClick={onClose}>
              <Button 
                variant="ghost" 
                w={{ base: 'full', md: 'auto' }} 
                justifyContent={{ base: 'flex-start', md: 'center' }}
                colorScheme="gray"
                fontWeight="bold"
                bgGradient="linear-gradient(135deg, rgba(128, 128, 128, 0.1) 0%, rgba(64, 64, 64, 0.1) 100%)"
                _hover={{ 
                  bgGradient: 'linear-gradient(135deg, rgba(128, 128, 128, 0.2) 0%, rgba(64, 64, 64, 0.2) 100%)',
                  transform: 'scale(1.05)'
                }}
                border="1px solid"
                borderColor="gray.300"
              >
                🔐 Administration
              </Button>
            </Link>
          )}
          <Text 
            fontSize="sm" 
            color="gray.600" 
            fontWeight="medium"
            display={{ base: 'none', md: 'block' }}
            px={0}
            ml={1}
          >
            {user?.username || user?.email}
          </Text>
          <Button 
            variant="gradient" 
            onClick={handleLogout} 
            size={{ base: 'md', md: 'sm' }}
            w={{ base: 'full', md: 'auto' }}
            ml={1}
          >
            {t('common.logout')}
          </Button>
        </>
      ) : (
        <>
          <Link to="/login" onClick={onClose}>
            <Button 
              variant="ghost" 
              w={{ base: 'full', md: 'auto' }} 
              justifyContent={{ base: 'flex-start', md: 'center' }}
              minH="44px"
              fontSize={{ base: 'md', md: 'sm' }}
            >
              {t('common.login')}
            </Button>
          </Link>
          <Link to="/register" onClick={onClose}>
            <Button 
              variant="gradient"
              w={{ base: 'full', md: 'auto' }}
              minH="44px"
              fontSize={{ base: 'md', md: 'sm' }}
            >
              {t('common.register')}
            </Button>
          </Link>
        </>
      )}
    </>
  )

  return (
    <>
      <Box 
        bg={bg} 
        boxShadow="soft"
        position="sticky" 
        top={0} 
        zIndex={1000}
        backdropFilter="blur(20px)"
        borderBottom="1px solid"
        borderColor="blue.100"
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)"
        _hover={{
          boxShadow: 'soft-lg',
          borderColor: 'blue.200',
        }}
      >
        <Flex
          maxW="1200px"
          mx="auto"
          px={{ base: 4, md: 6 }}
          py={{ base: 2, md: 3 }}
          justify="space-between"
          align="center"
        >
          <Link to="/">
            <HStack 
              spacing={{ base: 1, md: 1.5 }} 
              _hover={{ transform: 'scale(1.05)' }} 
              transition="all 0.3s ease"
            >
              <Logo size={{ base: '10', md: '12' }} variant="default" />
              <Text 
                fontSize={{ base: 'xl', md: '2xl' }}
                fontWeight="bold" 
                color="brand.500"
                display={{ base: 'none', sm: 'block' }}
              >
                Kaïrox
              </Text>
            </HStack>
          </Link>

          {/* Desktop Navigation */}
          <HStack spacing={1} display={{ base: 'none', md: 'flex' }}>
            <NavLinks />
          </HStack>

          {/* Mobile Menu Button */}
          <IconButton
            aria-label="Menu"
            icon={<HamburgerIcon />}
            variant="ghost"
            display={{ base: 'flex', md: 'none' }}
            onClick={onOpen}
            size="lg"
            minW="48px"
            minH="48px"
            fontSize="xl"
            data-touch-target="true"
          />
        </Flex>
      </Box>

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="right" onClose={onClose} size={{ base: 'full', sm: 'xs' }}>
        <DrawerOverlay />
        <DrawerContent data-safe-area-top="true" data-safe-area-bottom="true">
          <DrawerCloseButton size="lg" minW="48px" minH="48px" data-touch-target="true" />
          <DrawerHeader px={4} py={4} borderBottom="1px solid" borderColor="gray.200">
            <HStack spacing={2}>
              <Logo size="8" variant="default" />
              <Text 
                fontSize="lg"
                fontWeight="bold" 
                color="brand.500"
              >
                Kaïrox
              </Text>
            </HStack>
          </DrawerHeader>
          <DrawerBody px={0} py={4}>
            <VStack spacing={0} align="stretch">
              {isAuthenticated && (
                <>
                  <Box px={4} py={3} bg="gray.50" mb={2}>
                    <Text fontSize="xs" color="gray.500" mb={1} fontWeight="500">
                      Connecté en tant que
                    </Text>
                    <Text fontSize="sm" color="gray.700" fontWeight="600">
                      {user?.username || user?.email}
                    </Text>
                  </Box>
                  <Divider />
                </>
              )}
              <Stack spacing={0} mt={2}>
                <NavLinks />
              </Stack>
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  )
}

export default Navbar

