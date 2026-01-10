@echo off
echo ========================================
echo   Demarrage de MongoDB pour EduVerse
echo ========================================
echo.

REM Vérifier si Docker Desktop est démarré
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker Desktop n'est pas demarre!
    echo.
    echo Veuillez demarrer Docker Desktop et reessayer.
    echo Ou installez MongoDB manuellement depuis:
    echo https://www.mongodb.com/try/download/community
    pause
    exit /b 1
)

echo [1/3] Demarrage de MongoDB avec Docker...
docker run -d --name eduverse-mongodb -p 27017:27017 -v mongodb_data:/data/db mongo:7.0
if errorlevel 1 (
    echo [ATTENTION] Le conteneur existe deja, tentative de demarrage...
    docker start eduverse-mongodb
)

echo.
echo [2/3] Attente du demarrage de MongoDB (10 secondes)...
timeout /t 10 /nobreak >nul

echo.
echo [3/3] Test de la connexion...
docker exec eduverse-mongodb mongosh --eval "db.adminCommand('ping')" --quiet
if errorlevel 1 (
    echo [ERREUR] MongoDB ne repond pas correctement
    pause
    exit /b 1
)

echo.
echo ========================================
echo   MongoDB est demarre et pret!
echo ========================================
echo.
echo MongoDB est accessible sur: mongodb://localhost:27017
echo Base de donnees: eduverse
echo.
echo Pour arreter MongoDB: docker stop eduverse-mongodb
echo Pour redemarrer: docker start eduverse-mongodb
echo.
pause





