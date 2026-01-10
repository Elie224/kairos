@echo off
echo ========================================
echo   Demarrage de l'Application Kairos
echo   Mode Developpement Local
echo ========================================
echo.

REM Vérifier Docker
docker ps >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker Desktop n'est pas demarre!
    echo Veuillez demarrer Docker Desktop et reessayer.
    pause
    exit /b 1
)

echo [1/4] Demarrage de MongoDB...
docker-compose up -d mongodb >nul 2>&1
if errorlevel 1 (
    echo [ATTENTION] MongoDB existe deja ou erreur
    docker start kaïros-mongodb >nul 2>&1
)
echo ✅ MongoDB demarre

echo.
echo [2/4] Attente du demarrage de MongoDB (5 secondes)...
timeout /t 5 /nobreak >nul

echo.
echo [3/4] Demarrage du Backend...
start "Kairos Backend" cmd /k "cd /d %~dp0backend && venv\Scripts\activate && python main.py"

echo.
echo [4/4] Demarrage du Frontend...
timeout /t 3 /nobreak >nul
start "Kairos Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo   Application demarree!
echo ========================================
echo.
echo Services accessibles:
echo   - Frontend: http://localhost:5173
echo   - Backend:  http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Les terminaux Backend et Frontend sont ouverts.
echo Appuyez sur une touche pour fermer ce script.
echo.
pause
