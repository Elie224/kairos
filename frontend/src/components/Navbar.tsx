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
  Divider,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem
} from '@chakra-ui/react'
import { HamburgerIcon } from '@chakra-ui/icons'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { FiLogOut, FiUser } from 'react-icons/fi'
import Logo from '../components/Logo'
import { useAuthStore } from '../store/authStore'

const Navbar = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { isAuthenticated, user, logout } = useAuthStore()
  const bg = useColorModeValue('rgba(255, 255, 255, 0.95)', 'gray.800')
  const { isOpen, onOpen, onClose } = useDisclosure()

  const handleLogout = () => {
    logout()
    navigate('/')
    onClose()
  }

  const NavLinks = () => (
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
      <Link to="/gamification" onClick={onClose}>
        <Button 
          variant="ghost" 
          w={{ base: 'full', md: 'auto' }} 
          justifyContent={{ base: 'flex-start', md: 'center' }} 
          px={{ base: 4, md: 2 }}
          minH="44px"
          fontSize={{ base: 'md', md: 'sm' }}
        >
          🏆 Récompenses
        </Button>
      </Link>
      <Link to="/visualizations" onClick={onClose}>
        <Button 
          variant="ghost" 
          w={{ base: 'full', md: 'auto' }} 
          justifyContent={{ base: 'flex-start', md: 'center' }} 
          px={{ base: 4, md: 2 }}
          minH="44px"
          fontSize={{ base: 'md', md: 'sm' }}
        >
          👁️ Visualisations
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
            {isAuthenticated ? (
              <Menu>
                <MenuButton
                  as={Button}
                  variant="ghost"
                  leftIcon={<Avatar size="sm" name={user?.username || user?.email} />}
                  minH="44px"
                >
                  <Text display={{ base: 'none', lg: 'block' }}>
                    {user?.username || user?.email}
                  </Text>
                </MenuButton>
                <MenuList>
                  <MenuItem icon={<FiUser />} as={Link} to="/profile">
                    Mon profil
                  </MenuItem>
                  <MenuItem icon={<FiLogOut />} onClick={handleLogout}>
                    Déconnexion
                  </MenuItem>
                </MenuList>
              </Menu>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" size="md" minH="44px">
                    Connexion
                  </Button>
                </Link>
                <Link to="/register">
                  <Button 
                    colorScheme="blue" 
                    size="md"
                    bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                    _hover={{
                      bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)',
                    }}
                    minH="44px"
                  >
                    Inscription
                  </Button>
                </Link>
              </>
            )}
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
              <Stack spacing={0} mt={2}>
                <NavLinks />
                <Divider my={2} />
                {isAuthenticated ? (
                  <>
                    <Box px={4} py={2}>
                      <HStack spacing={2}>
                        <Avatar size="sm" name={user?.username || user?.email} />
                        <Text fontSize="sm" fontWeight="600">
                          {user?.username || user?.email}
                        </Text>
                      </HStack>
                    </Box>
                    <Link to="/profile" onClick={onClose}>
                      <Button 
                        variant="ghost" 
                        w="full" 
                        justifyContent="flex-start" 
                        leftIcon={<FiUser />}
                        px={4}
                        minH="44px"
                      >
                        Mon profil
                      </Button>
                    </Link>
                    <Button 
                      variant="ghost" 
                      w="full" 
                      justifyContent="flex-start" 
                      leftIcon={<FiLogOut />}
                      onClick={handleLogout}
                      px={4}
                      minH="44px"
                      color="red.500"
                    >
                      Déconnexion
                    </Button>
                  </>
                ) : (
                  <>
                    <Link to="/login" onClick={onClose}>
                      <Button 
                        variant="ghost" 
                        w="full" 
                        justifyContent="flex-start" 
                        px={4}
                        minH="44px"
                      >
                        Connexion
                      </Button>
                    </Link>
                    <Link to="/register" onClick={onClose}>
                      <Button 
                        colorScheme="blue" 
                        w="full"
                        bgGradient="linear-gradient(135deg, blue.500 0%, blue.600 100%)"
                        _hover={{
                          bgGradient: 'linear-gradient(135deg, blue.600 0%, blue.700 100%)',
                        }}
                        px={4}
                        minH="44px"
                      >
                        Inscription
                      </Button>
                    </Link>
                  </>
                )}
              </Stack>
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>
    </>
  )
}

export default Navbar

