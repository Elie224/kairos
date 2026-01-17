import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import { useState, useEffect } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import { Onboarding } from './components'
import ProtectedRoute from './components/ProtectedRoute'
import ProtectedAdminRoute from './components/ProtectedAdminRoute'
import { useAuthStore } from './store/authStore'

// Import direct de TOUTES les pages pour éviter les erreurs de chargement dynamique sur Render
// Le lazy loading cause des erreurs "Failed to fetch dynamically imported module" sur Render
import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import Modules from './pages/Modules'
import ModuleDetail from './pages/ModuleDetail'
import Dashboard from './pages/Dashboard'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import Support from './pages/Support'
import Feedback from './pages/Feedback'
import Admin from './pages/Admin'
import Exams from './pages/Exams'
import ExamDetail from './pages/ExamDetail'
import Gamification from './pages/Gamification'
import Visualizations from './pages/Visualizations'
// Pages légales en import direct pour garantir l'accessibilité
import LegalMentions from './pages/LegalMentions'
import LegalPrivacy from './pages/LegalPrivacy'
import LegalCGU from './pages/LegalCGU'

// PageLoader retiré car on n'utilise plus Suspense (toutes les pages sont importées directement)

function App() {
  const location = useLocation()
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'
  const { isAuthenticated } = useAuthStore()
  const [showOnboarding, setShowOnboarding] = useState(false)

  // Restaurer le scroll en haut de page lors de la navigation (sans bloquer le rendu)
  useEffect(() => {
    // Fonction simple pour forcer le scroll en haut
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
    
    // Scroll après un court délai pour ne pas bloquer le rendu initial
    const timer = setTimeout(scrollToTop, 100)
    
    return () => clearTimeout(timer)
  }, [location.pathname])
  
  // S'assurer que le scroll est en haut lors du chargement initial (une seule fois, sans bloquer)
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
    
    // Scroll après un délai pour ne pas interférer avec le rendu initial
    const timer = setTimeout(scrollToTop, 200)
    
    return () => clearTimeout(timer)
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
        <Routes location={location}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<Home />} />
          <Route path="/index.html" element={<Home />} />
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



