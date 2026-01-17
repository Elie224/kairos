// Script pour garantir la présence du fichier _redirects dans dist/
// Compatible avec "type": "module" dans package.json
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const distDir = path.join(__dirname, '..', 'dist');
const publicDir = path.join(__dirname, '..', 'public');

// Créer le dossier dist s'il n'existe pas
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
}

// 1. Créer le fichier _redirects dans dist/
const redirectsFile = path.join(distDir, '_redirects');
const redirectsContent = `# Configuration Render.com pour SPA
# IMPORTANT: Render sert automatiquement les fichiers statiques (.js, .css, images, etc.)
# Ce fichier _redirects ne gère QUE les routes SPA

# Rediriger toutes les routes SPA vers index.html
# Les fichiers statiques (/.js, /.css, /assets/*, etc.) sont automatiquement servis par Render
/*    /index.html   200
`;

// Copier aussi le fichier _headers si il existe
const publicHeaders = path.join(publicDir, '_headers');
const distHeaders = path.join(distDir, '_headers');
if (fs.existsSync(publicHeaders)) {
  fs.copyFileSync(publicHeaders, distHeaders);
  console.log('✅ Fichier _headers copié dans dist/');
}
fs.writeFileSync(redirectsFile, redirectsContent, 'utf8');
console.log('✅ Fichier _redirects créé dans dist/');

// 2. Copier aussi le fichier _redirects depuis public/ si il existe (mais utiliser notre contenu par défaut)
const publicRedirects = path.join(publicDir, '_redirects');
if (fs.existsSync(publicRedirects)) {
  // Utiliser le fichier public s'il existe, sinon utiliser le contenu par défaut
  const publicContent = fs.readFileSync(publicRedirects, 'utf8');
  if (publicContent.trim().length > 0) {
    fs.writeFileSync(redirectsFile, publicContent, 'utf8');
    console.log('✅ Fichier _redirects copié depuis public/');
  } else {
    fs.writeFileSync(redirectsFile, redirectsContent, 'utf8');
    console.log('✅ Fichier _redirects créé avec contenu par défaut');
  }
} else {
  fs.writeFileSync(redirectsFile, redirectsContent, 'utf8');
  console.log('✅ Fichier _redirects créé avec contenu par défaut');
}

// 3. Créer aussi un fichier .htaccess pour Apache (si nécessaire)
const htaccessFile = path.join(distDir, '.htaccess');
const htaccessContent = `# Enable Rewrite Engine
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
`;
fs.writeFileSync(htaccessFile, htaccessContent, 'utf8');
console.log('✅ Fichier .htaccess créé dans dist/');

// 4. Créer un fichier nginx.conf pour Nginx (si nécessaire)
const nginxFile = path.join(distDir, 'nginx.conf');
const nginxContent = `# Configuration Nginx pour SPA
location / {
  try_files $uri $uri/ /index.html;
}
`;
fs.writeFileSync(nginxFile, nginxContent, 'utf8');
console.log('✅ Fichier nginx.conf créé dans dist/');
