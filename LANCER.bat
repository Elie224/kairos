@echo off
echo ========================================
echo   EduVerse - Demarrage de l'application
echo ========================================
echo.

echo [1/2] Demarrage du backend...
cd backend
start "EduVerse Backend" cmd /k "venv\Scripts\activate && python main.py"
timeout /t 3 /nobreak >nul

echo [2/2] Demarrage du frontend...
cd ..\frontend
start "EduVerse Frontend" cmd /k "npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   Application demarree !
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Appuyez sur une touche pour fermer...
pause >nul






