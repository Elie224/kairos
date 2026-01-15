import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import { lazy, Suspense } from 'react'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import { LoadingSpinner } from './components'

// Code splitting - Lazy loading des pages
const Home = lazy(() => import('./pages/Home'))
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
      <Navbar />
      <Box flex="1" position="relative" zIndex={1}>
        <Suspense fallback={<PageLoader />}>
          <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/modules" element={<Modules />} />
          <Route path="/modules/:id" element={<ModuleDetail />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/support" element={<Support />} />
          <Route path="/feedback" element={<Feedback />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="/exams" element={<Exams />} />
          {/* Redirection des anciennes routes /exams/:subject vers /exams */}
          <Route path="/exams/:subject" element={<Navigate to="/exams" replace />} />
          <Route path="/modules/:moduleId/exam" element={<ExamDetail />} />
          </Routes>
        </Suspense>
      </Box>
      <Footer />
    </Box>
  )
}

export default App



