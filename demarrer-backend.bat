@echo off
echo ========================================
echo   Demarrage du Backend Kairos
echo ========================================
echo.

cd backend

echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo.
echo Demarrage du serveur FastAPI...
echo Le serveur sera accessible sur: http://localhost:8000
echo Documentation API: http://localhost:8000/docs
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur.
echo.

python main.py

pause
