import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import { lazy, Suspense } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import { LoadingSpinner } from './components'
import ProtectedRoute from './components/ProtectedRoute'

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

// Composant de chargement
const PageLoader = () => <LoadingSpinner size="lg" text="Chargement..." />

function App() {
  const location = useLocation()
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'

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
      <Box flex="1" position="relative" zIndex={1}>
        <Suspense fallback={<PageLoader />}>
          <Routes>
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
          <Route path="/admin" element={<ProtectedRoute><Admin /></ProtectedRoute>} />
          <Route path="/exams" element={<ProtectedRoute><Exams /></ProtectedRoute>} />
          {/* Redirection des anciennes routes /exams/:subject vers /exams */}
          <Route path="/exams/:subject" element={<Navigate to="/exams" replace />} />
          <Route path="/modules/:moduleId/exam" element={<ProtectedRoute><ExamDetail /></ProtectedRoute>} />
          </Routes>
        </Suspense>
      </Box>
      {!isAuthPage && <Footer />}
    </Box>
  )
}

export default App



