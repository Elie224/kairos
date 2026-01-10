@echo off
echo ========================================
echo   Demarrage du Frontend Kairos
echo ========================================
echo.

REM Se placer dans le bon repertoire
cd /d "%~dp0"
cd frontend

REM Ajouter Node.js au PATH
set "PATH=%PATH%;C:\Program Files\nodejs"

echo Verification de Node.js...
where node >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERREUR] Node.js n'est pas installe!
    echo.
    echo Veuillez installer Node.js depuis: https://nodejs.org/
    echo Version requise: Node.js 18 ou superieur
    echo.
    pause
    exit /b 1
)

node --version
echo Node.js trouve!
echo.

if not exist "node_modules" (
    echo Installation des dependances npm (cela peut prendre quelques minutes)...
    call npm install
    if errorlevel 1 (
        echo [ERREUR] Echec de l'installation des dependances
        pause
        exit /b 1
    )
    echo.
    echo Dependances installees avec succes!
    echo.
)

echo ========================================
echo   Demarrage du serveur de developpement...
echo ========================================
echo.
echo Le frontend sera accessible sur: http://localhost:5173
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur.
echo.

call npm run dev

pause


