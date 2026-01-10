-- Script SQL pour configurer l'encodage UTF-8 sur la base de données eduverse
-- À exécuter dans psql ou pgAdmin

-- Vérifier l'encodage actuel
SELECT datname, pg_encoding_to_char(encoding) as encoding 
FROM pg_database 
WHERE datname = 'eduverse';

-- Si l'encodage n'est pas UTF8, vous devez recréer la base de données
-- ATTENTION: Cela supprimera toutes les données existantes

-- Option 1: Modifier l'encodage de la connexion (temporaire)
SET client_encoding = 'UTF8';

-- Option 2: Modifier l'encodage par défaut de la base (recommandé)
ALTER DATABASE eduverse SET client_encoding = 'UTF8';

-- Vérifier que le changement a été appliqué
SHOW client_encoding;
