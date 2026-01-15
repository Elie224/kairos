// Script pour garantir la présence du fichier _redirects dans dist/
// Compatible avec "type": "module" dans package.json
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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
