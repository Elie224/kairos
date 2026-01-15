import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Charger les variables d'environnement selon le mode (development/production)
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [react()],
    server: {
      port: 5173,
      host: '0.0.0.0', // Écouter sur toutes les interfaces
      strictPort: false, // Permettre d'utiliser un autre port si 5173 est occupé
      proxy: {
        '/api': {
          // En développement local, rediriger vers le backend Render pour éviter de démarrer le backend local
          // Si vous voulez utiliser le backend local, créer .env.local avec VITE_API_URL=http://localhost:8000
          // Si VITE_API_URL est définie (ex: http://localhost:8000), l'utiliser
          // Sinon, utiliser le backend Render par défaut
          target: env.VITE_API_URL 
            ? (env.VITE_API_URL.startsWith('http') ? env.VITE_API_URL.replace('/api', '') : `http://${env.VITE_API_URL.replace('/api', '')}`)
            : 'https://kairos-0aoy.onrender.com',
          changeOrigin: true,
          secure: true, // Accepter les certificats HTTPS (nécessaire pour Render)
          // Ne pas supprimer /api car le backend attend /api/auth/login, /api/modules, etc.
          // Le backend inclut les routeurs avec prefix="/api/auth", "/api/modules", etc.
          // Pas de rewrite : garder /api dans l'URL finale
        },
      },
    },
    build: {
      // Optimisations de build
      rollupOptions: {
        output: {
          // Code splitting manuel pour optimiser les chunks
          manualChunks: (id) => {
            // Vendor chunks
            if (id.includes('node_modules')) {
              if (id.includes('react') || id.includes('react-dom') || id.includes('react-router')) {
                return 'react-vendor'
              }
              if (id.includes('@chakra-ui') || id.includes('@emotion') || id.includes('framer-motion')) {
                return 'chakra-vendor'
              }
              if (id.includes('react-query') || id.includes('axios')) {
                return 'query-vendor'
              }
              if (id.includes('i18next')) {
                return 'i18n-vendor'
              }
              // Autres vendors
              return 'vendor'
            }
            // Pages en chunks séparés pour lazy loading optimal
            if (id.includes('/pages/')) {
              const pageName = id.split('/pages/')[1]?.split('/')[0]
              if (pageName) {
                return `page-${pageName}`
              }
            }
            // Components en chunks séparés pour les gros composants
            if (id.includes('/components/')) {
              const componentName = id.split('/components/')[1]?.split('/')[0]
              if (componentName && ['AITutor', 'Admin', 'Exam', 'Quiz'].includes(componentName)) {
                return `component-${componentName}`
              }
            }
          },
        },
      },
      // Augmenter la limite de taille des chunks
      chunkSizeWarningLimit: 1000,
      // Optimiser les assets
      assetsInlineLimit: 4096, // Inline les assets < 4KB
      // Minification avec esbuild (inclus avec Vite, pas besoin de terser)
      minify: 'esbuild',
      // Supprimer les console.log en production (via esbuild)
      esbuildOptions: {
        drop: import.meta.env.PROD ? ['console', 'debugger'] : [],
      },
      // Compression des assets
      assetsDir: 'assets',
      // Source maps seulement en développement
      sourcemap: !import.meta.env.PROD,
    },
    // Optimiser les dépendances
    optimizeDeps: {
      include: ['react', 'react-dom', 'react-router-dom', '@chakra-ui/react'],
      // Exclure les dépendances qui ne doivent pas être pré-bundlées
      exclude: [],
    },
    // Optimisations de performance
    build: {
      ...(import.meta.env.PROD ? {
        // En production, activer les optimisations agressives
        cssCodeSplit: true,
        cssMinify: true,
        reportCompressedSize: false, // Désactiver pour accélérer le build
      } : {}),
    },
  }
})
