@echo off
REM Script pour demarrer Redis avec Docker
echo ========================================
echo   Demarrage de Redis pour Kaïros
echo ========================================
echo.

REM Vérifier si Docker est disponible
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR: Docker n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Solutions:
    echo   1. Installez Docker Desktop pour Windows
    echo   2. Ou utilisez Memurai (Redis pour Windows): https://www.memurai.com/
    echo.
    pause
    exit /b 1
)

echo Verification de Docker...
docker --version
echo.

REM Vérifier si le conteneur existe déjà
docker ps -a --filter "name=kairos-redis" --format "{{.Names}}" | findstr /C:"kairos-redis" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Le conteneur Redis existe deja.
    echo.
    echo Verification de l'etat...
    docker ps --filter "name=kairos-redis" --format "{{.Names}}" | findstr /C:"kairos-redis" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo OK: Redis est deja demarre!
        echo.
        echo Test de connexion...
        docker exec kairos-redis redis-cli ping
        if %ERRORLEVEL% EQU 0 (
            echo.
            echo Redis fonctionne correctement!
        ) else (
            echo.
            echo ERREUR: Redis ne repond pas
        )
    ) else (
        echo Redis est arrete. Demarrage...
        docker start kairos-redis
        if %ERRORLEVEL% EQU 0 (
            echo.
            echo OK: Redis demarre avec succes!
            timeout /t 2 >nul
            echo.
            echo Test de connexion...
            docker exec kairos-redis redis-cli ping
        ) else (
            echo.
            echo ERREUR: Impossible de demarrer Redis
        )
    )
) else (
    echo Creation et demarrage du conteneur Redis...
    echo.
    docker run -d ^
        -p 6379:6379 ^
        --name kairos-redis ^
        --restart unless-stopped ^
        redis:7-alpine ^
        redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo OK: Conteneur Redis cree et demarre!
        timeout /t 2 >nul
        echo.
        echo Test de connexion...
        docker exec kairos-redis redis-cli ping
        if %ERRORLEVEL% EQU 0 (
            echo.
            echo Redis fonctionne correctement!
        ) else (
            echo.
            echo ATTENTION: Redis demarre mais ne repond pas encore
            echo   Attendez quelques secondes et reessayez
        )
    ) else (
        echo.
        echo ERREUR: Impossible de creer le conteneur Redis
        echo.
        echo Verifiez:
        echo   1. Que Docker est demarre
        echo   2. Que le port 6379 n'est pas deja utilise
        echo   3. Que vous avez les permissions Docker
    )
)

echo.
echo ========================================
echo   Informations Redis
echo ========================================
echo.
echo URL de connexion: redis://localhost:6379/0
echo.
echo Pour tester manuellement:
echo   docker exec -it kairos-redis redis-cli
echo.
echo Pour arreter Redis:
echo   docker stop kairos-redis
echo.
echo Pour redemarrer Redis:
echo   docker start kairos-redis
echo.
pause
