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
      // Gérer les erreurs 404 pour les fichiers statiques
      fs: {
        strict: false, // Permettre l'accès aux fichiers en dehors de root
      },
    },
    build: {
      // Optimisations de build - Code splitting désactivé pour éviter les erreurs React
      // Vite gérera automatiquement le code splitting de manière sûre
      rollupOptions: {
        output: {
          // Désactiver le code splitting manuel pour éviter l'erreur useLayoutEffect
          // Vite utilisera son code splitting automatique qui est plus sûr
          manualChunks: undefined,
        },
        // Ignorer les avertissements Three.js (BatchedMesh n'est pas critique)
        onwarn(warning, warn) {
          // Ignorer l'avertissement BatchedMesh de three-mesh-bvh
          if (warning.code === 'UNRESOLVED_IMPORT' && warning.message.includes('BatchedMesh')) {
            return;
          }
          // Afficher les autres avertissements
          warn(warning);
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
        drop: mode === 'production' ? ['console', 'debugger'] : [],
      },
      // Compression des assets
      assetsDir: 'assets',
      // Source maps seulement en développement
      sourcemap: mode !== 'production',
      // CSS code splitting
      cssCodeSplit: true,
      cssMinify: true,
      // Désactiver le rapport de taille compressée pour accélérer le build
      reportCompressedSize: false,
    },
    // Optimiser les dépendances
    optimizeDeps: {
      include: [
        'react',
        'react-dom',
        'react/jsx-runtime',
        'react-router-dom',
        '@chakra-ui/react',
        '@emotion/react',
        '@emotion/styled',
        'framer-motion'
      ],
      // Exclure les dépendances qui ne doivent pas être pré-bundlées
      exclude: [],
    },
    // Résolution des dépendances pour éviter les duplications de React
    resolve: {
      dedupe: ['react', 'react-dom'],
    },
  }
})
