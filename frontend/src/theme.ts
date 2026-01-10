import { extendTheme } from '@chakra-ui/react'
// IMPORTANT : Initialiser le thème bleu AVANT de récupérer la config
import './utils/initTheme'
import { getThemeConfig, generateColorPalette } from './utils/themeColors'

/**
 * Récupère les couleurs du logo depuis localStorage
 */
const getLogoColors = () => {
  try {
    const stored = localStorage.getItem('kairos-logo-colors')
    if (stored) {
      const parsed = JSON.parse(stored)
      return {
        dominant: parsed.dominant,
        secondary: parsed.secondary || [],
        palette: parsed.palette || {}
      }
    }
  } catch (e) {
    console.error('Erreur lors de la récupération des couleurs:', e)
  }
  return null
}

/**
 * Génère une palette de couleurs Chakra UI à partir d'une couleur de base
 */
const generateColorPalette = (baseColor: string): Record<string, string> => {
  const hexToRgb = (hex: string) => {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : { r: 74, g: 144, b: 226 }
  }

  const rgbToHex = (r: number, g: number, b: number) => {
    return '#' + [r, g, b].map(x => {
      const hex = Math.round(x).toString(16)
      return hex.length === 1 ? '0' + hex : hex
    }).join('')
  }

  const rgb = hexToRgb(baseColor)
  const palette: Record<string, string> = {}

  // Nuances claires (50-400)
  for (let i = 50; i <= 400; i += 50) {
    const factor = (500 - i) / 500
    const r = Math.min(255, rgb.r + (255 - rgb.r) * factor)
    const g = Math.min(255, rgb.g + (255 - rgb.g) * factor)
    const b = Math.min(255, rgb.b + (255 - rgb.b) * factor)
    palette[i] = rgbToHex(r, g, b)
  }

  // Couleur principale (500)
  palette[500] = baseColor

  // Nuances foncées (600-900)
  for (let i = 600; i <= 900; i += 100) {
    const factor = (i - 500) / 500
    const r = Math.max(0, rgb.r * (1 - factor * 0.8))
    const g = Math.max(0, rgb.g * (1 - factor * 0.8))
    const b = Math.max(0, rgb.b * (1 - factor * 0.8))
    palette[i] = rgbToHex(r, g, b)
  }

  return palette
}

// Récupérer les couleurs du logo OU utiliser le thème par domaine
const logoColors = getLogoColors()
const themeConfig = getThemeConfig()

// Priorité : Thème par domaine > Logo > Couleur par défaut
// Pour une meilleure cohérence visuelle, on privilégie le thème par domaine
const primaryColor = themeConfig.primary || logoColors?.dominant || '#2563EB'
const secondaryColor = themeConfig.secondary || logoColors?.secondary?.[0] || '#3B82F6'
const accentColor = themeConfig.accent || logoColors?.secondary?.[1] || '#60A5FA'

// Générer les palettes
const brandPalette = logoColors?.palette && Object.keys(logoColors.palette).length > 0
  ? logoColors.palette
  : generateColorPalette(primaryColor)

const secondaryPalette = generateColorPalette(secondaryColor)
const accentPalette = generateColorPalette(accentColor)

const theme = extendTheme({
  // Breakpoints optimisés pour mobile, tablette et desktop
  breakpoints: {
    base: '0em',    // 0px - Mobile
    sm: '30em',     // 480px - Grand mobile
    md: '48em',     // 768px - Tablette
    lg: '62em',     // 992px - Desktop
    xl: '80em',     // 1280px - Grand desktop
    '2xl': '96em',  // 1536px - Très grand desktop
  },
  colors: {
    brand: brandPalette, // Palette basée sur les couleurs du thème
    secondary: secondaryPalette,
    accent: accentPalette,
    logo: {
      primary: primaryColor,
      secondary: secondaryColor,
      accent: accentColor,
    },
    // Ajouter les couleurs Chakra UI standards pour une meilleure intégration
    blue: {
      50: '#EFF6FF',
      100: '#DBEAFE',
      200: '#BFDBFE',
      300: '#93C5FD',
      400: '#60A5FA',
      500: primaryColor, // Utiliser la couleur principale du thème
      600: brandPalette[600] || '#1D4ED8',
      700: brandPalette[700] || '#1E40AF',
      800: brandPalette[800] || '#1E3A8A',
      900: brandPalette[900] || '#1E3A8A',
    },
    dark: {
      50: '#1a1a1a',
      100: '#0f0f0f',
      200: '#0A0A0A', // Noir - Background sombre
      300: '#000000',
      400: '#000000',
      500: '#000000',
      600: '#000000',
      700: '#000000',
      800: '#000000',
      900: '#000000',
    },
    anthracite: {
      50: '#f5f5f5',
      100: '#e5e5e5',
      200: '#d4d4d4',
      300: '#a3a3a3',
      400: '#737373',
      500: '#525252',
      600: '#404040',
      700: '#2B2B2B', // Gris anthracite
      800: '#262626',
      900: '#1a1a1a',
    },
    premium: {
      50: '#f5f5f5',
      100: '#e5e5e5',
      200: '#d4d4d4',
      300: '#a3a3a3',
      400: '#737373',
      500: '#525252',
      600: '#404040',
      700: '#2B2B2B',
      800: '#262626',
      900: '#1a1a1a',
    },
    gradient: {
      primary: `linear-gradient(135deg, ${primaryColor} 0%, ${brandPalette[700] || primaryColor} 100%)`,
      secondary: `linear-gradient(135deg, ${secondaryColor} 0%, ${secondaryPalette[700] || secondaryColor} 100%)`,
      accent: `linear-gradient(135deg, ${accentColor} 0%, ${accentPalette[700] || accentColor} 100%)`,
      dark: 'linear-gradient(135deg, #0A0A0A 0%, #000000 100%)',
      black: 'linear-gradient(135deg, #2B2B2B 0%, #0A0A0A 100%)',
      anthracite: 'linear-gradient(135deg, #2B2B2B 0%, #404040 100%)',
      white: 'linear-gradient(135deg, #FFFFFF 0%, #F5F5F5 100%)',
      logo: `linear-gradient(135deg, ${primaryColor} 0%, ${secondaryColor} 100%)`,
    },
  },
  fonts: {
    heading: `'Poppins', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`,
    body: `'Inter', 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`,
  },
  styles: {
    global: {
      html: {
        fontSize: {
          base: '14px',  // Mobile
          md: '15px',    // Tablette
          lg: '16px',    // Desktop
        },
      },
      body: {
        bg: '#FFFFFF',
        color: '#0A0A0A',
        transition: 'background-color 0.3s ease',
        WebkitFontSmoothing: 'antialiased',
        MozOsxFontSmoothing: 'grayscale',
        overflowX: 'hidden',
        fontFamily: `'Inter', 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`,
        letterSpacing: '0.01em',
      },
      '*::placeholder': {
        color: 'gray.400',
      },
      '*, *::before, &::after': {
        borderColor: 'gray.200',
      },
      // Amélioration du touch sur mobile
      'button, a': {
        WebkitTapHighlightColor: 'transparent',
      },
      // Optimisation du scroll sur mobile
      '*': {
        WebkitOverflowScrolling: 'touch',
      },
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: '600',
        borderRadius: 'xl',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        minH: { base: '44px', md: '42px' },
        px: { base: 6, md: 8 },
        fontSize: { base: 'sm', md: 'md' },
        letterSpacing: '0.02em',
        fontFamily: 'body',
        _hover: {
          transform: { base: 'none', md: 'translateY(-2px)' },
          boxShadow: 'soft-lg',
        },
        _active: {
          transform: 'translateY(0) scale(0.98)',
        },
        _focus: {
          boxShadow: `0 0 0 3px ${primaryColor}33`,
          outline: 'none',
        },
        _disabled: {
          opacity: 0.5,
          cursor: 'not-allowed',
        },
      },
      defaultProps: {
        colorScheme: 'blue', // Utiliser 'blue' qui utilise maintenant primaryColor
      },
      variants: {
        gradient: {
          bgGradient: `linear-gradient(135deg, ${primaryColor} 0%, ${brandPalette[700] || primaryColor} 100%)`,
          color: '#FFFFFF',
          fontWeight: '700',
          boxShadow: 'glow-blue',
          letterSpacing: '0.02em',
          _hover: {
            bgGradient: `linear-gradient(135deg, ${brandPalette[600] || primaryColor} 0%, ${primaryColor} 100%)`,
            transform: { base: 'none', md: 'translateY(-3px) scale(1.02)' },
            boxShadow: 'glow-blue-lg',
          },
          _active: {
            transform: 'translateY(-1px) scale(0.98)',
          },
        },
        glass: {
          bg: 'whiteAlpha.200',
          backdropFilter: 'blur(10px)',
          border: '1px solid',
          borderColor: 'whiteAlpha.300',
          color: 'white',
          _hover: {
            bg: 'whiteAlpha.300',
            borderColor: 'whiteAlpha.400',
            transform: { base: 'none', md: 'translateY(-2px)' },
          },
        },
        ghost: {
          _hover: {
            bg: 'blue.50',
            transform: { base: 'none', md: 'translateX(4px)' },
          },
        },
      },
      sizes: {
        lg: {
          px: { base: 8, md: 10 },
          py: { base: 6, md: 7 },
          fontSize: { base: 'md', md: 'lg' },
          minH: { base: '48px', md: '48px' },
        },
        md: {
          px: { base: 6, md: 8 },
          py: { base: 4, md: 5 },
          fontSize: { base: 'sm', md: 'md' },
        },
        sm: {
          px: { base: 4, md: 5 },
          py: { base: 3, md: 4 },
          fontSize: { base: 'xs', md: 'sm' },
          minH: { base: '36px', md: '32px' },
        },
      },
    },
    Input: {
      defaultProps: {
        focusBorderColor: 'blue.500', // Utiliser la couleur du thème
      },
      baseStyle: {
        field: {
          transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
          fontSize: { base: '16px', md: 'inherit' }, // Évite le zoom sur iOS
          borderRadius: 'lg',
          borderWidth: '2px',
          _focus: {
            boxShadow: '0 0 0 3px var(--chakra-colors-blue-200)',
            borderColor: 'blue.500',
            transform: { base: 'none', md: 'scale(1.01)' },
          },
          _hover: {
            borderColor: 'blue.400',
          },
          _invalid: {
            borderColor: 'red.500',
            boxShadow: '0 0 0 3px rgba(229, 62, 62, 0.1)',
          },
        },
      },
      sizes: {
        lg: {
          field: {
            fontSize: { base: '16px', md: 'lg' },
            px: { base: 5, md: 5 },
            h: { base: '48px', md: '52px' },
          },
        },
        md: {
          field: {
            fontSize: { base: '16px', md: 'md' },
            px: { base: 4, md: 4 },
            h: { base: '44px', md: '44px' },
          },
        },
      },
    },
    Select: {
      baseStyle: {
        field: {
          fontSize: { base: '16px', md: 'inherit' }, // Évite le zoom sur iOS
        },
      },
    },
    Card: {
      baseStyle: {
        container: {
          borderRadius: { base: 'xl', md: '2xl' },
          transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
          boxShadow: 'soft',
          border: '1px solid',
          borderColor: 'gray.100',
          overflow: 'hidden',
          bg: 'white',
          _hover: {
            transform: { base: 'none', md: 'translateY(-8px) scale(1.02)' },
            boxShadow: { base: 'soft-lg', md: 'elevated' },
            borderColor: 'blue.300',
            borderWidth: '2px',
          },
        },
      },
      variants: {
        elevated: {
          container: {
            boxShadow: 'xl',
            _hover: {
              boxShadow: '2xl',
            },
          },
        },
        outline: {
          container: {
            borderWidth: '2px',
            borderColor: 'blue.200',
          },
        },
        glass: {
          container: {
            bg: 'whiteAlpha.100',
            backdropFilter: 'blur(10px)',
            borderColor: 'whiteAlpha.200',
          },
        },
      },
    },
    Container: {
      baseStyle: {
        maxW: '1200px',
        px: { base: 4, md: 6, lg: 8 },
      },
    },
    Box: {
      baseStyle: {
        transition: 'all 0.3s ease',
      },
    },
    Heading: {
      baseStyle: {
        fontWeight: '700',
        letterSpacing: '-0.02em',
        lineHeight: '1.2',
        color: 'gray.900',
        fontFamily: 'heading',
      },
      sizes: {
        '4xl': {
          fontSize: { base: '2xl', md: '3xl', lg: '4xl' },
        },
        '3xl': {
          fontSize: { base: 'xl', md: '2xl', lg: '3xl' },
        },
        '2xl': {
          fontSize: { base: 'lg', md: 'xl', lg: '2xl' },
        },
      },
    },
    Text: {
      baseStyle: {
        lineHeight: '1.7',
        color: 'gray.800',
        fontFamily: 'body',
        letterSpacing: '0.01em',
        fontWeight: '400',
      },
    },
    Badge: {
      baseStyle: {
        fontWeight: 'semibold',
        textTransform: 'none',
        borderRadius: 'full',
        px: 3,
        py: 1,
      },
      variants: {
        gradient: {
          bgGradient: `linear-gradient(135deg, ${primaryColor} 0%, ${secondaryColor} 100%)`,
          color: 'white',
        },
      },
    },
    Stat: {
      baseStyle: {
        container: {
          color: 'gray.800',
        },
      },
    },
    StatLabel: {
      baseStyle: {
        color: 'gray.700',
        fontWeight: 'semibold',
        fontSize: 'sm',
      },
    },
    StatNumber: {
      baseStyle: {
        color: 'gray.800',
        fontWeight: 'bold',
      },
    },
    StatHelpText: {
      baseStyle: {
        color: 'gray.600',
        fontSize: 'xs',
      },
    },
  },
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false,
  },
  shadows: {
    'glow-gray': '0 0 20px rgba(128, 128, 128, 0.3)',
    'glow-black': '0 0 20px rgba(0, 0, 0, 0.3)',
    'glow-white': '0 0 20px rgba(255, 255, 255, 0.3)',
    'glow-blue': `0 0 30px ${primaryColor}40, 0 0 60px ${primaryColor}20`,
    'glow-blue-lg': `0 0 40px ${primaryColor}50, 0 0 80px ${primaryColor}30`,
    'soft': '0 2px 8px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06)',
    'soft-lg': '0 4px 16px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.08)',
    'elevated': '0 10px 25px rgba(0, 0, 0, 0.1), 0 4px 10px rgba(0, 0, 0, 0.06)',
  },
})

export default theme
