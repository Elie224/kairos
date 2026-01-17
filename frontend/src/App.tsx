import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import { lazy, Suspense, useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import { LoadingSpinner, Onboarding } from './components'
import ProtectedRoute from './components/ProtectedRoute'
import ProtectedAdminRoute from './components/ProtectedAdminRoute'
import { useAuthStore } from './store/authStore'

// Code splitting - Lazy loading des pages
// Pages critiques en import direct pour éviter les erreurs de chargement dynamique sur Render
import Login from './pages/Login'
import Register from './pages/Register'
import Modules from './pages/Modules'
import Dashboard from './pages/Dashboard'
const Home = lazy(() => import('./pages/Home'))
const ModuleDetail = lazy(() => import('./pages/ModuleDetail'))
const Profile = lazy(() => import('./pages/Profile'))
const Settings = lazy(() => import('./pages/Settings'))
const Support = lazy(() => import('./pages/Support'))
const Feedback = lazy(() => import('./pages/Feedback'))
const Admin = lazy(() => import('./pages/Admin'))
const Exams = lazy(() => import('./pages/Exams'))
const ExamDetail = lazy(() => import('./pages/ExamDetail'))
const Gamification = lazy(() => import('./pages/Gamification'))
const Visualizations = lazy(() => import('./pages/Visualizations'))
// Pages légales en import direct pour garantir l'accessibilité
import LegalMentions from './pages/LegalMentions'
import LegalPrivacy from './pages/LegalPrivacy'
import LegalCGU from './pages/LegalCGU'

// Composant de chargement optimisé pour la navigation
const PageLoader = () => (
  <Box 
    minH="100vh" 
    display="flex" 
    alignItems="center" 
    justifyContent="center"
    bg="gray.50"
  >
    <LoadingSpinner size="lg" text="Chargement..." />
  </Box>
)

function App() {
  const location = useLocation()
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'
  const { isAuthenticated } = useAuthStore()
  const [showOnboarding, setShowOnboarding] = useState(false)

  // Restaurer le scroll en haut de page lors de la navigation ET du rechargement (optimisé)
  useEffect(() => {
    // Fonction robuste pour forcer le scroll en haut
    const scrollToTop = () => {
      try {
        // Méthode 1: window.scrollTo
        window.scrollTo(0, 0)
        // Méthode 2: documentElement
        if (document.documentElement) {
          document.documentElement.scrollTop = 0
          document.documentElement.scrollLeft = 0
        }
        // Méthode 3: body
        if (document.body) {
          document.body.scrollTop = 0
          document.body.scrollLeft = 0
        }
        // Méthode 4: window.scroll avec behavior
        window.scroll({ top: 0, left: 0, behavior: 'instant' })
      } catch (e) {
        // Fallback silencieux
      }
    }
    
    // Scroll immédiat
    scrollToTop()
    
    // Scroll après que le DOM soit prêt
    const rafId = requestAnimationFrame(() => {
      scrollToTop()
      // Double vérification
      setTimeout(scrollToTop, 10)
      setTimeout(scrollToTop, 50)
    })
    
    return () => cancelAnimationFrame(rafId)
  }, [location.pathname])
  
  // S'assurer que le scroll est en haut lors du chargement initial
  useEffect(() => {
    const scrollToTop = () => {
      try {
        window.scrollTo(0, 0)
        if (document.documentElement) {
          document.documentElement.scrollTop = 0
        }
        if (document.body) {
          document.body.scrollTop = 0
        }
      } catch (e) {
        // Fallback silencieux
      }
    }
    
    // Si la page est déjà chargée
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
      scrollToTop()
      setTimeout(scrollToTop, 100)
    } else {
      const handleLoad = () => {
        scrollToTop()
        setTimeout(scrollToTop, 100)
      }
      document.addEventListener('DOMContentLoaded', handleLoad)
      window.addEventListener('load', handleLoad)
      return () => {
        document.removeEventListener('DOMContentLoaded', handleLoad)
        window.removeEventListener('load', handleLoad)
      }
    }
  }, [])

  // Vérifier si l'utilisateur a déjà vu l'onboarding (une seule fois)
  useEffect(() => {
    if (isAuthenticated && !isAuthPage) {
      const hasSeenOnboarding = localStorage.getItem('kairos-onboarding-completed')
      // Vérifier aussi si l'utilisateur a déjà complété l'onboarding dans cette session
      const sessionOnboarding = sessionStorage.getItem('kairos-onboarding-session')
      if (!hasSeenOnboarding && !sessionOnboarding) {
        // Attendre un peu pour que l'interface se charge
        const timer = setTimeout(() => {
          setShowOnboarding(true)
        }, 500)
        return () => clearTimeout(timer)
      }
    }
  }, [isAuthenticated, isAuthPage])

  const handleOnboardingComplete = () => {
    localStorage.setItem('kairos-onboarding-completed', 'true')
    sessionStorage.setItem('kairos-onboarding-session', 'true')
    setShowOnboarding(false)
  }

  const handleOnboardingSkip = () => {
    localStorage.setItem('kairos-onboarding-completed', 'true')
    sessionStorage.setItem('kairos-onboarding-session', 'true')
    setShowOnboarding(false)
  }

  return (
    <Box minH="100vh" bg="gray.50" display="flex" flexDirection="column" position="relative">
      {/* Effet de gradient en arrière-plan */}
      <Box
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        bgGradient="linear-gradient(135deg, rgba(37, 99, 235, 0.03) 0%, rgba(30, 64, 175, 0.02) 100%)"
        zIndex={0}
        pointerEvents="none"
      />
      {!isAuthPage && <Navbar />}
      <Box 
        as="main" 
        flex="1" 
        position="relative" 
        zIndex={1}
        role="main"
        id="main-content"
        tabIndex={-1}
        aria-label="Contenu principal"
      >
        <Suspense fallback={<PageLoader />}>
          <Routes location={location}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<Home />} />
          <Route path="/modules" element={<ProtectedRoute><Modules /></ProtectedRoute>} />
          <Route path="/modules/:id" element={<ProtectedRoute><ModuleDetail /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
          <Route path="/support" element={<ProtectedRoute><Support /></ProtectedRoute>} />
          <Route path="/feedback" element={<ProtectedRoute><Feedback /></ProtectedRoute>} />
          <Route path="/admin" element={<ProtectedAdminRoute><Admin /></ProtectedAdminRoute>} />
          <Route path="/exams" element={<ProtectedRoute><Exams /></ProtectedRoute>} />
          {/* Redirection des anciennes routes /exams/:subject vers /exams */}
          <Route path="/exams/:subject" element={<Navigate to="/exams" replace />} />
          <Route path="/modules/:moduleId/exam" element={<ProtectedRoute><ExamDetail /></ProtectedRoute>} />
          <Route path="/gamification" element={<ProtectedRoute><Gamification /></ProtectedRoute>} />
          <Route path="/visualizations" element={<ProtectedRoute><Visualizations /></ProtectedRoute>} />
          {/* Pages légales - Accessibles sans authentification */}
          <Route path="/legal/mentions-legales" element={<LegalMentions />} />
          <Route path="/legal/politique-confidentialite" element={<LegalPrivacy />} />
          <Route path="/legal/cgu" element={<LegalCGU />} />
          </Routes>
        </Suspense>
      </Box>
      {!isAuthPage && <Footer />}
      
      {/* Écran d'onboarding */}
      {showOnboarding && (
        <Onboarding
          onComplete={handleOnboardingComplete}
          onSkip={handleOnboardingSkip}
        />
      )}
    </Box>
  )
}

export default App



