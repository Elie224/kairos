// Script pour garantir la présence du fichier _redirects dans dist/
const fs = require('fs');
const path = require('path');

const distDir = path.join(__dirname, '..', 'dist');
const redirectsFile = path.join(distDir, '_redirects');
const redirectsContent = '/*    /index.html   200\n';

// Créer le dossier dist s'il n'existe pas
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// Écrire le fichier _redirects
fs.writeFileSync(redirectsFile, redirectsContent, 'utf8');
console.log('✅ Fichier _redirects créé dans dist/');
