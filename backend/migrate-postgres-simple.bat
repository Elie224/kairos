@echo off
REM Script simple de migration PostgreSQL pour Kaïros
REM Configure l'encodage et exécute les migrations

echo ========================================
echo   Migration PostgreSQL - Kaïros
echo ========================================
echo.

REM Vérifier que l'environnement virtuel existe
if not exist "venv\Scripts\python.exe" (
    echo ❌ Erreur: Environnement virtuel introuvable!
    pause
    exit /b 1
)

echo Étape 1: Configuration de l'encodage UTF-8...
echo.
echo IMPORTANT: Si vous voyez une erreur d'encodage, exécutez d'abord:
echo   psql -U postgres -d eduverse -c "ALTER DATABASE eduverse SET client_encoding = 'UTF8';"
echo.
pause

echo.
echo Étape 2: Exécution des migrations...
echo.

call venv\Scripts\python.exe scripts\fix_encoding_and_migrate.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Migration terminée avec succès!
    echo.
    echo Tables créées dans PostgreSQL:
    echo   - users
    echo   - courses
    echo   - modules
    echo   - enrollments
    echo   - user_progress
    echo.
) else (
    echo.
    echo ❌ Erreur lors de la migration!
    echo.
    echo Solutions:
    echo   1. Configurez l'encodage manuellement:
    echo      psql -U postgres -d eduverse
    echo      ALTER DATABASE eduverse SET client_encoding = 'UTF8';
    echo   2. Vérifiez que PostgreSQL 18 est démarré
    echo   3. Vérifiez les paramètres dans .env
    echo.
)

pause
