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
# IMPORTANT: L'ordre des règles est crucial
# Les règles spécifiques doivent être AVANT la règle catch-all

# Ne PAS rediriger les fichiers statiques - ils doivent être servis directement
/assets/*  /assets/:splat  200
/*.js      /:splat.js      200
/*.css     /:splat.css     200
/*.json    /:splat.json    200
/*.png     /:splat.png     200
/*.jpg     /:splat.jpg   200
/*.jpeg    /:splat.jpeg    200
/*.gif     /:splat.gif     200
/*.svg     /:splat.svg     200
/*.ico     /:splat.ico     200
/*.woff    /:splat.woff    200
/*.woff2   /:splat.woff2   200
/*.ttf     /:splat.ttf     200
/*.eot     /:splat.eot     200
/*.map     /:splat.map     200

# Rediriger toutes les autres routes (routes SPA) vers index.html
# Cette règle doit être EN DERNIER
/*         /index.html     200
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
