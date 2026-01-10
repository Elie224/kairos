@echo off
REM Script de migration PostgreSQL pour Kaïros
REM Crée toutes les tables dans la base de données eduverse

echo ========================================
echo   Migration PostgreSQL - Kaïros
echo ========================================
echo.

REM Vérifier que l'environnement virtuel existe
if not exist "venv\Scripts\python.exe" (
    echo ❌ Erreur: Environnement virtuel introuvable!
    echo    Créez l'environnement virtuel avec: python -m venv venv
    pause
    exit /b 1
)

REM Activer l'environnement virtuel et exécuter les migrations
echo Exécution des migrations PostgreSQL...
echo.

call venv\Scripts\python.exe scripts\migrate_postgres.py create

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
    echo    Vérifiez:
    echo    1. Que PostgreSQL 18 est démarré
    echo    2. Que la base de données 'eduverse' existe
    echo    3. Que les paramètres dans .env sont corrects
    pause
    exit /b 1
)

pause
