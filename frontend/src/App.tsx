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
const Home = lazy(() => import('./pages/Home'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const Modules = lazy(() => import('./pages/Modules'))
const ModuleDetail = lazy(() => import('./pages/ModuleDetail'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Profile = lazy(() => import('./pages/Profile'))
const Settings = lazy(() => import('./pages/Settings'))
const Support = lazy(() => import('./pages/Support'))
const Feedback = lazy(() => import('./pages/Feedback'))
const Admin = lazy(() => import('./pages/Admin'))
const Exams = lazy(() => import('./pages/Exams'))
const ExamDetail = lazy(() => import('./pages/ExamDetail'))
const Gamification = lazy(() => import('./pages/Gamification'))
const Visualizations = lazy(() => import('./pages/Visualizations'))

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

  // Restaurer le scroll en haut de page lors de la navigation (optimisé)
  useEffect(() => {
    // Utiliser requestAnimationFrame pour s'assurer que le DOM est prêt
    requestAnimationFrame(() => {
      window.scrollTo({ top: 0, behavior: 'instant' }) // 'instant' pour éviter le délai
    })
  }, [location.pathname])

  // Vérifier si l'utilisateur a déjà vu l'onboarding
  useEffect(() => {
    if (isAuthenticated && !isAuthPage) {
      const hasSeenOnboarding = localStorage.getItem('kairos-onboarding-completed')
      if (!hasSeenOnboarding) {
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
    setShowOnboarding(false)
  }

  const handleOnboardingSkip = () => {
    localStorage.setItem('kairos-onboarding-completed', 'true')
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
          <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
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



