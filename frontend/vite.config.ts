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
          // Si vous voulez utiliser le backend local, définir VITE_API_URL=http://localhost:8000 dans .env.local
          target: env.VITE_API_URL?.replace('/api', '') || 'https://kairos-0aoy.onrender.com',
          changeOrigin: true,
          secure: true, // Accepter les certificats HTTPS
          // Ne pas supprimer /api car le backend attend /api/auth/login, /api/modules, etc.
          // Le backend inclut les routeurs avec prefix="/api/auth", "/api/modules", etc.
          // rewrite: (path) => path, // Pas de rewrite, garder /api dans l'URL
        },
      },
    },
    build: {
      // Optimisations de build
      rollupOptions: {
        output: {
          // Code splitting manuel pour optimiser les chunks
          manualChunks: {
            'react-vendor': ['react', 'react-dom', 'react-router-dom'],
            'chakra-vendor': ['@chakra-ui/react', '@emotion/react', '@emotion/styled', 'framer-motion'],
            'query-vendor': ['react-query', 'axios'],
            'i18n-vendor': ['i18next', 'react-i18next'],
          },
        },
      },
      // Augmenter la limite de taille des chunks
      chunkSizeWarningLimit: 1000,
      // Optimiser les assets
      assetsInlineLimit: 4096, // Inline les assets < 4KB
      // Minification avec esbuild (inclus avec Vite, pas besoin de terser)
      minify: 'esbuild',
      // Options esbuild pour la minification
      // Note: esbuild ne supporte pas drop_console directement, on peut utiliser un plugin si nécessaire
    },
    // Optimiser les dépendances
    optimizeDeps: {
      include: ['react', 'react-dom', 'react-router-dom', '@chakra-ui/react'],
    },
  }
})
